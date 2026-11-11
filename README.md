# Car Service Estimate Explainer

**Clarity before approval**

A Streamlit + GenAI MVP built for the IIM Visakhapatnam Executive MBA **Digital Product Management** course project.

The product helps an individual car owner review a workshop service estimate or job card and decide:

- what may need prompt attention;
- what can proceed after discussion;
- what needs evidence or clarification before approval;
- what may reasonably wait until a later service;
- what may be an optional add-on; and
- when a second opinion may be useful.

> **Decision support, not diagnosis.** The app does not inspect the vehicle, verify market prices, or replace advice from a qualified automotive professional.

---

## MVP scope

**Target user:** Individual/private car owner who participates in service or repair approval decisions.

**Primary use case:** Review a service estimate before approving workshop-recommended work.

**Core workflow:**

1. Select vehicle type, manufacturer, model and vehicle context.
2. Add current symptoms/issues, if any.
3. Provide the service estimate using one of three methods:
   - Enter service estimate / job-card text
   - Build the estimate manually from service items
   - Upload a JPG/JPEG/PNG job-card photo
4. Run the GenAI analysis.
5. Review the decision recommendation:
   - Address now / highest priority
   - Proceed after discussion
   - Clarify before approval
   - Can wait until next service
   - Optional / consider skipping
   - Consider a second opinion
6. Review item-level evidence, urgency, risk and questions to ask the service advisor.
7. Submit optional MVP feedback.

---

## Key product capabilities

- India-focused **Vehicle type → Manufacturer → Model** cascading selection
- Vehicle context including model year, fuel type, odometer reading, warranty and service-centre type
- Categorised current issues across:
  - Brakes & suspension
  - Electrical & AC
  - Body & exterior
  - Engine & drivetrain
- Three estimate-input methods:
  - Text entry
  - Manual workshop job-card builder with recommended work, quoted cost and advisor notes
  - Job-card image upload
- Structured AI output for each service item:
  - Plain-language explanation
  - Why it may have been recommended
  - Evidence status
  - Approval readiness
  - Urgency
  - Delay risk
  - Evidence to request
  - Question to ask
  - Recommended action and reason
- Red / amber / green decision signals
- Overall customer decision and prioritised next steps
- Optional Google Sheets usage and feedback logging

---

## AI guardrails

The AI is instructed to:

- use only the vehicle and estimate information supplied by the user;
- preserve quoted service-item names and prices where available;
- avoid inventing inspection results, symptoms, measurements or service history;
- avoid claiming a quoted price is fair, cheap or expensive without verified pricing data;
- avoid remote mechanical diagnosis;
- request evidence when necessity depends on inspection or measurement;
- treat high-priority recommendations as a prompt to seek professional attention or clarification, not as a confirmed diagnosis;
- mark unreadable image content as unclear rather than guessing.

---

# Run locally

The repository can be used as a **local fallback** if the deployed Streamlit app is unavailable.

## Prerequisites

- Python **3.10+** recommended
- Internet connection for Gemini API access
- A Google Gemini API key
- Git (optional, if cloning the repository)

---

## 1. Get the project

Clone the repository:

```bash
git clone https://github.com/vidyutbiswas/car-service-estimate-explainer.git
cd car-service-estimate-explainer
```

Or download the repository ZIP from GitHub and extract it.

---

## 2. Create a virtual environment

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

---

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Current dependencies include:

- Streamlit
- Google GenAI SDK
- gspread
- google-auth

---

## 4. Configure Streamlit secrets

Create this file in the project root:

```text
.streamlit/secrets.toml
```

### Minimum configuration — enough to run the AI analysis

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

With only the Gemini key, the core estimate analysis works locally.

Google Sheets logging will not be available, so the app may display a logging warning after analysis. This does not prevent the AI result from being generated.

> **Never commit `.streamlit/secrets.toml` or any real API/service-account credential to GitHub.**

---

## 5. Optional: enable Google Sheets usage and feedback logging

The deployed MVP logs usage/feedback to a Google Sheet using a Google Cloud service account.

Add the following structure to `.streamlit/secrets.toml` **only if you need logging in the local fallback**:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"

[connections.gsheets]
spreadsheet = "YOUR_GOOGLE_SHEET_URL"
worksheet = "Sheet1"

