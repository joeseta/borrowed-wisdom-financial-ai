import streamlit as st
from html import escape
from math import ceil

st.set_page_config(page_title="Borrowed Wisdom — What do I need to do today?", page_icon="🧭", layout="centered")

SCENARIOS = {
    "1 · Spending more than income": dict(cash=1350, income=1800, bills=2150, card=620, annual=0, description="Monthly spending is higher than monthly income."),
    "2 · Large unexpected bill": dict(cash=900, income=950, bills=2050, card=200, annual=0, description="An unexpected car repair added $1,400 to upcoming bills."),
    "3 · Credit-card spending rising": dict(cash=1650, income=1500, bills=1100, card=1750, annual=0, description="Credit-card spending rose this month."),
    "4 · Annual bill needs reserving": dict(cash=2400, income=1600, bills=900, card=350, annual=1500, description="An annual insurance bill is due."),
    "5 · Problem corrected": dict(cash=1400, income=950, bills=1550, card=200, annual=0, description="A previous spending problem has been addressed; confirm payments clear."),
}
CATEGORIES = [
    ("Rent", 1200, 0), ("Groceries", 400, 75), ("Restaurants", 300, 150),
    ("Shopping", 250, 150), ("Entertainment", 180, 100),
    ("Transportation", 160, 40), ("Utilities", 150, 0), ("Other expenses", 130, 0),
]
APR = 0.25  # illustrative fixed annual percentage rate; not a real offer

def money(n):
    return f"${n:,.0f}"

def numbers_table(rows):
    body = "".join(
        '<tr style="border-bottom:1px solid #e5e7eb;{}"><td style="padding:10px 8px">{}</td>'
        '<td style="padding:10px 8px;text-align:right;white-space:nowrap">{}</td></tr>'.format(
            "font-weight:700;background:#f8fafc" if bold else "", escape(label), escape(value)
        ) for label, value, bold in rows
    )
    st.markdown('<table style="width:100%;border-collapse:collapse;font-size:16px">'+body+'</table>', unsafe_allow_html=True)

def bar_chart(series, labels, color, ymax=None):
    ymax = max(ymax or 0, max(series), 1)
    cells = []
    for value, label in zip(series, labels):
        h = max(2, int(max(0, value) / ymax * 174)) if value > 0 else 0
        cells.append(
            f'<div style="flex:1;min-width:0;text-align:center">'
            f'<div style="font-size:clamp(12px,2.7vw,18px);font-weight:800;color:{color}">{money(value)}</div>'
            f'<div style="height:185px;display:flex;align-items:flex-end;justify-content:center">'
            f'<div style="width:70%;max-width:90px;height:{h}px;background:{color};border-radius:8px 8px 0 0"></div></div>'
            f'<div style="font-size:13px;font-weight:600;margin-top:10px">{label}</div></div>'
        )
    st.markdown('<div style="display:flex;gap:10px;border-bottom:1px solid #cbd5e1;padding-bottom:9px">'+"".join(cells)+'</div>', unsafe_allow_html=True)

st.title("🧭 Borrowed Wisdom")
st.caption("What do I need to do today? · Fictional financial examples")
scenario = st.selectbox("Choose a situation to test", list(SCENARIOS))
s = SCENARIOS[scenario]
case = scenario[0]
if st.session_state.get("active_case") != case:
    st.session_state["active_case"] = case
    st.session_state["section"] = "Today"
    st.session_state["reduced"] = {}
    st.session_state["other"] = False
    st.session_state["help"] = False
    st.session_state["plan"] = False

with st.expander("Change this fictional example"):
    p, q = st.columns(2)
    with p:
        cash = st.number_input("Money in account ($)", 0, 1000000, s["cash"], 50, key=f"cash{case}")
        income = st.number_input("Income expected ($)", 0, 1000000, s["income"], 50, key=f"income{case}")
    with q:
        bills = st.number_input("Other upcoming bills ($)", 0, 1000000, s["bills"], 50, key=f"bills{case}")
        card = st.number_input("Card payment due ($)", 0, 1000000, s["card"], 50, key=f"card{case}")
    st.caption("Example amounts only. The annual bill in scenario 4 is included separately.")

outgoing = float(bills + card + s["annual"])
remaining_cash = float(cash + income) - outgoing
monthly_shortfall = max(0, outgoing - float(income)) if case == "1" else 0

# Streamlit forbids changing a widget's session-state key after that widget
# has been created in the same run. Button callbacks run before the next render.
def open_section(destination):
    st.session_state["section"] = destination

# Show one section at a time. This is navigation, not a pile of expanded panels.
sections = ["Today", "Spend less", "See my future"] if case == "1" else ["Today", "Get help"]
st.radio("What would you like to see?", sections, horizontal=True, key="section", label_visibility="collapsed")
section = st.session_state["section"]

