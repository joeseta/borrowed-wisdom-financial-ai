import streamlit as st
from html import escape

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

st.markdown('#### ② What do I need to do today?')
if key == '1' and monthly_gap > 0:
    st.write(f'**Find ways to close your ${monthly_gap:,.0f} monthly gap.**')
    if st.button(f'Help me find ${monthly_gap:,.0f}', use_container_width=True):
        st.session_state['finder'] = not st.session_state.get('finder', False)
    if st.session_state.get('finder', False):
        st.write('How much could you cut from your monthly spending?')
        cut = st.number_input('Monthly spending you could reduce ($)', min_value=0, max_value=1000000, value=0, step=25, key='proposed_cut_'+key)
        remaining = max(0, monthly_gap - cut)
        if remaining:
            st.info(f'You would still need to find ${remaining:,.0f} each month.')
        else:
            st.success('Your proposed cuts would cover the monthly gap, if you can keep them up.')
        st.caption('This is a plan, not money saved yet. We have not checked your actual purchases.')
elif expected < 0:
    st.write(f'**Find a way to cover the ${abs(expected):,.0f} shortfall before your next bill is due.**')
elif key == '4':
    st.write(f'**Set aside ${annual_due:,.0f} for your annual insurance bill.**')
elif key == '5':
    st.write('**Check that your next bill is paid.**')
else:
    st.write(f'**Check your next payment: {s["label"].lower()}.**')

st.markdown('#### ③ What happens if I do nothing?')
if key == '1' and monthly_gap > 0:
    st.write('You’ll keep using up your money. Eventually, you may not have enough to pay your bills.')
elif expected < 0:
    st.write('You may miss a payment. Depending on the bill, you could face fees, extra interest, or a service interruption.')
elif key == '5':
    st.write('If the payment does not go through, the bill will still be unpaid.')
else:
    st.write('A missed payment could cost you more. Check the due date and make sure the money is there.')

st.markdown('#### ③ What happens now?')
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
