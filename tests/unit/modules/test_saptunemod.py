
# -*- coding: utf-8 -*-
'''
    :codeauthor: Dario Maiocchi <dmaiocchi@suse.com>
'''

# Import Python Libs
from __future__ import absolute_import, print_function, unicode_literals

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
import salt.modules.saptunemod as saptune


class SaptuneModuleTest(TestCase, LoaderModuleMockMixin):
    '''
    This class contains a set of functions that test salt.modules.saptune.
    '''

    def setup_loader_modules(self):
        return {saptune: {}}

    @mock.patch('salt.utils.path.which')
    def test_virtual_saptune(self, mock_which):
        mock_pkg_version = MagicMock(return_value='2.0.0')
        mock_pkg_version_cmp = MagicMock(return_value=2)
        mock_which.return_value = True
        with patch.dict(saptune.__salt__, {
                'pkg.version': mock_pkg_version,
                'pkg.version_cmp': mock_pkg_version_cmp}):
            assert saptune.__virtual__() == 'saptune'

        mock_which.return_value = False
        assert saptune.__virtual__() == (
            False, 'The saptune execution module failed to load: the saptune'
                   ' package is not available, or the version is older than 2.0.0')
    # test_lower_then_supported_version
        mock_pkg_version = MagicMock(return_value='1.0.0')
        mock_pkg_version_cmp = MagicMock(return_value=2)
        mock_which.return_value = True
        with patch.dict(saptune.__salt__, {
                'pkg.version': mock_pkg_version,
                'pkg.version_cmp': mock_pkg_version_cmp}):
            assert saptune.__virtual__() == 'saptune'

        mock_which.return_value = False
        assert saptune.__virtual__() == (
            False, 'The saptune execution module failed to load: the saptune'
            ' package is not available, or the version is older than 2.0.0')

    def test_is_solution_applied(self):
        '''
        Test is_solution_applied method
        '''

        builtin_name = "salt.utils.files.fopen"

        sol_name = "foo"
        file_content = "TUNE_FOR_SOLUTIONS=\"foo\""
        with patch(builtin_name, mock_open(read_data=file_content)) as mock_file:
            assert saptune.is_solution_applied(sol_name)
            #mock_file.assert_called_once_with(saptune.SAPTUNE_CONF)

        file_content = "TUNE_FOR_SOLUTIONS=\"baz\""
        with patch(builtin_name, mock_open(read_data=file_content)) as mock_file:
            assert not saptune.is_solution_applied(sol_name)
            #mock_file.assert_called_once_with(saptune.SAPTUNE_CONF)

    def test_apply_solution(self):
        '''
        Test apply solution method
        '''
        mock_cmd = MagicMock(return_value=True)
        with patch.dict(saptune.__salt__, {'cmd.retcode': mock_cmd}):
            assert saptune.apply_solution('foo')

    def test_apply_solution_false(self):
        '''
        Test apply solution method
        '''
        mock_cmd = MagicMock(return_value=False)
        with patch.dict(saptune.__salt__, {'cmd.retcode': mock_cmd}):
            assert not saptune.apply_solution('foo_false')
