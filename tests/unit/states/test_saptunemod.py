
# -*- coding: utf-8 -*-
'''
    :codeauthor: Dario Maiocchi <dmaiocchi@suse.com>
'''
# Import Python libs
from __future__ import absolute_import, unicode_literals, print_function

from salt import exceptions

# Import Salt Testing Libs
from tests.support.mixins import LoaderModuleMockMixin
from tests.support.unit import skipIf, TestCase
from tests.support import mock
from tests.support.mock import (
    NO_MOCK,
    NO_MOCK_REASON,
    MagicMock,
    patch
)

# Import Salt Libs
import salt.states.saptunemod as saptune


@skipIf(NO_MOCK, NO_MOCK_REASON)
class SaptunemodTestCase(TestCase, LoaderModuleMockMixin):
    '''
    Test cases for salt.states.saptunemod
    '''
    def setup_loader_modules(self):
        return {saptune: {'__opts__': {'test': False}}}


    def test_solution_applied(self):
        '''
        Test solution is applied method
        '''

        ret = {'name': 'fakesolution',
               'changes': {},
               'result': True,
               'comment': 'Saptune solution applied'}

        response = MagicMock(return_value=True)
        with patch.dict(saptune.__salt__, {'saptune.is_solution_applied': response}):
            assert saptune.solution_applied('fakesolution')

