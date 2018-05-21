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

from cbstas.cbstas_fw.cbstas_gdata import config as cfg

cbstas = None


def _set_framework_anchor(anchor_obj):
    global cbstas
    cbstas = anchor_obj

def _get_cbstas_handle():
    '''Since the initial value of cbstas handle is None, need this internal
       function to get it in the other parts of core'''
    global cbstas
    return cbstas

