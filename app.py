import streamlit as st
from google import genai

st.set_page_config(
    page_title="Car Service Estimate Explainer",
    page_icon="🚗",
    layout="wide",
)

st.title("🚗 Car Service Estimate Explainer")
st.caption("Clarity before approval")

st.info(
    "This MVP helps car owners understand a service estimate before discussing it "
    "with a service advisor. It does not replace professional mechanical diagnosis."
)

with st.form("estimate_form"):
    col1, col2 = st.columns(2)

    with col1:
        brand = st.text_input("Car brand", placeholder="e.g. Tata")
        model = st.text_input("Car model", placeholder="e.g. Harrier")

    with col2:
        year = st.number_input("Model year", min_value=1990, max_value=2030, value=2022)
        mileage = st.number_input("Mileage (km)", min_value=0, step=1000)

    estimate = st.text_area(
        "Paste the service estimate / job-card items",
        height=220,
        placeholder="Example:\nBrake pads replacement - ₹6,500\nWheel alignment - ₹1,200",
    )

    submitted = st.form_submit_button("Explain My Estimate", type="primary")

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
                st.success("Estimate explained successfully.")
                st.subheader("AI-assisted estimate explanation")
                st.markdown(response.text)

                st.divider()
                st.caption(
                    "This output is for decision support only and does not replace inspection "
                    "or advice from a qualified automotive professional."
                )
            else:
                st.error("The AI service is temporarily unavailable. Please try again.")
                if last_error:
                    st.code(str(last_error))

        except KeyError:
            st.error("Gemini API key is not configured in Streamlit Secrets.")
        except Exception as exc:
            st.error("The AI service could not complete the analysis.")
            st.code(str(exc))
