# -*- coding: utf-8 -*-
'''
Module to provide Saptune functionality to Salt

.. versionadded:: pending

:maintainer:    Dario Maiocchi <dmaiocchi@suse.com>
:maturity:      alpha
:depends:       ``saptune`` Python module
:platform:      all

:configuration: This module requires the saptune python module and uses the
    following defaults which may be overridden in the minion configuration:

.. code-block:: yaml
 TODO
'''

# Import Python libs
from __future__ import absolute_import, unicode_literals, print_function
import logging

from salt import exceptions
import salt.utils.path


__virtualname__ = 'saptune'

SAPTUNE_BIN = '/usr/sbin/saptune'

LOGGER = logging.getLogger(__name__)

def __virtual__():
    '''
    Only load this module if crm package is installed
    '''
    if bool(salt.utils.path.which(SAPTUNE_BIN)):
        return __virtualname__

    else:
        return (
            False,
            'The saptune execution module failed to load: the saptune package'
            ' is not available.')



def apply_solution(solution_name):
    '''
    Tune system for all notes applicable to your SAP solution:


    CLI Example:

    .. code-block:: bash

        salt '*' saptune.apply_solution solution-name
    '''
    cmd = '{0} solution apply {1}'.format(SAPTUNE_BIN, solution_name)
    return __salt__['cmd.retcode'](cmd)
