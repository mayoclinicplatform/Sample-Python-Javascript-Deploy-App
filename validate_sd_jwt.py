import http.client

# Replace these with values from your integration
MAYO_PROVIDED_SECRET_TOKEN = "REPLACE_WITH_YOUR_SECRET"
SD_JWT = "REPLACE_WITH_YOUR_SD_JWT"

conn = http.client.HTTPSConnection("catswebapi.mcp.org")

payload = f"token={SD_JWT}"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Bearer {MAYO_PROVIDED_SECRET_TOKEN}",
}

conn.request("POST", "/api/v1/token/introspect", payload, headers)

res = conn.getresponse()

data = res.read()

print(data.decode("utf-8"))
