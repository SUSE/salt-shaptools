
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
class CrmshModuleTest(TestCase, LoaderModuleMockMixin):
    '''
    This class contains a set of functions that test salt.modules.crm.
    '''

    def setup_loader_modules(self):
        return {crmshmod: {}}

    @mock.patch('salt.utils.path.which')
    def test_virtual_crm(self, mock_which):
        mock_pkg_version = MagicMock(return_value='1.0.0')
        mock_pkg_version_cmp = MagicMock(return_value=1)

        mock_which.side_effect = [True, True]
        with patch.dict(crmshmod.__salt__, {
                'pkg.version': mock_pkg_version,
                'pkg.version_cmp': mock_pkg_version_cmp}):
            assert crmshmod.__virtual__() == 'crm'
            mock_which.assert_called_once_with(crmshmod.CRM_COMMAND)
