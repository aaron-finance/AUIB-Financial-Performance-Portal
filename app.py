
import copy
import json
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AUIB Financial Performance Portal v2.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

CRIMSON = "#AB0A3D"
GREY = "#8C9091"
NAVY = "#17365D"
LIGHT_GREY = "#F1F3F5"
BG = "#FAFAFB"
APP_VERSION = "2.0.1"


# ============================================================
# PUBLISHED BASELINE SNAPSHOT
# This is intentionally embedded so the portal is standalone.
# Users do not need access to Excel, OneDrive, or GitHub.
# ============================================================

BASELINE = {
    "metadata": {
        "portal_name": "AUIB Financial Performance Portal",
        "model_name": "College Financial Performance Model",
        "source_period": "FY26 / FY27 Scenario",
        "currency": "USD",
        "note": (
            "Standalone published management snapshot. Portal users do not "
            "require access to Excel, OneDrive, or GitHub."
        ),
        "disclaimer": (
            "Management-planning model. Validate against the approved Finance "
            "workbook before formal decisions."
        ),
    },
    "global": {
        "shared_services_fy26": 11_282_198.17,
        "shared_services_growth": 0.05,
        "expense_variable_pct": 0.65,
        "expense_inflation": 0.00,
        "ela_revenue_fy26": 3_082_685.61,
        "ela_expense_fy26": 3_239_800.54,
        "ela_revenue_growth": 0.125,
        "ceid_revenue_fy26": 500_000.00,
        "ceid_expense_fy26": 1_709_726.89,
        "ceid_revenue_growth": 5.0,
    },
    "programmes": [
        {
            "college": "Arts & Sciences",
            "programme": "Undergraduate",
            "fy26_enrolled": 212,
            "fy27_new_intake": 56,
            "fy27_projected": 193,
            "fy26_tuition": 4469.70,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.00,
        },
        {
            "college": "Business",
            "programme": "Undergraduate",
            "fy26_enrolled": 523,
            "fy27_new_intake": 208,
            "fy27_projected": 617,
            "fy26_tuition": 4318.18,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.75,
        },
        {
            "college": "Business",
            "programme": "MBA",
            "fy26_enrolled": 44,
            "fy27_new_intake": 24,
            "fy27_projected": 48,
            "fy26_tuition": 15909.09,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.00,
        },
        {
            "college": "Dentistry",
            "programme": "Undergraduate",
            "fy26_enrolled": 729,
            "fy27_new_intake": 154,
            "fy27_projected": 742,
            "fy26_tuition": 10606.06,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.75,
        },
        {
            "college": "Education & Human Development",
            "programme": "Undergraduate",
            "fy26_enrolled": 23,
            "fy27_new_intake": 2,
            "fy27_projected": 25,
            "fy26_tuition": 4318.18,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.75,
        },
        {
            "college": "Education & Human Development",
            "programme": "M-HEAL",
            "fy26_enrolled": 11,
            "fy27_new_intake": 11,
            "fy27_projected": 22,
            "fy26_tuition": 15909.09,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.00,
        },
        {
            "college": "Engineering",
            "programme": "Undergraduate",
            "fy26_enrolled": 402,
            "fy27_new_intake": 270,
            "fy27_projected": 672,
            "fy26_tuition": 6818.18,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.75,
        },
        {
            "college": "Health Care Technologies",
            "programme": "Undergraduate",
            "fy26_enrolled": 275,
            "fy27_new_intake": 59,
            "fy27_projected": 209,
            "fy26_tuition": 5530.30,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.75,
        },
        {
            "college": "International Studies",
            "programme": "Undergraduate",
            "fy26_enrolled": 95,
            "fy27_new_intake": 44,
            "fy27_projected": 119,
            "fy26_tuition": 4318.18,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.75,
        },
        {
            "college": "Law",
            "programme": "Undergraduate",
            "fy26_enrolled": 98,
            "fy27_new_intake": 34,
            "fy27_projected": 110,
            "fy26_tuition": 4318.18,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.75,
        },
        {
            "college": "Pharmacy",
            "programme": "Undergraduate",
            "fy26_enrolled": 760,
            "fy27_new_intake": 134,
            "fy27_projected": 775,
            "fy26_tuition": 8333.33,
            "tuition_increase": 0.15,
            "teaching_allocation": 0.75,
        },
    ],
    "colleges": {
        "Arts & Sciences": {
            "fy27_baseline_tuition": 862_151.52,
            "scholarship_rate": 0.04311313,
            "fy26_direct_expense": 3_894_549.27,
        },
        "Business": {
            "fy27_baseline_tuition": 3_556_000.00,
            "scholarship_rate": 0.18146070,
            "fy26_direct_expense": 1_436_505.66,
        },
        "Dentistry": {
            "fy27_baseline_tuition": 7_138_393.94,
            "scholarship_rate": 0.25468670,
            "fy26_direct_expense": 1_987_782.18,
        },
        "Education & Human Development": {
            "fy27_baseline_tuition": 478_818.18,
            "scholarship_rate": 0.33817770,
            "fy26_direct_expense": 623_427.69,
        },
        "Engineering": {
            "fy27_baseline_tuition": 4_829_454.55,
            "scholarship_rate": 0.28049270,
            "fy26_direct_expense": 293_735.42,
        },
        "Health Care Technologies": {
            "fy27_baseline_tuition": 1_156_518.94,
            "scholarship_rate": 0.17802310,
            "fy26_direct_expense": 1_150_131.08,
        },
        "International Studies": {
            "fy27_baseline_tuition": 532_500.00,
            "scholarship_rate": 0.46408691,
            "fy26_direct_expense": 505_442.13,
        },
        "Law": {
            "fy27_baseline_tuition": 483_659.09,
            "scholarship_rate": 0.36743141,
            "fy26_direct_expense": 646_281.31,
        },
        "Pharmacy": {
            "fy27_baseline_tuition": 6_155_469.70,
            "scholarship_rate": 0.22465874,
            "fy26_direct_expense": 1_381_408.25,
        },
    },
}


