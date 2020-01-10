
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


    def test_solution_applied_true(self):
        '''
        Test solution is applied method true
        '''
        solution_name = 'normalmode'
        expected_ret = { 'changes': {}, 
          'result': True,
          'name': solution_name,
          'comment': "Saptune {} solution is already applied".format(solution_name)} 
        expected_ret2 = { 'changes': {}, 
          'result': False,
          'name': solution_name,
          'comment': 'Saptune solution was not applied correctly. Perhaps an already applied solution need to be reverted first'}
          
        sol_applied_resp = MagicMock(return_value=True)
        with patch.dict(saptune.__salt__, {'saptune.is_solution_applied': sol_applied_resp}):
            assert saptune.solution_applied(solution_name) == expected_ret

        sol_applied_resp = MagicMock(return_value=False)
        apply_sol_response = MagicMock(return_value=True)
        with patch.dict(saptune.__salt__, {'saptune.is_solution_applied': sol_applied_resp, 'saptune.apply_solution': apply_sol_response}):
                assert saptune.solution_applied(solution_name) == expected_ret2
    

    def test_solution_applied_test_mode(self):
        '''
        Test solution is applied method false
        '''
        solution_name = 'testmode'
        expected_ret = {'changes': {'name': solution_name},
               'result': None,
               'name':  solution_name,
               'comment': "Saptune {} solution would be applied".format(solution_name)}

        response = MagicMock(return_value=False)
     
        with patch.dict(saptune.__salt__, {'saptune.is_solution_applied': response}):
            with patch.dict(saptune.__opts__, {'test': True}):
              ret = saptune.solution_applied(solution_name)
              assert ret == expected_ret

