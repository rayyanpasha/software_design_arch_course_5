import unittest
from splitsmart.models import User, EqualExpense, PercentExpense, UnequalExpense, SharesExpense, Group


class TestSplits(unittest.TestCase):
    def setUp(self):
        self.a = User("Alice", "alice@example.com")
        self.b = User("Bob", "bob@example.com")
        self.c = User("Carol", "carol@example.com")
        self.group = Group("Trip", [self.a, self.b, self.c])

    def test_equal_split(self):
        e = EqualExpense("Dinner", 2400, self.b, [self.a, self.b, self.c])
        shares = e.calculateShares()
        self.assertAlmostEqual(shares[self.a], 800.0)
        self.assertAlmostEqual(shares[self.b], 800.0)
        self.assertAlmostEqual(shares[self.c], 800.0)
        self.group.addExpense(e)
        debts = self.group.getSimplifiedDebts()
        # After Bob paid 2400, both Alice and Carol owe Bob 800 each
        self.assertIn("Alice owes Bob", "\n".join(debts))

    def test_percent_split(self):
        perc = {self.a: 50.0, self.b: 25.0, self.c: 25.0}
        e = PercentExpense("Cab", 400.0, self.a, perc)
        shares = e.calculateShares()
        self.assertAlmostEqual(shares[self.a], 200.0)
        self.assertAlmostEqual(shares[self.b], 100.0)
        self.assertAlmostEqual(shares[self.c], 100.0)
        self.group.addExpense(e)
        debts = self.group.getSimplifiedDebts()
        self.assertTrue(len(debts) >= 1)

    def test_unequal_split_validation(self):
        shares = {self.a: 100.0, self.b: 150.0}
        with self.assertRaises(ValueError):
            UnequalExpense("Bad", 500.0, self.a, shares).calculateShares()

    def test_shares_expense(self):
        share_counts = {self.a: 2, self.b: 1, self.c: 1}
        e = SharesExpense("Food", 400.0, self.c, share_counts)
        shares = e.calculateShares()
        # total units = 4, per unit = 100
        self.assertAlmostEqual(shares[self.a], 200.0)
        self.assertAlmostEqual(shares[self.b], 100.0)
        self.assertAlmostEqual(shares[self.c], 100.0)


if __name__ == "__main__":
    unittest.main()
