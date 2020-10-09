
# -*- coding: utf-8 -*-
'''
    :codeauthor: Simranpal Singh <sisingh@suse.com>
'''

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals
import pytest

from salt import exceptions

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import TestCase, skipIf
from tests.support import mock
from tests.support.mock import (
    MagicMock,
    patch,
    mock_open
)

# Import Salt Libs
import salt.modules.sapcarmod as sapcarmod


class SapcarModuleTest(TestCase, LoaderModuleMockMixin):
    '''
    This class contains a set of functions that test salt.modules.sapcarmod.
    '''

    def setup_loader_modules(self):
        return {sapcarmod: {}}

    @patch('salt.modules.sapcarmod.saputils.extract_sapcar_file')
    def test_extract_return(self, mock_extract):
        '''
        Test extract method - return
        '''
        mock_extract.return_value = 0
        assert sapcarmod.extract('/sapmedia/SAPCAR','/sapmedia/IMDB_SERVER_LINUX.SAR', '/sapmedia/HANA', '-v') == 0
        mock_extract.assert_called_once_with(
            sapcar_exe='/sapmedia/SAPCAR', sar_file='/sapmedia/IMDB_SERVER_LINUX.SAR',
            output_dir='/sapmedia/HANA', options='-v')

    @patch('salt.modules.sapcarmod.saputils.extract_sapcar_file')
    def test_extract_raise(self, mock_extract):
        '''
        Test extract method - raise
        '''
        mock_extract.side_effect = sapcarmod.saputils.SapUtilsError('error')
        with pytest.raises(exceptions.CommandExecutionError) as err:
            sapcarmod.extract('/sapmedia/SAPCAR','/sapmedia/IMDB_SERVER_LINUX.SAR', '/sapmedia/HANA', '-v')
        mock_extract.assert_called_once_with(
            sapcar_exe='/sapmedia/SAPCAR', sar_file='/sapmedia/IMDB_SERVER_LINUX.SAR',
            output_dir='/sapmedia/HANA', options='-v')