# ============================================================
# STYLING
# ============================================================

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
    }}
    [data-testid="stSidebar"] {{
        background-color: {LIGHT_GREY};
    }}
    h1, h2, h3 {{
        color: {NAVY};
    }}
    div[data-testid="stMetric"] {{
        background: white;
        border: 1px solid #E3E6EA;
        padding: 14px 16px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,.05);
    }}
    .portal-banner {{
        background: linear-gradient(90deg, {NAVY}, #284F7C);
        color: white;
        padding: 18px 22px;
        border-radius: 12px;
        margin-bottom: 14px;
    }}
    .portal-banner h1 {{
        color: white;
        margin: 0;
        font-size: 1.65rem;
    }}
    .portal-banner p {{
        margin: 4px 0 0 0;
        opacity: .9;
    }}
    .section-title {{
        color: {CRIMSON};
        font-weight: 700;
        font-size: 1.05rem;
        border-bottom: 2px solid {CRIMSON};
        padding-bottom: 5px;
        margin: 10px 0 12px 0;
    }}

    :root,
    html,
    body,
    [data-testid="stAppViewContainer"],
    [data-testid="stSidebar"] {{
        --primary-color: {NAVY} !important;
    }}
    [data-testid="stSlider"] [role="slider"] {{
        background-color: {NAVY} !important;
        border-color: {NAVY} !important;
        box-shadow: 0 0 0 1px {NAVY} !important;
    }}
    [data-testid="stSlider"] div[data-baseweb="slider"] > div > div {{
        background-color: #C7D0DB !important;
    }}
    [data-testid="stSlider"] div[data-baseweb="slider"] > div > div > div {{
        background-color: {NAVY} !important;
    }}
    [data-testid="stSlider"] svg {{
        color: {NAVY} !important;
        fill: {NAVY} !important;
    }}
    .model-note {{
        background: #FFF8E8;
        border-left: 4px solid #D99A00;
        padding: 10px 12px;
        border-radius: 5px;
        font-size: .9rem;
        margin-bottom: 12px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# UTILITIES
# ============================================================

def money(value: float, decimals: int = 1) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}${value/1_000_000:,.{decimals}f}M"
    if value >= 1_000:
        return f"{sign}${value/1_000:,.0f}K"
    return f"{sign}${value:,.0f}"


def percent(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}%}"


def section(title: str) -> None:
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )


def fresh_scenario() -> dict:
    return {
        "name": "Workbook baseline",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "global": copy.deepcopy(BASELINE["global"]),
        "programmes": copy.deepcopy(BASELINE["programmes"]),
        "college_tuition_pct": {
            college: round(
                100 * max(
                    programme["tuition_increase"]
                    for programme in BASELINE["programmes"]
                    if programme["college"] == college
                ),
                1,
            )
            for college in BASELINE["colleges"]
        },
        "scholarships": {
            college: values["scholarship_rate"]
            for college, values in BASELINE["colleges"].items()
        },
    }


# ============================================================
# CALCULATION ENGINE
# ============================================================

