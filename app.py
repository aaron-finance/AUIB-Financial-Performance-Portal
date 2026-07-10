import os
# Set Streamlit theme BEFORE importing streamlit so every control uses AUIB navy.
os.environ.setdefault("STREAMLIT_THEME_BASE", "light")
os.environ.setdefault("STREAMLIT_THEME_PRIMARY_COLOR", "#17365D")
os.environ.setdefault("STREAMLIT_THEME_BACKGROUND_COLOR", "#FAFAFB")
os.environ.setdefault("STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR", "#F1F3F5")
os.environ.setdefault("STREAMLIT_THEME_TEXT_COLOR", "#20242A")

from datetime import datetime
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_VERSION = "3.1.0"
CRIMSON = "#AB0A3D"
NAVY = "#17365D"
GREY = "#8C9091"

st.set_page_config(
    page_title=f"AUIB Financial Performance Portal v{APP_VERSION}",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Baseline data ----------
PROGRAMMES = [
    {"college":"Arts & Sciences","programme":"Undergraduate","fy26_enrolled":212,"fy27_new_intake":56,"fy27_projected":193,"fy26_tuition":4469.70,"teaching_allocation":0.00},
    {"college":"Business","programme":"Undergraduate","fy26_enrolled":523,"fy27_new_intake":208,"fy27_projected":617,"fy26_tuition":4318.18,"teaching_allocation":0.75},
    {"college":"Business","programme":"MBA","fy26_enrolled":44,"fy27_new_intake":24,"fy27_projected":48,"fy26_tuition":15909.09,"teaching_allocation":0.00},
    {"college":"Dentistry","programme":"Undergraduate","fy26_enrolled":729,"fy27_new_intake":154,"fy27_projected":742,"fy26_tuition":10606.06,"teaching_allocation":0.75},
    {"college":"Education & Human Development","programme":"Undergraduate","fy26_enrolled":23,"fy27_new_intake":2,"fy27_projected":25,"fy26_tuition":4318.18,"teaching_allocation":0.75},
    {"college":"Education & Human Development","programme":"M-HEAL","fy26_enrolled":11,"fy27_new_intake":11,"fy27_projected":22,"fy26_tuition":15909.09,"teaching_allocation":0.00},
    {"college":"Engineering","programme":"Undergraduate","fy26_enrolled":402,"fy27_new_intake":270,"fy27_projected":672,"fy26_tuition":6818.18,"teaching_allocation":0.75},
    {"college":"Health Care Technologies","programme":"Undergraduate","fy26_enrolled":275,"fy27_new_intake":59,"fy27_projected":209,"fy26_tuition":5530.30,"teaching_allocation":0.75},
    {"college":"International Studies","programme":"Undergraduate","fy26_enrolled":95,"fy27_new_intake":44,"fy27_projected":119,"fy26_tuition":4318.18,"teaching_allocation":0.75},
    {"college":"Law","programme":"Undergraduate","fy26_enrolled":98,"fy27_new_intake":34,"fy27_projected":110,"fy26_tuition":4318.18,"teaching_allocation":0.75},
    {"college":"Pharmacy","programme":"Undergraduate","fy26_enrolled":760,"fy27_new_intake":134,"fy27_projected":775,"fy26_tuition":8333.33,"teaching_allocation":0.75},
]
COLLEGES = {
    "Arts & Sciences":{"fy27_baseline_tuition":862151.52,"scholarship_rate":0.04311313,"fy26_direct_expense":3894549.27},
    "Business":{"fy27_baseline_tuition":3556000.00,"scholarship_rate":0.18146070,"fy26_direct_expense":1436505.66},
    "Dentistry":{"fy27_baseline_tuition":7138393.94,"scholarship_rate":0.25468670,"fy26_direct_expense":1987782.18},
    "Education & Human Development":{"fy27_baseline_tuition":478818.18,"scholarship_rate":0.33817770,"fy26_direct_expense":623427.69},
    "Engineering":{"fy27_baseline_tuition":4829454.55,"scholarship_rate":0.28049270,"fy26_direct_expense":293735.42},
    "Health Care Technologies":{"fy27_baseline_tuition":1156518.94,"scholarship_rate":0.17802310,"fy26_direct_expense":1150131.08},
    "International Studies":{"fy27_baseline_tuition":532500.00,"scholarship_rate":0.46408691,"fy26_direct_expense":505442.13},
    "Law":{"fy27_baseline_tuition":483659.09,"scholarship_rate":0.36743141,"fy26_direct_expense":646281.31},
    "Pharmacy":{"fy27_baseline_tuition":6155469.70,"scholarship_rate":0.22465874,"fy26_direct_expense":1381408.25},
}
GLOBAL_DEFAULTS = {
    "shared_growth": 5.0,
    "variable_expense_pct": 65.0,
    "expense_inflation": 0.0,
    "ela_growth": 12.5,
    "ceid_growth": 500.0,
}
TUITION_DEFAULTS = {c: 15.0 for c in COLLEGES}
SCHOLARSHIP_DEFAULTS = {c: round(v["scholarship_rate"]*100,1) for c,v in COLLEGES.items()}
INTAKE_DEFAULTS = {f"{p['college']}|{p['programme']}": p["fy27_new_intake"] for p in PROGRAMMES}
ALLOC_DEFAULTS = {f"{p['college']}|{p['programme']}": round(p["teaching_allocation"]*100,0) for p in PROGRAMMES}

# ---------- Styling ----------
st.markdown(f"""
<style>
.stApp {{ background: #FAFAFB; }}
[data-testid='stSidebar'] {{ background:#F1F3F5; }}
h1,h2,h3 {{ color:{NAVY}; }}
.portal-banner {{ background:linear-gradient(90deg,{NAVY},#284F7C); color:white; padding:20px 22px; border-radius:12px; margin-bottom:12px; }}
.portal-banner h1 {{ color:white; margin:0; font-size:1.7rem; }}
.portal-banner p {{ margin:5px 0 0; opacity:.92; }}
.section-title {{ color:{CRIMSON}; font-weight:700; font-size:1.05rem; border-bottom:2px solid {CRIMSON}; padding-bottom:5px; margin:10px 0 12px; }}
.notice {{ background:#FFF8E8; border-left:4px solid #D99A00; padding:10px 12px; border-radius:5px; margin-bottom:12px; }}
div[data-testid='stMetric'] {{ background:white; border:1px solid #E3E6EA; padding:14px 16px; border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,.05); }}
/* Force every interactive slider to AUIB navy in both main canvas and sidebar. */
[data-testid='stSlider'] [role='slider'] {{
  background-color:{NAVY} !important;
  border-color:{NAVY} !important;
  box-shadow:0 0 0 1px {NAVY} !important;
}}
[data-testid='stSlider'] [data-baseweb='slider'] > div > div {{
  background-color:#C7D0DB !important;
}}
[data-testid='stSlider'] [data-baseweb='slider'] > div > div > div {{
  background-color:{NAVY} !important;
}}
[data-testid='stSlider'] svg {{ color:{NAVY} !important; fill:{NAVY} !important; }}
[data-testid='stRadio'] [aria-checked='true'] {{ color:{NAVY} !important; }}
button[kind='primary'], button[data-testid='stBaseButton-primary'] {{ background-color:{NAVY} !important; border-color:{NAVY} !important; }}
</style>
""", unsafe_allow_html=True)

def section(title):
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)

