import streamlit as st
from google import genai
from google.genai import types
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

.recommendation-box{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:1.1rem 1.15rem;margin:.8rem 0;box-shadow:var(--shadow)}
.recommendation-title{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;font-weight:800;color:var(--primary);margin-bottom:.45rem}
.recommendation-headline{font-size:1.15rem;font-weight:800;line-height:1.4;color:var(--text)}
.action-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.75rem;margin:.85rem 0 1rem 0}
.action-card{border:1px solid var(--border);border-radius:14px;padding:.9rem 1rem;background:var(--surface-soft)}
.action-card h4{margin:0 0 .45rem 0!important;font-size:.94rem!important}
.action-card ul{margin:.25rem 0 0 1rem;padding:0}
.action-card li{margin:.25rem 0;line-height:1.45}
.action-now{border-left:5px solid #dc2626}
.action-proceed{border-left:5px solid #16a34a}
.action-clarify{border-left:5px solid #d97706}
.action-later{border-left:5px solid #64748b}
.action-optional{border-left:5px solid #7c3aed}
@media(max-width:768px){.action-grid{grid-template-columns:1fr}}
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


VEHICLE_CATALOG = {
    "Hatchback": {
        "Tata": ["Altroz", "Tiago", "Tiago EV"],
        "Maruti Suzuki": ["Swift", "Baleno", "WagonR", "Celerio", "Alto K10"],
        "Hyundai": ["i20", "Grand i10 Nios"],
        "Toyota": ["Glanza"],
        "MG": ["Comet EV"],
        "Renault": ["Kwid"],
        "Citroen": ["C3"],
        "MINI": ["Cooper", "Cooper S", "Cooper Electric"],
        "Mercedes-Benz": ["A-Class Hatchback"],
    },
    "Sedan": {
        "Tata": ["Tigor", "Tigor EV"],
        "Maruti Suzuki": ["Dzire", "Ciaz"],
        "Hyundai": ["Verna", "Aura"],
        "Honda": ["City", "Amaze"],
        "Skoda": ["Slavia"],
        "Volkswagen": ["Virtus"],
        "BYD": ["Seal"],
        "BMW": ["2 Series Gran Coupe", "3 Series", "5 Series", "7 Series", "i4", "i5", "i7"],
        "Mercedes-Benz": ["C-Class", "E-Class", "S-Class", "CLA Electric", "EQS"],
        "Audi": ["A4", "A6", "A8 L", "e-tron GT"],
        "Volvo": ["S90"],
        "Lexus": ["ES", "LS"],
        "Porsche": ["Panamera", "Taycan"],
    },
    "Compact SUV": {
        "Tata": ["Nexon", "Nexon EV", "Punch", "Punch EV", "Curvv", "Curvv EV"],
        "Maruti Suzuki": ["Brezza", "Fronx"],
        "Hyundai": ["Venue", "Exter", "Creta Electric"],
        "Mahindra": ["XUV 3XO", "XUV400 EV"],
        "Kia": ["Sonet", "Syros"],
        "Honda": ["Elevate"],
        "Skoda": ["Kushaq", "Kylaq"],
        "Volkswagen": ["Taigun"],
        "MG": ["Astor", "ZS EV", "Windsor EV"],
        "Renault": ["Kiger"],
        "Nissan": ["Magnite"],
        "Citroen": ["C3 Aircross", "eC3"],
        "BYD": ["Atto 3"],
        "VinFast": ["VF 6"],
        "BMW": ["X1", "iX1"],
        "Mercedes-Benz": ["GLA"],
        "Audi": ["Q3"],
        "Volvo": ["EX30", "EX40", "XC40"],
        "Lexus": ["UX"],
        "MINI": ["Countryman", "Countryman Electric"],
    },
    "SUV": {
        "Tata": ["Harrier", "Harrier EV", "Safari"],
        "Maruti Suzuki": ["Grand Vitara", "Jimny"],
        "Hyundai": ["Creta", "Alcazar", "Tucson", "Ioniq 5"],
        "Mahindra": ["XUV700", "Scorpio-N", "Thar", "Thar Roxx", "Scorpio Classic", "BE 6", "XEV 9e"],
        "Toyota": ["Fortuner", "Urban Cruiser Hyryder", "Land Cruiser 300"],
        "Kia": ["Seltos", "EV6", "EV9"],
        "Renault": ["Duster", "Duster Strong Hybrid E-Tech"],
        "Skoda": ["Kodiaq"],
        "Volkswagen": ["Tiguan", "Tiguan R-Line"],
        "MG": ["Hector", "Gloster", "M9", "Cyberster"],
        "Nissan": ["X-Trail"],
        "Jeep": ["Compass", "Meridian", "Wrangler", "Grand Cherokee"],
        "Citroen": ["C5 Aircross"],
        "BYD": ["Sealion 7"],
        "VinFast": ["VF 7"],
        "Tesla": ["Model Y", "Model Y L"],
        "BMW": ["X3", "X5", "X7", "iX"],
        "Mercedes-Benz": ["GLC", "GLE", "GLS", "EQS SUV", "G-Class", "G-Class Electric"],
        "Audi": ["Q5", "Q7", "Q8", "Q8 e-tron", "Q6 e-tron"],
        "Volvo": ["XC60", "XC90", "EX90"],
        "Lexus": ["NX", "RX", "LX"],
        "Land Rover": ["Range Rover Evoque", "Range Rover Velar", "Range Rover Sport", "Range Rover", "Discovery Sport", "Discovery", "Defender 90", "Defender 110", "Defender 130"],
        "Porsche": ["Macan", "Macan Electric", "Cayenne"],
        "Lamborghini": ["Urus"],
        "Bentley": ["Bentayga"],
        "Rolls-Royce": ["Cullinan"],
    },
    "MUV / MPV": {
        "Maruti Suzuki": ["Ertiga", "XL6", "Invicto"],
        "Toyota": ["Innova Crysta", "Innova Hycross", "Rumion", "Vellfire"],
        "Kia": ["Carens", "Carnival"],
        "Renault": ["Triber"],
        "BYD": ["eMAX 7"],
        "VinFast": ["VF MPV 7"],
        "Mercedes-Benz": ["V-Class"],
        "Lexus": ["LM"],
    },
    "Coupe / Performance": {
        "BMW": ["M2", "M4 Competition", "Z4"],
        "Mercedes-Benz": ["CLE Coupe", "AMG GT Coupe", "CLE Cabriolet", "Mercedes-Maybach SL Monogram Series"],
        "Audi": ["RS5", "RS e-tron GT"],
        "Porsche": ["911", "718 Cayman", "718 Boxster"],
        "Ferrari": ["Roma", "296 GTB", "296 GTS", "12Cilindri", "SF90 Stradale"],
        "Lamborghini": ["Temerario", "Revuelto"],
        "McLaren": ["Artura", "750S", "GT"],
        "Aston Martin": ["Vantage", "DB12", "Vanquish"],
        "Bentley": ["Continental GT", "Continental GTC"],
        "Rolls-Royce": ["Spectre"],
        "Lotus": ["Emira", "Emeya"],
    },
    "Pickup / Utility": {
        "Mahindra": ["Bolero", "Bolero Camper"],
        "Toyota": ["Hilux"],
        "Isuzu": ["D-Max V-Cross", "D-Max S-Cab"],
        "Force Motors": ["Gurkha"],
    },
    "Other / Not sure": {
        "Other / Not listed": ["Other / Not listed"],
    },
}

VEHICLE_TYPES = list(VEHICLE_CATALOG.keys())

SYMPTOM_GROUPS = {
    "Brakes & suspension": [
        "Brake noise / squeal",
        "Brake pedal feels soft / hard",
        "Steering vibration",
        "Vehicle pulls to one side",
        "Suspension noise",
        "Uneven tyre wear",
    ],
    "Electrical & AC": [
        "TPMS warning / tyre-pressure alert",
        "Headlight / tail-light issue",
        "Fuse / electrical issue",
        "Battery / slow-start issue",
        "Dashboard warning light",
        "AC cooling or airflow issue",
    ],
    "Body & exterior": [
        "Denting / body damage",
        "Paint damage / scratches",
        "Loose body panel",
        "Side mirror issue",
        "Wiper / washer issue",
    ],
    "Engine & drivetrain": [
        "Engine warning light",
        "Unusual engine noise",
        "Rough idle",
        "Power loss / hesitation",
        "Poor fuel economy",
        "Oil / fluid leak",
        "Cooling-system / overheating issue",
        "Gearbox / transmission issue",
        "Power-steering issue",
        "Other / not sure",
    ],
}

SERVICE_ITEMS_BY_SECTION = {
    "Brakes & suspension": [
        "Front brake pads",
        "Rear brake pads / brake shoes",
        "Brake discs / rotors",
        "Brake fluid",
        "Brake cleaning / inspection",
        "Suspension inspection",
        "Shock absorber / strut",
        "Wheel alignment",
        "Wheel balancing",
        "Tyre rotation",
    ],
    "Electrical & AC": [
        "Battery health check",
        "Battery replacement",
        "TPMS inspection",
        "Headlight / tail-light repair",
        "Fuse / wiring inspection",
        "AC inspection",
        "AC filter / cabin filter",
        "AC gas / refrigerant service",
        "Diagnostic scan",
    ],
    "Body & exterior": [
        "Denting",
        "Painting",
        "Loose panel repair",
        "Side mirror repair / replacement",
        "Wiper blade replacement",
        "Washer system repair",
    ],
    "Engine & drivetrain": [
        "Engine oil replacement",
        "Oil filter replacement",
        "Air filter replacement",
        "Fuel filter",
        "Coolant / cooling-system service",
        "Radiator inspection / repair",
        "Engine noise diagnosis",
        "Valve timing / timing-system inspection",
        "Gearbox / transmission inspection",
        "Power-steering inspection",
        "Injector cleaning",
        "Throttle-body cleaning",
        "Engine flush treatment",
    ],
}

ALL_SERVICE_ITEMS = [
    item
    for section_items in SERVICE_ITEMS_BY_SECTION.values()
    for item in section_items
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
            <div class="step-title">Add your service estimate</div>
            <div class="step-copy">Enter, build, or upload the workshop estimate or job card.</div>
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
    st.caption("Most fields are quick selections. Add the service estimate using the option that suits you best.")

    st.markdown("##### Choose your car")
    car_c1, car_c2, car_c3 = st.columns(3)

    with car_c1:
        vehicle_type = st.selectbox(
            "Vehicle type",
            VEHICLE_TYPES,
            index=None,
            placeholder="Select vehicle type",
            key="vehicle_type_selector",
        )

    available_makes = (
        list(VEHICLE_CATALOG[vehicle_type].keys())
        if vehicle_type in VEHICLE_CATALOG
        else []
    )

    with car_c2:
        brand = st.selectbox(
            "Car maker",
            available_makes,
            index=None,
            placeholder="Select manufacturer",
            key=f"car_maker_selector_{vehicle_type or 'none'}",
            disabled=not bool(vehicle_type),
            help="Choose the vehicle type first. Only matching manufacturers will then be shown.",
        )

    available_models = (
        VEHICLE_CATALOG[vehicle_type][brand]
        if vehicle_type in VEHICLE_CATALOG
        and brand in VEHICLE_CATALOG[vehicle_type]
        else []
    )

    with car_c3:
        selected_model = st.selectbox(
            "Car model",
            available_models,
            index=None,
            placeholder="Select model",
            key=f"car_model_selector_{vehicle_type or 'none'}_{brand or 'none'}",
            disabled=not bool(brand),
            help="Choose the manufacturer first. Only matching models will then be shown.",
        )

    model = (
        selected_model
        if brand == "Other / Not listed"
        else f"{brand} {selected_model}"
        if brand and selected_model
        else ""
    )

    st.caption(
        "Vehicle type filters the manufacturer list, and manufacturer filters the model list."
    )

    with st.container(border=True):
        st.markdown("##### Tester details")
        st.caption(
            "Used only to link this MVP test with the saved estimate and feedback. "
            "Name and email are stored in the private research sheet and are not sent to the AI model."
        )

        user_c1, user_c2 = st.columns(2)
        with user_c1:
            user_name = st.text_input("Name *", placeholder="Enter your name", max_chars=80)
        with user_c2:
            user_email = st.text_input("Email *", placeholder="name@example.com", max_chars=254)

        consent = st.checkbox(
            "I agree that my name, email, estimate details and feedback may be stored for this course MVP evaluation."
        )

        st.markdown("##### Vehicle details")
        if vehicle_type and model:
            st.caption(f"Selected vehicle: {vehicle_type} · {model}")
        else:
            st.caption("Complete the vehicle type, manufacturer and model selections above.")

        r2c1, r2c2, r2c3 = st.columns(3)

        with r2c1:
            year = st.selectbox(
                "Model year",
                list(range(2026, 1994, -1)),
                index=None,
                placeholder="Select model year",
            )
        with r2c2:
            fuel_type = st.selectbox(
                "Fuel type",
                FUEL_TYPES,
                index=None,
                placeholder="Select fuel type",
            )
        with r2c3:
            mileage = st.number_input(
                "KMs driven (odometer reading)",
                min_value=0,
                max_value=300000,
                value=None,
                step=1000,
                placeholder="e.g., 28,000",
            )

        r3c1, r3c2, r3c3 = st.columns(3)

        with r3c1:
            service_centre = st.selectbox(
                "Service centre type",
                SERVICE_CENTRE_TYPES,
                index=None,
                placeholder="Select service centre type",
            )
        with r3c2:
            warranty_status = st.selectbox(
                "Warranty status",
                WARRANTY_OPTIONS,
                index=None,
                placeholder="Select warranty status",
            )
        with r3c3:
            last_service = st.selectbox(
                "Last service",
                LAST_SERVICE_OPTIONS,
                index=None,
                placeholder="Select when the car was last serviced",
            )

        st.markdown("##### Current issues / symptoms")
        st.caption("Select only what you have actually noticed. Leave all sections blank if there are no noticeable symptoms.")

        symptoms_selected = []
        symptom_cols = st.columns(2)
        for idx, (section_name, section_options) in enumerate(SYMPTOM_GROUPS.items()):
            with symptom_cols[idx % 2]:
                selected = st.multiselect(
                    section_name,
                    section_options,
                    default=[],
                    key=f"symptoms_{section_name}",
                    placeholder="None selected",
                )
                symptoms_selected.extend(selected)

        symptoms = ", ".join(symptoms_selected) if symptoms_selected else "No noticeable symptoms reported"

        st.divider()
        st.markdown("##### Workshop estimate / job card")
        st.caption(
            "Now add what the service advisor or workshop has recommended. "
            "This is separate from the issues you noticed above."
        )

        input_mode = st.radio(
            "How would you like to add the workshop estimate?",
            ["Enter service estimate", "Build job card manually", "Upload job card photo"],
            horizontal=True,
            key="estimate_input_mode",
        )

        manual_rows = []
        uploaded_job_card = None
        estimate = ""

        if input_mode == "Enter service estimate":
            st.markdown("##### Service estimate / job card")
            st.caption("Enter or copy the service items exactly as shown on the workshop estimate or job card. Prices are optional.")
            estimate = st.text_area(
                "Estimate details",
                height=240,
                max_chars=6000,
                label_visibility="collapsed",
                placeholder=(
                    "Enter or copy the workshop estimate here. Example:\n"
                    "Engine oil replacement - ₹4,200\n"
                    "Front brake pads - ₹7,500"
                ),
            )
        elif input_mode == "Build job card manually":
            st.caption(
                "Enter the workshop's recommended work and quoted price exactly as communicated. "
                "Add or remove rows as needed — you do not need to select the owner's issues again."
            )
            manual_rows = st.data_editor(
                [
                    {"Recommended work / service item": "", "Quoted cost (₹)": None, "Workshop note / reason": ""},
                    {"Recommended work / service item": "", "Quoted cost (₹)": None, "Workshop note / reason": ""},
                    {"Recommended work / service item": "", "Quoted cost (₹)": None, "Workshop note / reason": ""},
                ],
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                column_config={
                    "Recommended work / service item": st.column_config.TextColumn(
                        "Recommended work / service item",
                        help="Enter the job or part recommended by the workshop.",
                        max_chars=120,
                    ),
                    "Quoted cost (₹)": st.column_config.NumberColumn(
                        "Quoted cost (₹)",
                        min_value=0,
                        step=100,
                    ),
                    "Workshop note / reason": st.column_config.TextColumn(
                        "Workshop note / reason",
                        help="Optional: copy the advisor's reason or note.",
                        max_chars=250,
                    ),
                },
                key="manual_job_card_editor",
            )

            manual_lines = []
            if manual_rows is not None:
                rows_iter = (
                    manual_rows.to_dict("records")
                    if hasattr(manual_rows, "to_dict")
                    else manual_rows
                )
                for row in rows_iter:
                    item = str(row.get("Recommended work / service item", "") or "").strip()
                    cost = row.get("Quoted cost (₹)")
                    details = str(row.get("Workshop note / reason", "") or "").strip()
                    if item:
                        line = item
                        if cost is not None:
                            try:
                                line += f" - ₹{float(cost):,.0f}"
                            except (TypeError, ValueError):
                                pass
                        if details:
                            line += f" | {details}"
                        manual_lines.append(line)
            estimate = "\n".join(manual_lines)
            if manual_lines:
                st.caption("These workshop recommendations and quoted costs will be analysed against the vehicle context and owner-reported issues.")
            else:
                st.info("Add at least one workshop-recommended job or service item.")

        else:
            uploaded_job_card = st.file_uploader(
                "Upload the workshop estimate / job card",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=False,
                help="Use a clear, readable image. Avoid uploading registration number, VIN, phone number or other unnecessary personal information.",
                key="job_card_uploader",
            )
            if uploaded_job_card is not None:
                st.image(uploaded_job_card, caption="Uploaded workshop job card", width="stretch")
                estimate = f"Uploaded job card image: {uploaded_job_card.name}"
            st.caption("The uploaded workshop job-card photo will be read by the AI when you analyse it.")

        submitted = st.button(
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


def quoted_total_from_items(items):
    total = 0.0
    found = False
    for item in items:
        price = str(item.get("quoted_price", ""))
        match = re.search(r"([0-9][0-9,]*(?:\\.\\d{1,2})?)", price)
        if match:
            try:
                total += float(match.group(1).replace(",", ""))
                found = True
            except ValueError:
                pass
    return total if found else 0.0


def extract_json(text):
    cleaned = text.strip()
    cleaned = re.sub(r"^\s*```(?:json)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        first = cleaned.find("{")
        last = cleaned.rfind("}")
        if first != -1 and last != -1 and last > first:
            return json.loads(cleaned[first:last + 1])
        raise


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

    # Preserve the existing sheet structure and append tester identity columns at V/W.
    worksheet.update(
        range_name="V1:X1",
        values=[["name", "email", "estimate_input_mode"]],
        value_input_option="USER_ENTERED",
    )
    worksheet.append_row(row, value_input_option="USER_ENTERED")


def update_feedback_for_session(session_id, useful, decision_help, comment):
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

    session_cell = worksheet.find(str(session_id), in_column=2)
    if not session_cell:
        raise ValueError("Could not find the matching analysis session in the usage sheet.")

    row_number = session_cell.row
    worksheet.update(
        range_name=f"S{row_number}:U{row_number}",
        values=[[useful, decision_help, comment]],
        value_input_option="USER_ENTERED",
    )


def is_valid_name(value):
    value = value.strip()
    if len(value) < 2 or len(value) > 80:
        return False
    return bool(re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ.' -]+", value))


def is_valid_email(value):
    value = value.strip()
    if len(value) > 254:
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", value))


def is_valid_estimate(value):
    value = value.strip()
    if len(value) < 10 or len(value) > 6000:
        return False
    return bool(re.search(r"[A-Za-z]", value))


def is_valid_vehicle_selection(vehicle_type, brand, selected_model):
    return (
        vehicle_type in VEHICLE_CATALOG
        and brand in VEHICLE_CATALOG[vehicle_type]
        and selected_model in VEHICLE_CATALOG[vehicle_type][brand]
    )

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
    if not is_valid_name(user_name):
        st.warning("Please enter a valid name using letters, spaces, apostrophes, hyphens or periods.")
    elif not is_valid_email(user_email):
        st.warning("Please enter a valid email address, for example name@example.com.")
    elif not consent:
        st.warning("Please confirm the consent checkbox before analysing the estimate.")
    elif not vehicle_type:
        st.warning("Please select the vehicle type.")
    elif not brand:
        st.warning("Please select the car manufacturer.")
    elif not selected_model:
        st.warning("Please select the car model.")
    elif not is_valid_vehicle_selection(vehicle_type, brand, selected_model):
        st.warning("The selected vehicle type, manufacturer and model combination is invalid. Please select the car again.")
    elif year is None:
        st.warning("Please select the model year.")
    elif fuel_type is None:
        st.warning("Please select the fuel type.")
    elif mileage is None:
        st.warning("Please enter the approximate KMs driven.")
    elif service_centre is None:
        st.warning("Please select the service centre type.")
    elif warranty_status is None:
        st.warning("Please select the warranty status.")
    elif last_service is None:
        st.warning("Please select when the car was last serviced.")
    elif input_mode == "Enter service estimate" and not is_valid_estimate(estimate):
        st.warning("Please enter a valid service estimate between 10 and 6,000 characters.")
    elif input_mode == "Build job card manually" and not estimate.strip():
        st.warning("Please add at least one workshop-recommended job or service item.")
    elif input_mode == "Upload job card photo" and uploaded_job_card is None:
        st.warning("Please upload a JPG, JPEG or PNG job-card image.")
    elif input_mode == "Upload job card photo" and uploaded_job_card.size > 8 * 1024 * 1024:
        st.warning("Please upload an image smaller than 8 MB.")
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
- KMs driven (odometer reading): approximately {mileage} km
- Fuel type: {fuel_type}
- Service centre type: {service_centre}
- Warranty status: {warranty_status}
- Last service: {last_service}
- Current symptoms: {symptoms}

Estimate input method: {input_mode}

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
      "question_to_ask": "one concise question for the service advisor",
      "recommended_action": "Address now | Proceed after discussion | Clarify before approval | Can wait until next service | Optional / consider skipping | Second opinion before approval",
      "action_reason": "short reason for the recommended action based only on supplied facts"
    }}
  ],
  "customer_recommendation": {{
    "headline": "one concise overall recommendation telling the customer what to do next",
    "address_now": ["items that may need prompt attention because of safety, high urgency, warning signs or credible risk"],
    "proceed_after_discussion": ["items that appear reasonable to proceed with after a normal discussion"],
    "clarify_before_approval": ["items where evidence, measurement or explanation should be requested first"],
    "can_wait_until_next_service": ["items that appear low urgency and may reasonably be deferred based on supplied information"],
    "optional_or_consider_skipping": ["items that appear optional/add-on or not sufficiently justified"],
    "second_opinion_before_approval": ["items where independent confirmation may materially help"],
    "next_steps": ["maximum 5 concrete actions for the customer, ordered by priority"]
  }},
  "top_questions": ["maximum 5 highest-priority questions"],
  "decision_summary": "2-4 sentence summary focused on what the customer should clarify before approval",
  "possible_optional_addons": ["item names that appear optional/add-on based only on supplied information"],
  "second_opinion_items": ["item names where a second opinion may be useful"]
}}

Strict rules:
- Keep every estimate item in the same order as supplied.
- Preserve the selected vehicle context, item names and quoted prices exactly. Treat the odometer reading as approximate because the UI captures it in 1,000 km steps.
- Do not invent manufacturer schedules, inspection results, measurements, symptoms, market prices, or service history.
- Do not claim a quoted price is fair, expensive or cheap because you do not have verified live market pricing.
- Do not diagnose the vehicle remotely.
- If necessity depends on inspection evidence, use "Evidence required before approval" and "Cannot determine from estimate alone".
- "Ready to discuss/approve" means the information appears sufficient for an informed discussion; it is NOT a mechanical approval or diagnosis.
- Use "Second opinion advisable" sparingly, for high-cost/condition-based work or unclear add-ons where independent confirmation could materially help.
- Make the recommendation action-oriented, not just explanatory.
- Use "Address now" only when supplied symptoms, safety context, warning signs, or evidence support prompt attention.
- "Address now" means seek prompt professional attention or clarification; it is not a remote diagnosis.
- Use "Can wait until next service" only when the supplied information suggests low urgency and no safety concern. If uncertain, use "Clarify before approval".
- Use "Optional / consider skipping" only for add-ons or treatments that are not clearly supported by supplied evidence. Never advise skipping a safety-critical item.
- Every service item should appear in one practical recommendation bucket in customer_recommendation. Second-opinion items may additionally appear in second_opinion_before_approval.
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
                        request_contents = prompt
                        if input_mode == "Upload job card photo" and uploaded_job_card is not None:
                            image_bytes = uploaded_job_card.getvalue()
                            request_contents = [
                                prompt
                                + "\nRead the uploaded job-card image carefully. Extract only visible service items, quoted prices and workshop notes. "
                                  "Do not invent unreadable text. If something cannot be read, mark it as unclear.",
                                types.Part.from_bytes(
                                    data=image_bytes,
                                    mime_type=uploaded_job_card.type,
                                ),
                            ]

                        response = client.models.generate_content(
                            model=model_name,
                            contents=request_contents,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                temperature=0.2,
                            ),
                        )
                        if response and response.text:
                            break
                    except Exception as exc:
                        last_error = exc

            if response and response.text:
                try:
                    data = extract_json(response.text)
                    items = data.get("items", [])
                    quoted_total = (
                        quoted_total_from_items(items)
                        if input_mode == "Upload job card photo"
                        else parse_quoted_total(estimate)
                    )

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
                        user_name.strip(),
                        user_email.strip().lower(),
                        input_mode,
                    ]

                    try:
                        append_usage_row(usage_row)
                        st.session_state.feedback_available = True
                        st.session_state.feedback_submitted = False
                    except Exception as log_exc:
                        st.warning(
                            "Analysis completed, but usage logging could not be saved. "
                            "Please check the Google Sheets connection settings."
                        )
                        with st.expander("Logging details"):
                            st.code(str(log_exc))

                    recommendation = data.get("customer_recommendation", {})
                    if recommendation:
                        st.markdown('<div class="section-kicker">Your decision</div>', unsafe_allow_html=True)
                        st.subheader("Recommended next steps")

                        headline = str(recommendation.get("headline", "")).strip()
                        if headline:
                            st.markdown(
                                f"""
                                <div class="recommendation-box">
                                  <div class="recommendation-title">Overall recommendation</div>
                                  <div class="recommendation-headline">{headline}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        def render_action_list(title, values, css_class, icon):
                            clean_values = [str(x).strip() for x in (values or []) if str(x).strip()]
                            if not clean_values:
                                return ""
                            lis = "".join(f"<li>{x}</li>" for x in clean_values)
                            return (
                                f'<div class="action-card {css_class}">'
                                f'<h4>{icon} {title}</h4><ul>{lis}</ul></div>'
                            )

                        action_cards = [
                            render_action_list("Address now / highest priority", recommendation.get("address_now", []), "action-now", "🔴"),
                            render_action_list("Proceed after discussion", recommendation.get("proceed_after_discussion", []), "action-proceed", "🟢"),
                            render_action_list("Clarify before approval", recommendation.get("clarify_before_approval", []), "action-clarify", "🟠"),
                            render_action_list("Can wait until next service", recommendation.get("can_wait_until_next_service", []), "action-later", "⏳"),
                            render_action_list("Optional / consider skipping", recommendation.get("optional_or_consider_skipping", []), "action-optional", "🟣"),
                            render_action_list("Consider a second opinion", recommendation.get("second_opinion_before_approval", []), "action-clarify", "🔎"),
                        ]
                        action_cards = [card for card in action_cards if card]
                        if action_cards:
                            st.markdown(
                                '<div class="action-grid">' + "".join(action_cards) + "</div>",
                                unsafe_allow_html=True,
                            )

                        next_steps = recommendation.get("next_steps", [])
                        if next_steps:
                            st.markdown("#### What to do next")
                            for step_no, step in enumerate(next_steps[:5], 1):
                                st.markdown(f"**{step_no}.** {step}")

                        st.caption(
                            "These recommendations are decision support based on the information supplied. "
                            "They do not replace inspection or diagnosis by a qualified automotive professional."
                        )
                        st.divider()

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
                                  <strong>Recommended action:</strong>
                                  <p>{item.get("recommended_action", signal_label)}</p>
                                  <strong>Why:</strong>
                                  <p>{item.get("action_reason", "")}</p>
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
                            The quoted-total calculation uses only prices available in the submitted estimate or extracted job card.
                            It does not verify market prices, inspect the vehicle, diagnose faults, or replace
                            advice from a qualified automotive professional.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                except Exception as parse_exc:
                    st.error(
                        "The analysis was generated, but the response could not be structured correctly. "
                        "Please run the analysis again."
                    )
                    with st.expander("Technical details"):
                        st.code(str(parse_exc))

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

if st.session_state.get("feedback_available"):
    st.write("")
    st.markdown('<div class="section-kicker">Help us improve</div>', unsafe_allow_html=True)
    st.subheader("How useful was this analysis?")

    if st.session_state.get("feedback_submitted"):
        st.success("Thanks — your feedback has been saved.")
    else:
        with st.container(border=True):
            st.caption(
                "Your feedback is linked to the name and email entered for this MVP test. "
                "Please do not include registration numbers, VINs, phone numbers or other sensitive details in comments."
            )

            with st.form("feedback_form"):
                feedback_useful = st.radio(
                    "Was this analysis useful?",
                    ["Yes", "Somewhat", "No"],
                    horizontal=True,
                )
                feedback_decision_help = st.radio(
                    "Did it help you decide what to ask or clarify before approving the service?",
                    ["Yes", "Somewhat", "No"],
                    horizontal=True,
                )
                feedback_comment = st.text_area(
                    "Anything confusing or one improvement you would suggest? (optional)",
                    max_chars=500,
                    placeholder="Short feedback only — avoid registration number, VIN, phone number or other sensitive details.",
                )
                feedback_submit = st.form_submit_button(
                    "Submit feedback",
                    type="primary",
                    use_container_width=True,
                )

            if feedback_submit:
                try:
                    update_feedback_for_session(
                        st.session_state.session_id,
                        feedback_useful,
                        feedback_decision_help,
                        feedback_comment.strip(),
                    )
                    st.session_state.feedback_submitted = True
                    st.success("Thanks — your feedback has been saved.")
                except Exception as feedback_exc:
                    st.error("We could not save the feedback. Please try again.")
                    with st.expander("Feedback logging details"):
                        st.code(str(feedback_exc))

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
