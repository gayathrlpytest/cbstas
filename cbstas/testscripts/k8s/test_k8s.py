# python imports
import pytest
import time

# cbstas imports
from cbstas.cbstas_fw.core.cbstas_logger import get_mod_logger
from cbstas.cbstas_fw.core.testbed import get_all_dut_handlers

log = get_mod_logger(__name__)

# module setup/teardown
@pytest.fixture(scope="module")
def module_setup(request, pre_test):
    """
      Module level configs/setup
    """
    log.info('Module level setup')
    log.info('Get device handlers for ontap1 and master')
    all_dut = get_all_dut_handlers()
    global ontap1, master
    ontap1 = all_dut['ontap1']
    master = all_dut['master']

    def module_teardown():
        """
          Module level deconfig/cleanup/teardown
        """
        log.info('Module level teardown')

    request.addfinalizer(module_teardown)


# test_1
def test_1(request, module_setup):
    """
      Testcase level configs/setup
    """
    log.info('test_1 setup')

    log.info('Execute cmds on %s ' % ontap1.name)
    cmdlist = [
        'hostname', 'version', 'set -confirmations off', 'set -privilege test', '?',
        'volume show', 'vserver show'
    ]
    for cmd in cmdlist:
        assert (ontap1.run_shell(cmd) != -1)

    log.info('Execute cmd on %s ' % master.name)
    cmdlist = [
        'hostname', 'kubectl get nodes', 'kubectl get pods --all-namespaces'
    ]
    for cmd in cmdlist:
        assert (master.run_shell(cmd) != -1)

    time.sleep(10)

    def teardown_1():
        """
          Testcase level deconfig/cleanup/teardown
        """
        log.info('test_1 teardown')

    request.addfinalizer(teardown_1)


# test_2
def test_2(request, module_setup):
    """
      Testcase level configs/setup
    """
    log.info('test_2 setup')
    log.info('Execute show version on ontap')
    assert (ontap1.get_ontap_node() != -1)
    assert (ontap1.show_version() != -1)
    assert (ontap1.get_vserver_list() != -1)

    time.sleep(10)

    def teardown_2():
        """
          Testcase level deconfig/cleanup/teardown
        """
        log.info('test_2 teardown')

    request.addfinalizer(teardown_2)
