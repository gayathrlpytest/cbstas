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

from cbsTAS.core.cbstas_logging import get_logger


# This is the entrypoint of the script - cbsats requires this
def start_user(**kwargs):

    cbsats_logger = get_logger('cbsATS')

    cbsats_logger.info("Internal pytest user script: %s", __file__)
    cbsats_logger.info(kwargs['TEST_PARAM'])
    opts = kwargs['TEST_PARAM']
    dirs = opts['dirs']
    if type(dirs) != list:
        dirs = dirs.split()

    params = opts['params']
    if type(params) != list:
        params = params.split()
        temp_params = []
        for i, param in enumerate(params):
            if param[0] != '-':
                temp_params[-1] += ' ' + param
            else:
                temp_params.append(param)
        params = temp_params

    # Setup Args for pytest
    sys.argv = ['runtest'] + params

    # Tell where to pick tests and in which order
    for d in dirs:
        sys.argv.append(d)

    # START TESTING
    res = main()
    cbsats_logger.info("user script Done")

    # Done
    return res


if __name__ == '__main__':
    sys.exit(1)

