import streamlit as st

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
        st.success("Input received. AI analysis will be connected in the next development step.")
        st.subheader("Vehicle details")
        st.write(
            {
                "brand": brand or "Not provided",
                "model": model or "Not provided",
                "year": year,
                "mileage_km": mileage,
            }
        )
        st.subheader("Estimate submitted")
        st.code(estimate)
