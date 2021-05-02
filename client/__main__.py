import json
import pathlib
import gnupg
import sys
import requests
import time

session = requests.session()

client_name = sys.argv[1]

# change it
passphrase = 'test'

server_url = "http://localhost:5000/"

node_id = "node@dothttp.dev"
path = pathlib.Path(f"/node/{client_name}", parents=True)
if not path.exists():
    path.mkdir()

gpg = gnupg.GPG(gnupghome=path)


if len(gpg.list_keys()) == 0:
    input_data = gpg.gen_key_input(
        name_email=f'{client_name}@dothttp.dev',
        passphrase='test')
    key = gpg.gen_key(input_data)

    fingerprint = gpg.list_keys()[0]['fingerprint']

    ascii_armored_public_keys = gpg.export_keys(fingerprint)
    regi_resp = session.post("http://localhost:5000/register", json={
        "pgp": ascii_armored_public_keys
    })
    public_key = regi_resp.json()['public_key']
    gpg.import_keys(public_key)


count = 0
for i in range(100):
    count += 1
    time.sleep(1)
    input_message = {
        "message": {
            "message": f"test_{client_name}_{count}"
        }
    }
    message = json.dumps(input_message)
    signed_message = gpg.encrypt(
        message, passphrase=passphrase, always_trust=True, recipients=[node_id])
    resp = session.post(f"{server_url}/message", json={
        "message": signed_message.data.decode('utf-8')
    })
    print(input_message, resp.text)
