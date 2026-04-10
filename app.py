import streamlit as st
import pandas as pd
import altair as alt
import resend
import os

st.set_page_config(page_title="DSCR Covenant Risk Checker", layout="wide", page_icon="📈")

# Define Covenant Thresholds
DSCR_BREACH_THRESHOLD = 1.25
DSCR_WARNING_THRESHOLD = 1.50

# Initial Mock Data (Last 3 Years)
DEFAULT_DATA = {
    "Quarter": ["Q4 2023", "Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024", 
                "Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", 
                "Q1 2026", "Q2 2026", "Q3 2026"],
    "Revenue": [8.00, 9.00, 10.00, 11.50, 13.00, 14.50, 15.00, 14.50, 13.50, 12.50, 11.25, 10.00],
    "COGS": [4.00, 4.40, 4.80, 5.20, 5.50, 6.00, 6.30, 6.40, 6.20, 6.25, 5.85, 5.50],
    "Opex": [2.00, 2.20, 2.40, 2.60, 2.90, 3.20, 3.50, 3.70, 3.80, 3.75, 3.50, 3.20],
    "AI_Costs": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.50, 0.0],
    "D_and_A": [0.50]*12,
    "Interest_Expense": [1.00]*12,
    "Tax": [0.15, 0.25, 0.35, 0.55, 0.85, 1.15, 1.10, 0.80, 0.50, 0.45, 0.16, 0.12],
    "Scheduled_Principal": [0.675]*12
}

def init_state():
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(DEFAULT_DATA)
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None
    if "selected_company" not in st.session_state:
        st.session_state.selected_company = None

init_state()

st.title("📈 DSCR Covenant Risk Checker")
st.markdown("Monitor Debt Service Coverage Ratio (DSCR) against credit agreement covenants to identify and mitigate breach risks.")

with st.sidebar:
    st.header("1. Data Source")
    st.markdown("Upload a CSV file containing your company data.")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    
    if uploaded_file is not None:
        if st.session_state.uploaded_filename != uploaded_file.name:
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.full_uploaded_df = pd.read_csv(uploaded_file)
            st.session_state.selected_company = None
            
        if "Company" in st.session_state.full_uploaded_df.columns:
            companies = st.session_state.full_uploaded_df["Company"].unique()
            selected_company = st.selectbox("Select Company", companies)
            
            if selected_company != st.session_state.selected_company:
                st.session_state.selected_company = selected_company
                df_filtered = st.session_state.full_uploaded_df[st.session_state.full_uploaded_df["Company"] == selected_company].drop(columns=["Company"])
                st.session_state.df = df_filtered.reset_index(drop=True)
                st.rerun() # Refresh the view with new data
        else:
            if st.session_state.selected_company != "Unknown (Single File)":
                st.session_state.selected_company = "Unknown (Single File)"
                st.session_state.df = st.session_state.full_uploaded_df.copy()
                st.rerun()

    st.markdown("---")
    st.header("Settings")
    alert_email = st.text_input("Alert Email Address", help="Email to receive risk alerts.")

# --- Data Input Section ---
st.header("1. Financial Data ($ millions)")
st.markdown("Edit the current quarterly data or add new quarters to forecast risk.")
edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
st.session_state.df = edited_df

# --- Scenario Analysis Section ---
st.header("2. Scenario Analysis")
col1, col2 = st.columns(2)
with col1:
    rev_scenario = st.slider("Latest Quarter Revenue Adjustment (%)", -50, 50, 0, 1)
with col2:
    opex_scenario = st.slider("Latest Quarter Opex Adjustment (%)", -50, 50, 0, 1)

# --- Calculation Section ---
calc_df = st.session_state.df.copy()

if len(calc_df) > 0:
    last_idx = calc_df.index[-1]
    calc_df.at[last_idx, 'Revenue'] = calc_df.at[last_idx, 'Revenue'] * (1 + rev_scenario / 100.0)
    calc_df.at[last_idx, 'Opex'] = calc_df.at[last_idx, 'Opex'] * (1 + opex_scenario / 100.0)

