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
    log.info('Get device handlers')
    all_dut = get_all_dut_handlers()
    global ontap1, master
    ontap1 = all_dut['ontap21']
    master = all_dut['master2']

    def module_teardown():
        """
          Module level deconfig/cleanup/teardown
        """
        log.info('Module level teardown')

    request.addfinalizer(module_teardown)


# test_3
def test_3(request, module_setup):
    """
      Testcase level configs/setup
    """
    log.info('test_3 setup')

    log.info('Execute cmd on ontap')
    assert (ontap1.run_shell('hostname') != -1)

    log.info('Execute cmd on master')
    cmdlist = [
        'hostname', 'kubectl get nodes', 'kubectl get pods --all-namespaces'
    ]
    for cmd in cmdlist:
        assert (master.run_shell(cmd) != -1)
    time.sleep(10)

    def teardown_3():
        """
          Testcase level deconfig/cleanup/teardown
        """
        log.info('test_3 teardown')

    request.addfinalizer(teardown_3)


# test_4
def test_4(request, module_setup):
    """
      Testcase level configs/setup
    """
    log.info('test_4 setup')
    time.sleep(10)

    def teardown_4():
        """
          Testcase level deconfig/cleanup/teardown
        """
        log.info('test_4 teardown')

    request.addfinalizer(teardown_4)
