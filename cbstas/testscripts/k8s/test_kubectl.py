###################################################################################################
# Copyright (c) 2018 NetApp, Inc.
# All rights reserved
#
#
# Testcases:
# +++++++++
#     - test_get_nodes: Get node details in k8s
#     - test_get_all_namespaces: Get k8s all namespaces
#
#
# Test Feature:
# ++++++++++++
#     kubectl
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
    global master
    master = get_dut_handler('master')

    # module cleanup
    # clear the global configs if any
    def module_teardown():
        """ Module level deconfig/cleanup/teardown """
        log.info('Module teardown')

    request.addfinalizer(module_teardown)


# testcase
def test_get_nodes(request, module_setup):
    """ Testcase level configs/setup """

    log.info('Get nodes in k8s cluster on %s ' % master.name)
    assert (master.run_shell('hostname') != -1)
    assert (master.run_shell('kubectl get nodes') != -1)

    time.sleep(10)

    def teardown():
        """ Testcase deconfig/cleanup/teardown """
        log.info('Testcase teardown/cleanup')
        pytest.fail(msg='Failing test intentionally', pytrace=True)

    request.addfinalizer(teardown)


# testcase
def test_get_all_namespaces(request, module_setup):
    """ Testcase level configs/setup """

    log.info('Get k8s all namespaces on %s ' % master.name)
    assert (master.run_shell('hostname') != -1)
    assert (master.run_shell('kubectl get pods --all-namespaces') != -1)

    time.sleep(10)

    def teardown():
        """ Testcase deconfig/cleanup/teardown """
        log.info('Testcase teardown/cleanup')

    request.addfinalizer(teardown)