if section == "Today":
    st.subheader("① Where do I stand?")
    if case == "1" and monthly_shortfall:
        st.error(f"**You're spending {money(monthly_shortfall)} more than you earn each month.**")
        st.markdown("**Money coming in vs. money going out**")
        ceiling = max(income, outgoing, 1)
        # Paired bars are intentionally narrow and close together.
        green_h = round(income / ceiling * 165)
        red_h = round(outgoing / ceiling * 165)
        st.markdown(f'''<div style="max-width:450px;margin:8px auto 16px">
          <div style="height:210px;display:flex;justify-content:center;align-items:end;gap:16px;border-bottom:1px solid #cbd5e1">
          <div style="width:39%;text-align:center"><strong style="color:#15803d">{money(income)}</strong><div style="background:#16a34a;height:{green_h}px;border-radius:8px 8px 0 0"></div></div>
          <div style="width:39%;text-align:center"><strong style="color:#b91c1c">{money(outgoing)}</strong><div style="background:#dc2626;height:{red_h}px;border-radius:8px 8px 0 0"></div></div></div>
          <div style="display:flex;gap:16px;justify-content:center;font-size:14px;font-weight:600;margin-top:8px;text-align:center">
          <div style="width:39%">Money coming in</div><div style="width:39%">Money going out</div></div></div>''', unsafe_allow_html=True)
    elif remaining_cash < 0:
        st.error(f"**You may be {money(abs(remaining_cash))} short for upcoming payments.**")
    else:
        st.success(f"**Your listed bills appear covered. {money(remaining_cash)} left.**")
    st.subheader("② What do I need to do today?")
    if case == "1" and monthly_shortfall:
        st.markdown(f"**Find a way to spend {money(monthly_shortfall)} less each month.**")
        st.button(f"Help me find {money(monthly_shortfall)}", use_container_width=True,
                  on_click=open_section, args=("Spend less",))
    elif remaining_cash < 0:
        st.write(f"**Find a way to cover {money(abs(remaining_cash))} before your bills are due.**")
    elif case == "4":
        st.write(f"**Set aside {money(s['annual'])} for the annual insurance bill.**")
    else:
        st.write("**Check that your next bill is paid.**")
    if case == "1" and monthly_shortfall:
        st.subheader("③ What happens if I do nothing?")
        st.write("**Your available money will fall or your debt will rise.**")
        st.button("Show me my future", use_container_width=True,
                  on_click=open_section, args=("See my future",))
    with st.expander("Show the numbers"):
        rows = [("Money in your account", money(cash), False),
                ("Income expected", "+ " + money(income), False),
                ("Total available", money(cash + income), True),
                ("Upcoming bills", "− " + money(bills), False)]
        if s["annual"]:
            rows.append(("Annual insurance", "− " + money(s["annual"]), False))
        rows += [("Card payment", "− " + money(card), False),
                 ("Money left after payments", money(remaining_cash), True)]
        numbers_table(rows)
        st.caption("Only listed bills are included. Income is not guaranteed until received.")

elif section == "Spend less":
    st.subheader("What do I need to do today?")
    st.write(f"**You need to reduce monthly spending by {money(monthly_shortfall)}. Start here.**")
    if abs(sum(amount for _, amount, _ in CATEGORIES) - outgoing) > 0.01:
        st.warning("The sample spending categories don't match the amounts you entered. Update the example before relying on these reductions.")
    st.caption("Choose what you'll stop or reduce. Nothing is selected for you.")
    saved = 0
    for title, spent, suggested in CATEGORIES:
        left, mid, right = st.columns([2.7, 1.3, 2.0], vertical_alignment="center")
        with left:
            active = st.checkbox(title, key=f"select_{case}_{title}", disabled=suggested == 0)
        with mid:
            st.write(money(spent))
        with right:
            if active and suggested:
                change = st.number_input(f"Spend less on {title}", min_value=0, max_value=spent,
                    value=suggested, step=10, label_visibility="collapsed", key=f"cut_{case}_{title}")
                saved += change
            elif suggested:
                st.caption(f"Try {money(suggested)}")
            else:
                st.caption("Essential / review first")
    left, right = st.columns(2)
    left.metric("Spend less each month", money(saved))
    still = max(0, monthly_shortfall - saved)
    right.metric("Still need each month", money(still))
    if still:
        st.warning(f"**You still need {money(still)} each month.**")
        st.write("**Can you spend less on anything else?**")
        if st.button("No. Show other options"):
            st.session_state["other"] = True
        if st.session_state["other"]:
            with st.expander("Other options", expanded=True):
                st.write("**Earn more:** More work costs time and energy.")
                st.write("**Ask for help:** Contact bill providers about payment plans or assistance.")
                st.write("**Borrow:** You'll have to repay it. Borrowing does not fix a monthly shortage.")
                with st.expander("Compare borrowing costs"):
                    st.caption("Illustrative cost of borrowing the remaining amount once, not actual loan offers.")
                    examples = [("Family or friend, 0%", 0),
                                ("Credit union, 12% APR for 30 days", still * .12 * 30 / 365),
                                ("Credit card, 25% APR for 30 days", still * .25 * 30 / 365),
                                ("Payday loan, $15 per $100 for 14 days", still * .15)]
                    numbers_table([(name, money(still + fee), False) for name, fee in examples])
                    st.error("**Borrowing once does not solve a monthly spending problem.**")
                    st.write("**Where will you get the money to repay it?**")
    else:
        st.success("**Your choices could cover the monthly difference. Now you must follow through.**")
    st.button("Show what my choices do to my future", use_container_width=True,
              on_click=open_section, args=("See my future",))

