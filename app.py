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

Vehicle details:
- Brand: {brand or "Not provided"}
- Model: {model or "Not provided"}
- Model year: {year}
- Mileage: {mileage} km

Service estimate / job-card text:
{estimate}

Explain the estimate in clear, non-technical language.

For each service item, provide:
1. What it means
2. Why it may have been recommended
3. Urgency: High / Medium / Low / Cannot determine from estimate alone
4. What could happen if it is delayed
5. Evidence the customer should ask the service centre to show
6. One or two questions the customer should ask the service advisor

Then provide a short section called "Before You Approve" summarizing the most important clarifications the customer should get.

Important guardrails:
- Do not diagnose the vehicle remotely.
- Do not state that a repair is definitely necessary or unnecessary unless the estimate itself proves it.
- Do not invent measurements, inspection findings, manufacturer requirements, prices, or service history.
- Clearly say when the estimate alone is insufficient to judge necessity or urgency.
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
