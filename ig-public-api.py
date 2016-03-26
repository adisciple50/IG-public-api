import requests
import json
import base64

urlRoot = "https://demo-api.ig.com/gateway/deal"


def login(api_key: str, username: str, password: str):
    # Get username and password from user interface fields

    if not api_key:
        print("Api Key Missing")
        return False

    if not username:
        print("Username Missing")
        return False

    if not password:
        print("Password Missing")
        return False

    password = base64.b64encode(password)  # encrytion method is currently unknown.
    print("Encrypted password " + password)

    # Create a login request, ie a POST request to /session
    method = "POST"
    url = urlRoot + "/session"

    # Set up standard request headers, i.e. the api key, the request content type (JSON),
    # and the expected response content type (JSON)
    headers = {
      "Content-Type": "application/json; charset=UTF-8",
      "Accept": "application/json; charset=UTF-8",
      "X-IG-API-KEY": api_key,
      "Version": "2"
    }

    # Set up the request body with the user username (username) and password
    body_params = {"identifier": username, 'password': password, "encryptedPassword": True}

    # Send the request via a (Javascript AJAX call) ... nope this is python. we use a request call.
    try:
        req = requests.request(method, url, headers=headers, data=body_params)

        if req.status_code == 200:
            response = json.loads(req.json())
            account_token = req.headers["X-SECURITY-TOKEN"]
            print("X-SECURITY-TOKEN: " + account_token)
            client_token = req.headers["CST"]
            print("CST: " + client_token)
            account_id = response['currentAccountId']
            ls_endpoint = response['lightstreamerEndpoint']
            print("Logged in as " + account_id)
    finally:
        return {'account_token': account_token, 'client_token': client_token, 'accountId': account_id, 'lsEndpoint': ls_endpoint}