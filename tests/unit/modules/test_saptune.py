
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
import salt.modules.saptune as saptune


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
