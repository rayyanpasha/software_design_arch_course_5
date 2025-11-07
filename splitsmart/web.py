from flask import Flask, render_template, request, redirect, url_for, flash
from .app import SplitSmartApp
from .models import User

app = Flask(__name__)
app.secret_key = "dev-secret-key"
store = SplitSmartApp()

@app.route('/')
def index():
    users = list(store.users.keys())
    groups = list(store.groups.keys())
    return render_template('index.html', users=users, groups=groups)

@app.route('/users', methods=['GET', 'POST'])
def users_view():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        if not name or not email:
            flash('Name and email are required', 'danger')
        else:
            try:
                store.addUser(name, email)
                flash(f'User "{name}" added', 'success')
                return redirect(url_for('users_view'))
            except Exception as e:
                flash(str(e), 'danger')
    return render_template('users.html', users=list(store.users.keys()))

@app.route('/groups', methods=['GET', 'POST'])
def groups_view():
    if request.method == 'POST':
        gname = request.form.get('name', '').strip()
        members_raw = request.form.get('members', '').strip()
        members = [m.strip() for m in members_raw.split(',') if m.strip()]
        if not gname or not members:
            flash('Group name and at least one member required', 'danger')
        else:
            try:
                store.createGroup(gname, members)
                flash(f'Group "{gname}" created', 'success')
                return redirect(url_for('groups_view'))
            except Exception as e:
                flash(str(e), 'danger')
    return render_template('groups.html', groups=list(store.groups.keys()), users=list(store.users.keys()))

@app.route('/group/<group_name>', methods=['GET', 'POST'])
def group_detail(group_name):
    g = store.groups.get(group_name)
    if g is None:
        flash('Unknown group', 'danger')
        return redirect(url_for('index'))
    members = [u.getName() for u in g.getMembers()]
    debts = g.getSimplifiedDebts()
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'add_expense':
                desc = request.form.get('description', '').strip()
                amount = float(request.form.get('amount', 0))
                payer = request.form.get('payer')
                participants_raw = request.form.get('participants', '').strip()
                participants = [p.strip() for p in participants_raw.split(',') if p.strip()]
                stype = request.form.get('split_type')
                extra = None
                if stype == 'unequal':
                    vals = request.form.get('extra', '').split(',')
                    extra = {store.users[participants[i]]: float(vals[i]) for i in range(len(participants))}
                elif stype == 'percent':
                    vals = request.form.get('extra', '').split(',')
                    extra = {store.users[participants[i]]: float(vals[i]) for i in range(len(participants))}
                elif stype == 'shares':
                    vals = request.form.get('extra', '').split(',')
                    extra = {store.users[participants[i]]: int(vals[i]) for i in range(len(participants))}
                store.addExpense(group_name, stype, desc, amount, payer, participants, extra)
                flash('Expense recorded', 'success')
                return redirect(url_for('group_detail', group_name=group_name))
            elif action == 'settle':
                frm = request.form.get('from')
                to = request.form.get('to')
                amt = float(request.form.get('amount', 0))
                store.settleUp(group_name, frm, to, amt)
                flash('Settlement recorded', 'success')
                return redirect(url_for('group_detail', group_name=group_name))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('group.html', group=group_name, members=members, debts=debts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
