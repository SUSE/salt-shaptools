
# -*- coding: utf-8 -*-
'''
    :codeauthor: Dario Maiocchi <dmaiocchi@suse.com>
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
    NO_MOCK,
    NO_MOCK_REASON
)

# Import Salt Libs
import salt.modules.saptunemod as saptune


@skipIf(NO_MOCK, NO_MOCK_REASON)
class SaptuneModuleTest(TestCase, LoaderModuleMockMixin):
    '''
    This class contains a set of functions that test salt.modules.saptune.
    '''

    def setup_loader_modules(self):
        return {saptune: {}}

    @mock.patch('salt.utils.path.which')
    def test_virtual_saptune(self, mock_which):
        mock_which.side_effect = [True, True]
        assert saptune.__virtual__() == 'saptune'
        mock_which.assert_called_once_with(saptune.SAPTUNE_BIN)

    @mock.patch('salt.utils.path.which')
    def test_virtual_saptune_error(self, mock_which):

        mock_which.side_effect = [False, True]
        response = saptune.__virtual__()
        assert response == (
            False, 'The saptune execution module failed to load: the saptune package'
            ' is not available.')
        mock_which.assert_called_once_with(saptune.SAPTUNE_BIN)

    def test_is_solution_applied_return_false(self):
        '''
        Test is_solution_applied method return false
        '''
        saptune.is_solution_applied = MagicMock(return_value=False)
        assert not saptune.is_solution_applied('fakesolution')
        saptune.is_solution_applied.assert_called_once_with('fakesolution')

    def test_is_solution_applied_return_true(self):
        '''
        Test is_solution_applied method return true
        '''
        saptune.is_solution_applied = MagicMock(return_value=True)
        assert saptune.is_solution_applied('fakesolution')
        saptune.is_solution_applied.assert_called_once_with('fakesolution')

    def test_apply_solution(self):
        '''
        Test apply solution method 
        '''
        saptune.apply_solution = MagicMock(return_value=0)
        assert saptune.apply_solution('fakesolution') == 0
        saptune.apply_solution.assert_called_once_with('fakesolution')
