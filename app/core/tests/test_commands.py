'''
Test custom Django management commands.
'''
# mocking behavior
from unittest.mock import patch

# operationalError : 데이터베이스가 준비되기 전에 발생할 수 있는 에러의 한 종류
from psycopg2 import OperationalError as Psycopg2Error

# 특정 커맨드에 대한 simulate을 지원하는 모듈
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    '''Test commands.'''

    def test_wait_for_db_ready(self, patched_check):
        '''test waiting for database if database is ready.'''
        patched_check.return_value = True

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        '''Test waiting for database when getting OperationError'''
        # 처음 두번은 Psycopg2Error를 raise하고, 다음 3번은 OperationalError를 raise하라는 것
        # 이후 마지막 6번째에 True를 반환
        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
