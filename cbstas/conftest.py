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
import os
import sys
import time
from colors import blue

# pytest imports
import pytest
from _pytest.terminal import TerminalReporter
#from _pytest.config import get_config
from pluggy import HookspecMarker
hookspec = HookspecMarker("pytest")

# cbsTAS imports
from cbstas.cbstas_fw.core.cbstas_logger import get_logger, get_mod_logger, get_run_id, get_out_dir
from cbstas.cbstas_fw.core.cbstas_init import gen_run_id, cbstas_fw_init
from cbstas.cbstas_fw.core.testbed import get_all_duts_info

log = get_logger(__name__)

def pytest_addoption(parser):
    parser.addoption(
        '--basedir',
        action='store',
        dest='basedir',
        help='Base cbstas repo path')
    parser.addoption(
        '--testbed',
        action='store',
        dest='testbed',
        help='Testbed path - yml ')
    parser.addoption(
        '--outdir',
        action='store',
        dest='outdir',
        help='Dir for saving test run-logs of all types')


def pytest_configure(config):
    sys.path.append(config.option.basedir)
    from cbstas.cbstas_fw.cbstas_gdata import config as cfg
    global cfg
    config.option.importmode = 'append'
    config.option.self_contained_html = 'True'
    run_id = gen_run_id()
    if config.option.outdir != None:
        cfg._cfg_out_dir = config.option.outdir + '/RUN_' + run_id
        os.mkdir(cfg._cfg_out_dir)

        config.option.htmlpath = cfg._cfg_out_dir + '/run.html'
        config.option.xmlpath = cfg._cfg_out_dir + '/run.xml'
        config.option.log_file = cfg._cfg_out_dir + '/run.log'
    #config.option.confcutdir = config.option.basedir + '/cbstas/conftest.py'
    config.option.log_format = '[%(asctime)s], %(levelname)s, %(filename)s, %(funcName)s, %(lineno)d  ::  %(message)s'
    config.option.log_level = 'INFO'
    config.option.log_date_format = '%Y-%m-%d %H:%M:%S'
    config.option.log_file_format = '[%(asctime)s], %(levelname)s, %(filename)s, %(funcName)s, %(lineno)d  ::  %(message)s'
    config.option.log_file_level = 'DEBUG'
    config.option.log_file_date_format = '%Y-%m-%d %H:%M:%S'
    config.option.log_cli = True
    config.option.log_cli_format = '[%(asctime)s], %(levelname)s, %(filename)s, %(funcName)s, %(lineno)d  ::  %(message)s'
#    config.option.log_cli_level = 'DEBUG'
#    config.option.log_cli_level = 'INFO'
    config.option.log_cli_date_format = '%Y-%m-%d %H:%M:%S'


def pytest_report_header(config):
    st = '\n===> LOG DIR  : {0} \n'.format(config.option.log_file)
    st += '===> HTML DIR : {0}  \n'.format(config.option.htmlpath)
    st += '===> XML DIR  : {0} \n'.format(config.option.xmlpath)
    return blue(st)


def pytest_runtest_setup(item):
    cfg._cfg_module = item.module.__name__
    mod_log = get_mod_logger(cfg._cfg_module)
    mod_log.info('{0}'.format('=' * 80))
    msg = 'STARTED : {0} '.format(item.name)
    mod_log.info('{0}'.format(msg.center(75, ' ')))
    mod_log.info('{0}'.format('=' * 80))

def pytest_unconfigure(config):
    """ called before test process is exited."""
    if config.option.log_file:
        TerminalReporter(config).write('\n')
        TerminalReporter(config).write_sep(
            '-', 'generated log file: ' + config.option.log_file)
        TerminalReporter(config).write('\n\n')

@hookspec(firstresult=True)
def pytest_report_teststatus(report):
    """ return result-category, shortletter and verbose word for reporting.
    Stops at first non-None result, see :ref:`firstresult` """
    report.toterminal


def pytest_terminal_summary(terminalreporter, exitstatus):
    """Add a section to terminal summary reporting. TBD """
    pass

@pytest.fixture(scope='session')
def pre_test(request):
    """
    Session/RUNID level configs/setup
    """
    log.info('Executing Pre-test ')
    log.info('Initialize framework!!')

    input_dict = {}
    input_dict['iniconfig'] = request.config.option
    input_dict['dut_info'] = get_all_duts_info()
    input_dict['outdir'] = get_out_dir()
    input_dict['run_id'] = get_run_id()
    input_dict['basetemp'] = request.config.option.basedir
    input_dict['tb_path'] = request.config.option.testbed
    input_dict['user_lib'] = input_dict['basetemp'] + '/cbstas/userlib/'

    cbstas_fw_init(**input_dict)

    def post_test():
        """
        Session level deconfig/cleanup/teardown
        """
        log.info('Executing Post test')

    request.addfinalizer(post_test)
