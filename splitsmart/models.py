from __future__ import annotations
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import uuid


class User:
    def __init__(self, name: str, email: str):
        self.userId = str(uuid.uuid4())
        self.name = name
        self.email = email

    def getUserId(self) -> str:
        return self.userId

    def getName(self) -> str:
        return self.name

    def getEmail(self) -> str:
        return self.email

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.userId == other.userId

    def __hash__(self) -> int:
        return hash(self.userId)


class Debt:
    def __init__(self, _from: User, _to: User, amount: float):
        self._from = _from
        self._to = _to
        self.amount = round(amount, 2)

    def getFrom(self) -> User:
        return self._from

    def getTo(self) -> User:
        return self._to

    def getAmount(self) -> float:
        return self.amount

    def __str__(self) -> str:
        return f"{self._from.getName()} owes {self._to.getName()} ₹{self.amount:.2f}"


class Expense(ABC):
    def __init__(self, description: str, amount: float, payer: User, participants: List[User]):
        self.expenseId = str(uuid.uuid4())
        self.description = description
        self.totalAmount = round(float(amount), 2)
        self.payer = payer
        self.participants = participants.copy()
        self.date = datetime.utcnow()

    def getExpenseId(self) -> str:
        return self.expenseId

    def getDescription(self) -> str:
        return self.description

    def getTotalAmount(self) -> float:
        return self.totalAmount

    def getPayer(self) -> User:
        return self.payer

    def getParticipants(self) -> List[User]:
        return self.participants

    def getDate(self) -> datetime:
        return self.date

    @abstractmethod
    def calculateShares(self) -> Dict[User, float]:
        """Return mapping User -> amount owed (their share). Sum of shares should equal totalAmount (within rounding)."""
        pass

    def __str__(self) -> str:
        return f"{self.description}: ₹{self.totalAmount:.2f} paid by {self.payer.getName()}"


class EqualExpense(Expense):
    def calculateShares(self) -> Dict[User, float]:
        n = len(self.participants)
        if n == 0:
            return {}
        share = round(self.totalAmount / n, 2)
        shares = {u: share for u in self.participants}
        # fix rounding remainder by adjusting the payer's share
        total_assigned = sum(shares.values())
        diff = round(self.totalAmount - total_assigned, 2)
        if diff != 0 and self.payer in shares:
            shares[self.payer] = round(shares[self.payer] + diff, 2)
        return shares


class UnequalExpense(Expense):
    def __init__(self, description: str, amount: float, payer: User, shares: Dict[User, float]):
        participants = list(shares.keys())
        super().__init__(description, amount, payer, participants)
        self.customShares = {u: round(float(v), 2) for u, v in shares.items()}

    def validateShares(self) -> bool:
        return round(sum(self.customShares.values()), 2) == round(self.totalAmount, 2)

    def calculateShares(self) -> Dict[User, float]:
        if not self.validateShares():
            raise ValueError("Custom shares do not sum up to total amount")
        return self.customShares.copy()


class PercentExpense(Expense):
    def __init__(self, description: str, amount: float, payer: User, percentages: Dict[User, float]):
        participants = list(percentages.keys())
        super().__init__(description, amount, payer, participants)
        self.percentages = {u: float(p) for u, p in percentages.items()}

    def validatePercentages(self) -> bool:
        return round(sum(self.percentages.values()), 2) == 100.00

    def calculateShares(self) -> Dict[User, float]:
        if not self.validatePercentages():
            raise ValueError("Percentages must sum to 100")
        shares = {u: round(self.totalAmount * (p / 100.0), 2) for u, p in self.percentages.items()}
        # fix rounding remainder
        total_assigned = sum(shares.values())
        diff = round(self.totalAmount - total_assigned, 2)
        if diff != 0 and self.payer in shares:
            shares[self.payer] = round(shares[self.payer] + diff, 2)
        return shares