def money(v):
    if not math.isfinite(float(v)): return "$0"
    sign = "-" if v < 0 else ""
    v = abs(float(v))
    if v >= 1_000_000: return f"{sign}${v/1_000_000:,.1f}M"
    if v >= 1_000: return f"{sign}${v/1_000:,.0f}K"
    return f"{sign}${v:,.0f}"

def reset_all():
    for key, value in GLOBAL_DEFAULTS.items(): st.session_state[key] = value
    for college, value in TUITION_DEFAULTS.items(): st.session_state[f"tuition::{college}"] = value
    for college, value in SCHOLARSHIP_DEFAULTS.items(): st.session_state[f"scholarship::{college}"] = value
    for key, value in INTAKE_DEFAULTS.items(): st.session_state[f"intake::{key}"] = value
    for key, value in ALLOC_DEFAULTS.items(): st.session_state[f"allocation::{key}"] = value
    st.session_state["college_select"] = "Engineering"
    st.session_state["page_nav"] = "Executive Dashboard"

# Initialise only when absent.
for key, value in GLOBAL_DEFAULTS.items(): st.session_state.setdefault(key, value)
for college, value in TUITION_DEFAULTS.items(): st.session_state.setdefault(f"tuition::{college}", value)
for college, value in SCHOLARSHIP_DEFAULTS.items(): st.session_state.setdefault(f"scholarship::{college}", value)
for key, value in INTAKE_DEFAULTS.items(): st.session_state.setdefault(f"intake::{key}", value)
for key, value in ALLOC_DEFAULTS.items(): st.session_state.setdefault(f"allocation::{key}", value)
st.session_state.setdefault("college_select", "Engineering")
st.session_state.setdefault("page_nav", "Executive Dashboard")

