import streamlit as st
from google import genai
import json
import re
import uuid
from datetime import datetime, timezone
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Car Service Estimate Explainer",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
:root{
  --page-bg:#f7f9fc;
  --accent1:rgba(219,234,254,.82);
  --accent2:rgba(220,252,231,.62);
  --surface:#ffffff;
  --surface-soft:#f8fafc;
  --text:#0f172a;
  --muted:#475569;
  --soft:#64748b;
  --border:#d7dee8;
  --input-bg:#ffffff;
  --input-text:#0f172a;
  --placeholder:#94a3b8;
  --primary:#2563eb;
  --primary2:#3b82f6;
  --primary-soft:#eff6ff;
  --success-bg:#ecfdf5;
  --success-border:#bbf7d0;
  --success-text:#166534;
  --warning-bg:#fff7ed;
  --warning-border:#fed7aa;
  --warning-text:#9a3412;
  --shadow:0 12px 36px rgba(15,23,42,.07);
}

@media (prefers-color-scheme: dark){
  :root{
    --page-bg:#0b1120;
    --accent1:rgba(30,64,175,.22);
    --accent2:rgba(5,150,105,.15);
    --surface:#111827;
    --surface-soft:#172033;
    --text:#f8fafc;
    --muted:#cbd5e1;
    --soft:#94a3b8;
    --border:#334155;
    --input-bg:#0f172a;
    --input-text:#f8fafc;
    --placeholder:#94a3b8;
    --primary:#60a5fa;
    --primary2:#3b82f6;
    --primary-soft:rgba(37,99,235,.18);
    --success-bg:rgba(6,78,59,.38);
    --success-border:rgba(52,211,153,.30);
    --success-text:#a7f3d0;
    --warning-bg:rgba(124,45,18,.34);
    --warning-border:rgba(251,146,60,.30);
    --warning-text:#fed7aa;
    --shadow:0 14px 40px rgba(0,0,0,.24);
  }
}

html[data-theme="dark"]{
  --page-bg:#0b1120;
  --accent1:rgba(30,64,175,.22);
  --accent2:rgba(5,150,105,.15);
  --surface:#111827;
  --surface-soft:#172033;
  --text:#f8fafc;
  --muted:#cbd5e1;
  --soft:#94a3b8;
  --border:#334155;
  --input-bg:#0f172a;
  --input-text:#f8fafc;
  --placeholder:#94a3b8;
  --primary:#60a5fa;
  --primary2:#3b82f6;
  --primary-soft:rgba(37,99,235,.18);
  --success-bg:rgba(6,78,59,.38);
  --success-border:rgba(52,211,153,.30);
  --success-text:#a7f3d0;
  --warning-bg:rgba(124,45,18,.34);
  --warning-border:rgba(251,146,60,.30);
  --warning-text:#fed7aa;
  --shadow:0 14px 40px rgba(0,0,0,.24);
}

html[data-theme="light"]{
  --page-bg:#f7f9fc;
  --accent1:rgba(219,234,254,.82);
  --accent2:rgba(220,252,231,.62);
  --surface:#ffffff;
  --surface-soft:#f8fafc;
  --text:#0f172a;
  --muted:#475569;
  --soft:#64748b;
  --border:#d7dee8;
  --input-bg:#ffffff;
  --input-text:#0f172a;
  --placeholder:#94a3b8;
  --primary:#2563eb;
  --primary2:#3b82f6;
  --primary-soft:#eff6ff;
  --success-bg:#ecfdf5;
  --success-border:#bbf7d0;
  --success-text:#166534;
  --warning-bg:#fff7ed;
  --warning-border:#fed7aa;
  --warning-text:#9a3412;
  --shadow:0 12px 36px rgba(15,23,42,.07);
}