def calculate_scenario(scenario: dict):
    programmes = pd.DataFrame(scenario["programmes"]).copy()
    programmes["tuition_increase"] = programmes["college"].map(
        {
            college: value / 100
            for college, value in scenario["college_tuition_pct"].items()
        }
    )
    programmes["fy27_tuition"] = (
        programmes["fy26_tuition"] * (1 + programmes["tuition_increase"])
    )
    programmes["new_intake_revenue"] = (
        programmes["fy27_new_intake"] * programmes["fy27_tuition"]
    )

    preliminary = []
    internal_to_as = 0.0

    for college, college_base in BASELINE["colleges"].items():
        college_programmes = programmes[
            programmes["college"] == college
        ].copy()

        baseline_new_revenue = (
            college_programmes["fy27_new_intake"]
            * college_programmes["fy26_tuition"]
            * 1.15
        ).sum()

        continuing_revenue = max(
            college_base["fy27_baseline_tuition"]
            - baseline_new_revenue,
            0.0,
        )

        gross_tuition = (
            continuing_revenue
            + college_programmes["new_intake_revenue"].sum()
        )

        transfer = 0.0
        if college != "Arts & Sciences":
            transfer = (
                college_programmes["fy27_new_intake"]
                * college_programmes["fy27_tuition"]
                * college_programmes["teaching_allocation"]
            ).sum()
            internal_to_as += transfer

        preliminary.append(
            (
                college,
                college_programmes,
                college_base,
                gross_tuition,
                transfer,
            )
        )

    rows = []

    for college, college_programmes, college_base, gross_tuition, transfer in preliminary:
        internal_allocation = (
            internal_to_as if college == "Arts & Sciences" else -transfer
        )

        scholarship_rate = float(
            scenario["scholarships"][college]
        )
        scholarships = gross_tuition * scholarship_rate
        net_revenue = (
            gross_tuition + internal_allocation - scholarships
        )

        fy26_students = int(
            college_programmes["fy26_enrolled"].sum()
        )
        fy27_students = int(
            college_programmes["fy27_projected"].sum()
        )

        student_growth = (
            fy27_students / fy26_students - 1
            if fy26_students
            else 0.0
        )

        global_assumptions = scenario["global"]

        direct_expense = (
            college_base["fy26_direct_expense"]
            * (
                1
                + global_assumptions["expense_inflation"]
                + global_assumptions["expense_variable_pct"]
                * student_growth
            )
        )

        contribution = net_revenue - direct_expense

        rows.append(
            {
                "College": college,
                "FY26 Students": fy26_students,
                "FY27 Students": fy27_students,
                "Student Growth %": student_growth,
                "New Intake": int(
                    college_programmes["fy27_new_intake"].sum()
                ),
                "Gross Tuition Revenue": gross_tuition,
                "Internal Teaching Allocation": internal_allocation,
                "Scholarships": scholarships,
                "Scholarship %": scholarship_rate,
                "Net Revenue": net_revenue,
                "Net Revenue / Student": (
                    net_revenue / fy27_students
                    if fy27_students
                    else 0.0
                ),
                "Operating Expenses": direct_expense,
                "Operating Expenses / Student": (
                    direct_expense / fy27_students
                    if fy27_students
                    else 0.0
                ),
                "Operating Expenses %": (
                    direct_expense / net_revenue
                    if net_revenue
                    else 0.0
                ),
                "College Contribution": contribution,
                "College Contribution / Student": (
                    contribution / fy27_students
                    if fy27_students
                    else 0.0
                ),
                "College Contribution %": (
                    contribution / net_revenue
                    if net_revenue
                    else 0.0
                ),
            }
        )

    college_results = pd.DataFrame(rows)

    global_assumptions = scenario["global"]

    ela_revenue = (
        global_assumptions["ela_revenue_fy26"]
        * (1 + global_assumptions["ela_revenue_growth"])
    )
    ela_expense = (
        global_assumptions["ela_expense_fy26"]
        * (1 + global_assumptions["expense_inflation"])
    )

    ceid_revenue = (
        global_assumptions["ceid_revenue_fy26"]
        * (1 + global_assumptions["ceid_revenue_growth"])
    )
    ceid_expense = (
        global_assumptions["ceid_expense_fy26"]
        * (1 + global_assumptions["expense_inflation"])
    )

    shared_services = (
        global_assumptions["shared_services_fy26"]
        * (1 + global_assumptions["shared_services_growth"])
    )

    college_contribution = float(
        college_results["College Contribution"].sum()
    )

    ela_result = ela_revenue - ela_expense
    ceid_result = ceid_revenue - ceid_expense
    other_profit_centres = ela_result + ceid_result

    university_result = (
        college_contribution
        + other_profit_centres
        - shared_services
    )

    totals = {
        "projected_students": int(
            college_results["FY27 Students"].sum()
        ),
        "net_college_revenue": float(
            college_results["Net Revenue"].sum()
        ),
        "college_contribution": college_contribution,
        "shared_services": shared_services,
        "other_profit_centres": other_profit_centres,
        "ela_result": ela_result,
        "ceid_result": ceid_result,
        "university_result": university_result,
    }

    return college_results, programmes, totals


