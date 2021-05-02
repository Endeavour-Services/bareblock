import pathlib

import flask
import json
import gnupg
from flask import jsonify, request
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import hashlib


queue = queue.LifoQueue(5)


executor = ThreadPoolExecutor(8)
counter = 0


readlock = threading.Lock()
writelock = threading.Lock()


class wierdlist():

    def __init__(self) -> None:
        self.blocks = []
        self.block_map = {}

        self.last_hash = empty_hash

    def add(self, value, hash):
        readlock.acquire()
        self.blocks.append({hash: hash, value: value})
        self.block_map[hash] = value
        self.last_hash = hash
        readlock.release()

    def all_blocks(self):
        return list(self.block_map.keys())


def get_hash(data):
    if type(data) != bytes:
        # wierd hack
        # be warned
        data = data.encode('utf-8')
    gfg = hashlib.sha3_256()
    gfg.update(data)
    return gfg.hexdigest()


empty_hash = get_hash('')
blocks = wierdlist()

path = pathlib.Path("/home/vscode/node")
if not path.exists():
    path.mkdir()


gpg = gnupg.GPG(gnupghome=path)


allkeys = gpg.list_keys()
if len(allkeys) == 0:
    input_data = gpg.gen_key_input(
        name_email='node@dothttp.dev',
        passphrase='test')

    key = gpg.gen_key(input_data)

node_keyid = allkeys[0]['keyid']
node_fingerprint = allkeys[0]['fingerprint']

app = flask.Flask(__name__)


def create_block():
    messages = []
    while not queue.empty():
        message = queue.get()
        messages.append(message['message'])
    block = json.dumps(dict(message=messages, prev_hash=blocks.last_hash))
    block_hash = get_hash(block)
    blocks.add(block, block_hash)
    queue.all_tasks_done()
    print('hi')


@app.route('/list', methods=['GET'])
def list_blocks():
    return jsonify(blocks.all_blocks())


@app.route('/pick/<pick>', methods=['GET'])
def get_block(pick):
    return jsonify(blocks.block_map[pick])


@app.route('/message', methods=['POST'])
def recieve_message():
    body = request.get_json()
    try:
        message: str = body.get("message", "")
        decrypted = gpg.decrypt(message, passphrase="test")
        if decrypted:
            if queue.full():
                executor.submit(create_block)
                # queue.join()
            queue.put({"decrypted": decrypted, "message": message})
            return jsonify({'message': 'valid'})
        response = jsonify({"message": "invalid pgp key"})
        response.status_code = 400
        return response
    except:
        pass
    response = jsonify({"message": "invalid pgp key"})
    response.status_code = 400
    return response


@app.route('/register', methods=['POST'])
def register():
    body = request.get_json()
    try:
        pgp_key: str = body.get("pgp", "")
        if pgp_key.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----") and pgp_key.endswith("-----END PGP PUBLIC KEY BLOCK-----\n"):
            imp_result = gpg.import_keys(pgp_key)
            ascii_armored_public_keys = gpg.export_keys(node_fingerprint)
            return jsonify({"message": "imported_successfully", 'public_key': ascii_armored_public_keys})
        response = jsonify({"message": "invalid pgp key"})
        response.status_code = 400
        return response
    except:
        pass
    response = jsonify({"message": "invalid pgp key"})
    response.status_code = 400
    return response


if __name__ == "__main__":
    app.run(debug=True)
