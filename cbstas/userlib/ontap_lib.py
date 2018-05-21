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

# python imports
import re

# cbstas imports
from cbstas.cbstas_fw.core.cbstas_logger import get_logger, get_mod_logger
from cbstas.cbstas_fw.cbstas_gdata import config as cfg
from cbstas.cbstas_fw.core.api import cbsTASUserAPI_Class

log = get_logger()
if cfg._cfg_module:
    log = get_mod_logger(cfg._cfg_module)

# All methods of this class bind to ontap devices
class ONTAP(cbsTASUserAPI_Class):

    OS = ['ontap']
    def __init__(self):
        self.delimiter = ':::'
        self.privilege = 'test'

    def get_aggregates(self, dut, *args, **kwargs):
        """
        Purpose : To retrieve aggregate from user defined list

        Syntax  :  get_aggregates(aggregates)

        Args : 
            aggregates -- (Mandatory) List of aggregates

        Returns :
            returns  aggregate_list
                     -1  -- failure

        Author : 
            gayathrl@netapp.com

        Modifications(user-date-reason) :
        """

        aggregates = args[0]

        aggregate_list = list()

        if type(aggregates) is not list:
            aggregates = [aggregates]

        results = dut.run_shell("aggr show")

        for aggr in aggregates:
            add_to_list = None

            for element in results:
                if element['aggregate'] == aggr:
                    add_to_list = aggr

            if add_to_list is not None:
                aggregate_list.append(add_to_list)

        if not len(aggregate_list):
            log.error('Testbed yml file error please verify')
            return -1

        return aggregate_list

    def get_ontap_node(self, dut, *args, **kwargs):
        """
        Get node name

        :return: String, node name
        """
        return dut.name

    def show_version(self, dut, *args, **kwargs):
        """
        Returns the ontap running version
        """
        return dut.run_shell("version") 

    def get_vserver_list(self, dut, *args, **kwargs):
        """Returns a dictionary of vservers, and associated root volumes
        present on the system.
        """

        result = self.run_cmd(dut, "vserver show")
        vserver_list = dict()
        for element in result:
            if element['type'] == "data":
                vserver_list[element['vserver']] = element['rootvolume']

        log.info("Vservers present on the system:: %s" %(vserver_list))
        return vserver_list

    def _get_cmd_prefix(self, return_raw=False):
        """ This function sets the prefix to turn off confirmations,
        get output seperated by delimiter.
        """

        prefix_cmd = 'set -confirmations off;'
        prefix_cmd += 'set -privilege ' + self.privilege +';'
        if not return_raw:
            prefix_cmd += 'set -showallfields true ;'
            prefix_cmd += 'set -showseparator ' + self.delimiter  + ';'
        return prefix_cmd

    def run_cmd(self, dut, cmd, return_raw=False, timeout=300,
                raise_error=True, bg=False, outfile=None):
        """ Establishes the ssh connection, runs the command, and gets the
        output.
        """

        run_cd = self._get_cmd_prefix(return_raw) + cmd
        log.info("Executing command '{0}'" . format(run_cd));

        raw_output = dut.run_shell(cmd = run_cd,
                                    timeout = timeout,
                                    raise_error = raise_error,
                                    bg = bg,
                                    outfile = outfile)
        if return_raw:
            return raw_output
        else:
            if re.search('Error: ', raw_output['raw_output']) and raise_error:
                raise ExecutionError(raw_output['raw_output'])
            return self.parse_cmd_output(raw_output['raw_output'])

    def parse_cmd_output(self, output):
        """
        Purpose : parse the output got from the ontap, which is delimeter seperated

        Syntax  :  parse_cmd_output(output)

        Args : 
            output -- (Mandatory) raw_output of command exceution

        Returns :
            list of dictionaries, -1 on failure

        Author : 
            gayathrl@netapp.com

        Modifications(user-date-reason) :
        """

        table = list()
        header = list()
        lines = output.strip().split('\n')

        # If the table is empty, return an empty dictionary
        if 'This table is currently empty' in output or\
           'There are no entries matching your query.' in output:
            return dict()

        # If the output is just a message. For instance if we run a create
        # command it will return a single line with the job id (shown below):
        # [Job 665] Job succeeded: Successful
        if len(lines) <= 2:
            return lines

        log.info("output length " + str(len(lines)))
        header = lines.pop(0).split(self.delimiter)[:-1]
        # Remove the next line, because it repeats the header...
        lines.pop(0)

        #for line in lines:
        for line in range(0,len(lines)):
            # Parse line on delimiter
            output_split = lines[line].split(self.delimiter)[:-1]

            table.append(dict())
            for i in range(0,len(header)):
                table[line][header[i]] = output_split[i]

        return table