def validate_results(college_results: pd.DataFrame, totals: dict):
    checks = []

    internal_difference = float(
        college_results["Internal Teaching Allocation"].sum()
    )
    checks.append(
        {
            "Control": "Internal teaching allocations net to zero",
            "Difference": internal_difference,
            "Status": (
                "OK" if abs(internal_difference) < 1 else "CHECK"
            ),
        }
    )

    recalculated_contribution = float(
        (
            college_results["Net Revenue"]
            - college_results["Operating Expenses"]
        ).sum()
    )
    contribution_difference = (
        recalculated_contribution
        - totals["college_contribution"]
    )
    checks.append(
        {
            "Control": "College Contribution recalculation",
            "Difference": contribution_difference,
            "Status": (
                "OK"
                if abs(contribution_difference) < 1
                else "CHECK"
            ),
        }
    )

    recalculated_university = (
        totals["college_contribution"]
        + totals["other_profit_centres"]
        - totals["shared_services"]
    )
    university_difference = (
        recalculated_university
        - totals["university_result"]
    )
    checks.append(
        {
            "Control": "University result bridge",
            "Difference": university_difference,
            "Status": (
                "OK"
                if abs(university_difference) < 1
                else "CHECK"
            ),
        }
    )

    return pd.DataFrame(checks)


# ============================================================
# SESSION STATE
# ============================================================

if "scenario" not in st.session_state:
    st.session_state.scenario = fresh_scenario()

scenario = st.session_state.scenario


# ============================================================
# WIDGET-STATE HELPERS
# ============================================================

def clear_scenario_widget_state() -> None:
    """Clear keyed widgets so a preset can safely replace their values."""
    prefixes = (
        "college_tuition_",
        "intake_",
        "allocation_",
        "scholarship_",
    )
    for key in list(st.session_state.keys()):
        if any(str(key).startswith(prefix) for prefix in prefixes):
            del st.session_state[key]


def reset_to_baseline() -> None:
    clear_scenario_widget_state()
    st.session_state.scenario = fresh_scenario()


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.markdown("## Scenario controls")
st.sidebar.caption(
    "All changes recalculate immediately. "
    "Portal users do not need Excel."
)

st.sidebar.button(
    "Reset to workbook baseline",
    use_container_width=True,
    on_click=reset_to_baseline,
)

scenario["name"] = st.sidebar.text_input(
    "Scenario name",
    value=scenario.get("name", "Scenario"),
)

with st.sidebar.expander(
    "University assumptions",
    expanded=True,
):
    scenario["global"]["shared_services_growth"] = (
        st.slider(
            "Shared Services growth",
            min_value=-0.10,
            max_value=0.25,
            value=float(
                scenario["global"][
                    "shared_services_growth"
                ]
            ),
            step=0.005,
            format="%.1f%%",
        )
    )

    scenario["global"]["expense_variable_pct"] = (
        st.slider(
            "Variable portion of College expenses",
            min_value=0.0,
            max_value=1.0,
            value=float(
                scenario["global"][
                    "expense_variable_pct"
                ]
            ),
            step=0.05,
            format="%.0f%%",
        )
    )

    scenario["global"]["expense_inflation"] = (
        st.slider(
            "General expense inflation",
            min_value=-0.05,
            max_value=0.20,
            value=float(
                scenario["global"][
                    "expense_inflation"
                ]
            ),
            step=0.005,
            format="%.1f%%",
        )
    )

    scenario["global"]["ela_revenue_growth"] = (
        st.slider(
            "ELA revenue growth",
            min_value=-0.25,
            max_value=1.00,
            value=float(
                scenario["global"][
                    "ela_revenue_growth"
                ]
            ),
            step=0.025,
            format="%.1f%%",
        )
    )

    scenario["global"]["ceid_revenue_growth"] = (
        st.slider(
            "CEID revenue growth",
            min_value=-0.50,
            max_value=6.00,
            value=float(
                scenario["global"][
                    "ceid_revenue_growth"
                ]
            ),
            step=0.25,
            format="%.0f%%",
        )
    )

