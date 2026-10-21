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
    st.error(f'🔴 **Action needed: ${abs(expected):,.0f} projected shortfall**')
    st.write(f'Based on this example, **{s["name"]}** may be **${abs(expected):,.0f} short** after the listed upcoming payments.')
elif key == '1' and monthly_gap > 0:
    st.warning(f'🟡 **Bills covered for now — but spending exceeds income by ${monthly_gap:,.0f}**')
    st.write(f'You may have **${expected:,.0f} left** after these payments, but you are using existing cash to make up the difference.')
elif expected < 250:
    st.warning(f'🟡 **Very little room left: ${expected:,.0f}**')
    st.write('The listed bills appear covered, but there is very little money left for surprises.')
else:
    st.success(f'🟢 **Listed bills covered • ${expected:,.0f} remaining**')
    st.write('No immediate shortfall is projected from the information entered in this example.')

st.markdown(f'**Next significant obligation:** {s["label"]} — approximately ${s["big_bill"]:,.0f}, in {s["deadline"]} days.')

if key == '1':
    st.markdown('##### Money coming in vs. money going out')
    st.caption('Illustrative monthly comparison based on the entered amounts.')
    # Native HTML keeps the two bars close together without additional packages.
    ceiling = max(float(money_in), outflow, 1.0)
    income_height = max(3, round(float(money_in) / ceiling * 190))
    spend_height = max(3, round(outflow / ceiling * 190))
    st.markdown(f"""
    <div style="max-width:440px;margin:6px auto 10px auto;">
      <div style="display:flex;align-items:flex-end;justify-content:center;gap:22px;height:230px;border-bottom:1px solid #cbd5e1;">
        <div style="width:42%;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:#137b3c;">${money_in:,.0f}</div>
          <div style="height:{income_height}px;background:linear-gradient(#47d36b,#169a4a);border-radius:10px 10px 0 0;"></div>
        </div>
        <div style="width:42%;text-align:center;">
          <div style="font-size:18px;font-weight:700;color:#bd2127;">${outflow:,.0f}</div>
          <div style="height:{spend_height}px;background:linear-gradient(#ff6565,#d71925);border-radius:10px 10px 0 0;"></div>
        </div>
      </div>
      <div style="display:flex;justify-content:center;gap:22px;padding-top:8px;text-align:center;font-size:14px;font-weight:600;">
        <div style="width:42%;">Money coming in</div><div style="width:42%;">Money going out</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if monthly_gap > 0:
        st.warning(f'**${monthly_gap:,.0f} more going out than coming in** in this example. If this repeats, available cash will fall.')
    else:
        st.success(f'Income covers these modeled monthly expenses by ${-monthly_gap:,.0f}.')

with st.expander('Show the simple math'):
    st.markdown('**Can I cover the listed upcoming payments?**')
    rows = [
        ('Money in my account today', f'${cash:,.0f}'),
        ('Expected money coming in', f'+ ${money_in:,.0f}'),
        ('**Total available**', f'**${float(cash)+float(money_in):,.0f}**'),
        ('Upcoming bills', f'− ${bills:,.0f}'),
    ]
    if annual_due:
        rows.append(('Annual insurance renewal (additional)', f'− ${annual_due:,.0f}'))
    rows.append(('Credit-card payments', f'− ${cards:,.0f}'))
    if st.session_state['extra']:
        rows.append(('Additional money received', f'+ ${st.session_state["extra"]:,.0f}'))
    rows.append(('**Estimated money remaining**', f'**${expected:,.0f}**'))
    for label, amount in rows:
        c1, c2 = st.columns([3, 1])
        c1.markdown(label)
        c2.markdown(amount)
    st.caption('Estimated figures only. Expected income is not confirmed cash. Timing and omitted transactions may change the result.')

st.markdown('#### ② What do I need to do today?')
st.write('**What caused this?** ' + s['cause'])
st.caption(s['detail'])
if expected<0:
    st.write('**If nothing changes:** You may not be able to cover the listed payments on time. Depending on the bill, late fees, added interest or interruption of a service could follow.')
elif key == '1' and monthly_gap > 0:
    st.write(f'**If nothing changes:** The projected ${monthly_gap:,.0f} monthly gap can gradually use up available cash. Check your expenses before the next payment cycle.')
else:
    st.write('**What happens next:** Keep enough money available for these bills and confirm they are paid. New spending or missing deposits could change the picture.')
for i, action in enumerate(s['actions'][:3], 1):
    st.write(f'**{i}.** {action}')

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
