import streamlit as st
from html import escape
from math import ceil

st.set_page_config(page_title="Borrowed Wisdom — What do I need to do today?", page_icon="🧭", layout="centered")

# One consistent visual language: type, spacing, headings, and unmistakable controls.
st.markdown("""<style>
:root { --bw-ink:#14263e; --bw-blue:#174f95; --bw-blue-pale:#e9f1fc; }
[data-testid="stAppViewContainer"] { font-family: Arial, Helvetica, sans-serif; color:var(--bw-ink); }
.block-container {max-width:810px; padding-top:2.2rem; padding-bottom:3rem;}
h1,h2,h3,p,div,span,label,button {font-family:Arial,Helvetica,sans-serif;}
h1 {font-size:2rem !important; font-weight:750 !important; letter-spacing:-.035em;}
h2,h3 {font-size:1.3rem !important; font-weight:750 !important; letter-spacing:-.02em;}
[data-testid="stCaptionContainer"] p {font-size:.81rem;color:#697789;}
/* Distinct, consistent click surfaces rather than text disguised as controls. */
.stButton > button {min-height:48px !important; border-radius:10px !important;
   border:2px solid #174f95 !important; color:#174f95 !important;
   background:#e9f1fc !important; font-size:1rem !important;font-weight:750 !important;}
.stButton > button:hover {background:#d6e8ff !important; color:#123d75 !important;}
.stButton > button[kind="primary"] {color:white !important; background:#174f95 !important;}
.stButton > button[kind="primary"]:hover {background:#103969 !important;}
[data-testid="stExpander"] {border:1px solid #c8d7e7 !important;border-radius:9px !important;}
[data-testid="stExpander"] summary {background:#eef4fc; font-weight:700; color:#174f95;}
@media(max-width:600px){.block-container{padding:1rem 1rem 2rem;}h1{font-size:1.7rem !important;}}
</style>""", unsafe_allow_html=True)

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

def compare_bars(original, changed, labels, unit="savings"):
    """Compare paths. Savings may go below zero: that is an unfunded gap, not a bank balance."""
    color_bad = "#c52332"
    color_good = "#168a50"
    cards = []
    if unit == "savings":
        # Common zero line across all dates; negative portions drop below it.
        top_limit = max([0, *original, *changed, 1])
        bottom_limit = max([0, *(-x for x in original), *(-x for x in changed), 1])
        top_px, bottom_px = 135, 64

        def bar(value, color):
            above = round(max(0, value) / top_limit * top_px)
            below = round(max(0, -value) / bottom_limit * bottom_px) if bottom_limit > 1 else 0
            label = money(value) if value >= 0 else f"SHORT {money(-value)}"
            return (f'<div style="flex:1;min-width:0;text-align:center">'
                    f'<div style="font-size:clamp(10px,1.55vw,14px);font-weight:750;'
                    f'color:{color};white-space:normal;min-height:36px">{label}</div>'
                    f'<div style="height:{top_px}px;display:flex;align-items:flex-end;justify-content:center">'
                    f'<div style="height:{above}px;width:80%;background:{color};border-radius:5px 5px 0 0"></div></div>'
                    f'<div style="border-top:2px solid #566477;height:{bottom_px}px;'
                    f'display:flex;align-items:flex-start;justify-content:center">'
                    f'<div style="height:{below}px;width:80%;background:#991b1b;'
                    f'border-radius:0 0 5px 5px"></div></div></div>')
    else:
        maximum = max([*original, *changed, 1])
        def bar(value, color):
            height = max(3, round(max(0,value) / maximum * 155)) if value > 0 else 0
            return (f'<div style="flex:1;min-width:0;text-align:center">'
                    f'<div style="font-size:clamp(11px,2vw,15px);font-weight:700;color:{color};'
                    f'white-space:nowrap">{money(value)}</div>'
                    f'<div style="height:165px;display:flex;align-items:flex-end;justify-content:center">'
                    f'<div style="height:{height}px;width:80%;background:{color};'
                    f'border-radius:5px 5px 0 0"></div></div></div>')
    for old, new, label in zip(original, changed, labels):
        cards.append('<div style="flex:1;min-width:0;text-align:center">'
                     '<div style="display:flex;gap:5px;align-items:start">'
                     +bar(old,color_bad)+bar(new,color_good)+'</div>'
                     f'<div style="font-size:13px;font-weight:700;margin-top:7px">{label}</div></div>')
    st.markdown('<div style="display:flex;gap:10px;margin:12px 0 4px;padding-bottom:12px">'
                + ''.join(cards) + '</div>', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;gap:20px;flex-wrap:wrap;font-size:14px;margin:0 0 15px">'
                '<span><b style="color:#c52332">■</b> No changes</span>'
                '<span><b style="color:#168a50">■</b> With your selected cuts</span>'
                + ('<span><b style="color:#991b1b">■</b> Below zero = money still needed</span>' if unit == "savings" else '')
                + '</div>', unsafe_allow_html=True)

