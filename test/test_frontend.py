import sys
import os
import unittest
from unittest.mock import patch
from io import StringIO

# Shto rrugën e projektit për të importuar frontend.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import frontend

class TestBankFrontend(unittest.TestCase):

    def setUp(self):
        # Reset session dhe accounts para çdo testi
        frontend.session.update({
            "logged_in": False,
            "account_number": None,
            "user_name": None,
            "is_admin": False,
            "withdrawn_this_session": 0.0,
            "transferred_this_session": 0.0,
            "deposited_this_session": 0.0,
            "paidbills_this_session": 0.0,
        })
        frontend.accounts.clear()
        frontend.accounts["54321"] = {
            "name": "TestUser",
            "status": "A",
            "balance": 1000.0,
            "password": "1234"
        }
        frontend.accounts["00000"] = {
            "name": "Admin",
            "status": "A",
            "balance": 5000.0,
            "password": "adminpass"
        }
    # --- Testet për login/logout ---
    @patch('builtins.input', side_effect=['standard', 'TestUser'])
    @patch('frontend.password_me_yje', return_value='1234')
    def test_login_standard_user(self, mock_pass, mock_input):
        frontend.login()
        self.assertTrue(frontend.session['logged_in'])
        self.assertEqual(frontend.session['user_name'], "TestUser")
        self.assertFalse(frontend.session['is_admin'])

    @patch('builtins.input', side_effect=['admin', 'Admin'])
    @patch('frontend.password_me_yje', return_value='adminpass')
    def test_login_admin(self, mock_pass, mock_input):
        frontend.login()
        self.assertTrue(frontend.session['logged_in'])
        self.assertEqual(frontend.session['user_name'], "Admin")
        self.assertTrue(frontend.session['is_admin'])

    def test_logout(self):
        frontend.session['logged_in'] = True
        frontend.session['account_number'] = '54321'
        frontend.session['user_name'] = 'TestUser'
        frontend.logout()
        self.assertFalse(frontend.session['logged_in'])
        self.assertIsNone(frontend.session['account_number'])
        self.assertIsNone(frontend.session['user_name'])

    # --- Test për output tekstual ---

    @patch('builtins.input', side_effect=['200'])
    def test_some_output(self, mock_input):
        frontend.session['logged_in'] = True
        frontend.session['account_number'] = '54321'
        frontend.session['user_name'] = 'TestUser'
        with patch('sys.stdout', new=StringIO()) as fake_out:
            frontend.depozite()
            output = fake_out.getvalue()
            self.assertIn('u pranua për depozitë në llogarinë 54321', output)


    # --- Test për paguaj_fature ---

    @patch('builtins.input', side_effect=['EC', '100'])
    def test_paguaj_fature_valid(self, mock_input):
        frontend.session['logged_in'] = True
        frontend.session['account_number'] = '54321'
        frontend.session['user_name'] = 'TestUser'
        initial_balance = frontend.accounts['54321']['balance']
        frontend.paguaj_fature()
        self.assertLess(frontend.accounts['54321']['balance'], initial_balance)

    @patch('builtins.input', side_effect=['WRONG_COMPANY', '100'])
    def test_paguaj_fature_invalid_company(self, mock_input):
        frontend.session['logged_in'] = True
        frontend.session['account_number'] = '54321'
        frontend.session['user_name'] = 'TestUser'
        initial_balance = frontend.accounts['54321']['balance']
        frontend.paguaj_fature()
        self.assertEqual(frontend.accounts['54321']['balance'], initial_balance)

    # --- Test për depozite ---

    @patch('builtins.input', side_effect=['200'])
    def test_depozite(self, mock_input):
        frontend.session['logged_in'] = True
        frontend.session['account_number'] = '54321'
        frontend.session['user_name'] = 'TestUser'
        initial_balance = frontend.accounts['54321']['balance']
        frontend.depozite()
        # Kontrollo që shuma të jetë në pritje
        self.assertIn('54321', frontend.pending_deposits)
        self.assertEqual(frontend.pending_deposits['54321'], 200)
        # Bilanci nuk duhet të ndryshojë deri në logout
        self.assertEqual(frontend.accounts['54321']['balance'], initial_balance)


    # --- Test për terheqje (siguro që funksioni në frontend.py është 'terheqje') ---

    @patch('builtins.input', side_effect=['100'])
    def test_terheqje(self, mock_input):
        frontend.session['logged_in'] = True
        frontend.session['account_number'] = '54321'
        frontend.session['user_name'] = 'TestUser'
        initial_balance = frontend.accounts['54321']['balance']
        frontend.terheqje()
        self.assertEqual(frontend.accounts['54321']['balance'], initial_balance - 100)

    # --- Test për transfero ---

    @patch('builtins.input', side_effect=['00000', '300'])
    def test_transfero(self, mock_input):
        frontend.session['logged_in'] = True
        frontend.session['account_number'] = '54321'
        frontend.session['user_name'] = 'TestUser'
        initial_balance_sender = frontend.accounts['54321']['balance']
        initial_balance_receiver = frontend.accounts['00000']['balance']
        frontend.transfero()
        self.assertEqual(frontend.accounts['54321']['balance'], initial_balance_sender - 300)
        self.assertEqual(frontend.accounts['00000']['balance'], initial_balance_receiver + 300)


if __name__ == '__main__':
    unittest.main()
