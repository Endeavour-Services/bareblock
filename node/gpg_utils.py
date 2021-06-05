import pathlib
import ed25519
from ed25519.keys import SigningKey
import gnupg
import os
name = 'node' + os.environ['NAME']

path = pathlib.Path("/node")
passphrase = 'test'


if not path.exists():
    path.mkdir()


gpg = gnupg.GPG(gnupghome=path)

node_id = f'{name}@dothttp.dev'


allkeys = gpg.list_keys()
if len(allkeys) == 0:
    input_data = gpg.gen_key_input(
        name_email=node_id,
        passphrase=passphrase)

    key = gpg.gen_key(input_data)
    allkeys = gpg.list_keys()
    node_keyid = allkeys[0]['keyid']
    node_fingerprint = allkeys[0]['fingerprint']
    ascii_armored_public_keys = gpg.export_keys(node_fingerprint)
    os.mkdir('/signatures')
    with open(f'/signatures/{node_id}.key', 'w') as f:
        f.write(ascii_armored_public_keys)
    private_key_ed255, public_key_ed255 = ed25519.create_keypair()
    with open(f'/signatures/{node_id}_public.ed25519', 'wb') as f:
        f.write(public_key_ed255.to_bytes())
    os.mkdir("/node_private")
    with open(f'/node_private/{node_id}_private.ed25519', 'wb') as f:
        f.write(private_key_ed255.to_bytes())

node_keyid = allkeys[0]['keyid']
node_fingerprint = allkeys[0]['fingerprint']
existing_private_ed255_key = os.listdir('/node_private/')[0]
with open(os.path.join('/node_private/', existing_private_ed255_key), 'rb') as f:
    private_key_ed255 = SigningKey(f.read())