st.title("🧭 Borrowed Wisdom")
st.caption("What do I need to do today?  |  Fictional examples")
scenario = st.selectbox("Choose a situation to test", list(SCENARIOS))
s = SCENARIOS[scenario]
case = scenario[0]
if st.session_state.get("active_case") != case:
    st.session_state["active_case"] = case
    st.session_state["section"] = "Today"
    # Keep plans per scenario even when changing screens.
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
# PERMANENT plan state and TEMPORARY widget state are intentionally separate.
# Streamlit deletes widget state when a screen is hidden. It must never delete the plan.
def saved_selected_key(label):
    return f"bw_saved_selected_{case}_{label}"

def saved_amount_key(label):
    return f"bw_saved_amount_{case}_{label}"

def checkbox_key(label):
    return f"bw_ui_selected_{case}_{label}"

def amount_widget_key(label):
    return f"bw_ui_amount_{case}_{label}"

def ensure_saved_choice(label, suggested):
    st.session_state.setdefault(saved_selected_key(label), False)
    st.session_state.setdefault(saved_amount_key(label), suggested)

def store_choice(label):
    st.session_state[saved_selected_key(label)] = bool(
        st.session_state.get(checkbox_key(label), False)
    )
    if amount_widget_key(label) in st.session_state:
        st.session_state[saved_amount_key(label)] = int(
            st.session_state[amount_widget_key(label)]
        )

def snapshot_spending_screen():
    # Save active widgets *before* switching away from the spending page.
    if st.session_state.get("section") != "Spend less":
        return
    for label, spent, suggested in CATEGORIES:
        if not suggested:
            continue
        ensure_saved_choice(label, suggested)
        if checkbox_key(label) in st.session_state:
            store_choice(label)

def open_section(destination):
    snapshot_spending_screen()
    if st.session_state.get("section") == "Spend less" and destination != "Spend less":
        for label, _, suggested in CATEGORIES:
            if suggested:
                st.session_state.pop(checkbox_key(label), None)
                st.session_state.pop(amount_widget_key(label), None)
    st.session_state["section"] = destination

def set_full_spending_cut(label, spent):
    # This button represents a planned 100% reduction, not verified savings.
    st.session_state[saved_selected_key(label)] = True
    st.session_state[saved_amount_key(label)] = spent
    st.session_state[checkbox_key(label)] = True
    st.session_state[amount_widget_key(label)] = spent

# Show only one screen at a time.
sections = ["Today", "Spend less", "See my future"] if case == "1" else ["Today", "Get help"]
if st.session_state.get("section") not in sections:
    st.session_state["section"] = "Today"
nav_columns = st.columns(len(sections), gap="small")
for nav_column, nav_section in zip(nav_columns, sections):
    with nav_column:
        st.button(nav_section, key=f"nav_{nav_section}", use_container_width=True,
                  type="primary" if st.session_state["section"] == nav_section else "secondary",
                  on_click=open_section, args=(nav_section,))
section = st.session_state["section"]

def total_selected_cuts():
    total = 0
    for label, spent, suggested in CATEGORIES:
        if suggested:
            ensure_saved_choice(label, suggested)
            if st.session_state[saved_selected_key(label)]:
                total += min(spent, max(0, int(st.session_state[saved_amount_key(label)])))
    return total

