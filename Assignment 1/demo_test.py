from splitsmart.app import SplitSmartApp


def main():
    app = SplitSmartApp()

    # Create users
    app.addUser("Alice", "alice@example.com")
    app.addUser("Bob", "bob@example.com")
    app.addUser("Carol", "carol@example.com")

    # Create group
    app.createGroup("Goa Trip", ["Alice", "Bob", "Carol"])

    # Add an equal expense: Dinner ₹2400 paid by Bob split among Alice,Bob,Carol
    app.addExpense("Goa Trip", "equal", "Dinner", 2400.0, "Bob", ["Alice", "Bob", "Carol"])
    debts = app.viewDebts("Goa Trip")
    print("Debts after Dinner:")
    for d in debts:
        print(" -", d)

    assert any("Alice owes Bob" in d for d in debts), "Expected Alice owes Bob"
    assert any("Carol owes Bob" in d for d in debts), "Expected Carol owes Bob"

    # Alice settles with Bob ₹800
    app.settleUp("Goa Trip", "Alice", "Bob", 800.0)
    debts_after = app.viewDebts("Goa Trip")
    print("\nDebts after Alice settles 800 to Bob:")
    for d in debts_after:
        print(" -", d)

    assert not any("Alice owes Bob" in d for d in debts_after), "Alice should no longer owe Bob"

    # Save and load state
    path = "demo_state.json"
    app.save(path)
    app2 = SplitSmartApp()
    app2.load(path)
    # Loading currently restores users and groups (but not full expenses in this simple snapshot)
    try:
        debts_loaded = app2.viewDebts("Goa Trip")
    except Exception:
        debts_loaded = []
    print("\nDebts after load into new app (may be empty because expenses aren't fully serialized):")
    for d in debts_loaded:
        print(" -", d)

    print("\nAll checks passed")


if __name__ == "__main__":
    main()
