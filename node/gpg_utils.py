
import pathlib
import gnupg


# path
# change permissions of this path
# reading this directory can leak private keys
path = pathlib.Path("/node")
# change it
# get it from oskeychain
passphrase = 'test'


if not path.exists():
    path.mkdir()


gpg = gnupg.GPG(gnupghome=path)

node_id = 'node@dothttp.dev'


allkeys = gpg.list_keys()
if len(allkeys) == 0:
    input_data = gpg.gen_key_input(
        name_email=node_id,
        passphrase=passphrase)

    key = gpg.gen_key(input_data)
    allkeys = gpg.list_keys()

node_keyid = allkeys[0]['keyid']
node_fingerprint = allkeys[0]['fingerprint']
