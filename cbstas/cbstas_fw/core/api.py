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
import types
import importlib
import imp
import glob
import os
import sys
from jinja2 import Template

# cbstas imports
from cbstas.cbstas_fw.cbstas_gdata import config as cfg
from cbstas.cbstas_fw.core.cbstas_logger import get_logger, get_mod_logger

log = get_logger()
meta_api_class_inited = False

class USER_API_BINDER(object):
    """
    It represents the user api and takes care of its invocation.

    Attributes:
        name (str): user API function name
        method (function object): user API function object
        api (object): user API class instance
    """

    def __init__(self, api_name, method, user_api):
        self.name = api_name
        self.method = method
        self.api = user_api

    def issue_user_api(self, *args, **kwargs):
        """
        Invokes the user api.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        dut = args[0]
        args = args[1:]
        return dut.invoke_user_api(self.name, self.api, *args, **kwargs)

    def get_api(self):
        return self.api

    def get_api_name(self):
        return self.name


def api_bind_with_dut(dut):
    """
    Attaches the user API to the dut based on its platform

    Args:
        dut (object): cbsTASDUT object

    Returns:
        True if name exists in the platform api dict and bind success
    """

    cbstas_logger = get_logger('cbsTAS')
    # get the API binder for this platform, if not create one
    platform = dut.os
    # Check in cfg._cfg_user_extended_api dict
    if platform in cfg._cfg_user_extended_api:
        for api in cfg._cfg_user_extended_api[platform]:
            #cbstas_logger.info('Adding method %s -> %s' % (api, dut.name))
            sa  = cfg._cfg_user_extended_api[platform][api]
            try:
                setattr(dut, sa.name, types.MethodType(sa.issue_user_api, dut))
            except:
                cbstas_logger.error('Error adding method %s -> %s' %
                                   (sa.name, dut.name))
                return False
    else:
        cbstas_logger.info('No APIs to bind dut: {0} -> platform: {1}'.format(dut.name,platform))


def bind_user_apis(lib_list):
    """
    Dynamically imports python modules present in a list of directories.
    Class definitions getting appeared during import will get created using
    'cbsTASAPIMeta' metaclass i.e cbsTASAPIMeta constructor will get called 
    for each class definition.

    Args:
        lib_list (list): list of paths carrying user API modules
    """
    cbstas_logger = get_logger('cbsTAS')
    for lib_dir in lib_list:
        # Add the user-lib path so that user can import local files
        if lib_dir not in sys.path:
            sys.path.append(lib_dir)
        for dirName, subdirList, fileList in os.walk(lib_dir):
            for f in fileList:
                mod_name, file_extension = os.path.splitext(f)
                if file_extension != '.py':
                    continue
                try:
                    cbstas_logger.debug('API module: %s (%s)' %
                                       (mod_name.ljust(12), dirName))
                    fname = os.path.join(dirName, f)
                    mod = imp.load_source(mod_name, fname)
                except Exception, e:
                    cbstas_logger.error('Failed to import module %s: %s' %
                                       (mod_name, e))


def create_user_api_binder(plist, api_name, method, user_api):
    """
    Creates USER_API_BINDER object for a user api.

    Args:
        plist (list): list of platforms
        api_name (str): user API name
        method (function object): function object of the api
        user_api (object): instance of the user API class
    """
    api_binder = USER_API_BINDER(api_name, method, user_api)
    cbstas_logger = get_logger('cbsTAS')
    if plist == None:
        cfg._cfg_user_extended_api['all'][api_name] = api_binder
        cbstas_logger.debug("API %s (ALL)" % (api_name.ljust(32)))
    else:
        for p in plist:
            cbstas_logger.debug("API %s (%s)" % (api_name.ljust(32), p))
            if p in cfg._cfg_user_extended_api:
                cfg._cfg_user_extended_api[p][api_name] = api_binder
            else:
                cfg._cfg_user_extended_api[p] = {}
                cfg._cfg_user_extended_api[p][api_name] = api_binder


# Identity decorator to convert any function to API
def cbsTASUserAPI_Bind(user_api):
    """
    Decorator to bind specific user APIs. func_name of user_api
    will be renamed to __cbstas_user_extend_api_wrapper__.

    Args:
        user_api (function object): function object
    """
    def __cbstas_user_extend_api_wrapper__(self, dut, *args, **kwargs):
        user_api(self, dut, *args, **kwargs)

    return __cbstas_user_extend_api_wrapper__


class cbsTASAPIMeta(type):
    """
    API meta class.
    """

    def __init__(cls, name, bases, attrs):
        """
        Called when a cbsTASUserAPI derived class is imported.

        Args:
            cls (class object): user api class object
            name (str): user api class name
            bases (tuple): parent classes if any
            attrs (dict): class atrributes
        """

        global meta_api_class_inited
        if meta_api_class_inited == False:
            # Called when the metaclass is first instantiated
            meta_api_class_inited = True
        else:
            # Called when a cbsTASUserAPI class is imported - Register it
            try:
                plist = attrs['OS']
            except:
                plist = None
            try:
                bind_all = attrs['bind_all']
            except:
                bind_all = True
            # Instantiate the user-api object, extract all methods known to us
            user_api = cls()
            for mname, method in cls.__dict__.items():
                if type(method) == types.FunctionType:
                    if mname[:2] == '__' and mname[-2:] == '__':
                        continue
                    if bind_all == True:
                        create_user_api_binder(plist, mname, method, user_api)
                    elif method.__name__ == "__cbstas_user_extend_api_wrapper__":
                        create_user_api_binder(plist, mname, method, user_api)


class cbsTASUserAPI_Class(object):
    """
    User API classes inheriting this class will get created using 
    'cbsTASAPIMeta' metaclass. All API classes are bound to inherit
    this class; else those APIs won't get attached to dut object in runtime.
    """
    __metaclass__ = cbsTASAPIMeta

