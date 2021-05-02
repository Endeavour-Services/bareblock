import pathlib
import gnupg
import sys
import requests
import time

session = requests.session()

client_name = sys.argv[1]

path = pathlib.Path(f"/home/vscode/{client_name}")
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
while True:
    count += 1
    time.sleep(1)
    message = f"test_{count}"
    signed_message = gpg.encrypt(
        message, passphrase='test', always_trust=True, recipients=["node@dothttp.dev"])
    print(session.post("http://localhost:5000/message", json={
        "message": signed_message.data.decode('utf-8')
    }))
