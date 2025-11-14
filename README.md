# Project: Embedded PostMessage + FHIR Gateway Example

Quick instructions to build, run, and access the embedded listener page.

Prerequisites
- Python 3.8+
- Git (optional)
- Windows / macOS / Linux command line

Install (recommended inside a virtual environment)
```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
# or: source .venv/bin/activate  # macOS / Linux
pip install --upgrade pip
pip install fastapi uvicorn aiohttp markdown2 jinja2
```

Run the app (development)
```bash

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open the embedded page
- In a browser, visit: http://localhost:8000/embedded
- The page is intended to be loaded inside an iframe; it listens for a postMessage from the parent window.

Example postMessage (from parent frame)
1. Suppose you have an iframe element that points to the embedded page:
```html
<iframe id="embeddedFrame" src="http://localhost:8000/embedded"></iframe>
```
2. From the parent window's JavaScript console you can send the JSON payload (replace values as needed):
```javascript
const payload = {
  "fhirPatient": "patient-123",
  "patientFirstName": "Jane",
  "patientLastName": "Doe",
  "encounterUniqueId": "enc-456",
  "userName": "jdoe",
  "userFullName": "Jane Doe",
  "userFirstName": "Jane",
  "userLastName": "Doe",
  "encounterDate": "2025-11-01T10:00:00Z",
  "parentFrameUrl": "https://your-parent.example",
  "gatewayUrl": "https://wic-sandbox.dev.app-nonprod.mcp.org",
  "sdJwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "emr": "ExampleEMR"
};

const iframe = document.getElementById('embeddedFrame');
iframe.contentWindow.postMessage(JSON.stringify(payload), '*');
```

Notes
- The embedded page will:
  - Display "Welcome, {firstName} {lastName}" using patient or user name fields.
  - Show the received payload.
  - Perform an async FHIR GET against `{gatewayUrl}/Patient/{fhirPatient}` using `Authorization: Bearer {sdJwt}` (if provided) and display the returned JSON.
- If your gateway uses a different path for the patient resource, update `static/embedded.js` accordingly.
- The app includes a header variable for Content-Security-Policy in `main.py`. THis is the current CSP for Mayo Clinic Platform deployment launches. If your environment requires additional origins, update the CSP list there.
- For production, secure the postMessage origin checks and do not use `'*'` for targetOrigin when posting sensitive data.

Troubleshooting
- If the FHIR call fails, check browser console for CORS / network errors and ensure the gateway accepts the sdJwt header.
- Ensure the app is reachable from the parent frame origin when embedding in another domain (CSP and network/firewall).