# ---------- Sidebar ----------
st.sidebar.markdown("## Scenario controls")
st.sidebar.caption("All changes recalculate immediately. No Excel access is required.")
st.sidebar.button("Reset to workbook baseline", on_click=reset_all, width="stretch")

with st.sidebar.expander("University assumptions", expanded=True):
    st.slider("Shared Services growth", -10.0, 25.0, step=0.5, key="shared_growth", format="%.1f%%")
    st.slider("Variable portion of College expenses", 0.0, 100.0, step=5.0, key="variable_expense_pct", format="%.0f%%")
    st.slider("General expense inflation", -5.0, 20.0, step=0.5, key="expense_inflation", format="%.1f%%")
    st.slider("ELA revenue growth", -25.0, 100.0, step=2.5, key="ela_growth", format="%.1f%%")
    st.slider("CEID revenue growth", -50.0, 600.0, step=25.0, key="ceid_growth", format="%.0f%%")

st.sidebar.markdown("### College tuition assumptions")
for college in COLLEGES:
    st.sidebar.slider(college, -20.0, 100.0, step=1.0, key=f"tuition::{college}", format="%.0f%%")

st.sidebar.markdown("### Programme intake assumptions")
for p in PROGRAMMES:
    pkey = f"{p['college']}|{p['programme']}"
    with st.sidebar.expander(f"{p['college']} — {p['programme']}"):
        st.number_input("New intake", 0, 3000, step=1, key=f"intake::{pkey}")
        if p["programme"] == "Undergraduate" and p["college"] != "Arts & Sciences":
            st.slider("Arts & Sciences teaching allocation", 0.0, 100.0, step=5.0, key=f"allocation::{pkey}", format="%.0f%%")

st.sidebar.markdown("### Scholarships")
for college in COLLEGES:
    st.sidebar.slider(college, 0.0, 70.0, step=0.5, key=f"scholarship::{college}", format="%.1f%%")

