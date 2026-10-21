import streamlit as st
from html import escape
import pandas as pd

st.set_page_config(page_title='Borrowed Wisdom • What do I do today?', page_icon='🧭', layout='centered')

SCENARIOS = {
    '1 · Spending more than income': {
        'name':'Alex', 'balance':1350, 'income':1800, 'card':620, 'bills':2150, 'deadline':10,
        'label':'Monthly expenses', 'big_bill':1200, 'cause':'Regular spending is exceeding regular income.',
        'detail':'Monthly income is $1,800. Bills and planned card payments total $2,770. Cash on hand covers part of the difference.',
        'actions':['Review the largest optional purchases from the last 30 days.', 'Identify which payments can safely be reduced or postponed.', 'Ask a trusted person for help if the remaining gap cannot be covered.'],
        'note':'This is an ongoing mismatch, not just a one-time large bill.'},
    '2 · Large unexpected bill': {
        'name':'Jordan', 'balance':900, 'income':950, 'card':200, 'bills':2050, 'deadline':8,
        'label':'Car repair', 'big_bill':1400, 'cause':'An unexpected $1,400 repair was added to the usual bills.',
        'detail':'The repair is the main cause of this shortfall. It is not evidence of repeated overspending.',
        'actions':['Ask the repair shop for a written estimate and whether payment can be scheduled.', 'Protect rent, food, and essential transportation first.', 'Ask your support person to review possible options before taking on debt.'],
        'note':'A one-time expense needs a one-time response and a future emergency-fund plan.'},
    '3 · Credit-card spending rising': {
        'name':'Taylor', 'balance':1650, 'income':1500, 'card':1750, 'bills':1100, 'deadline':12,
        'label':'Credit-card bill', 'big_bill':1750, 'cause':'Credit-card purchases increased significantly this month.',
        'detail':'The projected payment is $1,750. Checking and forecast income must also cover $1,100 in other bills.',
        'actions':['Review recent card purchases and stop optional purchases for now.', 'Check the actual card due date and minimum required payment.', 'If you cannot pay in full, estimate interest costs and contact the issuer before missing a payment.'],
        'note':'Credit-card purchases count as spending when purchased; paying the bill is not new spending.'},
    '4 · Annual bill needs reserving': {
        'name':'Morgan', 'balance':2400, 'income':1600, 'card':350, 'bills':900, 'deadline':18,
        'label':'Annual insurance renewal', 'big_bill':1500, 'cause':'The annual insurance payment is arriving in the same month as ordinary bills.',
        'detail':'A $1,500 annual renewal was expected, but no dedicated reserve has been confirmed.',
        'actions':['Set aside $1,500 for the upcoming insurance renewal.', 'Avoid treating the reserved money as available for discretionary purchases.', 'After payment, plan to set aside approximately $125 a month for next year.'],
        'note':'An annual bill is a real payment in its due month, even if its cost is budgeted monthly.'},
    '5 · Problem corrected': {
        'name':'Riley', 'balance':1400, 'income':950, 'card':200, 'bills':1550, 'deadline':6,
        'label':'Rent and utilities', 'big_bill':1150, 'cause':'An earlier $300 shortfall was addressed by reducing optional expenses.',
        'detail':'The revised forecast shows $600 remaining after listed obligations.',
        'actions':['Confirm the upcoming payment clears.', 'Keep your current spending plan until your next paycheck.', 'Review which change helped most so you can repeat it next month.'],
        'note':'Positive feedback should be tied to a better forecast, not just clicking “done”.'},
}

st.markdown('### 🧭 Borrowed Wisdom — Phase 1')
st.caption('“What do I need to do today?” • Interactive concept test • Fictional people and financial figures')
scenario_name = st.selectbox('Choose a situation to test', list(SCENARIOS.keys()))
s = SCENARIOS[scenario_name]
key = scenario_name[0]
if st.session_state.get('case_key') != key:
    st.session_state['case_key'] = key
    st.session_state['ack'] = False
    st.session_state['help'] = False
    st.session_state['plan'] = False
    st.session_state['reserve'] = 0
    st.session_state['extra'] = 0
    st.session_state['finder'] = False
    st.session_state['show_other_options'] = False
    st.session_state['behavior_prompt'] = False

