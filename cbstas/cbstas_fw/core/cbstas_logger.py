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

import os
import logging
import logging.handlers
from logging import Logger, LoggerAdapter
from cbstas.cbstas_fw.cbstas_gdata import config as cfg

STEP_LEVEL = 22
logging.addLevelName(STEP_LEVEL, "STEP")

class ExtraLogging(LoggerAdapter):
    '''
    Inserts extra information to the logging call of logger instance.
    '''

    def process(self, msg, kwargs):
        '''
        Method of LoggerAdapter class.
        Inserts extra information to the kwargs
        dictionary which will be passed during the logging call.
        '''
        # Simply pass on the extra
        kwargs['extra'] = self.extra
        return (msg, kwargs)


class AppLogging(Logger):
    @staticmethod
    def get_logger(logger_name='cbsTAS',
                   log_file_name=None,
                   log_level='INFO',
                   fm='',
                   fsize=8 * 1024 * 1024,
                   fcount=1024):
        '''
        Creates logger, adds file handler and stores 
        the logger instance in a dictionary which is
        accessed later by other logging related functions.
        Default severity level is set to INFO.
        '''
        # Check if the file path exists, if not create it.
        if not os.path.exists(log_file_name):
            file_path = '/'.join(log_file_name.split('/')[:-1])
            if not os.path.exists(file_path):
                os.makedirs(file_path, 0777)
            file(log_file_name, 'w').close()

        log_level = log_level.upper()
        level = eval('logging.' + log_level)

        # Initialize the logger object and return it
        my_logger = logging.getLogger(logger_name)
        formatter = logging.Formatter(fm, "%Y-%m-%d %H:%M:%S")
        # File rotate handler
        fileHandler = logging.handlers.RotatingFileHandler(
            log_file_name, mode='a', maxBytes=fsize, backupCount=fcount)
        fileHandler.setFormatter(formatter)
        my_logger.setLevel(level)
        if len(my_logger.handlers) == 0:
            my_logger.addHandler(fileHandler)
        cfg._cfg_logger_db[logger_name] = my_logger
        return

    def _i(self, msg, *args, **kwargs):
        self._I = 20
        logging.addLevelName(self._I, 'I')
        if self.isEnabledFor(self._I):
            self.log(self._I, msg, args, **kwargs)

    logging.Logger._i = _i

    def _step(self, msg, *args, **kwargs):
        """
          Internal method to add support for a special log level: step.
          This method also adds additional formatting for the STEP level
        """
        if self.isEnabledFor(STEP_LEVEL):
            decoration = '-'*60
            msg = msg.center(55, ' ')
            msg = 'STEP:' + msg
            self._log(STEP_LEVEL, decoration, args, **kwargs)
            self._log(STEP_LEVEL, msg, args, **kwargs)
            self._log(STEP_LEVEL, decoration, args, **kwargs)

    logging.Logger.step = _step


def get_logger(logger_name='cbsATS'):
    '''
    Function to get a logger instance by name specified in the create_logger.
    If name not available returns the default cbsATS logger instance.

    Args:
        logger_name: Logger name needed. Default cbsATS.
    '''
    if logger_name in cfg._cfg_logger_db:
        return cfg._cfg_logger_db[logger_name]
    if 'cbsATS' in cfg._cfg_logger_db:
        return cfg._cfg_logger_db['cbsATS']
    return logging.getLogger()


def create_logger(*args, **kwargs):
    '''
    Function to create a logger instance.

    Args:
        logger_name: Name for the logger instance.
        log_file_name: File name for the logger (Will be created under output directory).
        log_level: Severity level (Debug, Info, Warning, Error).
        fm: optional, Format String needed for the logger. Default format '[%(asctime)s], %(levelname)s, %(module)s, %(funcName)s, %(message)s'.
    '''
    if 'fm' not in kwargs:
        kwargs[
            'fm'] = '[%(asctime)s] %(levelname)s %(filename)s %(funcName)s %(lineno)s :: %(message)s'
    AppLogging.get_logger(kwargs['logger_name'], kwargs['log_file_name'],
                          kwargs['log_level'], kwargs['fm'])
    return


def get_out_dir():
    '''
    Function to get the output directory path where log files
    and other traffic gen related configuration files are saved.

    Returns:
        String: Output directory path.
    '''
    return cfg._cfg_out_dir

def get_run_id():
    '''
    Function to get the output directory path where log files
    and other traffic gen related configuration files are saved.

    Returns:
        String: Output directory path.
    '''
    return cfg._cfg_run_id

def get_log_level():
    '''
    Function to get the log level as set by user
    in test suite ini file under 'log_level'.

    Returns:
        String: Log level (Info, Debug, Warning, Error).
    '''
    return cfg._cfg_log_level


def get_mod_logger(*args):
    '''
    It creates testcase level logs. Log level is the
    specified through test suite file.
    Logs created using this object are sent to <mod_name>.log.

    Args:
        args: Name of the test module - optional.

    Returns:
        Object: Logger instance to log into dut log file.
    '''
    if len(args) > 0:
        mod_name = args[0]
    else:
        mod_name = 'none'
        if mod_name == 'none':
            log = get_logger()
            log.error('Unable to get module name')
            return None
    mod_name = mod_name.strip()
    logger_name = 'cbsATS.%s' % (mod_name)
    if logger_name not in cfg._cfg_logger_db:
        fname = os.path.join(get_out_dir(), '%s.log' % mod_name)
        create_logger(
            logger_name=logger_name,
            log_file_name=fname,
            log_level=cfg._cfg_log_level,
            fm=
            '[%(asctime)s], %(levelname)s, %(filename)s, %(funcName)s, %(lineno)d  ::  %(message)s'
        )
        log = cfg._cfg_logger_db[logger_name]
        extra = {'tc': mod_name, 'status': 'none'}
        ext_log = ExtraLogging(log, extra)
        # Overwrite with extra logger instance
        cfg._cfg_logger_db[logger_name] = ext_log.logger
    return cfg._cfg_logger_db[logger_name]