# ---------- Calculation ----------
def calculate():
    rows = []
    prepared = []
    total_transfer = 0.0
    for college, cbase in COLLEGES.items():
        cps = [p for p in PROGRAMMES if p["college"] == college]
        tuition_pct = st.session_state[f"tuition::{college}"] / 100.0
        baseline_new = 0.0
        scenario_new = 0.0
        transfer = 0.0
        fy26_students = 0
        fy27_students = 0
        new_intake = 0
        for p in cps:
            pkey = f"{p['college']}|{p['programme']}"
            intake = int(st.session_state[f"intake::{pkey}"])
            new_fee = p["fy26_tuition"] * (1 + tuition_pct)
            baseline_new += p["fy27_new_intake"] * p["fy26_tuition"] * 1.15
            scenario_new += intake * new_fee
            alloc_pct = st.session_state.get(f"allocation::{pkey}", ALLOC_DEFAULTS[pkey]) / 100.0
            if college != "Arts & Sciences": transfer += intake * new_fee * alloc_pct
            fy26_students += p["fy26_enrolled"]
            # Projected student count changes by movement in new intake versus baseline.
            fy27_students += max(0, p["fy27_projected"] + intake - p["fy27_new_intake"])
            new_intake += intake
        continuing = max(cbase["fy27_baseline_tuition"] - baseline_new, 0.0)
        gross = continuing + scenario_new
        if college != "Arts & Sciences": total_transfer += transfer
        prepared.append((college,cbase,gross,transfer,fy26_students,fy27_students,new_intake))

    for college,cbase,gross,transfer,fy26_students,fy27_students,new_intake in prepared:
        internal = total_transfer if college == "Arts & Sciences" else -transfer
        scholarship_pct = st.session_state[f"scholarship::{college}"] / 100.0
        scholarships = gross * scholarship_pct
        net = gross + internal - scholarships
        growth = fy27_students / fy26_students - 1 if fy26_students else 0.0
        expense = cbase["fy26_direct_expense"] * (1 + st.session_state["expense_inflation"]/100 + st.session_state["variable_expense_pct"]/100 * growth)
        expense = max(expense, 0.0)
        contribution = net - expense
        rows.append({
            "College":college,"FY26 Students":fy26_students,"FY27 Students":fy27_students,"New Intake":new_intake,
            "Gross Tuition Revenue":gross,"Internal Teaching Allocation":internal,"Scholarships":scholarships,
            "Scholarship %":scholarship_pct,"Net Revenue":net,"Net Revenue / Student":net/fy27_students if fy27_students else 0.0,
            "Operating Expenses":expense,"Operating Expenses / Student":expense/fy27_students if fy27_students else 0.0,
            "Operating Expenses %":expense/net if net else 0.0,"College Contribution":contribution,
            "College Contribution %":contribution/net if net else 0.0,
        })
    df = pd.DataFrame(rows)
    shared = 11_282_198.17 * (1 + st.session_state["shared_growth"]/100)
    ela = 3_082_685.61 * (1 + st.session_state["ela_growth"]/100) - 3_239_800.54 * (1 + st.session_state["expense_inflation"]/100)
    ceid = 500_000.00 * (1 + st.session_state["ceid_growth"]/100) - 1_709_726.89 * (1 + st.session_state["expense_inflation"]/100)
    college_contribution = float(df["College Contribution"].sum())
    university_result = college_contribution + ela + ceid - shared
    totals = {"students":int(df["FY27 Students"].sum()),"net_revenue":float(df["Net Revenue"].sum()),"college_contribution":college_contribution,"shared":shared,"other":ela+ceid,"result":university_result}
    return df, totals

results, totals = calculate()

# ---------- Header and navigation ----------
st.markdown(f"<div class='portal-banner'><h1>AUIB Financial Performance Portal</h1><p>Monthly Performance Pack · College Financial Performance Model · Version {APP_VERSION}</p></div>", unsafe_allow_html=True)
st.markdown("<div class='notice'><b>Standalone management model:</b> users do not require Excel or OneDrive access. Validate formal recommendations against the approved Finance workbook.</div>", unsafe_allow_html=True)

page = st.radio("Navigation", ["Executive Dashboard","Tuition Planning","College Performance","Statements","Controls"], horizontal=True, key="page_nav", label_visibility="collapsed")

if page == "Executive Dashboard":
    section("University at a glance")
    cols = st.columns(5)
    cols[0].metric("Projected Students", f"{totals['students']:,}")
    cols[1].metric("Net College Revenue", money(totals["net_revenue"]))
    cols[2].metric("College Contribution", money(totals["college_contribution"]))
    cols[3].metric("Shared Services", money(totals["shared"]))
    cols[4].metric("University Result", money(totals["result"]))
    left,right = st.columns(2)
    with left:
        d = results[results["College"] != "Arts & Sciences"].copy()
        fig = px.scatter(d, x="Net Revenue / Student", y="College Contribution %", size="FY27 Students", text="College", hover_name="College", title="College positioning")
        fig.update_traces(textposition="top center")
        fig.update_xaxes(tickprefix="$", title="Net Revenue per Student")
        fig.update_yaxes(tickformat=".0%", title="College Contribution %")
        fig.add_hline(y=0, line_dash="dot", line_color=GREY)
        fig.update_layout(height=460)
        st.plotly_chart(fig, width="stretch")
    with right:
        fig = go.Figure(go.Waterfall(x=["College Contribution","ELA & CEID","Shared Services","University Result"], y=[totals["college_contribution"],totals["other"],-totals["shared"],totals["result"]], measure=["absolute","relative","relative","total"]))
        fig.update_layout(title="Contribution to University result", yaxis_tickprefix="$", yaxis_tickformat="~s", height=460)
        st.plotly_chart(fig, width="stretch")

