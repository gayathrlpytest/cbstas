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
        args, kwargs = invoke_pre_pluggin(self, dut, args, kwargs)
        return dut.user_extended_api(self.name, self.api, *args, **kwargs)

    def get_api_group(self):
        return None

    def get_api_desc(self):
        return None

    def get_api(self):
        return self.api

    def get_cli(self):
        return self.api

    def get_api_name(self):
        return self.name

    def get_api_tpl_fname(self):
        return None

def api_generate_plaform(platform):
    """
    Creates 'API_BINDER' object for all CLIs specific to a platform.

    Args:
        platform (str): platform name

    Returns:
        dict: dictionary of cli name and its 'API_BINDER' object 
    """
    cbstas_logger = get_logger('cbsTAS')
    # Get the platform API-list: common, specific to the platform
    import pdb; pdb.set_trace()
    plat_obj = cfg._cfg_platforms[platform]
#    plat_obj = get_platform(platform)
    if plat_obj == None:
        return {}
    if plat_obj.api_list == None:
        return {}
    # Merge all the API in the platform api-list in that order
    api_platform_desc = {}
    api_desc_rev_map = {}
    for api_name in plat_obj.api_list:
        api_desc = cfg._cfg_api_desc[api_name]
        # Update the cli records, flattened out
        api_platform_desc.update(api_desc)
        # create a reverse map to get back to cli-group
        for api in api_desc:
            api_desc_rev_map[api] = api_name

    api_binder = {}
    for api in api_platform_desc:
        cli = api_platform_desc[api]['cli']
        try:
            desc = api_platform_desc[api]['desc']
        except:
            desc = None
        try:
            method = api_platform_desc[api]['method']
        except:
            method = None
        try:
            type = api_platform_desc[api]['type']
        except:
            type = None
        try:
            data = api_platform_desc[api]['data']
        except:
            data = None
        try:
            tpl = api_platform_desc[api]['tpl']
        except:
            tpl = 'null.tpl'
        try:
            timeout = api_platform_desc[api]['timeout']
        except:
            timeout = None
        try:
            group_name = api_desc_rev_map[api]
        except:
            group_name = None
        try:
            api_binder[api] = API_BINDER(api, cli, desc, method, type,
                                        data, tpl, group_name, timeout)
        except:
            cbstas_logger.error('Error creating Api Binder object for %s' % cli)
    return api_binder


def api_bind_with_dut(dut):
    """
    Attaches the CLIs and user APIs to the dut object.
    Binds the 'issue_cli' method of API_BINDER object of a cli to the dut
    object in case of CLIs.
    Binds the 'issue_user_api' method of USER_API_BINDER object of a 
    user api to the dut object in case of user APIs.

    Args:
        dut (object): cbsTASDUT object
    """
    cbstas_logger = get_logger('cbsTAS')
    # get the API binder for this platform, if not create one
    platform = dut.os
    if platform not in cfg._cfg_platform_api:
        cfg._cfg_platform_api[platform] = api_generate_plaform(platform)

    # Dynamically bind API to this DUT
    platform_binder = cfg._cfg_platform_api[platform]
    for api in platform_binder:
        # The following will create a method in DUT whose name is api
        try:
            if api in dir(dut):
                cbstas_logger.error(
                    'Invalid API name %s. It is a DUT property/method. Please use another name.'
                    % api)
                raise
            setattr(dut, api, types.MethodType(platform_binder[api].issue_cli,
                                               dut))
        except:
            cbstas_logger.error('Error adding method %s to %s' % (api, dut.name))
    for api in cfg._cfg_user_extended_api['all']:
        sa  = cfg._cfg_user_extended_api['all'][api]
        try:
            setattr(dut, sa.name, types.MethodType(sa.issue_user_api, dut))
        except:
            cbstas_logger.error('Error adding method %s to %s' %
                               (sa.name, dut.name))

    if platform in cfg._cfg_user_extended_api:
        for api in cfg._cfg_user_extended_api[platform]:
            sa  = cfg._cfg_user_extended_api[platform][api]
            try:
                setattr(dut, sa.name, types.MethodType(sa.issue_user_api, dut))
            except:
                cbstas_logger.error('Error adding method %s to %s' %
                                   (sa.name, dut.name))


def on_demand_bind_api(dut, api):
    """
    Attaches the CLI or user API to the dut object on demand.
    Binds the 'issue_cli' method of API_BINDER object of a cli to the dut
    object in case of CLIs.
    Binds the 'issue_user_api' method of USER_API_BINDER object of a 
    user api to the dut object in case of user APIs.

    Args:
        dut (object): cbsTASDUT object
        api (str): name of the API/CLI to bind

    Returns:
        True if name exists in the platform api/cli db and bind success
    """
    cbstas_logger = get_logger('cbsTAS')
    # for testing: cbstas_logger.debug('adding method %s to %s' % (api, dut.name))
    # get the API binder for this platform, if not create one
    platform = dut.get_dut_platform()
    if platform not in cfg._cfg_platform_api:
        cfg._cfg_platform_api[platform] = api_generate_plaform(platform)

    # on demand Dynamically bind API to this DUT
    platform_binder = cfg._cfg_platform_api[platform]
    # Check in specific platform CLI db
    if api in platform_binder:
        # The following will create a method in DUT whose name is api
        try:
            setattr(dut, api, types.MethodType(platform_binder[api].issue_cli,
                                               dut))
        except:
            cbstas_logger.error('Error adding method %s to %s' % (api, dut.name))
            return False
        return True
    # Check in common platform User extended api db
    if api in cfg._cfg_user_extended_api['all']:
        sa  = cfg._cfg_user_extended_api['all'][api]
        try:
            setattr(dut, sa.name, types.MethodType(sa.issue_user_api, dut))
        except:
            cbstas_logger.error('Error adding method %s to %s' %
                               (sa.name, dut.name))
            return False
        return True

    # Check in specific platform User extended api db
    if platform in cfg._cfg_user_extended_api:
        if api in cfg._cfg_user_extended_api[platform]:
            sa  = cfg._cfg_user_extended_api[platform][api]
            try:
                setattr(dut, sa.name, types.MethodType(sa.issue_user_api, dut))
            except:
                cbstas_logger.error('Error adding method %s to %s' %
                                   (sa.name, dut.name))
                return False
            return True
    # no api found in any db
    return False


def make_api(dir_list):
    """
    Converts the JSON content of CLI files to a single dict where key is
    cli-group name and value is a dict with details such as cli, desc, tpl.

    Args:
        dir_list (list): list of paths carrying CLIs (json files)

    Returns:
        dict: dictionary of all cli group names 
    """
    cbstas_logger = get_logger('cbsTAS')
    api = {}
    for dirname in dir_list:
        all_api_files = sorted(glob.glob('%s/*.json' % dirname))
        for fname in all_api_files:
            cbstas_logger.debug('API: Import CLI: %s' % fname)
            with open(fname) as f:
                data = f.read()
                api_data = cfgdb_read_data(data, f.name)
                for group in api_data:
                    if group in api:
                        api[group].update(api_data[group])
                    else:
                        api[group] = api_data[group]
    return api


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

