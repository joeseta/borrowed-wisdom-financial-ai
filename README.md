# Borrowed Wisdom — Daily Financial Assistant (Phase 1)

## Purpose
A small, *working*, fictional-data prototype to test the question: **“What do I need to do today?”** It models the 3-screen experience: financial position, specific warning and suggested next action, and asking a trusted person for help.

## Run locally
1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run `python -m pip install -r requirements.txt`.
4. Run `python -m streamlit run app.py`.
5. Open the local URL Streamlit shows.

## Phase 1 tests
Try each of the five fictional cases, vary expected income/cash/bills, open the explanation, select “I have a plan” and “I need help,” and ask a novice tester *what they would do next*. Do not hand them instructions.

## Explicitly not yet implemented
- Live Simplifi access or transaction upload
- Actual bank balance / credit-card balance reconciliation
- AI-generated cause analysis (the scenario causes are scripted)
- Alerts/notifications, helper messaging, account login, persistent user data
- Automatic matching of predicted to actual transactions

## Security and deployment
This prototype has no live financial data. For a family pilot with sensitive data, use a **separate private GitHub repository** for code, private authenticated hosting, encrypted persistent storage, and permission-based access. Do not place exported financial data in GitHub, Streamlit Community Cloud public apps, or repository secrets. Validate integration options and data permissions before connecting Simplifi.

## Next step
Add a documented Simplifi-CSV adapter; validate classification (income vs transfers; card purchases vs card payments), due dates and actual balances against known statements. Add read-only forecasting, explainable rule-based alerts, consent-based trusted helper escalation, and only then AI for diagnosis and suggested actions with strict fact-checking.