.stApp{
  background:
    radial-gradient(circle at top left,var(--accent1),transparent 34%),
    radial-gradient(circle at top right,var(--accent2),transparent 30%),
    var(--page-bg);
  color:var(--text);
}
.block-container{max-width:1180px;padding-top:2.2rem;padding-bottom:4rem}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.stApp h6,
.stApp p,.stApp label,[data-testid="stMarkdownContainer"]{color:var(--text)!important}
[data-testid="stCaptionContainer"] p{color:var(--soft)!important}
h1,h2,h3{letter-spacing:-.025em}

.hero{
  padding:2.2rem 2.3rem;border-radius:24px;
  background:linear-gradient(135deg,var(--surface),var(--surface-soft));
  border:1px solid var(--border);box-shadow:var(--shadow);margin-bottom:1.25rem
}
.eyebrow{display:inline-block;padding:.38rem .72rem;border-radius:999px;background:var(--primary-soft);color:var(--primary);font-size:.78rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;margin-bottom:.8rem}
.hero-title{font-size:clamp(2rem,4vw,3.35rem);line-height:1.03;font-weight:800;color:var(--text);margin:0}
.hero-copy{max-width:760px;color:var(--muted);font-size:1.06rem;line-height:1.65;margin-top:.85rem;margin-bottom:0}
.trust-row{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1.1rem}
.trust-pill{background:var(--surface);border:1px solid var(--border);color:var(--muted);border-radius:999px;padding:.48rem .78rem;font-size:.86rem;font-weight:600}
.section-kicker{color:var(--primary);font-weight:700;font-size:.78rem;letter-spacing:.06em;text-transform:uppercase;margin-bottom:.25rem}
.step-card{min-height:132px;background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:1.05rem 1.1rem;box-shadow:var(--shadow)}
.step-number{width:32px;height:32px;border-radius:10px;display:inline-flex;align-items:center;justify-content:center;background:var(--primary-soft);color:var(--primary);font-weight:800;margin-bottom:.65rem}
.step-title{color:var(--text);font-weight:750;margin-bottom:.2rem}
.step-copy{color:var(--soft);font-size:.9rem;line-height:1.45}

div[data-testid="stVerticalBlockBorderWrapper"]>div{
  background:var(--surface)!important;border-color:var(--border)!important;box-shadow:var(--shadow)
}
div[data-testid="stForm"]{background:transparent!important;border-color:var(--border)!important}

div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stWidgetLabel"]{
  color:var(--text)!important;font-weight:650!important
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea{
  background:var(--input-bg)!important;
  color:var(--input-text)!important;
  -webkit-text-fill-color:var(--input-text)!important;
  border:1px solid var(--border)!important;
  border-radius:12px!important;
  caret-color:var(--input-text)!important
}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder{
  color:var(--placeholder)!important;
  -webkit-text-fill-color:var(--placeholder)!important;
  opacity:1!important
}
div[data-testid="stNumberInput"] button{
  background:var(--surface-soft)!important;color:var(--text)!important;border-color:var(--border)!important
}

div[data-baseweb="select"] > div,
div[data-testid="stMultiSelect"] [data-baseweb="select"] > div{
  background:var(--input-bg)!important;
  color:var(--input-text)!important;
  border-color:var(--border)!important;
  border-radius:12px!important;
}
div[data-baseweb="select"] span,
div[data-baseweb="select"] input{
  color:var(--input-text)!important;
  -webkit-text-fill-color:var(--input-text)!important;
}
div[data-testid="stSlider"]{
  color:var(--text)!important;
}