class SharesExpense(Expense):
    def __init__(self, description: str, amount: float, payer: User, shares: Dict[User, int]):
        participants = list(shares.keys())
        super().__init__(description, amount, payer, participants)
        self.shares = {u: int(v) for u, v in shares.items()}

    def calculateShares(self) -> Dict[User, float]:
        total_shares = sum(self.shares.values())
        if total_shares == 0:
            raise ValueError("Total shares cannot be zero")
        per_unit = self.totalAmount / total_shares
        shares = {u: round(per_unit * count, 2) for u, count in self.shares.items()}
        total_assigned = sum(shares.values())
        diff = round(self.totalAmount - total_assigned, 2)
        if diff != 0 and self.payer in shares:
            shares[self.payer] = round(shares[self.payer] + diff, 2)
        return shares


class BalanceSheet:
    def __init__(self, members: List[User]):
        self.balances: Dict[User, float] = {u: 0.0 for u in members}

    def ensure_member(self, user: User):
        if user not in self.balances:
            self.balances[user] = 0.0

    def updateBalances(self, expense: Expense):
        # Using net positions: positive = others owe them, negative = they owe others
        shares = expense.calculateShares()
        payer = expense.getPayer()
        self.ensure_member(payer)
        for u in shares.keys():
            self.ensure_member(u)

        for u in self.balances.keys():
            # no-op to ensure all keys exist
            pass

        # payer paid total, so payer's paid amount = total, others paid 0
        for u in shares:
            paid = expense.totalAmount if u == payer else 0.0
            delta = round(paid - shares[u], 2)
            self.balances[u] = round(self.balances.get(u, 0.0) + delta, 2)

    def recordSettlement(self, _from: User, _to: User, amount: float):
        self.ensure_member(_from)
        self.ensure_member(_to)
        amt = round(float(amount), 2)
        # When _from pays _to an amount, _from's net balance increases (they owe less),
        # and _to's net balance decreases (they are owed less).
        self.balances[_from] = round(self.balances.get(_from, 0.0) + amt, 2)
        self.balances[_to] = round(self.balances.get(_to, 0.0) - amt, 2)

    def getBalance(self, user: User) -> float:
        return round(self.balances.get(user, 0.0), 2)

    def _split_lists(self):
        creditors = []
        debtors = []
        for u, bal in self.balances.items():
            if round(bal, 2) > 0:
                creditors.append([u, round(bal, 2)])
            elif round(bal, 2) < 0:
                debtors.append([u, round(-bal, 2)])
        creditors.sort(key=lambda x: x[1], reverse=True)
        debtors.sort(key=lambda x: x[1], reverse=True)
        return creditors, debtors

    def simplifyDebts(self) -> List[Debt]:
        creditors, debtors = self._split_lists()
        simplified: List[Debt] = []
        i, j = 0, 0
        while i < len(debtors) and j < len(creditors):
            debtor, d_amt = debtors[i]
            creditor, c_amt = creditors[j]
            settle_amt = round(min(d_amt, c_amt), 2)
            simplified.append(Debt(debtor, creditor, settle_amt))
            d_amt = round(d_amt - settle_amt, 2)
            c_amt = round(c_amt - settle_amt, 2)
            debtors[i][1] = d_amt
            creditors[j][1] = c_amt
            if d_amt == 0:
                i += 1
            if c_amt == 0:
                j += 1
        return simplified

    def getSimplifiedDebts(self) -> List[str]:
        return [str(d) for d in self.simplifyDebts()]


class Group:
    def __init__(self, name: str, members: List[User]):
        self.groupId = str(uuid.uuid4())
        self.name = name
        self.members = members.copy()
        self.expenses: List[Expense] = []
        self.balanceSheet = BalanceSheet(self.members)

    def addMember(self, user: User):
        if user not in self.members:
            self.members.append(user)
            self.balanceSheet.ensure_member(user)

    def addExpense(self, expense: Expense):
        # ensure participants are members
        for p in expense.getParticipants():
            if p not in self.members:
                self.addMember(p)
        if expense.getPayer() not in self.members:
            self.addMember(expense.getPayer())
        self.expenses.append(expense)
        self.balanceSheet.updateBalances(expense)

    def getMembers(self) -> List[User]:
        return self.members

    def getExpenses(self) -> List[Expense]:
        return self.expenses

    def getName(self) -> str:
        return self.name

    def getSimplifiedDebts(self) -> List[str]:
        return self.balanceSheet.getSimplifiedDebts()

    def recordSettlement(self, _from: User, _to: User, amount: float):
        self.balanceSheet.recordSettlement(_from, _to, amount)
