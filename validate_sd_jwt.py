import http.client
import json

# Replace these with values from your integration
MAYO_PROVIDED_SECRET_TOKEN = "REPLACE_WITH_YOUR_SECRET"
SD_JWT = "REPLACE_WITH_YOUR_SD_JWT"

conn = http.client.HTTPSConnection("catswebapi.mcp.org")

payload = f"token={SD_JWT}"

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Bearer {MAYO_PROVIDED_SECRET_TOKEN}",
}

try:
    conn.request("POST", "/api/v1/token/introspect", payload, headers)
    res = conn.getresponse()

    status = res.status
    body = res.read().decode("utf-8")

    if status == 401:
        print("Error: received 401 Unauthorized. The MAYO_PROVIDED_SECRET_TOKEN is likely wrong.")
    elif status == 200:
        try:
            response_json = json.loads(body)
        except json.JSONDecodeError:
            print(f"Error: could not decode JSON response from introspection endpoint: {body}")
        else:
            active = response_json.get("active")
            if active is True:
                print("Success: introspection succeeded and the token is legitimate.")
                print(json.dumps(response_json, indent=2))
            elif active is False:
                print("Error: introspection returned active=false. The token is invalid or has expired.")
                print(json.dumps(response_json, indent=2))
            else:
                print(f"Warning: introspection response did not include a clear 'active' value: {response_json}")
    else:
        print(f"Unexpected HTTP status {status} returned from introspection endpoint.")
        print(body)
except Exception as exc:
    print(f"Unspecified error while validating the token: {exc}")