calc_df['Net_Income'] = calc_df['Revenue'] - calc_df['COGS'] - calc_df['Opex'] - calc_df['AI_Costs'] - calc_df['D_and_A'] - calc_df['Interest_Expense'] - calc_df['Tax']
calc_df['Covenant_EBITDA'] = calc_df['Net_Income'] + calc_df['Interest_Expense'] + calc_df['Tax'] + calc_df['D_and_A'] + calc_df['AI_Costs']
calc_df['Debt_Service'] = calc_df['Interest_Expense'] + calc_df['Scheduled_Principal']
calc_df['DSCR'] = calc_df['Covenant_EBITDA'] / calc_df['Debt_Service']
calc_df['DSCR'] = calc_df['DSCR'].round(2)

# --- Visualization Section ---
st.header("3. Covenant Risk Dashboard")

if len(calc_df) > 0:
    current_dscr = calc_df.iloc[-1]['DSCR']
    
    if current_dscr < DSCR_BREACH_THRESHOLD:
        status_color = "red"
        status_text = "🚨 BREACH RISK: Critical"
    elif current_dscr < DSCR_WARNING_THRESHOLD:
        status_color = "orange"
        status_text = "⚠️ WARNING: Distribution Lock-up (1.50x)"
    else:
        status_color = "green"
        status_text = "✅ COMPLIANT"

    st.subheader(f"Current Status: {status_text}")
    
    chart_data = calc_df[['Quarter', 'DSCR']].copy()
    
    base = alt.Chart(chart_data).mark_line(point=True, size=3).encode(
        x=alt.X('Quarter:O', sort=None),
        y=alt.Y('DSCR:Q', title="Debt Service Coverage Ratio (DSCR)", scale=alt.Scale(domain=[0, max(3.0, chart_data['DSCR'].max() + 0.5)])),
        tooltip=['Quarter', 'DSCR']
    )
    
    breach_line = alt.Chart(pd.DataFrame({'y': [DSCR_BREACH_THRESHOLD]})).mark_rule(color='red', strokeDash=[5,5], size=2).encode(y='y')
    warning_line = alt.Chart(pd.DataFrame({'y': [DSCR_WARNING_THRESHOLD]})).mark_rule(color='orange', strokeDash=[5,5], size=2).encode(y='y')
    
    st.altair_chart(base + warning_line + breach_line, use_container_width=True)

