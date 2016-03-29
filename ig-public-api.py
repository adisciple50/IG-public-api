import requests
import json
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
import base64
urlRoot = "https://demo-api.ig.com/gateway/deal"

# TODO - Test Login

def encryptionKey(api_key):

    # Set up the request as a GET request to the address /session/encryptionkey
    req = requests.get(urlRoot + "/session/encryptionKey",headers={
        "X-IG-API-KEY": api_key,
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json; charset=UTF-8"
    })

    if req.status_code == 200:
        print("Encryption key retrieved ")
        return json.loads(req)# req contains the key in json format ... this returns a python dict
    else:
        return False

def encryptedPassword(password,api_key):

    key = encryptionKey(api_key)
    decodedKey = base64.decode(key['encryptionKey']) # DER key for rsa folk

    seq = asn1.DerSequence()
    seq.decode(decodedKey)
    keyPub = RSA.construct( (seq[0], seq[1]) )

    #  roughly translated from
    '''
    asn = pidCrypt.ASN1.decode(pidCryptUtil.toByteArray(decodedKey))
    tree = asn.toHexTree()

    rsa.setPublicKeyFromASN(tree)

    return pidCryptUtil.encodeBase64(pidCryptUtil.convertFromHex(rsa.encrypt(password += '|' + key.timeStamp)))
    '''

    return base64(str(bytearray.fromhex(keyPub.encrypt(password + '|' + key['timestamp'])))) # assumed converting from hex to string



""""
 * Encryption key getter function
"""



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

    password = encryptedPassword(password,api_key)  # encrytion method is currently unknown.
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

    return {'account_token': account_token, 'client_token': client_token, 'accountId': account_id, 'lsEndpoint': ls_endpoint}


# TODO