st.sidebar.markdown("### Scenario presets")

preset_cols = st.sidebar.columns(2)

def apply_preset(name: str) -> None:
    """Apply a complete preset and reset Streamlit widget state safely."""
    preset = fresh_scenario()
    preset["name"] = name

    if name == "Conservative":
        for college in preset["college_tuition_pct"]:
            preset["college_tuition_pct"][college] = 5.0
        for programme in preset["programmes"]:
            programme["fy27_new_intake"] = max(
                0,
                round(programme["fy27_new_intake"] * 0.90),
            )

    elif name == "Growth":
        for college in preset["college_tuition_pct"]:
            preset["college_tuition_pct"][college] = 15.0
        for programme in preset["programmes"]:
            programme["fy27_new_intake"] = min(
                3000,
                round(programme["fy27_new_intake"] * 1.25),
            )

    elif name == "Extreme":
        for college in preset["college_tuition_pct"]:
            preset["college_tuition_pct"][college] = 50.0
        for programme in preset["programmes"]:
            programme["fy27_new_intake"] = min(
                3000,
                round(programme["fy27_new_intake"] * 1.75),
            )

    clear_scenario_widget_state()
    st.session_state.scenario = preset


preset_cols[0].button(
    "Baseline",
    use_container_width=True,
    on_click=apply_preset,
    args=("Workbook baseline",),
)

preset_cols[1].button(
    "Conservative",
    use_container_width=True,
    on_click=apply_preset,
    args=("Conservative",),
)

preset_cols_2 = st.sidebar.columns(2)

preset_cols_2[0].button(
    "Growth",
    use_container_width=True,
    on_click=apply_preset,
    args=("Growth",),
)

preset_cols_2[1].button(
    "Extreme",
    use_container_width=True,
    on_click=apply_preset,
    args=("Extreme",),
)

st.sidebar.markdown("### College tuition assumptions")

for college in scenario["college_tuition_pct"]:
    scenario["college_tuition_pct"][college] = st.sidebar.slider(
        college,
        min_value=-20.0,
        max_value=100.0,
        value=float(scenario["college_tuition_pct"][college]),
        step=1.0,
        format="%.0f%%",
        key=f"college_tuition_{college}",
        help=(
            "Stress-test from a 20% reduction to a 100% increase. "
            "The assumption applies to every programme in the College."
        ),
    )

st.sidebar.markdown("### Programme intake assumptions")

for index, programme in enumerate(
    scenario["programmes"]
):
    label = (
        f'{programme["college"]} — '
        f'{programme["programme"]}'
    )

    with st.sidebar.expander(label):
        programme["fy27_new_intake"] = (
            st.number_input(
                "New intake",
                min_value=0,
                max_value=3000,
                value=int(
                    programme["fy27_new_intake"]
                ),
                step=1,
                key=f"intake_{index}",
            )
        )

        if (
            programme["programme"]
            == "Undergraduate"
            and programme["college"]
            != "Arts & Sciences"
        ):
            programme["teaching_allocation"] = (
                st.slider(
                    "Arts & Sciences teaching allocation",
                    min_value=0.0,
                    max_value=1.0,
                    value=float(
                        programme[
                            "teaching_allocation"
                        ]
                    ),
                    step=0.05,
                    format="%.0f%%",
                    key=f"allocation_{index}",
                )
            )

st.sidebar.markdown("### Scholarships")

for college in scenario["scholarships"]:
    scenario["scholarships"][college] = (
        st.sidebar.slider(
            college,
            min_value=0.0,
            max_value=0.70,
            value=float(
                scenario["scholarships"][college]
            ),
            step=0.005,
            format="%.1f%%",
            key=f"scholarship_{college}",
        )
    )


# ============================================================
# CALCULATE
# ============================================================