div[data-testid="stFormSubmitButton"]>button{
  border-radius:12px!important;min-height:3rem!important;font-weight:750!important;
  background:linear-gradient(135deg,var(--primary),var(--primary2))!important;
  color:#fff!important;border:none!important;box-shadow:0 8px 20px rgba(37,99,235,.20)
}
div[data-testid="stFormSubmitButton"]>button:hover{filter:brightness(.96);color:#fff!important}

.result-banner{background:var(--success-bg);border:1px solid var(--success-border);border-radius:18px;padding:1rem 1.15rem;color:var(--success-text);margin-top:1.1rem;margin-bottom:1rem;font-weight:650}
.disclaimer{background:var(--warning-bg);border:1px solid var(--warning-border);border-radius:16px;padding:.9rem 1rem;color:var(--warning-text);font-size:.9rem;line-height:1.5}


.item-section-title{
  font-size:.76rem;
  font-weight:800;
  letter-spacing:.06em;
  text-transform:uppercase;
  color:var(--primary);
  margin:1rem 0 .45rem 0;
}
.item-copy{
  background:var(--surface-soft);
  border:1px solid var(--border);
  border-radius:12px;
  padding:.8rem .9rem;
  color:var(--text);
  line-height:1.55;
  margin-bottom:.65rem;
}
.status-grid{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:.7rem;
  margin:.35rem 0 .9rem 0;
}
.status-card{
  background:var(--surface-soft);
  border:1px solid var(--border);
  border-radius:12px;
  padding:.75rem .8rem;
}
.status-label{
  font-size:.72rem;
  text-transform:uppercase;
  letter-spacing:.05em;
  font-weight:800;
  color:var(--soft);
  margin-bottom:.25rem;
}
.status-value{
  font-size:.93rem;
  font-weight:700;
  color:var(--text);
  line-height:1.35;
}

.decision-summary-grid{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:.75rem;
  margin:.75rem 0 1rem 0;
}
.decision-summary-card{
  border-radius:14px;
  padding:.9rem 1rem;
  border:1px solid transparent;
}
.decision-green{background:rgba(34,197,94,.12);border-color:rgba(34,197,94,.35)}
.decision-amber{background:rgba(245,158,11,.13);border-color:rgba(245,158,11,.38)}
.decision-red{background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.35)}
.decision-label{font-size:.74rem;text-transform:uppercase;letter-spacing:.05em;font-weight:800;margin-bottom:.2rem}
.decision-count{font-size:1.5rem;font-weight:800;line-height:1.1}
.decision-green .decision-label,.decision-green .decision-count{color:#16a34a}
.decision-amber .decision-label,.decision-amber .decision-count{color:#d97706}
.decision-red .decision-label,.decision-red .decision-count{color:#dc2626}

.approval-green{background:rgba(34,197,94,.12)!important;border-color:rgba(34,197,94,.35)!important}
.approval-amber{background:rgba(245,158,11,.13)!important;border-color:rgba(245,158,11,.38)!important}
.approval-red{background:rgba(239,68,68,.12)!important;border-color:rgba(239,68,68,.35)!important}
.approval-green .status-value{color:#16a34a!important}
.approval-amber .status-value{color:#d97706!important}
.approval-red .status-value{color:#dc2626!important}
.next-action{
  background:var(--primary-soft);
  border:1px solid var(--border);
  border-radius:14px;
  padding:1rem 1rem;
  margin-top:.65rem;
}
.next-action-title{
  font-size:.78rem;
  text-transform:uppercase;
  letter-spacing:.06em;
  font-weight:800;
  color:var(--primary);
  margin-bottom:.45rem;
}
.next-action strong{color:var(--text)}
.next-action p{margin:.15rem 0 .65rem 0!important;line-height:1.5}
@media(max-width:768px){
  .status-grid{grid-template-columns:1fr}
}

@media(max-width:768px){
  .hero{padding:1.5rem 1.25rem;border-radius:18px}
  .block-container{padding-top:1rem}
}
</style>
    """,
    unsafe_allow_html=True,
)


VEHICLE_MAKES = [
    "Tata", "Maruti Suzuki", "Hyundai", "Mahindra", "Toyota", "Kia",
    "Honda", "Skoda", "Volkswagen", "MG", "Renault", "Nissan",
    "Jeep", "Citroen", "BMW", "Mercedes-Benz", "Audi", "Volvo",
    "Other / Not listed"
]

VEHICLE_MODELS = [
    "Not specified",
    "Tata Harrier", "Tata Safari", "Tata Nexon", "Tata Punch", "Tata Altroz", "Tata Tiago", "Tata Tigor",
    "Maruti Suzuki Swift", "Maruti Suzuki Baleno", "Maruti Suzuki Dzire", "Maruti Suzuki Brezza",
    "Maruti Suzuki Grand Vitara", "Maruti Suzuki Fronx", "Maruti Suzuki Ertiga", "Maruti Suzuki WagonR",
    "Hyundai Creta", "Hyundai Venue", "Hyundai i20", "Hyundai Grand i10 Nios", "Hyundai Verna", "Hyundai Alcazar",
    "Mahindra XUV700", "Mahindra Scorpio-N", "Mahindra Thar", "Mahindra XUV 3XO", "Mahindra Bolero",
    "Toyota Innova Crysta", "Toyota Innova Hycross", "Toyota Fortuner", "Toyota Urban Cruiser Hyryder", "Toyota Glanza",
    "Kia Seltos", "Kia Sonet", "Kia Carens",
    "Honda City", "Honda Amaze", "Honda Elevate",
    "Skoda Kushaq", "Skoda Slavia", "Volkswagen Taigun", "Volkswagen Virtus",
    "MG Hector", "MG Astor", "MG ZS EV", "Renault Kiger", "Renault Triber", "Nissan Magnite",
    "Jeep Compass", "Citroen C3", "Citroen C5 Aircross",
    "BMW 3 Series", "BMW X1", "BMW X3", "Mercedes-Benz C-Class", "Mercedes-Benz GLA",
    "Audi A4", "Audi Q3", "Volvo XC40",
    "Other / Not listed"
]

VEHICLE_TYPES = [
    "SUV", "Compact SUV", "Hatchback", "Sedan", "MUV / MPV",
    "Coupe / Performance", "Pickup / Utility", "Other / Not sure"
]

FUEL_TYPES = ["Petrol", "Diesel", "CNG", "Hybrid", "Electric", "Not sure"]

SERVICE_CENTRE_TYPES = [
    "Authorized service centre",
    "Independent multi-brand garage",
    "Local mechanic / workshop",
    "Not sure"
]

WARRANTY_OPTIONS = [
    "In manufacturer warranty",
    "Extended warranty",
    "Out of warranty",
    "Not sure"
]

LAST_SERVICE_OPTIONS = [
    "Less than 6 months ago",
    "6–12 months ago",
    "12–24 months ago",
    "More than 24 months ago",
    "First service / recently purchased",
    "Don't remember"
]

SYMPTOM_OPTIONS = [
    "No noticeable symptoms",
    "Brake noise / squeal",
    "Steering vibration",
    "Vehicle pulls to one side",
    "Engine warning light",
    "Other dashboard warning light",
    "Poor fuel economy",
    "Rough idle",
    "Slow engine start / weak battery",
    "AC cooling or airflow issue",
    "Suspension noise",
    "Unusual engine noise",
    "Power loss / hesitation",
    "Fluid leak",
    "Other / not sure"
]

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">AI-assisted service decision support</div>
        <div class="hero-title">Car Service Estimate Explainer</div>
        <p class="hero-copy">
            Turn a confusing service estimate into plain-language explanations, evidence to request,
            and practical questions to ask before you approve the work.
        </p>
        <div class="trust-row">
            <span class="trust-pill">✓ No remote diagnosis</span>
            <span class="trust-pill">✓ Evidence-first guidance</span>
            <span class="trust-pill">✓ Clear questions for the advisor</span>
            <span class="trust-pill">✓ Your input stays the source of truth</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-kicker">How it works</div>', unsafe_allow_html=True)
st.subheader("Clarity in three simple steps")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">1</div>
            <div class="step-title">Add vehicle context</div>
            <div class="step-copy">Enter the basic vehicle details that help frame the estimate.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">2</div>
            <div class="step-title">Paste the estimate</div>
            <div class="step-copy">Copy the service-centre estimate or job-card items exactly as received.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        """
        <div class="step-card">
            <div class="step-number">3</div>
            <div class="step-title">Review before approval</div>
            <div class="step-copy">Understand each item, what evidence to ask for, and what to clarify.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.markdown('<div class="section-kicker">Your estimate</div>', unsafe_allow_html=True)
st.subheader("Tell us about the car and the recommended work")

with st.container(border=True):
    st.markdown("##### Vehicle details")
    st.caption("Most fields are quick selections. Only paste the service estimate at the end.")

    with st.form("estimate_form"):
        r1c1, r1c2, r1c3 = st.columns(3)

        with r1c1:
            vehicle_type = st.selectbox("Vehicle type", VEHICLE_TYPES, index=0)
        with r1c2:
            brand = st.selectbox("Car maker", VEHICLE_MAKES, index=0)
        with r1c3:
            model = st.selectbox(
                "Car model",
                VEHICLE_MODELS,
                index=1,
                help="The list is searchable — start typing the model name."
            )

        r2c1, r2c2, r2c3 = st.columns(3)

        with r2c1:
            year = st.selectbox(
                "Model year",
                list(range(2026, 1994, -1)),
                index=4,
            )
        with r2c2:
            fuel_type = st.selectbox("Fuel type", FUEL_TYPES, index=1)
        with r2c3:
            mileage = st.slider(
                "Approx. mileage (km)",
                min_value=0,
                max_value=300000,
                value=40000,
                step=1000,
            )

        r3c1, r3c2, r3c3 = st.columns(3)

        with r3c1:
            service_centre = st.selectbox(
                "Service centre type",
                SERVICE_CENTRE_TYPES,
                index=0,
            )
        with r3c2:
            warranty_status = st.selectbox(
                "Warranty status",
                WARRANTY_OPTIONS,
                index=3,
            )
        with r3c3:
            last_service = st.selectbox(
                "Last service",
                LAST_SERVICE_OPTIONS,
                index=1,
            )

        symptoms_selected = st.multiselect(
            "Current symptoms (select all that apply)",
            SYMPTOM_OPTIONS,
            default=["No noticeable symptoms"],
            help="Choose the symptoms you currently notice. You can select more than one."
        )
        symptoms = ", ".join(symptoms_selected) if symptoms_selected else "None selected"

        st.markdown("##### Service estimate / job card")
        st.caption("Paste the line items exactly as shown on the estimate. Prices are optional.")

        estimate = st.text_area(
            "Estimate details",
            height=240,
            label_visibility="collapsed",
            placeholder=(
                "Example:\n"
                "Engine oil replacement - ₹4,200\n"
                "Front brake pad replacement - ₹7,500\n"
                "Wheel alignment and balancing - ₹1,800"
            ),
        )

        submitted = st.form_submit_button(
            "✨ Analyse My Estimate",
            type="primary",
            use_container_width=True,
        )

st.caption(
    "Tip: better input gives better guidance. Include the exact line items and quoted prices where available."
)

def parse_quoted_total(text):
    amounts = []
    patterns = [
        r"₹\s*([0-9][0-9,]*(?:\.\d{1,2})?)",
        r"(?i)rs\.?\s*([0-9][0-9,]*(?:\.\d{1,2})?)",
        r"(?i)inr\s*([0-9][0-9,]*(?:\.\d{1,2})?)",
    ]
    for pattern in patterns:
        for value in re.findall(pattern, text):
            try:
                amounts.append(float(value.replace(",", "")))
            except ValueError:
                pass
    return sum(amounts)


def extract_json(text):
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^\s*```(?:json)?\s*", "", cleaned, flags=re.I)
        cleaned = re.sub(r"\s*```\s*$", "", cleaned)
    return json.loads(cleaned)


def append_usage_row(row):
    gsheets = st.secrets["connections"]["gsheets"]
    credentials_info = dict(gsheets["credentials"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=scopes,
    )
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_url(gsheets["spreadsheet"])
    worksheet_name = gsheets.get("worksheet", "Sheet1")
    worksheet = spreadsheet.worksheet(worksheet_name)
    worksheet.append_row(row, value_input_option="USER_ENTERED")


def decision_signal(item):
    readiness = item.get("approval_readiness", "")
    evidence = item.get("evidence_status", "")
    urgency = item.get("urgency", "")
    category = item.get("category", "")

    if readiness in ["Second opinion advisable", "Evidence required before approval"]:
        return "red", "🔴", "Get proof before approval"

    if category == "Safety-related item" and (
        urgency == "High" or evidence in ["Evidence missing", "Inspection/measurement required"]
    ):
        return "red", "🔴", "Get proof before approval"

    if readiness == "Clarification needed" or evidence in [
        "Evidence missing",
        "Inspection/measurement required",
        "Manufacturer schedule should be checked",
    ]:
        return "amber", "🟠", "Clarify before approval"

    return "green", "🟢", "Proceed after discussion"


if submitted:
    if not estimate.strip():
        st.warning("Please paste at least one service estimate item.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)

            prompt = f"""
You are an automotive service estimate decision-support assistant for private car owners.

Use ONLY the user-provided facts below as vehicle facts. Do not round, alter, infer, or substitute them.

Vehicle context:
- Vehicle type: {vehicle_type}
- Brand: {brand}
- Model: {model}
- Model year: {year}
- Mileage: approximately {mileage} km
- Fuel type: {fuel_type}
- Service centre type: {service_centre}
- Warranty status: {warranty_status}
- Last service: {last_service}
- Current symptoms: {symptoms}

Service estimate / job-card text:
{estimate}

Return ONLY valid JSON with this exact structure:
{{
  "items": [
    {{
      "item": "exact estimate line-item name",
      "quoted_price": "exact quoted price if present, otherwise Not provided",
      "category": "Routine maintenance | Condition-based repair | Safety-related item | Diagnostic/check | Optional/add-on treatment | Cannot classify without evidence",
      "plain_explanation": "short plain-language explanation",
      "why_recommended": "conditional explanation using may/could",
      "evidence_status": "Enough evidence in estimate | Evidence missing | Inspection/measurement required | Manufacturer schedule should be checked",
      "approval_readiness": "Ready to discuss/approve | Clarification needed | Evidence required before approval | Second opinion advisable",
      "urgency": "High | Medium | Low | Cannot determine from estimate alone",
      "delay_risk": "possible consequence if delayed, without certainty",
      "evidence_to_request": "specific evidence/measurement/report to ask for",
      "question_to_ask": "one concise question for the service advisor"
    }}
  ],
  "top_questions": ["maximum 5 highest-priority questions"],
  "decision_summary": "2-4 sentence summary focused on what the customer should clarify before approval",
  "possible_optional_addons": ["item names that appear optional/add-on based only on supplied information"],
  "second_opinion_items": ["item names where a second opinion may be useful"]
}}

Strict rules:
- Keep every estimate item in the same order as supplied.
- Preserve the selected vehicle context, item names and quoted prices exactly. Treat mileage as approximate because the UI captures it in 1,000 km steps.
- Do not invent manufacturer schedules, inspection results, measurements, symptoms, market prices, or service history.
- Do not claim a quoted price is fair, expensive or cheap because you do not have verified live market pricing.
- Do not diagnose the vehicle remotely.
- If necessity depends on inspection evidence, use "Evidence required before approval" and "Cannot determine from estimate alone".
- "Ready to discuss/approve" means the information appears sufficient for an informed discussion; it is NOT a mechanical approval or diagnosis.
- Use "Second opinion advisable" sparingly, for high-cost/condition-based work or unclear add-ons where independent confirmation could materially help.
"""

            response = None
            last_error = None
            models_to_try = [
                "gemini-3.5-flash-lite",
                "gemini-3.8-flash",
                "gemini-3.6-flash",
            ]

            with st.spinner("Analysing your estimate and preparing a decision summary..."):
                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                        )
                        if response and response.text:
                            break
                    except Exception as exc:
                        last_error = exc

            if response and response.text:
                try:
                    data = extract_json(response.text)
                    items = data.get("items", [])
                    quoted_total = parse_quoted_total(estimate)

                    st.markdown(
                        '<div class="result-banner">✓ Analysis complete. Review the decision dashboard before speaking with your service advisor.</div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown('<div class="section-kicker">Decision dashboard</div>', unsafe_allow_html=True)
                    st.subheader("What your estimate is telling you")

                    evidence_needed = sum(
                        1 for x in items
                        if x.get("evidence_status") in ["Evidence missing", "Inspection/measurement required"]
                    )
                    optional_count = sum(
                        1 for x in items
                        if x.get("category") == "Optional/add-on treatment"
                    )
                    second_opinion_count = sum(
                        1 for x in items
                        if x.get("approval_readiness") == "Second opinion advisable"
                    )

                    signal_counts = {"green": 0, "amber": 0, "red": 0}
                    for x in items:
                        signal, _, _ = decision_signal(x)
                        signal_counts[signal] += 1

                    if "session_id" not in st.session_state:
                        st.session_state.session_id = str(uuid.uuid4())

                    usage_row = [
                        datetime.now(timezone.utc).isoformat(),
                        st.session_state.session_id,
                        vehicle_type,
                        brand,
                        model,
                        year,
                        fuel_type,
                        mileage,
                        service_centre,
                        warranty_status,
                        last_service,
                        symptoms,
                        quoted_total,
                        len(items),
                        signal_counts["red"],
                        signal_counts["amber"],
                        signal_counts["green"],
                        optional_count,
                        "",
                        "",
                        "",
                    ]

                    try:
                        append_usage_row(usage_row)
                    except Exception as log_exc:
                        st.warning(
                            "Analysis completed, but usage logging could not be saved. "
                            "Please check the Google Sheets connection settings."
                        )
                        with st.expander("Logging details"):
                            st.code(str(log_exc))

                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.metric("Quoted total", f"₹{quoted_total:,.0f}" if quoted_total else "Not available")
                    with m2:
                        st.metric("Line items", len(items))
                    with m3:
                        st.metric("Need more evidence", evidence_needed)
                    with m4:
                        st.metric("Possible add-ons", optional_count)

                    st.markdown(
                        f"""
                        <div class="decision-summary-grid">
                          <div class="decision-summary-card decision-red">
                            <div class="decision-label">Needs proof / caution</div>
                            <div class="decision-count">🔴 {signal_counts["red"]}</div>
                          </div>
                          <div class="decision-summary-card decision-amber">
                            <div class="decision-label">Clarify first</div>
                            <div class="decision-count">🟠 {signal_counts["amber"]}</div>
                          </div>
                          <div class="decision-summary-card decision-green">
                            <div class="decision-label">Proceed after discussion</div>
                            <div class="decision-count">🟢 {signal_counts["green"]}</div>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if second_opinion_count:
                        st.info(
                            f"{second_opinion_count} item(s) may benefit from an independent second opinion before approval."
                        )

                    st.markdown("### Item-by-item decision view")

                    for idx, item in enumerate(items, 1):
                        signal, signal_icon, signal_label = decision_signal(item)
                        title = f"{signal_icon} {idx}. {item.get('item', 'Service item')}"
                        price = item.get("quoted_price", "Not provided")
                        if price and price != "Not provided":
                            title += f" — {price}"
                        title += f" · {signal_label}"

                        with st.expander(title, expanded=(idx <= 2)):
                            category = item.get("category", "")
                            evidence_status = item.get("evidence_status", "")
                            approval_readiness = item.get("approval_readiness", "")
                            urgency = item.get("urgency", "")

                            st.markdown(
                                f"""
                                <div class="status-grid">
                                  <div class="status-card">
                                    <div class="status-label">Category</div>
                                    <div class="status-value">{category}</div>
                                  </div>
                                  <div class="status-card">
                                    <div class="status-label">Evidence status</div>
                                    <div class="status-value">{evidence_status}</div>
                                  </div>
                                  <div class="status-card approval-{signal}">
                                    <div class="status-label">Approval readiness</div>
                                    <div class="status-value">{signal_icon} {signal_label}</div>
                                  </div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                            st.markdown('<div class="item-section-title">1 · Understand the item</div>', unsafe_allow_html=True)
                            st.markdown(
                                f'<div class="item-copy"><strong>What it means</strong><br>{item.get("plain_explanation", "")}</div>',
                                unsafe_allow_html=True,
                            )
                            st.markdown(
                                f'<div class="item-copy"><strong>Why it may have been recommended</strong><br>{item.get("why_recommended", "")}</div>',
                                unsafe_allow_html=True,
                            )

                            st.markdown('<div class="item-section-title">2 · Assess the risk</div>', unsafe_allow_html=True)
                            risk_c1, risk_c2 = st.columns(2)
                            with risk_c1:
                                st.markdown("**Urgency**")
                                st.info(urgency)
                            with risk_c2:
                                st.markdown("**If delayed**")
                                st.write(item.get("delay_risk", ""))

                            st.markdown('<div class="item-section-title">3 · What you should verify</div>', unsafe_allow_html=True)
                            st.markdown(
                                f'<div class="item-copy"><strong>Evidence to request</strong><br>{item.get("evidence_to_request", "")}</div>',
                                unsafe_allow_html=True,
                            )

                            st.markdown('<div class="item-section-title">4 · Your next action</div>', unsafe_allow_html=True)
                            st.markdown(
                                f"""
                                <div class="next-action">
                                  <div class="next-action-title">Ask the service advisor</div>
                                  <p>{item.get("question_to_ask", "")}</p>
                                  <strong>Decision guidance:</strong>
                                  <p>{signal_icon} {signal_label}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )


                    st.markdown("### Before you approve")
                    st.write(data.get("decision_summary", ""))

                    questions = data.get("top_questions", [])
                    if questions:
                        st.markdown("#### Top questions to ask")
                        for q in questions[:5]:
                            st.markdown(f"- {q}")

                    optional_items = data.get("possible_optional_addons", [])
                    if optional_items:
                        st.markdown("#### Items to clarify as possible add-ons")
                        st.write(", ".join(optional_items))

                    second_items = data.get("second_opinion_items", [])
                    if second_items:
                        st.markdown("#### Consider a second opinion for")
                        st.write(", ".join(second_items))

                    st.write("")
                    st.markdown(
                        """
                        <div class="disclaimer">
                            <strong>Important:</strong> This tool provides decision support only.
                            The quoted-total calculation uses only prices present in the pasted estimate.
                            It does not verify market prices, inspect the vehicle, diagnose faults, or replace
                            advice from a qualified automotive professional.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                except Exception:
                    st.warning("The AI returned an unexpected format. Showing the raw explanation instead.")
                    with st.container(border=True):
                        st.markdown(response.text)

            else:
                st.error("The AI service is temporarily unavailable. Please try again.")
                if last_error:
                    with st.expander("Technical details"):
                        st.code(str(last_error))

        except KeyError:
            st.error("Gemini API key is not configured in Streamlit Secrets.")
        except Exception as exc:
            st.error("The AI service could not complete the analysis.")
            with st.expander("Technical details"):
                st.code(str(exc))

st.write("")
st.divider()

f1, f2, f3 = st.columns(3)
with f1:
    st.markdown("**Built for car owners**")
    st.caption("Designed for people who need clarity before approving service work.")
with f2:
    st.markdown("**Evidence over assumptions**")
    st.caption("The tool encourages measurements, reports and inspection evidence.")
with f3:
    st.markdown("**Decision support, not diagnosis**")
    st.caption("The final mechanical judgement remains with qualified professionals.")
