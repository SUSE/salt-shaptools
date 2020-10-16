
# -*- coding: utf-8 -*-
'''
    :codeauthor: Simranpal Singh <sisingh@suse.com>
'''
# Import Python libs
from __future__ import absolute_import, unicode_literals, print_function

from salt import exceptions

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import skipIf, TestCase
from tests.support import mock
from tests.support.mock import (
    MagicMock,
    patch
)

# Import Salt Libs
import salt.states.sapcarmod as sapcar


class SapcarmodTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.states.sapcarmod
    '''
    def setup_loader_modules(self):
        return {sapcar: {'__opts__': {'test': False}}}

    def test_available_test(self):
        '''
        Test to check extracted in test mode
        '''

        ret = {'name': '/sapmedia/IMDB_SERVER_LINUX.SAR',
               'changes': {'output_dir': '/sapmedia'},
               'result': None,
               'comment': '/sapmedia/IMDB_SERVER_LINUX.SAR would be extracted'}

        with patch.dict(sapcar.__opts__, {'test': True}):
            assert sapcar.extracted(
                name='/sapmedia/IMDB_SERVER_LINUX.SAR',  output_dir='/sapmedia',
                sapcar_exe='/sapmedia/SAPCAR')

    def test_extracted_basic(self):
        '''
        Test to check extracted when sapcar successfully extracts a sar file
        '''

        expected_ret = {
            'name': '/sapmedia/IMDB_SERVER_LINUX.SAR',
            'changes': {'output_dir': '/sapmedia'},
            'result': True,
            'comment': '/sapmedia/IMDB_SERVER_LINUX.SAR file extracted'
        }

        mock_extract = MagicMock()
        with patch.dict(sapcar.__salt__, {
                'sapcar.extract': mock_extract}):
            assert sapcar.extracted(
                name='/sapmedia/IMDB_SERVER_LINUX.SAR',  output_dir='/sapmedia',
                sapcar_exe='/sapmedia/SAPCAR') == expected_ret
        mock_extract.assert_called_once_with(
            sapcar_exe='/sapmedia/SAPCAR', sar_file='/sapmedia/IMDB_SERVER_LINUX.SAR',
            output_dir='/sapmedia', options=None)

    def test_extracted_error_exception(self):
        '''
        Test to check extracted when sapcar fails to extracts a sar file
        '''

        expected_ret = {
            'changes': {},
            'result': False,
            'name': '/sapmedia/IMDB_SERVER_LINUX.SAR',
            'comment': 'sapcar error'
        }

        mock_extract = MagicMock(side_effect=exceptions.CommandExecutionError('sapcar error'))
        with patch.dict(sapcar.__salt__, {
                'sapcar.extract': mock_extract}):
            assert sapcar.extracted(
                '/sapmedia/IMDB_SERVER_LINUX.SAR','/sapmedia/SAPCAR', options='-v') == expected_ret
        mock_extract.assert_called_once_with(
            sapcar_exe='/sapmedia/SAPCAR', sar_file='/sapmedia/IMDB_SERVER_LINUX.SAR',
            output_dir=None, options='-v')
