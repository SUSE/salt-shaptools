# -*- coding: utf-8 -*-
'''
Module to provide SAP tools functionality to Salt

.. versionadded:: pending

:maintainer:    Simranpal Singh <sisingh@suse.com>
:maturity:      alpha
:depends:       ``shaptools`` Python module
:platform:      all

:configuration: This module requires the shaptools package
'''


# Import Python libs
from __future__ import absolute_import, unicode_literals

from salt import exceptions

# Import third party libs
try:
    from shaptools import saputils
    HAS_SAPUTILS = True
except ImportError:  # pragma: no cover
    HAS_SAPUTILS = False

__virtualname__ = 'sapcar'


def __virtual__():  # pragma: no cover
    '''
    Only load this module if shaptools python module is installed
    '''
    if HAS_SAPUTILS:
        return __virtualname__
    return (
        False,
        'The sapcar execution module failed to load: the shaptools python'
        ' library is not available.')


def extract(
        sapcar_exe,
        sar_file,
        output_dir=None,
        options=None):
    '''
    Extract a SAP sar archive

    sapcar_exe_file
        Path to the SAPCAR executable file. SAPCAR is a SAP tool to extract SAP SAR format archives 
    sar_file
        Path to the sar file to be extracted
    output_dir
        Location where to extract the SAR file
    options:
        Additional parameters to the SAPCAR tool
    '''
    try:
        return saputils.extract_sapcar_file(
            sapcar_exe=sapcar_exe, sar_file=sar_file, output_dir=output_dir, options=options)
    except saputils.SapUtilsError as err:
        raise exceptions.CommandExecutionError(err)