elif page == "Tuition Planning":
    section("Tuition and enrolment plan")
    table=[]
    for p in PROGRAMMES:
        pkey=f"{p['college']}|{p['programme']}"
        inc=st.session_state[f"tuition::{p['college']}"]/100
        table.append({"College":p["college"],"Programme":p["programme"],"FY26 Enrolled":p["fy26_enrolled"],"FY27 New Intake":st.session_state[f"intake::{pkey}"],"FY27 Tuition":p["fy26_tuition"]*(1+inc),"Increase %":inc})
    tdf=pd.DataFrame(table)
    st.dataframe(tdf, hide_index=True, width="stretch", column_config={"FY27 Tuition":st.column_config.NumberColumn(format="$%.0f"),"Increase %":st.column_config.NumberColumn(format="%.1f%%")})

elif page == "College Performance":
    section("College Performance Scorecard")
    selected=st.selectbox("Select College", list(COLLEGES), key="college_select")
    row=results.loc[results["College"]==selected].iloc[0]
    cols=st.columns(4)
    cols[0].metric("Students", f"{int(row['FY27 Students']):,}")
    cols[1].metric("Net Revenue", money(row["Net Revenue"]))
    cols[2].metric("College Contribution", money(row["College Contribution"]))
    cols[3].metric("Contribution %", f"{row['College Contribution %']:.1%}")
    statement=pd.DataFrame({"Line Item":["Gross Tuition Revenue","Internal Teaching Allocation","Scholarships","Net Revenue","Operating Expenses","College Contribution"],"USD":[row["Gross Tuition Revenue"],row["Internal Teaching Allocation"],-row["Scholarships"],row["Net Revenue"],-row["Operating Expenses"],row["College Contribution"]]})
    left,right=st.columns([0.8,1.2])
    with left: st.dataframe(statement, hide_index=True, width="stretch", column_config={"USD":st.column_config.NumberColumn(format="$%.0f")})
    with right:
        fig=go.Figure(go.Waterfall(x=statement["Line Item"],y=statement["USD"],measure=["absolute","relative","relative","total","relative","total"]))
        fig.update_layout(title=f"{selected}: Statement of Financial Performance",yaxis_tickprefix="$",yaxis_tickformat="~s",height=430)
        st.plotly_chart(fig,width="stretch")

elif page == "Statements":
    section("Statements of Financial Performance")
    cols=["College","FY27 Students","Gross Tuition Revenue","Internal Teaching Allocation","Scholarships","Net Revenue","Operating Expenses","College Contribution","College Contribution %"]
    st.dataframe(results[cols],hide_index=True,width="stretch",column_config={"Gross Tuition Revenue":st.column_config.NumberColumn(format="$%.0f"),"Internal Teaching Allocation":st.column_config.NumberColumn(format="$%.0f"),"Scholarships":st.column_config.NumberColumn(format="$%.0f"),"Net Revenue":st.column_config.NumberColumn(format="$%.0f"),"Operating Expenses":st.column_config.NumberColumn(format="$%.0f"),"College Contribution":st.column_config.NumberColumn(format="$%.0f"),"College Contribution %":st.column_config.NumberColumn(format="%.1f%%")})

else:
    section("Model controls")
    checks=[
        {"Control":"Internal teaching allocations net to zero","Difference":float(results["Internal Teaching Allocation"].sum())},
        {"Control":"College Contribution recalculation","Difference":float((results["Net Revenue"]-results["Operating Expenses"]).sum()-totals["college_contribution"])},
        {"Control":"University result bridge","Difference":float(totals["college_contribution"]+totals["other"]-totals["shared"]-totals["result"])},
    ]
    cdf=pd.DataFrame(checks); cdf["Status"]=cdf["Difference"].abs().lt(1).map({True:"OK",False:"CHECK"})
    st.dataframe(cdf,hide_index=True,width="stretch",column_config={"Difference":st.column_config.NumberColumn(format="%.2f")})

st.markdown("---")
st.caption(f"AUIB Financial Performance Portal · Version {APP_VERSION} · Built {datetime.now().strftime('%d %b %Y')}")
