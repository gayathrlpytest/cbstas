#
# Copyright (c) 2018 Netapp pvt ltd - All Rights Reserved
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
#
# This file is part of cbsTAS project
#
# Author: Gayathri Lokesh <gayathrl@netapp.com>
#

# python imports
import glob
import yaml
import sys

# cbstas imports
from cbstas.cbstas_fw.core.cbstas_logger import get_logger
from cbstas.cbstas_fw.cbstas_gdata import config as cfg
from cbstas.cbstas_fw.core.client import Client

#inp = '/root/pytest_auto_framework/cbstas/testbeds/'
log = get_logger()

def get_all_duts_info():
    return cfg._cfg_all_dut_info

def get_csp_info():
    return cfg._cfg_all_csp_info

def get_dut_info(dut):
    return cfg._cfg_all_dut_info[dut]

def get_all_dut_handlers():
    return cfg._cfg_all_duts_obj

def get_dut_handler(dut):
    return cfg._cfg_all_duts_obj[dut]

def get_all_platforms():
    for dut in cfg._cfg_all_dut_info:
        cfg._cfg_platforms[dut] = cfg._cfg_all_dut_info[dut]['os']
    return cfg._cfg_platforms


class Testbed(Client):
    """
        This class initializes all resources mentioned in the testbed.yml
    """

    def __init__(self, path_list=None):
        """
          Purpose: Initialization code 
          Parameters :
            -> path_list :  List of all testbed paths
        """
        if path_list == None: path_list = []
        if type(path_list) == str: path_list = [path_list]

        self.all_res = []
        for path in path_list:
            self.scan_resources(path)
        self.create_duts()
        self.create_all_dut_handlers()

    def scan_resources(self, path):
        """
          Purpose: Scans all yml files in the list of path,  
                   add  resources to cfg._cfg_all_dut_info
                   and cfg._cfg_all_csp_info
          Parameters :
            -> path :  path to a directory containing host files
        """
        for yml_file in glob.glob(path + '/*.yml'):
            log.debug("Found testbed file : " + yml_file)
            file_handle = open(yml_file, 'r')
            self.all_res += yaml.load(file_handle)

    def create_duts(self):
        """
          Purpose: Seperates duts and csp info from input yml files
                   Update global dictionary _cfg_all_dut_info _cfg_all_csp_info
        """
        for a_res in self.all_res:
            if 'duts' in a_res.keys():
                for dut in a_res['duts']:
                    cfg._cfg_all_dut_info[dut['name']] = dut

            if 'csp' in a_res.keys():
                for cs in a_res['csp']:
                    cfg._cfg_all_csp_info[cs['name']] = cs

    def create_all_dut_handlers(self):
        """
          Purpose: Creates objects for all the resources of cfg._cfg_all_dut_info
        """
        for dut in cfg._cfg_all_dut_info.keys():
            log.info('*** Initializing dut -> %s ****' % dut)
            client_obj = Client(**cfg._cfg_all_dut_info[dut])
            cfg._cfg_all_duts_obj[dut] = client_obj


"""
tb = Testbed(path_list=[inp])
import pdb; pdb.set_trace()
print tb.get_all_duts_info()
#print tb.get_dut_info('master')
print cfg._cfg_all_dut_info.keys()
print cfg._cfg_all_csp_info
print '\n\n'
tb.get_all_dut_handlers()
print cfg._cfg_all_duts_obj
print cfg._cfg_all_duts_obj['master']
ssh_obj = cfg._cfg_all_duts_obj['ontap1']
import pdb; pdb.set_trace()
self.shell_obj.invoke_shell
print ssh_obj.run_shell('hostname')['raw_output']
print ssh_obj.run_shell('date')['raw_output']
print ssh_obj.run_shell('?')['raw_output']
print ssh_obj.run_shell('set -privilege admin')
print ssh_obj.run_shell('?')['raw_output']
"""
