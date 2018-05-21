###################################################################################################
# Copyright (c) 2018 NetApp, Inc.
# All rights reserved
#
#
# Testcases:
# +++++++++
#     - test_create_vserver : Create vservers on ontap
#     - test_get_vservers : Get vservers on ontap
#
#
# Test Feature:
# ++++++++++++
#     Ontap lrse
#
#
# Test case URL:
# +++++++++++++
#     <Testrail or qtest url>
#
#
# Topology:
# ++++++++
#
#  - <Work in progress>
#
#                       +-------------+          +--------------+
#                       |             |          |              |
#                ------ |    Master   |----------|     Worker   |
#                       |             |          |              |
#                       +-------------+          +--------------+
#
#
# Run-Time:
# ++++++++
#
#
# Authors:
# +++++++
#     gayathrl@netapp.com
#     xxxx@netapp.com
#
#
# Modification/Date/Reason:
# +++++++++++++++++++++++++
#
###################################################################################################

# python imports
import pytest
import time

# cbstas imports
from cbstas.cbstas_fw.core.cbstas_logger import get_mod_logger
from cbstas.cbstas_fw.core.testbed import get_all_dut_handlers, get_dut_handler

log = get_mod_logger(__name__)


# module setup/teardown
@pytest.fixture(scope="module")
def module_setup(request, pre_test):
    """ Module level setup/teardown """

    log.info('Module setup')
    log.info('Get device handlers')
    all_dut = get_all_dut_handlers()
    log.info(all_dut)

    global ontap1, master
    ontap1 = all_dut['ontap1']
    master = get_dut_handler('master')

    # module cleanup
    # clear the global configs if any
    def module_teardown():
        """ Module level deconfig/cleanup/teardown """
        log.info('Module teardown')

    request.addfinalizer(module_teardown)


# testcase
def test_create_vserver(request, module_setup):
    """ Testcase level configs/setup """

    log.info('Create vservers on %s ' % ontap1.name)
    assert (ontap1.run_shell('hostname') != -1)
    assert (ontap1.run_shell('version') != -1)

    log.info('Execute cmds on %s ' % ontap1.name)
    cmdlist = [
        'hostname', 'version', 'set -confirmations off', 'set -privilege test',
        '?', 'volume show', 'vserver show'
    ]
    for cmd in cmdlist:
        assert (ontap1.run_shell(cmd) != -1)

#    assert (ontap1.vserver_create(
#        vserver_name='test_cbs', aggregate=ontap1.aggregates[0]) != -1)

    time.sleep(10)

    def teardown():
        """ Testcase deconfig/cleanup/teardown """
        log.info('Testcase teardown/cleanup')

    request.addfinalizer(teardown)


# testcase
def test_get_vservers(request, module_setup):
    """ Testcase level configs/setup """

    log.info('Get vservers on %s ' % ontap1.name)
    assert (ontap1.run_shell('hostname') != -1)
    assert (ontap1.get_ontap_node() != -1)
    assert (ontap1.show_version() != -1)
    assert (ontap1.get_vserver_list() != -1)

    time.sleep(10)

    def teardown():
        """ Testcase deconfig/cleanup/teardown """
        log.info('Testcase teardown/cleanup')

    request.addfinalizer(teardown)