[connections.gsheets.credentials]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY
-----END PRIVATE KEY-----
"""
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CLIENT_CERT_URL"
```

The target Google Sheet must be shared with the service account email with appropriate access.

Do **not** paste real service-account credentials into the repository, README, screenshots or presentation.

---

## 6. Start the app

From the repository root:

```bash
streamlit run app.py
```

If the `streamlit` command is not found, use:

```bash
python -m streamlit run app.py
```

Streamlit normally opens the app automatically in the default browser. If it does not, open the **Local URL** shown in the terminal, typically:

```text
http://localhost:8501
```

---

## Quick local-fallback checklist

Before a presentation/evaluation:

- [ ] Python environment activates successfully
- [ ] `pip install -r requirements.txt` completes
- [ ] `.streamlit/secrets.toml` contains a valid `GEMINI_API_KEY`
- [ ] `streamlit run app.py` starts without import errors
- [ ] Browser opens the local Streamlit page
- [ ] Vehicle dropdowns work correctly
- [ ] Text estimate analysis works
- [ ] Manual workshop job-card builder works without repeating the owner's symptom selection
- [ ] Job-card image upload works
- [ ] Decision / Recommended Next Steps section appears
- [ ] Item-level analysis expands correctly
- [ ] Google Sheets logging works if logging credentials were configured

---

## Troubleshooting

### `GEMINI_API_KEY` is not configured

Check that the following file exists:

```text
.streamlit/secrets.toml
```

and contains:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

Restart Streamlit after changing secrets.

### Google Sheets logging warning

The AI analysis can still run with only the Gemini API key.

If you need logging, confirm:

- the `[connections.gsheets]` settings exist;
- the service-account fields are valid;
- the Google Sheet URL is correct;
- the worksheet exists; and
- the sheet is shared with the service-account email.

### Streamlit command not found

Use:

```bash
python -m streamlit run app.py
```

### Port 8501 is already in use

Run on another port:

```bash
streamlit run app.py --server.port 8502
```

### Uploaded job-card image is not analysed clearly

Use a well-lit, readable JPG/JPEG/PNG image. The app is instructed not to guess unreadable text.

---

## Privacy and limitations

For this course MVP:

- Users should avoid entering unnecessary personal information such as registration number, VIN or phone number.
- Name and email are collected for MVP evaluation when the feedback/logging flow is used.
- Name/email are not intentionally included in the Gemini analysis prompt.
- Vehicle context and estimate/job-card content are sent to the AI service for analysis.
- The application does not inspect the vehicle.
- The application does not provide verified live market-price benchmarking.
- The application does not recommend nearby garages in the current MVP.
- Nearby garage/service-centre maps, verified price benchmarking, authorised-vs-local estimate comparison and service-history features are part of the future backlog.

---

## Future roadmap / backlog

Potential future iterations include:

- verified authorised-service-centre vs local-garage estimate benchmarks;
- verified parts/labour price ranges;
- nearby garage and authorised-service-centre map;
- verified workshop information and ratings;
- OEM service-schedule integration;
- saved vehicle and service history;
- comparison of multiple estimates;
- second-opinion network / marketplace;
- user accounts and service reminders.

These are intentionally outside the current MVP so the product remains focused on one primary use case: **helping a car owner make a better approval decision from an existing service estimate.**

---

## Technology

- **Frontend / application:** Streamlit
- **Language:** Python
- **GenAI:** Google Gemini via `google-genai`
- **Usage / feedback logging:** Google Sheets via `gspread` and Google service-account authentication
- **Source control:** GitHub

---

## Academic project context

This MVP demonstrates the evolution from customer discovery to implementation of one minimum viable AI capability for the Digital Product Management course.

The product is intentionally designed around:

- one target user segment;
- one customer problem;
- one primary use case;
- one integrated workflow; and
- one AI capability centred on service-estimate decision support.

AI tools were used during prototyping/coding in accordance with the project workflow. The project team remains responsible for reviewing, testing and explaining the implemented product, its assumptions and limitations.

---

## Disclaimer

**Car Service Estimate Explainer provides informational decision support only.**

It does not diagnose vehicle faults, verify workshop findings, guarantee that a repair is necessary or unnecessary, or replace inspection/advice from a qualified automotive professional.