with st.expander('Adjust this fictional situation', expanded=False):
    a,b=st.columns(2)
    with a:
        cash=st.number_input('Money available now ($)',min_value=0,max_value=1000000,value=s['balance'],step=50,key='cash_'+key)
        money_in=st.number_input('Expected income before bills ($)',min_value=0,max_value=1000000,value=s['income'],step=50,key='income_'+key)
    with b:
        bills=st.number_input('Upcoming bills excluding cards ($)',min_value=0,max_value=1000000,value=s['bills'],step=50,key='bills_'+key)
        cards=st.number_input('Credit-card payment needs ($)',min_value=0,max_value=1000000,value=s['card'],step=50,key='cards_'+key)
    st.caption('Figures are illustrative. A live version would distinguish statement amounts, card purchases, expected deposits, reserves, and the timing of each payment to avoid double counting.')

cash = st.session_state.get('cash_'+key,s['balance'])
money_in = st.session_state.get('income_'+key,s['income'])
bills = st.session_state.get('bills_'+key,s['bills'])
cards = st.session_state.get('cards_'+key,s['card'])
# The annual renewal is a separate payment in Scenario 4; do not omit it.
annual_due = float(s['big_bill']) if key == '4' else 0.0
total_bills = float(bills) + annual_due
outflow = total_bills + float(cards)
expected = float(cash) + float(money_in) - outflow + st.session_state['extra']
monthly_gap = float(bills) + float(cards) - float(money_in) if key == '1' else 0.0
if st.session_state['plan']:
    st.session_state['reserve']=0

st.markdown('#### ① Where do I stand?')
if expected < 0:
    st.error(f'🔴 **You may be ${abs(expected):,.0f} short for your upcoming bills.**')
elif key == '1' and monthly_gap > 0:
    st.warning(f'🟡 **You’re spending ${monthly_gap:,.0f} more than you earn each month.**')
elif expected < 250:
    st.warning(f'🟡 **You may have only ${expected:,.0f} left after your bills.**')
else:
    st.success(f'🟢 **Your listed bills appear covered. ${expected:,.0f} left.**')

