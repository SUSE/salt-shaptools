'''
State module to provide SAP utilities functionality to Salt

.. versionadded:: pending

:maintainer:    Simranpal Singh <sisingh@suse.com>
:maturity:      alpha
:depends:       python-shaptools
:platform:      all

:configuration: This module requires the python-shaptools module

:usage:

.. code-block:: yaml
    extract_sap_car_file:
      sapcar.extracted:
      - name: home/sapuser/saprouter_600-80003478.sar
      - sapcar_exe: ./SAPCAR.exe
      - output_dir: home/sapuser/saprouter_inst
      - options: "-manifest SIGNATURE.SMF"
'''


# Import python libs
from __future__ import absolute_import, unicode_literals

# Import salt libs
from salt import exceptions
from salt.ext import six


__virtualname__ = 'sapcar'


def __virtual__():  # pragma: no cover
    '''
    Only load this module if sapcar python module is installed
    '''
    return 'sapcar.extract' in __salt__


def extracted(
        name,
        sapcar_exe,
        output_dir=None,
        options=None):
    """
    Extract a SAPCAR sar archive

    name
        SAR file name to be extracted
    sapcar_exe
        Path to the SAPCAR executable file. SAPCAR is a SAP tool to extract SAP SAR format archives 
    output_dir
        Location where to extract the SAR file. If not provided, use current directory as name
    options:
        Additional parameters to the SAPCAR tool
    """
    ret = {'name': name,
           'changes': {},
           'result': False,
           'comment': ''}

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = '{} would be extracted'.format(name)
        ret['changes']['output_dir'] = output_dir
        return ret
    
    try:
        #  Here starts the actual process
        __salt__['sapcar.extract'](
            sapcar_exe=sapcar_exe,
            sar_file=name,
            output_dir=output_dir,
            options=options)
            
        ret['changes']['output_dir'] = output_dir
        ret['comment'] = '{} file extracted'.format(name)
        ret['result'] = True
        return ret

    except exceptions.CommandExecutionError as err:
        ret['comment'] = six.text_type(err)
        return ret