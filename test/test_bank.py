# ----------------------------------------
# Testimi i back and front endit me unittest
# ----------------------------------------

import sys
import os
sys.path.insert(0, os.path.abspath("..")) 
import unittest
from backend import (
    lexo_master_accounts,
    lexo_transaksionet,
    apliko_transaksione,
    shkruaj_master,
    shkruaj_current
)

class TestBackend(unittest.TestCase):

    def setUp(self):
        self.accounts_file = "data/current_accounts.txt"
        self.trans_file = "data/session_transactions.txt"

    def test_lexo_master_accounts(self):
        accounts = lexo_master_accounts(self.accounts_file)
        print(accounts) 
        self.assertIn("54321", accounts)

    def test_lexo_transaksionet(self):
        trans = lexo_transaksionet(self.trans_file)
        self.assertIsInstance(trans, list)

    def test_apliko_transaksione(self):
        acc = lexo_master_accounts(self.accounts_file)
        trans = lexo_transaksionet(self.trans_file)
        before = acc["54321"]["balance"]
        apliko_transaksione(acc, trans)
        after = acc["54321"]["balance"]
        self.assertGreaterEqual(after, before)

    def test_write_files(self):
        acc = lexo_master_accounts(self.accounts_file)
        shkruaj_master(acc, "data/test_master.txt")
        shkruaj_current(acc, "data/test_current.txt")
        self.assertTrue(os.path.exists("data/test_master.txt"))
        self.assertTrue(os.path.exists("data/test_current.txt"))

if __name__ == "__main__":
    unittest.main()