college_results, programmes, totals = (
    calculate_scenario(scenario)
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="portal-banner">
        <h1>AUIB Financial Performance Portal</h1>
        <p>
            Monthly Performance Pack · College Financial
            Performance Model · Tuition and Scenario Planning · Version 2.0.1
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="model-note">
        <b>Published standalone model:</b>
        Portal users do not require access to Excel or OneDrive.
        Scenario results should be validated against the approved
        Finance baseline before formal use.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MAIN NAVIGATION
# ============================================================

tabs = st.tabs(
    [
        "Executive Dashboard",
        "Tuition Planning",
        "College Performance",
        "Statements of Financial Performance",
        "Controls",
        "About",
    ]
)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

with tabs[0]:
    section("University at a glance")

    metrics = st.columns(5)

    metrics[0].metric(
        "Projected Students",
        f'{totals["projected_students"]:,}',
        f'{totals["projected_students"] - int(college_results["FY26 Students"].sum()):+,.0f}',
    )

    metrics[1].metric(
        "Net College Revenue",
        money(totals["net_college_revenue"]),
    )

    metrics[2].metric(
        "College Contribution",
        money(totals["college_contribution"]),
    )

    metrics[3].metric(
        "Shared Services",
        money(totals["shared_services"]),
    )

    metrics[4].metric(
        "University Result",
        money(totals["university_result"]),
    )

    chart_left, chart_right = st.columns(
        [1.15, 1]
    )

    with chart_left:
        bubble_data = college_results[
            college_results["College"]
            != "Arts & Sciences"
        ].copy()

        bubble = px.scatter(
            bubble_data,
            x="Net Revenue / Student",
            y="College Contribution %",
            size="FY27 Students",
            text="College",
            hover_name="College",
            hover_data={
                "Net Revenue / Student": ":$,.0f",
                "College Contribution %": ":.1%",
                "FY27 Students": ":,.0f",
                "College Contribution": ":$,.0f",
            },
            title=(
                "College positioning: value, contribution and scale"
            ),
        )

        bubble.update_traces(
            textposition="top center"
        )
        bubble.update_yaxes(
            tickformat=".0%",
            title="College Contribution %",
        )
        bubble.update_xaxes(
            tickprefix="$",
            tickformat=",",
            title="Net Revenue per Student",
        )
        bubble.add_hline(
            y=0,
            line_dash="dot",
            line_color=GREY,
        )
        bubble.update_layout(
            height=480,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            bubble,
            use_container_width=True,
        )

    with chart_right:
        bridge = go.Figure(
            go.Waterfall(
                orientation="v",
                measure=[
                    "absolute",
                    "relative",
                    "relative",
                    "total",
                ],
                x=[
                    "College Contribution",
                    "ELA & CEID",
                    "Shared Services",
                    "University Result",
                ],
                y=[
                    totals["college_contribution"],
                    totals["other_profit_centres"],
                    -totals["shared_services"],
                    totals["university_result"],
                ],
                connector={
                    "line": {
                        "color": "#B8BDC4"
                    }
                },
            )
        )

        bridge.update_layout(
            title="Contribution to University result",
            yaxis_tickprefix="$",
            yaxis_tickformat="~s",
            height=480,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20,
            ),
        )

        st.plotly_chart(
            bridge,
            use_container_width=True,
        )

    lower_left, lower_right = st.columns(2)

    with lower_left:
        contribution_data = college_results.sort_values(
            "College Contribution",
            ascending=True,
        )

        contribution_chart = px.bar(
            contribution_data,
            x="College Contribution",
            y="College",
            orientation="h",
            color="College Contribution %",
            color_continuous_scale="RdYlGn",
            title=(
                "College Contribution before Shared Services"
            ),
        )

        contribution_chart.update_xaxes(
            tickprefix="$",
            tickformat="~s",
        )
        contribution_chart.update_layout(
            height=460,
            coloraxis_colorbar_title=(
                "Contribution %"
            ),
        )

        st.plotly_chart(
            contribution_chart,
            use_container_width=True,
        )

    with lower_right:
        scholarship_data = (
            college_results[
                ["College", "Scholarship %"]
            ]
            .sort_values(
                "Scholarship %",
                ascending=False,
            )
        )

        scholarship_chart = px.bar(
            scholarship_data,
            x="Scholarship %",
            y="College",
            orientation="h",
            color="Scholarship %",
            color_continuous_scale="YlOrRd",
            title=(
                "Scholarship and tuition-discount rate"
            ),
        )

        scholarship_chart.update_xaxes(
            tickformat=".0%",
        )
        scholarship_chart.update_layout(
            height=460,
            coloraxis_showscale=False,
        )

        st.plotly_chart(
            scholarship_chart,
            use_container_width=True,
        )


# ============================================================
# TUITION PLANNING
# ============================================================

