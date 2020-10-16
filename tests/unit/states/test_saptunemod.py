
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
    MagicMock,
    patch
)

# Import Salt Libs
import salt.states.saptunemod as saptune


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
        expected_ret = {
            'changes': {},
            'result': True,
            'name': solution_name,
            'comment': "Saptune {} solution is already applied".format(solution_name)
        }
        expected_ret2 = {
            'changes': {'name': 'normalmode'},
            'result': True,
            'name': solution_name,
            'comment': "Saptune solution applied"
        }

        sol_applied_resp = MagicMock(return_value=True)
        with patch.dict(saptune.__salt__, {'saptune.is_solution_applied': sol_applied_resp}):
            assert saptune.solution_applied(solution_name) == expected_ret

        with patch.dict(saptune.__salt__, {
                'saptune.is_solution_applied': MagicMock(side_effect=[False, True]),
                'saptune.apply_solution': MagicMock(return_value=0)}):
            assert saptune.solution_applied(solution_name) == expected_ret2

    def test_solution_applied_already(self):
        '''
        Test solution is applied method already
        '''
        solution_name = 'normalmode'

        expected_ret = {
            'changes': {},
            'result': False,
            'name': solution_name,
            'comment': 'Saptune solution was not applied correctly. Perhaps an already applied '
                       'solution need to be reverted first'
        }

        with patch.dict(saptune.__salt__, {
                'saptune.is_solution_applied': MagicMock(return_value=False),
                'saptune.apply_solution': MagicMock(return_value=0)}):
            assert saptune.solution_applied(solution_name) == expected_ret

    def test_solution_applied_error(self):
        '''
        Test solution is applied method error
        '''
        solution_name = 'normalmode'
        expected_ret = {
            'changes': {},
            'result': False,
            'name': solution_name,
            'comment': "Error appling saptune solution"
        }

        with patch.dict(saptune.__salt__, {
                'saptune.is_solution_applied': MagicMock(return_value=False),
                'saptune.apply_solution': MagicMock(return_value=1)}):
            assert saptune.solution_applied(solution_name) == expected_ret

    def test_solution_applied_test_mode(self):
        '''
        Test solution is applied method false
        '''
        solution_name = 'testmode'
        expected_ret = {
            'changes': {'name': solution_name},
            'result': None,
            'name':  solution_name,
            'comment': "Saptune {} solution would be applied".format(solution_name)
        }

        response = MagicMock(return_value=False)

        with patch.dict(saptune.__salt__, {'saptune.is_solution_applied': response}):
            with patch.dict(saptune.__opts__, {'test': True}):
                ret = saptune.solution_applied(solution_name)
                assert ret == expected_ret

    def test_solution_applied_error_exception(self):
        '''
        Test solution is applied method error exception
        '''
        solution_name = 'normalmode'

        expected_ret = {
            'changes': {},
            'result': False,
            'name': solution_name,
            'comment': 'saptune error'
        }

        with patch.dict(saptune.__salt__, {
                'saptune.is_solution_applied':  MagicMock(side_effect=[False, True]),
                'saptune.apply_solution': MagicMock(side_effect=exceptions.CommandExecutionError('saptune error'))}):
            assert saptune.solution_applied(solution_name) == expected_ret
