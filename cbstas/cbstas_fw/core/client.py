#
# Copyright (c) 2018 Netapp pvt ltd - All Rights Reserved
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
#
# This file is part of cbsTAS project
#
# Author: Gayathri Lokesh <gayathrl@netapp.com> + partial pitsa code
#
"""
This is a generic client object that supports command execution through ssh.
"""
# python imports
import re
import time
import sys
import paramiko

# cbstas imports
from cbstas.cbstas_fw.cbstas_gdata import config as cfg
from cbstas.cbstas_fw.core.cbstas_logger import get_logger, get_mod_logger

log = get_logger()


class Client(object):
    def __init__(self, **kwargs):

        self.info = kwargs
        self.os = 'linux'

        self.dev_type = kwargs['type']
        if self.dev_type == 'ontap':
            device = 'cisco_ios'  # needed for netmiko
        else:
            device = 'linux'

        self.info['device'] = device

        all_keys = kwargs.keys()
        all_keys.remove('type')

        if 'timeout' in all_keys:
            all_keys.remove('timeout')
            self.timeout = kwargs['timeout']
        else:
            self.timeout = 20

        for key in all_keys:
            setting = 'self.' + key + ' = kwargs["' + key + '"]'
            unsetting = 'self.' + key + ' = None'
            try:
                exec (setting)
            except:
                exec (unsetting)

        cfg._cfg_platforms.append(self.os)  
        log.info(self.info)
        self.ssh = None
        self.open_ssh()

    def open_ssh(self):
        """ 
            Method creates a new instance of paramiko ssh object. 
        """
        log.info("Creating ssh object to {0} ".format(self.info['name']))
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if 'key' in self.info:
                key = paramiko_av.RSAKey.from_private_key_file(self.key)
                self.ssh.connect(self.ip, username=self.username, pkey=key)
            else:
                self.ssh.connect(
                    self.ip,
                    username=self.username,
                    password=self.password,
                    timeout=10)
            log.info('Created successfully..')
        except Exception as e:
            log.error('Unable to create ssh objecct: \n {0}'.format(e))

    def get_ssh_obj(self):
        return self.ssh

    def run_shell(self,
                  cmd,
                  timeout=300,
                  raise_error=True,
                  bg=False,
                  outfile=None):
        """
            Runs the command passed in, on the client's shell.
              cmd: string, command to be executed at shell

              timeout: int, time in seconds to wait for command to complete.
                       Default is 300s, unused until polling code below is done

              raise_error: boolean, if it is set then an exception will be raised
                           when run_shell encounters an error. If set to 0, 
                           no errors will be raised. Default: 1

              bg: boolean, run input cmd as a background process, default is False

              outfile: string, redirect bg command to a specified file, default is
                       /var/tmp/bg_proc_timestamp

              RETURNS :
                {
                    stdin : Terminal object to write to
                    stdout : Terminal object to read from (file-like)
                    errors : Any errors encountered
                    raw_output : Merged stdout and stderr (raw text)
                    pid : (if async=1) process id number
                    outfile : (if async=1) local path to output
                }

              EXCEPTIONS : ExecutionError
        """
        if cfg._cfg_module:
            log = get_mod_logger(cfg._cfg_module)

        log.info("Executing '{0}' on '{1}'".format(cmd, self.info['name']))
        if bg:
            if not outfile:
                outfile = " /var/tmp/bg_proc_" + str(int(time.time()))
            cmd = "( ( " + cmd + " ) > " + outfile + " 2>&1 & echo pid is $! )"
            log.info("cmd '{0}'".format(cmd))

        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        result = {'stdin': stdin, 'stdout': "", 'errors': ""}

        for line in stdout.readlines():
            result['stdout'] += line

        for line in stderr.readlines():
            result['errors'] += line

        if (result['errors'] and raise_error) or re.search(
                'error', result['stdout'], re.IGNORECASE):
            log.error(result['stdout'] + result['errors'])
            log.error('CLI rejection, needs correction or revisit......')
            return -1

        result['raw_output'] = result['stdout'] + result['errors']
        log.info("\n" + "{0}".format(result['raw_output']))

        if bg:
            find_pid = re.search("pid is (\d+)", result['stdout'])
            if find_pid:
                result['pid'] = find_pid.groups(0)[0]
            if 'pid' not in result:
                raise Exception("Unable to find background pid for cmd")

            result['outfile'] = outfile

        return result

    def run_async(self, cmd):
        """
            Allows for asynchronous execution of commands
            returns process object
        """
        log.info("Creating a new async process for : \n" + cmd)

        # Create a new channel and set it to non-blocking mode
        channel = self.ssh.get_transport().open_session()

        # Force remote process to run on a controlling terminal by
        # forcing a pseudo-tty allocation. This way we can tie the
        # lifetime of the process to that of the terminal and not
        # leave zombie processes lying around for init to cleanup
        channel.get_pty()

        channel.setblocking(0)
        channel.exec_command(cmd)

        process = Proc(channel=channel)
        return process

    def invoke_user_api(self, name, api, *args, **kwargs):
        '''Invoke the user provided method by its name'''
        user_method = getattr(api, name)
        res = user_method(self, args, kwargs)
        return res