with tabs[1]:
    section("Tuition and enrolment plan")

    tuition_table = programmes[
        [
            "college",
            "programme",
            "fy26_enrolled",
            "fy27_new_intake",
            "fy27_projected",
            "fy26_tuition",
            "tuition_increase",
            "fy27_tuition",
            "new_intake_revenue",
        ]
    ].rename(
        columns={
            "college": "College",
            "programme": "Programme",
            "fy26_enrolled": "FY26 Enrolled",
            "fy27_new_intake": "FY27 New Intake",
            "fy27_projected": "FY27 Projected",
            "fy26_tuition": "FY26 Tuition",
            "tuition_increase": "Increase %",
            "fy27_tuition": "FY27 Tuition",
            "new_intake_revenue": (
                "New Intake Revenue"
            ),
        }
    )

    st.dataframe(
        tuition_table.style.format(
            {
                "FY26 Tuition": "${:,.0f}",
                "Increase %": "{:.1%}",
                "FY27 Tuition": "${:,.0f}",
                "New Intake Revenue": "${:,.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    revenue_source = college_results[
        [
            "College",
            "Gross Tuition Revenue",
            "Scholarships",
            "Net Revenue",
        ]
    ].copy()

    revenue_source["Scholarships"] = (
        -revenue_source["Scholarships"]
    )

    revenue_long = revenue_source.melt(
        id_vars="College",
        var_name="Measure",
        value_name="USD",
    )

    revenue_chart = px.bar(
        revenue_long,
        x="College",
        y="USD",
        color="Measure",
        barmode="group",
        title=(
            "Gross tuition, scholarships and net revenue"
        ),
    )

    revenue_chart.update_yaxes(
        tickprefix="$",
        tickformat="~s",
    )
    revenue_chart.update_layout(
        height=500,
        xaxis_tickangle=-35,
    )

    st.plotly_chart(
        revenue_chart,
        use_container_width=True,
    )


# ============================================================
# COLLEGE PERFORMANCE
# ============================================================

with tabs[2]:
    section("College Performance Scorecard")

    college_name = st.selectbox(
        "Select College",
        college_results["College"].tolist(),
        index=(
            college_results["College"]
            .tolist()
            .index("Engineering")
            if "Engineering"
            in college_results["College"].tolist()
            else 0
        ),
    )

    college_row = (
        college_results[
            college_results["College"]
            == college_name
        ]
        .iloc[0]
    )

    college_metrics = st.columns(4)

    college_metrics[0].metric(
        "Students",
        f'{college_row["FY27 Students"]:,.0f}',
        f'{college_row["FY27 Students"] - college_row["FY26 Students"]:+,.0f}',
    )

    college_metrics[1].metric(
        "Net Revenue",
        money(college_row["Net Revenue"]),
    )

    college_metrics[2].metric(
        "College Contribution",
        money(
            college_row[
                "College Contribution"
            ]
        ),
    )

    college_metrics[3].metric(
        "College Contribution %",
        percent(
            college_row[
                "College Contribution %"
            ]
        ),
    )

    college_metrics_2 = st.columns(4)

    college_metrics_2[0].metric(
        "Net Revenue / Student",
        money(
            college_row[
                "Net Revenue / Student"
            ]
        ),
    )

    college_metrics_2[1].metric(
        "Scholarship %",
        percent(
            college_row["Scholarship %"]
        ),
    )

    college_metrics_2[2].metric(
        "Operating Expenses / Student",
        money(
            college_row[
                "Operating Expenses / Student"
            ]
        ),
    )

    college_metrics_2[3].metric(
        "Operating Expenses %",
        percent(
            college_row[
                "Operating Expenses %"
            ]
        ),
    )

    statement_left, statement_right = st.columns(
        [0.9, 1.25]
    )

    statement_data = pd.DataFrame(
        {
            "Line Item": [
                "Gross Tuition Revenue",
                "Internal Teaching Allocation",
                "Scholarships",
                "Net Revenue",
                "Operating Expenses",
                "College Contribution",
            ],
            "USD": [
                college_row[
                    "Gross Tuition Revenue"
                ],
                college_row[
                    "Internal Teaching Allocation"
                ],
                -college_row["Scholarships"],
                college_row["Net Revenue"],
                -college_row[
                    "Operating Expenses"
                ],
                college_row[
                    "College Contribution"
                ],
            ],
        }
    )

    with statement_left:
        st.dataframe(
            statement_data.style.format(
                {"USD": "${:,.0f}"}
            ),
            hide_index=True,
            use_container_width=True,
        )

        st.markdown(
            "#### Dean / Finance commentary"
        )

        st.text_area(
            "Commentary",
            placeholder=(
                "Key performance observations, risks, "
                "opportunities and actions."
            ),
            height=160,
            label_visibility="collapsed",
        )

    with statement_right:
        statement_chart = go.Figure(
            go.Waterfall(
                x=statement_data["Line Item"],
                y=statement_data["USD"],
                measure=[
                    "absolute",
                    "relative",
                    "relative",
                    "total",
                    "relative",
                    "total",
                ],
            )
        )

        statement_chart.update_layout(
            title=(
                f"{college_name}: "
                "Statement of Financial Performance"
            ),
            yaxis_tickprefix="$",
            yaxis_tickformat="~s",
            height=430,
            xaxis_tickangle=-25,
        )

        st.plotly_chart(
            statement_chart,
            use_container_width=True,
        )


# ============================================================
# STATEMENTS OF FINANCIAL PERFORMANCE
# ============================================================

with tabs[3]:
    section("Statements of Financial Performance")

    statement_columns = [
        "College",
        "FY27 Students",
        "Gross Tuition Revenue",
        "Internal Teaching Allocation",
        "Scholarships",
        "Net Revenue",
        "Operating Expenses",
        "College Contribution",
        "College Contribution %",
    ]

    statement_formats = {
        "Gross Tuition Revenue": "${:,.0f}",
        "Internal Teaching Allocation": (
            "${:,.0f}"
        ),
        "Scholarships": "${:,.0f}",
        "Net Revenue": "${:,.0f}",
        "Operating Expenses": "${:,.0f}",
        "College Contribution": "${:,.0f}",
        "College Contribution %": "{:.1%}",
    }

    st.dataframe(
        college_results[
            statement_columns
        ].style.format(statement_formats),
        hide_index=True,
        use_container_width=True,
    )

    university_bridge = pd.DataFrame(
        [
            {
                "Line Item": (
                    "College Contribution before "
                    "Shared Services"
                ),
                "USD": totals[
                    "college_contribution"
                ],
            },
            {
                "Line Item": (
                    "Other Profit Centres "
                    "(ELA and CEID)"
                ),
                "USD": totals[
                    "other_profit_centres"
                ],
            },
            {
                "Line Item": "Shared Services",
                "USD": -totals[
                    "shared_services"
                ],
            },
            {
                "Line Item": (
                    "University Operating "
                    "Surplus / (Deficit)"
                ),
                "USD": totals[
                    "university_result"
                ],
            },
        ]
    )

    st.markdown("#### University bridge")

    st.dataframe(
        university_bridge.style.format(
            {"USD": "${:,.0f}"}
        ),
        hide_index=True,
        use_container_width=True,
    )


# ============================================================
# CONTROLS
# ============================================================

with tabs[4]:
    section("Model controls")

    controls = validate_results(
        college_results,
        totals,
    )

    st.dataframe(
        controls.style.format(
            {"Difference": "{:,.2f}"}
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.caption(
        "All controls should read OK before a "
        "scenario is used for formal decision-making."
    )


# ============================================================
# ABOUT
# ============================================================

with tabs[5]:
    section("About the model")

    st.markdown(
        """
        **Purpose:** AUIB's browser-based College Financial
        Performance Model and tuition-planning portal.

        **Standalone design:** Users of this portal do not need
        access to Excel, OneDrive, GitHub, Python, or any installed
        software. They only require the deployed browser link.

        **Current scope**
        - Tuition and new-intake scenarios
        - Scholarship assumptions
        - Arts & Sciences internal teaching allocations
        - College Statements of Financial Performance
        - College Contribution before Shared Services
        - ELA and CEID profit-centre assumptions
        - Shared Services and University operating result
        - Executive charts, scorecards, controls and CSV export

        **Important limitation**
        The detailed expense engine still uses high-level management
        assumptions. It should be progressively reconciled to the
        detailed GL-driven expense model and operational cost drivers.
        """
    )

    st.warning(
        BASELINE["metadata"]["disclaimer"]
    )


# ============================================================
# EXPORTS
# ============================================================

st.sidebar.markdown("---")
st.sidebar.markdown("### Export")

scenario_json = json.dumps(
    scenario,
    indent=2,
).encode("utf-8")

st.sidebar.download_button(
    "Download scenario JSON",
    data=scenario_json,
    file_name="AUIB_scenario.json",
    mime="application/json",
    use_container_width=True,
)

scenario_csv = (
    college_results
    .to_csv(index=False)
    .encode("utf-8")
)

st.sidebar.download_button(
    "Download results CSV",
    data=scenario_csv,
    file_name="AUIB_scenario_results.csv",
    mime="text/csv",
    use_container_width=True,
)


st.markdown("---")
st.caption(
    f"AUIB Financial Performance Portal · Version {APP_VERSION} · "
    "Standalone management-planning model"
)
