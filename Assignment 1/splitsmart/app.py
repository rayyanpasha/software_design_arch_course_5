from typing import List, Dict
from .models import (
    User,
    Group,
    EqualExpense,
    UnequalExpense,
    PercentExpense,
    SharesExpense,
)
import json
import os


class SplitSmartApp:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.groups: Dict[str, Group] = {}

    def addUser(self, name: str, email: str) -> User:
        u = User(name, email)
        self.users[u.getName()] = u
        return u

    def createGroup(self, name: str, member_names: List[str]) -> Group:
        members = []
        for n in member_names:
            u = self.users.get(n)
            if u is None:
                raise ValueError(f"Unknown user: {n}")
            members.append(u)
        g = Group(name, members)
        self.groups[g.getName()] = g
        return g

    def addExpense(self, group_name: str, expense_type: str, description: str, amount: float, payer_name: str, participant_names: List[str], extra=None):
        g = self.groups.get(group_name)
        if g is None:
            raise ValueError("Unknown group")
        payer = self.users.get(payer_name)
        if payer is None:
            raise ValueError("Unknown payer")
        participants = [self.users[n] for n in participant_names]
        et = expense_type.lower()
        if et == "equal":
            e = EqualExpense(description, amount, payer, participants)
        elif et == "unequal":
            e = UnequalExpense(description, amount, payer, extra)
        elif et == "percent":
            e = PercentExpense(description, amount, payer, extra)
        elif et == "shares":
            e = SharesExpense(description, amount, payer, extra)
        else:
            raise ValueError("Unknown expense type")
        g.addExpense(e)
        return e

    def viewDebts(self, group_name: str) -> List[str]:
        g = self.groups.get(group_name)
        if g is None:
            raise ValueError("Unknown group")
        return g.getSimplifiedDebts()

    def settleUp(self, group_name: str, from_name: str, to_name: str, amount: float):
        g = self.groups.get(group_name)
        if g is None:
            raise ValueError("Unknown group")
        _from = self.users.get(from_name)
        _to = self.users.get(to_name)
        if _from is None or _to is None:
            raise ValueError("Unknown user in settlement")
        g.recordSettlement(_from, _to, amount)

    def save(self, path: str):
        data = {
            "users": [{"name": u.getName(), "email": u.getEmail()} for u in self.users.values()],
            "groups": [],
        }
        for g in self.groups.values():
            grp = {
                "name": g.getName(),
                "members": [m.getName() for m in g.getMembers()],
                "expenses": [
                    {"desc": e.getDescription(), "amount": e.getTotalAmount(), "payer": e.getPayer().getName()} for e in g.getExpenses()
                ],
            }
            data["groups"].append(grp)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str):
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.users = {}
        for u in data.get("users", []):
            self.addUser(u["name"], u["email"])
        self.groups = {}
        for g in data.get("groups", []):
            members = g.get("members", [])
            try:
                self.createGroup(g["name"], members)
            except ValueError:
                # ignore or continue
                pass


def main():
    app = SplitSmartApp()
    print("SplitSmart Menu")
    while True:
        print("\n1. Add User\n2. Create Group\n3. Add Expense\n4. View Debts\n5. Settle Up\n6. Save Data\n7. Load Data\n8. Exit")
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                name = input("Enter user name: ").strip()
                email = input("Enter email: ").strip()
                app.addUser(name, email)
                print("User added successfully!")
            elif choice == "2":
                gname = input("Enter group name: ").strip()
                members = input("Add members (comma separated): ").strip().split(",")
                members = [m.strip() for m in members if m.strip()]
                app.createGroup(gname, members)
                print("Group created successfully!")
            elif choice == "3":
                gname = input("Enter group name: ").strip()
                desc = input("Enter expense description: ").strip()
                amount = float(input("Enter total amount: ").strip())
                payer = input("Who paid? ").strip()
                parts = input("Participants (comma separated): ").strip().split(",")
                parts = [p.strip() for p in parts if p.strip()]
                stype = input("Split type (equal / unequal / percent / shares): ").strip().lower()
                extra = None
                if stype == "unequal":
                    print("Enter amounts for each participant in same order, comma separated")
                    vals = input().strip().split(",")
                    extra = {app.users[parts[i]]: float(vals[i]) for i in range(len(parts))}
                elif stype == "percent":
                    print("Enter percentages for each participant in same order, comma separated")
                    vals = input().strip().split(",")
                    extra = {app.users[parts[i]]: float(vals[i]) for i in range(len(parts))}
                elif stype == "shares":
                    print("Enter share counts (integers) for each participant in same order, comma separated")
                    vals = input().strip().split(",")
                    extra = {app.users[parts[i]]: int(vals[i]) for i in range(len(parts))}
                app.addExpense(gname, stype, desc, amount, payer, parts, extra)
                print("Expense recorded successfully!")
            elif choice == "4":
                gname = input("Enter group name: ").strip()
                debts = app.viewDebts(gname)
                print("Current Debts:")
                if not debts:
                    print("No debts")
                for d in debts:
                    print(d)
            elif choice == "5":
                gname = input("Enter group name: ").strip()
                frm = input("From (name): ").strip()
                to = input("To (name): ").strip()
                amt = float(input("Amount: ").strip())
                app.settleUp(gname, frm, to, amt)
                print("Settlement recorded")
            elif choice == "6":
                path = input("Save path (file): ").strip()
                app.save(path)
                print("Saved")
            elif choice == "7":
                path = input("Load path (file): ").strip()
                app.load(path)
                print("Loaded")
            elif choice == "8":
                break
            else:
                print("Unknown choice")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
