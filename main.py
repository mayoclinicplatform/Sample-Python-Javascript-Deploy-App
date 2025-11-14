# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import aiohttp
import markdown2

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
headers = {"Content-Security-Policy": "frame-ancestors https://mcp-workflow-integration-container-og5rfrvg7q-uc.a.run.app https://mcp-wic-app-editor-new-og5rfrvg7q-uc.a.run.app https://vs-mcp-workflow-integration-container-og5rfrvg7q-uc.a.run.app *.mayo.edu *.epichosted.com *.mcp.org"}

INFERENCE_API_URL = "http://localhost:8000/inference"  # Replace with your actual URL

@app.get("/", response_class=HTMLResponse)
async def get_inference(request: Request):
    async with aiohttp.ClientSession() as session:
        async with session.get(INFERENCE_API_URL) as resp:
            if resp.status != 200:
                return HTMLResponse("Failed to fetch inference", status_code=500)

            markdown_text = await resp.text()
            html_content = markdown2.markdown(markdown_text, extras=["tables"])

    return templates.TemplateResponse("output.html", {
        "headers": headers,
        "request": request,
        "content": html_content
    })

# Add this to main.py temporarily
@app.get("/inference", response_class=HTMLResponse)
async def mock_inference():
    markdown_data = """
## 🏥 Patient Readmission Risk Report

<span class="risk-score">78%</span><span class="risk-label">High Risk</span>

---

### Model Inputs

| Feature                | Value                |
|------------------------|----------------------|
| **Age**                | 72                   |
| **Sex**                | Female               |
| **Primary Diagnosis**  | Congestive Heart Failure |
| **Comorbidities**      | Hypertension, CKD    |
| **Prior Admissions**   | 3 (past year)        |
| **Length of Stay**     | 6 days               |
| **Discharge Disposition** | Home with Services |
| **Recent Lab Abnormalities** | Elevated BNP, Low Sodium |

---

### Model Explanation

- **Top contributing factors:**  
  - Multiple prior admissions  
  - Congestive heart failure diagnosis  
  - Recent abnormal labs  
  - Advanced age

---

> *For clinical use only. Please review in context of full patient record.*
    """
    return HTMLResponse(content=markdown_data)

# Add an embedded page that listens for postMessage from a parent iframe
@app.get("/embedded", response_class=HTMLResponse)
async def embedded_listener(request: Request):
    # Render the embedded.html template which loads the JS from /static/embedded.js
    return templates.TemplateResponse("embedded.html", {"headers": headers, "request": request})