if section == "Today":
    st.subheader("Where do I stand?")
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
    st.subheader("What do I need to do today?")
    if case == "1" and monthly_shortfall:
        st.markdown(f"**Find a way to spend {money(monthly_shortfall)} less each month.**")
        st.button(f"Help me find {money(monthly_shortfall)}  →", type="primary", use_container_width=True,
                  on_click=open_section, args=("Spend less",))
    elif remaining_cash < 0:
        st.write(f"**Find a way to cover {money(abs(remaining_cash))} before your bills are due.**")
    elif case == "4":
        st.write(f"**Set aside {money(s['annual'])} for the annual insurance bill.**")
    else:
        st.write("**Check that your next bill is paid.**")
    if case == "1" and monthly_shortfall:
        st.subheader("What happens if I do nothing?")
        st.write("**Your available money will fall or your debt will rise.**")
        st.button("Show me my future  →", type="primary", use_container_width=True,
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
    # Each visit reconstructs temporary UI controls from a *permanent* plan.
    # The saved values survive Streamlit's cleanup of hidden widgets.
    for title, spent, suggested in CATEGORIES:
        select_key = checkbox_key(title)
        cut_key = amount_widget_key(title)
        if suggested:
            ensure_saved_choice(title, suggested)
            # Rehydrate on every visit; callbacks write every edit immediately.
            if select_key not in st.session_state:
                st.session_state[select_key] = st.session_state[saved_selected_key(title)]
            if cut_key not in st.session_state:
                st.session_state[cut_key] = min(spent, max(0, int(st.session_state[saved_amount_key(title)])))
        left, mid, right = st.columns([2.7, 1.3, 2.0], vertical_alignment="center")
        with left:
            if suggested:
                active = st.checkbox(title, key=select_key, on_change=store_choice, args=(title,))
            else:
                st.checkbox(title, key=f"disabled_{case}_{title}", value=False, disabled=True)
                active = False
        with mid:
            st.write(money(spent))
        with right:
            if active and suggested:
                amount_col, all_col = st.columns([3, 1], vertical_alignment="center")
                with amount_col:
                    st.number_input(f"Spend less on {title}", min_value=0, max_value=spent,
                        step=10, label_visibility="collapsed", key=cut_key,
                        on_change=store_choice, args=(title,))
                with all_col:
                    st.button("All", key=f"all_{case}_{title}",
                        help=f"Stop all {money(spent)} of {title.lower()} spending each month",
                        on_click=set_full_spending_cut, args=(title, spent),
                        use_container_width=True)
            elif suggested:
                st.caption(f"Try {money(suggested)}")
            else:
                st.caption("Essential / review first")
    saved = total_selected_cuts()
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
    st.button("Show what my choices do to my future  →", type="primary", use_container_width=True,
              on_click=open_section, args=("See my future",))

elif section == "See my future":
    st.subheader("SHOW ME THE MONEY!")
    st.markdown(f"**You spend {money(monthly_shortfall)} more than you earn each month. Where will you get the money?**")

    # Project both paths automatically. Selections are tentative plans, not verified savings.
    potential = total_selected_cuts()
    without_gap = monthly_shortfall
    with_gap = max(0, monthly_shortfall - potential)
    st.markdown(
        f'<div style="display:flex;gap:12px;flex-wrap:wrap;margin:14px 0 18px">'
        f'<div style="flex:1;min-width:195px;border-left:5px solid #c52332;background:#fff1f2;padding:13px;border-radius:7px">'
        f'<div style="font-size:14px;font-weight:700">No changes</div><div style="font-size:23px;font-weight:800;color:#aa202b">{money(without_gap)} / month</div></div>'
        f'<div style="flex:1;min-width:195px;border-left:5px solid #168a50;background:#eefaf2;padding:13px;border-radius:7px">'
        f'<div style="font-size:14px;font-weight:700">With your selected cuts</div><div style="font-size:23px;font-weight:800;color:#127846">{money(with_gap)} / month</div></div></div>',
        unsafe_allow_html=True)

    funding = st.radio("How are you covering the extra spending?", ["Using savings", "Using a credit card"], horizontal=True)
    months = [0, 3, 6, 12]
    labels = ["Today", "3 months", "6 months", "12 months"]
    if funding == "Using savings":
        savings = st.number_input("Savings available ($)", min_value=0, max_value=1000000, value=10000, step=100)
        no_change = [savings - without_gap * m for m in months]
        with_change = [savings - with_gap * m for m in months]
        st.markdown("**How much money will you have—or still need?**")
        compare_bars(no_change, with_change, labels, "savings")
        if without_gap > 0:
            when = ceil(savings / without_gap) if savings else 0
            st.error(f"**If nothing changes, your {money(savings)} savings run out in about {when} months.**")
            if no_change[-1] < 0:
                st.error(f"**At 12 months, your savings are gone. You still need {money(-no_change[-1])}. Where will you get the money?**")
        if potential:
            if with_change[-1] >= 0:
                st.success(f"**With your selected cuts, you could have {money(with_change[-1])} left after 12 months.**")
            else:
                st.warning(f"**Even with your selected cuts, you would still need {money(-with_change[-1])} after 12 months.**")
        if with_gap > 0 and savings - with_gap * 12 < 0:
            st.warning("Your selected cuts would still use up your savings within 12 months.")
        st.caption("Illustration assumes the same income and expenses each month, with no interest on savings. Amounts below $0 show an unfunded shortage—not a negative savings balance. Your selected cuts must actually happen.")
    else:
        def projected_debt(gap):
            balance = 0.0
            results = [0.0]
            for m in range(1, 13):
                balance = balance * (1 + APR / 12) + gap
                if m in (3, 6, 12):
                    results.append(balance)
            return results
        no_change = projected_debt(without_gap)
        with_change = projected_debt(with_gap)
        st.markdown("**How much could you owe?**")
        compare_bars(no_change, with_change, labels, "debt")
        st.error(f"**After 12 months: Without changes, you could owe {money(no_change[-1])}.**")
        if potential:
            st.success(f"**With your selected cuts, you could owe {money(with_change[-1])}.**")
        st.markdown("**Where will you get the money to pay it back?**")
        st.caption("Example: 25% yearly credit-card interest, compounded monthly; the remaining shortage is borrowed at each month-end, with no repayments or extra fees. Real cards require minimum payments. Your cuts must actually happen.")

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
    st.button("← Go back to ways to spend less", type="primary", use_container_width=True,
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