elif section == "See my future":
    st.subheader("🔴 SHOW ME THE MONEY!")
    st.markdown(f"**You're spending {money(monthly_shortfall)} more than you earn each month. Where will you get the money?**")
    # Reductions can be considered in the projection, but are NOT counted as verified.
    potential = sum(st.session_state.get(f"cut_{case}_{label}", suggestion)
        for label, _, suggestion in CATEGORIES
        if st.session_state.get(f"select_{case}_{label}", False))
    if potential:
        use_cuts = st.checkbox(f"What if I make the {money(potential)} in spending cuts I selected?", value=False)
    else:
        use_cuts = False
    gap = max(0, monthly_shortfall - (potential if use_cuts else 0))
    funding = st.radio("How are you covering the extra spending?", ["Using savings", "Using a credit card"], horizontal=True)
    months = [0,3,6,12]
    labels = ["Today", "3 months", "6 months", "12 months"]
    if funding == "Using savings":
        savings = st.number_input("Savings available ($)", min_value=0, max_value=1000000, value=10000, step=100)
        balances = [max(0, savings - gap * month) for month in months]
        st.markdown("**Your savings**")
        bar_chart(balances, labels, "#16a34a", ymax=max(savings, 1))
        if gap:
            st.error(f"**Your savings run out in about {ceil(savings / gap) if savings else 0} months at this rate. Where will you get the money then?**")
        else:
            st.success("**Your selected cuts could stop the loss of savings, if you follow through.**")
        st.caption("Illustration assumes the same income and spending, without interest earned. It does not account for other uses of savings.")
    else:
        rate = APR / 12
        balance = 0.0
        owed_by_month = {0:0.0}
        for m in range(1, 13):
            balance = balance * (1 + rate) + gap
            if m in months: owed_by_month[m] = balance
        owed = [owed_by_month[m] for m in months]
        st.markdown("**Your debt including interest**")
        bar_chart(owed, labels, "#dc2626")
        st.write(f"**After 12 months:** You borrowed {money(gap*12)}. You could owe **{money(owed[-1])}**.")
        st.error(f"**Where will you get {money(owed[-1])} to pay it back?**")
        st.caption("Example uses 25% yearly interest, compounded monthly, with $0 repayments or fees and borrowing at each month-end. Real credit cards require minimum payments.")
    with st.expander("What's making it hard to spend less?"):
        reason = st.radio("Choose what fits", ["My friends go out and I don't want to miss out.",
            "I enjoy shopping or eating out.", "I'm too tired or busy.",
            "I didn't realize how much I spent.", "I keep putting it off.", "Something else."])
        if reason == "Something else.":
            st.text_input("What's getting in the way?")
        if st.button("What can I do today?"):
            if reason.startswith("My friends"):
                st.info("Your friends don't pay your bills. Choose a less expensive way to spend time together this week.")
            else:
                st.info("Pick one expense to stop or reduce this week, then check whether you followed through.")
    st.caption("You don't know what someone else can afford. Live according to your numbers, not their appearance.")
    st.button("Go back to ways to spend less", use_container_width=True,
              on_click=open_section, args=("Spend less",))

else:
    st.subheader("Get help")
    st.write("Talk with someone you trust or contact the company you owe before missing a payment.")

st.divider()
with st.expander("I have a plan / I need help"):
    st.write("**A plan isn't the same as money saved.** Check what actually happens before marking a problem solved.")
    if st.button("I need help drafting a message"):
        st.session_state["help"] = True
    if st.session_state["help"]:
        st.text_area("Draft for someone you trust", "I need help looking at my finances and choosing what to change. Can we talk today?")
        st.caption("Nothing is sent by this demo.")
st.caption("Phase 1: fictional data only. No linked bank accounts, no AI diagnosis, no messages sent. Do not enter actual personal financial information in this public demo.")