# --- Recommendations & Email Alert ---
st.header("4. Remediation & Action Plan")
if len(calc_df) > 0 and current_dscr < DSCR_WARNING_THRESHOLD:
    if current_dscr < DSCR_BREACH_THRESHOLD:
        st.error(f"Company is projected to breach the {DSCR_BREACH_THRESHOLD}x DSCR covenant. Immediate action required.")
        shortfall_ebitda = (DSCR_BREACH_THRESHOLD * calc_df.iloc[-1]['Debt_Service']) - calc_df.iloc[-1]['Covenant_EBITDA']
        
        st.subheader("Recommended Actions based on Credit Agreement:")
        recommendations = f"""
* **Opt 1: Equity Cure (Section 8.02):** Raise **${shortfall_ebitda:.2f}M** in new equity to cure the EBITDA shortfall. You are permitted 2 cures during the loan term.
* **Opt 2: Reduce Operating Expenses:** Decrease Opex by **${shortfall_ebitda:.2f}M** to improve Covenant EBITDA organically.
* **Opt 3: Pay Down Debt:** Reduce scheduled principal/interest. Use available cash (Liquidity: > $5.0M) to prepay principal, which will reduce debt service.
"""
        st.markdown(recommendations)
        
        st.markdown("---")
        st.subheader("Send Risk Alert")
        st.info("💡 **Note on Free Resend Accounts:** When using the default sender (`onboarding@resend.dev`), Resend only permits sending emails to the exact email address you used to register your API key. For other addresses, you must verify a custom domain in Resend.")
        if st.button("📧 Email Breach Alert to Team"):
            resend_api_key = os.environ.get("RESEND_API_KEY")
            if not resend_api_key:
                st.warning("⚠️ RESEND_API_KEY environment variable not found. Please set it before sending emails.")
            elif not alert_email:
                st.warning("Please provide an Alert Email in the sidebar.")
            else:
                try:
                    display_company = st.session_state.selected_company if st.session_state.selected_company and st.session_state.selected_company != "Unknown (Single File)" else "The company"
                    resend.api_key = resend_api_key
                    email_body = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                        <div style="background-color: #d32f2f; color: white; padding: 20px; text-align: center;">
                            <h2 style="margin: 0; font-size: 24px;">🚨 URGENT: Covenant Breach Alert</h2>
                        </div>
                        <div style="padding: 30px; background-color: #fafafa;">
                            <p style="font-size: 16px; color: #333; line-height: 1.5;"><strong>{display_company}</strong> is currently projected to breach the <strong>{DSCR_BREACH_THRESHOLD}x</strong> Debt Service Coverage Ratio (DSCR) limit set by the credit agreement.</p>
                            
                            <div style="background-color: white; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                                <p style="margin: 0; font-size: 18px; color: #d32f2f;"><strong>Current DSCR Projection: {current_dscr}x</strong></p>
                            </div>

                            <h3 style="color: #444; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 30px;">Actionable Mitigation Steps</h3>
                            <p style="font-size: 15px; color: #555;">Based on the mock credit agreement provisions, {display_company} has the following options to cure this shortfall:</p>
                            
                            <ul style="font-size: 15px; color: #555; line-height: 1.6; padding-left: 20px;">
                                <li style="margin-bottom: 10px;"><strong>Equity Cure (Section 8.02):</strong> Raise <strong>${shortfall_ebitda:.2f}M</strong> in new equity to cure the EBITDA shortfall. You are permitted 2 cures during the loan term.</li>
                                <li style="margin-bottom: 10px;"><strong>Reduce Operating Expenses:</strong> Decrease Opex by <strong>${shortfall_ebitda:.2f}M</strong> to improve Covenant EBITDA organically.</li>
                                <li style="margin-bottom: 10px;"><strong>Pay Down Debt:</strong> Reduce scheduled principal/interest using available cash reserves.</li>
                            </ul>
                            
                            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                            <p style="font-size: 12px; color: #999; text-align: center;">This is an automated alert generated by your DSCR AI monitoring system.</p>
                        </div>
                    </div>
                    """
                    
                    r = resend.Emails.send({
                        "from": "onboarding@resend.dev",
                        "to": alert_email,
                        "subject": f"URGENT: DSCR Covenant Breach Projected for {display_company}",
                        "html": email_body
                    })
                    st.success("✅ Alert email sent to the API successfully! If it doesn't appear in 1-2 minutes, please check your Spam/Junk folder and confirm the email matches your Resend login.")
                except Exception as e:
                    st.error(f"Error from Resend API (Delivery failed): {e}")
                    
    else:
        st.warning("DSCR is below 1.50x. Distribution Lock-up is in effect.")
        st.markdown("Ensure Operating Expenses do not increase further and review upcoming debt service.")
else:
    st.success("Company is comfortably above all covenant thresholds. No immediate mitigation required.")

with st.expander("View Full Calculation Table"):
    st.dataframe(calc_df.style.format("{:.2f}", subset=['Revenue', 'COGS', 'Opex', 'AI_Costs', 'D_and_A', 'Interest_Expense', 'Tax', 'Scheduled_Principal', 'Net_Income', 'Covenant_EBITDA', 'Debt_Service', 'DSCR']))
