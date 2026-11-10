import streamlit as st
from google import genai

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

div[data-testid="stFormSubmitButton"]>button{
  border-radius:12px!important;min-height:3rem!important;font-weight:750!important;
  background:linear-gradient(135deg,var(--primary),var(--primary2))!important;
  color:#fff!important;border:none!important;box-shadow:0 8px 20px rgba(37,99,235,.20)
}
div[data-testid="stFormSubmitButton"]>button:hover{filter:brightness(.96);color:#fff!important}

.result-banner{background:var(--success-bg);border:1px solid var(--success-border);border-radius:18px;padding:1rem 1.15rem;color:var(--success-text);margin-top:1.1rem;margin-bottom:1rem;font-weight:650}
.disclaimer{background:var(--warning-bg);border:1px solid var(--warning-border);border-radius:16px;padding:.9rem 1rem;color:var(--warning-text);font-size:.9rem;line-height:1.5}

@media(max-width:768px){
  .hero{padding:1.5rem 1.25rem;border-radius:18px}
  .block-container{padding-top:1rem}
}
</style>
    """,
    unsafe_allow_html=True,
)

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
    st.caption("Only basic context is needed for this MVP.")

    with st.form("estimate_form"):
        col1, col2 = st.columns(2)

        with col1:
            brand = st.text_input("Car brand", placeholder="e.g. Tata")
            model = st.text_input("Car model", placeholder="e.g. Harrier")

        with col2:
            year = st.number_input("Model year", min_value=1990, max_value=2030, value=2022)
            mileage = st.number_input("Mileage (km)", min_value=0, step=1000)

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
            "✨ Explain My Estimate",
            type="primary",
            use_container_width=True,
        )

st.caption(
    "Tip: better input gives better guidance. Include the exact line items and quoted prices where available."
)

if submitted:
    if not estimate.strip():
        st.warning("Please paste at least one service estimate item.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
            client = genai.Client(api_key=api_key)

            prompt = f"""
You are an automotive service estimate explanation assistant for private car owners.

Use ONLY the user-provided facts below as vehicle facts. Copy them exactly and do not round, alter, infer, or substitute any value.

Vehicle details:
- Brand: {brand or "Not provided"}
- Model: {model or "Not provided"}
- Model year: {year}
- Mileage: {mileage} km

Service estimate / job-card text:
{estimate}

Your job is to help the customer understand the estimate and prepare better questions for the service advisor. You are NOT diagnosing the vehicle and you do NOT have access to manufacturer service schedules, inspection data, service history, diagnostic reports, measurements, or live market pricing unless explicitly included in the user's text.

For each service item, provide:
1. What it means — plain-language explanation
2. Why it may have been recommended — use conditional language such as "may" or "could"
3. Urgency — choose only:
   - High if the user-provided estimate itself contains clear evidence of an immediate safety/operability issue
   - Medium if attention may reasonably be needed but the estimate does not prove immediate urgency
   - Low if it appears non-urgent from the supplied information
   - Cannot determine from estimate alone whenever inspection evidence is required
4. What could happen if delayed — describe possibilities, not certainties
5. Evidence to ask for — measurements, photos, diagnostic reports, worn-part inspection, manufacturer schedule, etc.
6. One or two specific questions to ask the service advisor

Then provide a short section called "Before You Approve" with the most important clarifications the customer should get.

Strict guardrails:
- Preserve every user-entered fact exactly, especially mileage, year, brand, model, item names, and quoted prices.
- Never claim an item is part of the manufacturer's official service schedule unless that schedule was supplied in the input.
- Never claim that a component is "always" replaced with another component.
- Never invent measurements, inspection findings, diagnostic codes, manufacturer requirements, prices, service history, symptoms, or age-related conclusions.
- Do not state that a repair is definitely necessary or unnecessary unless the supplied estimate itself proves it.
- If necessity or urgency depends on inspection evidence, say "Cannot determine from estimate alone."
- Avoid unsupported generalisations such as fixed battery life, exact replacement intervals, or claims that skipping a treatment is harmless.
- Encourage professional inspection where appropriate.
- Keep the response concise, practical, and decision-oriented.
"""

            response = None
            last_error = None
            models_to_try = [
                "gemini-3.8-flash",
                "gemini-3.6-flash",
                "gemini-3.5-flash-lite",
            ]

            with st.spinner("Analysing your service estimate..."):
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
                st.markdown(
                    '<div class="result-banner">✓ Estimate explained successfully. Review the guidance below before speaking with your service advisor.</div>',
                    unsafe_allow_html=True,
                )

                st.markdown('<div class="section-kicker">Your explanation</div>', unsafe_allow_html=True)
                st.subheader("AI-assisted estimate review")

                with st.container(border=True):
                    st.markdown(response.text)

                st.write("")
                st.markdown(
                    """
                    <div class="disclaimer">
                        <strong>Important:</strong> This tool provides decision support only.
                        It does not inspect your vehicle, make a mechanical diagnosis, or replace advice
                        from a qualified automotive professional.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
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
