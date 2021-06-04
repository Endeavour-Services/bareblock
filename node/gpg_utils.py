import pathlib
import ed25519
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

node_keyid = allkeys[0]['keyid']
node_fingerprint = allkeys[0]['fingerprint']

# Generating ed25519 key pairs and storing inside signatures directory
privKey, pubKey = ed25519.create_keypair()
# os.mkdir('/signatures')
# with open(f'/signatures/{node_id}_ed25519_pub.key', 'w') as f:
#     f.write(pubKey)