if key == '1':
    st.markdown('##### Money coming in vs. money going out')
    ceiling = max(float(money_in), outflow, 1.0)
    income_height = max(3, round(float(money_in) / ceiling * 190))
    spend_height = max(3, round(outflow / ceiling * 190))
    # Two labeled bars; no chart library needed.
    st.markdown(f"""
    <div style="max-width:440px;margin:8px auto 16px auto;">
      <div style="display:flex;align-items:flex-end;justify-content:center;gap:18px;height:225px;border-bottom:1px solid #cbd5e1;">
        <div style="width:42%;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:#137b3c;">${money_in:,.0f}</div>
          <div style="height:{income_height}px;background:linear-gradient(#47d36b,#169a4a);border-radius:9px 9px 0 0;"></div>
        </div>
        <div style="width:42%;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:#bd2127;">${outflow:,.0f}</div>
          <div style="height:{spend_height}px;background:linear-gradient(#ff6565,#d71925);border-radius:9px 9px 0 0;"></div>
        </div>
      </div>
      <div style="display:flex;justify-content:center;gap:18px;padding-top:9px;text-align:center;font-size:14px;font-weight:600;">
        <div style="width:42%;">Money coming in</div><div style="width:42%;">Money going out</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with st.expander('Show the numbers'):
    st.markdown('**Money available for upcoming bills**')
    rows = [
        ('Money in your account', f'${cash:,.0f}', False),
        ('Expected income', f'+ ${money_in:,.0f}', False),
        ('Total available', f'${float(cash)+float(money_in):,.0f}', True),
        ('Upcoming bills', f'− ${bills:,.0f}', False),
    ]
    if annual_due:
        rows.append(('Annual insurance bill', f'− ${annual_due:,.0f}', False))
    rows.append(('Credit card payment', f'− ${cards:,.0f}', False))
    if st.session_state['extra']:
        rows.append(('Extra money received', f'+ ${st.session_state["extra"]:,.0f}', False))
    rows.append(('Money left after payments', f'${expected:,.0f}', True))
    # A real HTML table fixes alignment on phones and avoids extra markdown bullets.
    tr = ''.join(
        f'<tr style="border-bottom:1px solid #e5e7eb;{("font-weight:700;background:#f8fafc;" if bold else "")}">'
        f'<td style="padding:10px 8px;">{escape(label)}</td>'
        f'<td style="padding:10px 8px;text-align:right;white-space:nowrap;">{escape(amount)}</td></tr>'
        for label, amount, bold in rows
    )
    st.markdown('<table style="width:100%;border-collapse:collapse;font-size:16px;">'+tr+'</table>',unsafe_allow_html=True)
    st.caption('Estimate only. Expected income must arrive before these bills are due. Other transactions may change the result.')

selected_total = 0.0
st.markdown('#### ② What do I need to do today?')
if key == '1' and monthly_gap > 0:
    st.write(f'**Find a way to spend ${monthly_gap:,.0f} less each month.**')
    if st.button(f'Help me find ${monthly_gap:,.0f}', use_container_width=True):
        st.session_state['finder'] = not st.session_state.get('finder', False)
    if st.session_state.get('finder', False):
        st.markdown('##### Where does your money go?')
        st.caption('Fictional monthly spending. Choose what you can spend less on. Change any suggested amount.')
        # All figures are fictional. The default spending list is aligned with
        # Scenario 1's $2,770 monthly bills and planned card payments.
        categories = [
            ('Rent', 1200, 0, False),
            ('Groceries', 400, 75, True),
            ('Restaurants', 300, 150, True),
            ('Shopping', 250, 150, True),
            ('Entertainment', 180, 100, True),
            ('Transportation', 160, 40, True),
            ('Utilities', 150, 0, False),
            ('Other expenses', 130, 0, False),
        ]
        spending_total = sum(x[1] for x in categories)
        if abs(spending_total - outflow) > 0.01:
            st.warning('The example spending list does not match your adjusted bills. Savings below are illustrative until the list is updated.')
        st.markdown('**Select what you would change each month:**')
        selected_total = 0
        for label, spent, suggestion, editable in categories:
            left, mid, right = st.columns([3, 2, 2], vertical_alignment='center')
            with left:
                if editable:
                    chosen = st.checkbox(label, value=False, key=f'choose_{key}_{label}')
                else:
                    st.write(f'**{label}**')
                    chosen = False
            with mid:
                st.write(f'${spent:,.0f} now')
            with right:
                if chosen:
                    proposed = st.number_input(
                        f'Reduce {label} by ($)', min_value=0, max_value=spent,
                        value=suggestion, step=10, key=f'reduce_{key}_{label}',
                        label_visibility='collapsed',
                    )
                    selected_total += proposed
                elif editable:
                    st.caption(f'Suggested: ${suggestion:,.0f}')
                else:
                    st.caption('Essential / check first')
        remaining = max(0, monthly_gap - selected_total)
        st.markdown('---')
        a, b = st.columns(2)
        a.metric('You could save each month', f'${selected_total:,.0f}')
        b.metric('Still need each month', f'${remaining:,.0f}')
        if remaining > 0:
            st.warning(f'**You still need to spend ${remaining:,.0f} less each month.**')
            st.write('**Can you cut more from restaurants, shopping, or entertainment?**')
            st.caption('Check more expenses above or raise an amount you already selected.')
            if st.button('I cannot spend less. Show other options', key=f'other_{key}'):
                st.session_state['show_other_options'] = True
            if st.session_state.get('show_other_options', False):
                st.markdown('##### If spending less is not enough')
                st.write('**Earn more:** More work means less free time. Count only income you can rely on.')
                st.write('**Ask for help:** Contact a bill provider about a payment plan or hardship assistance before a bill is late.')
                st.write('**Borrow:** You must repay it. Borrowing once does not fix a monthly shortage.')
                with st.expander('Compare the cost of borrowing — only if you need it'):
                    st.caption('Example costs for borrowing the remaining amount just once. Actual terms vary.')
                    examples = [
                        ('Family / friend', 0.0, 'May strain relationships.'),
                        ('Credit union loan (12% APR, 30 days)', remaining * 0.12 * 30 / 365, 'Approval and terms vary.'),
                        ('Credit card (25% APR, 30 days)', remaining * 0.25 * 30 / 365, 'Cash advances can cost more.'),
                        ('Payday loan ($15 per $100, 14 days)', remaining * 0.15, 'High cost and rapid repayment.'),
                    ]
                    table_rows = ''.join(
                        f'<tr><td style="padding:8px;border-bottom:1px solid #ddd">{escape(name)}</td>'
                        f'<td style="padding:8px;text-align:right;border-bottom:1px solid #ddd">${remaining+cost:,.2f}</td></tr>'
                        for name,cost,_ in examples
                    )
                    st.markdown('<table style="width:100%;border-collapse:collapse"><thead><tr>'
                                '<th style="text-align:left">Where from</th><th style="text-align:right">Repay</th>'
                                '</tr></thead><tbody>'+table_rows+'</tbody></table>',unsafe_allow_html=True)
                    st.caption('Family loans can affect relationships. Payday loans can create expensive repeat borrowing.')
                    st.error(f'**Borrowing ${remaining:,.0f} today leaves you ${remaining:,.0f} short again next month if nothing changes.**')
                    st.write('**Where will you get the money to repay it?**')
        else:
            st.success('**Your choices could cover the monthly difference.** Next, put the changes into action.')
        st.caption('These are possible changes, not confirmed savings. We have not connected bank or card transactions.')
elif expected < 0:
    st.write(f'**Find a way to cover the ${abs(expected):,.0f} shortfall before your next bill is due.**')
elif key == '4':
    st.write(f'**Set aside ${annual_due:,.0f} for your annual insurance bill.**')
elif key == '5':
    st.write('**Check that your next bill is paid.**')
else:
    st.write(f'**Check your next payment: {s["label"].lower()}.**')

# Simple financial crystal ball: compare the same four dates in every view.
# This is a cash-flow illustration, never a forecast of contractual card payments.
if key == '1' and monthly_gap > 0:
    st.markdown('#### ③ What happens if I do nothing?')
    st.markdown('### 🔴 SHOW ME THE MONEY!')
    st.error(f'**You are spending ${monthly_gap:,.0f} more than you earn each month. Where will you get the money?**')
    choice = st.radio('How are you covering the extra spending?',
                      ['Using savings', 'Borrowing on a credit card'], horizontal=True,
                      key='projection_view_new')
    apply_plan = st.checkbox('Show what changes if I make my selected spending cuts',
                             key='projection_apply_plan_new')
    applied = float(selected_total) if apply_plan and st.session_state.get('finder',False) else 0.0
    shortfall = max(0.0, monthly_gap-applied)
    if apply_plan and applied == 0:
        st.caption('Select expenses to cut above, then check this box again.')
    periods=[0,3,6,12]
    period_labels=['Today','3 months','6 months','12 months']
    def dollar(n):
        return f'${n:,.0f}'
    if choice == 'Using savings':
        savings_now = st.number_input('How much savings can you use? ($)',min_value=0,
                                      max_value=1000000,value=10000,step=100,key='project_savings_new')
        remaining_bal=[max(0, savings_now-shortfall*m) for m in periods]
        max_y=max(float(savings_now),1.0)
        bars=''.join(
            f'<div style="flex:1;min-width:0;text-align:center">'
            f'<div style="font-size:15px;font-weight:750;color:{"#b91c1c" if (m>0 and v==0) else "#136c3c"}">{dollar(v)}</div>'
            f'<div style="height:{max(4,int(v/max_y*165))}px;background:{"#dc2626" if (m>0 and v==0) else "#16a34a"};border-radius:8px 8px 0 0;margin:6px auto 0;max-width:96px"></div>'
            f'<div style="font-size:13px;margin-top:10px;font-weight:600">{label}</div></div>'
            for m,v,label in zip(periods,remaining_bal,period_labels))
        st.markdown('**Your savings over time**')
        st.markdown('<div style="display:flex;align-items:flex-end;gap:12px;border-bottom:1px solid #cbd5e1;padding:8px 3px 6px">'+bars+'</div>',unsafe_allow_html=True)
        if shortfall>0:
            from math import ceil
            exhausted=ceil(savings_now/shortfall) if savings_now>0 else 0
            st.error(f'**At this rate your savings run out in about {exhausted} months. What will you do then?**')
        else:
            st.success('Your selected spending cuts could stop the monthly loss. Now you need to follow through.')
        st.caption('Example only. Assumes steady spending and income, no interest earned, and savings available for this purpose.')
    else:
        rate=st.number_input('Credit card interest rate (% per year)',min_value=0.0,
                             max_value=100.0,value=25.0,step=0.5,key='project_apr_new')
        r=rate/1200
        balances={0:0.0}
        balance=0.0
        for m in range(1,13):
            balance=balance*(1+r)+shortfall
            if m in periods: balances[m]=balance
        borrowing=[shortfall*m for m in periods]
        owed=[balances[m] for m in periods]
        max_y=max(max(owed),1)
        grouped=''
        for m,label,plain,with_int in zip(periods,period_labels,borrowing,owed):
            h1=max(3,int(plain/max_y*166)) if plain else 3
            h2=max(3,int(with_int/max_y*166)) if with_int else 3
            grouped+=(f'<div style="flex:1;text-align:center;min-width:0">'
                      f'<div style="font-size:14px;font-weight:800;color:#b91c1c">{dollar(with_int)}</div>'
                      f'<div style="height:172px;display:flex;align-items:flex-end;justify-content:center;gap:5px">'
                      f'<div title="Borrowed {dollar(plain)}" style="height:{h1}px;background:#9ca3af;width:35%;max-width:46px;border-radius:6px 6px 0 0"></div>'
                      f'<div title="With interest {dollar(with_int)}" style="height:{h2}px;background:#dc2626;width:35%;max-width:46px;border-radius:6px 6px 0 0"></div>'
                      f'</div><div style="font-size:13px;margin-top:10px;font-weight:600">{label}</div></div>')
        st.markdown('**What you could owe over time**')
        st.markdown('<div style="display:flex;align-items:flex-end;gap:12px;border-bottom:1px solid #cbd5e1">'+grouped+'</div>',unsafe_allow_html=True)
        st.caption('Gray = borrowed money. Red = total debt including interest.')
        st.markdown(f'**In 12 months, you borrow {dollar(borrowing[-1])}. With interest, you could owe {dollar(owed[-1])}.**')
        st.error(f'**Where will you get {dollar(owed[-1])} to pay it back?**')
        st.caption('Example only: borrowing occurs at each month-end; interest compounds monthly; no payments or fees. Real credit cards require minimum payments. Do not treat this as a repayment plan.')
    with st.expander('Why is it hard to spend less?'):
        reason=st.radio('Choose what fits best:',[
          'My friends go out and I do not want to miss out.',
          'I like going out or shopping.',
          'I am too tired or busy to change my routine.',
          'I did not realize how much I spent.',
          'I keep telling myself I will change next month.',
          'Something else',],key='spending_reason_v51')
        if reason=='Something else':
            st.text_input('Tell us what is getting in the way',key='spending_reason_other_v51')
        if st.button('Show my next step',key='reason_next_step_v51'):
            if reason.startswith('My friends'):
                st.info('Your friends do not pay your bills. Suggest a lower-cost way to see them this week.')
            else:
                st.info('Choose one expense to cut this week. Next week, check if you actually did it.')
    st.caption('You do not know what someone else can afford. Live according to your numbers, not their appearance.')
    st.caption('Fictional-data demo. No movie clip is embedded.')
else:
    st.markdown('#### ③ What happens if I do nothing?')
    if expected < 0:
        st.write('You may miss a payment. This could mean late fees, interest, or loss of a service, depending on the bill.')
    elif key == '5':
        st.write('If the payment does not go through, the bill will still be unpaid.')
    else:
        st.write('A missed payment could cost you more. Check the due date and make sure the money is there.')

st.markdown('#### Your next step')
a,b=st.columns(2)
with a:
    if st.button('✅ I have a plan',use_container_width=True): st.session_state['plan']=True
with b:
    if st.button('🤝 I need help',use_container_width=True): st.session_state['help']=True
if st.session_state['plan']:
    st.info('Plan acknowledged—not yet verified. The warning is resolved only when the forecast improves or the payment is confirmed.')
    with st.form('update_'+key):
        funding=st.number_input('Additional money actually received ($)',min_value=0,max_value=1000000,step=50,value=0)
        submitted=st.form_submit_button('Update this forecast')
        if submitted:
            st.session_state['extra']=float(funding)
            st.rerun()
if st.session_state['help']:
    st.info('**Support-person preview:** You choose whether to ask for help and what you share. No message is sent by this prototype.')
    st.text_area('Suggested message — edit in your own words',value=f'Hi, I could use help making a plan for my upcoming {s["label"].lower()}. I may have a shortfall and would appreciate talking it through. Can we speak today?',height=110)
    if st.button('Hide help draft'): st.session_state['help']=False; st.rerun()

st.markdown('---')
st.caption('PHASE 1 TEST: Local, illustrative, no bank access, no messages sent, no AI diagnosis, and no data saved. A later version can read an authorized Simplifi export and validate predictions against actual outcomes. Do not enter real account numbers or personal financial details in a publicly hosted demo.')
