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
import uuid

# cbstas imports
from cbstas.cbstas_fw.core import _set_framework_anchor
from cbstas.cbstas_fw.core.cbstas_logger import get_logger
from cbstas.cbstas_fw.cbstas_gdata import config as cfg
from cbstas.cbstas_fw.core.testbed import Testbed, get_all_dut_handlers, get_all_platforms, get_all_duts_info
from cbstas.cbstas_fw.core.api import bind_user_apis, api_bind_with_dut

log = get_logger()

def gen_run_id(ts=None):
    """
      Generates a unique run-id
      It uses unique-id facility of python/unix and extracts first 8 bytes out
      the id. This provides a unique string that can be used to create unique
      directory for output of each test run. Such a scheme helps user to easily
      invoke cbstas and and not worry about output being overwritten accidently.

      Args:
        ts (float): Timestamp (usually) or a float number appened to uuid

      Returns:
        rid (str): A unique string that can be used as output dir name
    """

    rid = str(uuid.uuid4()).replace('-', '')[:8]
    if ts:
        rid = '%s_%s' % (ts.strftime('%Y%m%d_%H%M%S'), rid)
    cfg._cfg_run_id = rid.upper()
    return rid.upper()


def cbstas_fw_init(**kwargs):
    """
        Initialzie framework objects and handlers
    """

    log.info('\n')
    log.info('ALL INPUTS : {0} '.format(kwargs))
    log.info('\n')
    log.info('RUN ID : {0}'.format(kwargs['run_id']))
    log.info('OUTPUT DIR : {0}'.format(kwargs['outdir']))
    log.info('BASE REPO PATH : {0}'.format(kwargs['basetemp']))
    log.info('TESTBED YML PATHS: {0}'.format(kwargs['tb_path']))
    log.info('USER LIB PATH: {0}\n'.format(kwargs['user_lib']))

    #  get all dut handlers
    log.info('CREATE DEVICE HANDLERS \n')
    tb = Testbed(path_list = kwargs['tb_path'])
    log.info('\n')
    log.info(get_all_duts_info())
    log.info('\n')
    log.info('\n')

    all_dut_handlers = get_all_dut_handlers()
    
    # bind user api's with their platforms
    log.info("Bind user api's with their platforms")
    user_lib = kwargs['user_lib']
    if type(kwargs['user_lib']) is str:
        user_lib = [user_lib]
    bind_user_apis(user_lib)

    log.info("Bind platform api's with dut")
    for handler in all_dut_handlers.values():
        api_bind_with_dut(handler)


     

