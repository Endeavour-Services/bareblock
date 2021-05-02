import json
import queue
from concurrent.futures import ThreadPoolExecutor

import flask
from flask import Response, jsonify, request
from jsonschema import validate

from node.gpg_utils import *
from node.schema import property_schema
from node.utils import BlockList, get_hash

# currently its using inmemory, can be changed it to pg or mysql
# when going to scale, queue should be externalized and should be run gunicorn/uwsgi
queue = queue.Queue(5)


executor = ThreadPoolExecutor(8)
counter = 0

blocks = BlockList()

app = flask.Flask(__name__)


def create_block():
    messages = []
    while not queue.empty():
        message = queue.get()
        # you may just want to send decrypted
        # TODO
        messages.append(message)
    block = json.dumps(dict(message=messages, prev_hash=blocks.last_hash))
    block_hash = get_hash(block)
    signed_hash = gpg.sign(block_hash, keyid=node_keyid)
    blocks.add(block, block_hash, signed_hash.data.decode('utf-8'))
    queue.all_tasks_done()


def invalid_input(message):
    resp = jsonify(message=message)
    resp.status_code = 400
    return resp


def invalid_error(message):
    resp = jsonify(message=message)
    resp.status_code = 500
    return resp


@app.route('/message', methods=['POST'])
def recieve_message():
    body = request.get_json()
    try:
        message: str = body.get("message", {})
        decrypted = json.loads(gpg.decrypt(
            message, passphrase=passphrase).data)
        if type(decrypted) != dict:
            return invalid_input('invalid message, message has to json')
        try:
            validate(instance=decrypted, schema=property_schema)
        except:
            return invalid_input('invalid message schema')
        if decrypted:
            if queue.full():
                executor.submit(create_block)
                # queue.join()
            queue.put({"decrypted": decrypted, "message": message})
            return jsonify({'message': 'valid'})
        return invalid_input("invalid pgp key")
    except:
        pass
    return invalid_error('unknown error')


@app.route('/register', methods=['POST'])
def register():
    body = request.get_json()
    try:
        pgp_key: str = body.get("pgp", "")
        if pgp_key.startswith("-----BEGIN PGP PUBLIC KEY BLOCK-----") and pgp_key.endswith("-----END PGP PUBLIC KEY BLOCK-----\n"):
            gpg.import_keys(pgp_key)
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


@app.route('/block/count', methods=['GET'])
def count_blocks():
    return str(len(blocks.blocks))


@app.route('/block/index/<int:index>', methods=['GET'])
def get_by_index(index):
    if len(blocks.blocks) > index:
        return jsonify(blocks.blocks[index])
    return invalid_input('invalid index')


@app.route('/block/latest/', methods=['GET'])
def get_latest_block():
    return blocks.last_hash


@app.route('/block/previous/<hash>', methods=['GET'])
def get_previous_block(hash):
    if hash in blocks.block_map:
        block = blocks.block_map[hash]
        prev_hash = block['prev_hash']
        if prev_hash in blocks.block_map:
            return jsonify(blocks.block_map[prev_hash])
        return invalid_input('first block woudn\'t have prev block')
    return invalid_input('invalid hash')


@app.route('/block/list', methods=['GET'])
def list_blocks():
    return jsonify(blocks.all_blocks())


@app.route('/block/<pick>', methods=['GET'])
def get_block(pick):
    if pick in blocks.block_map:
        return blocks.block_map[pick]
    return invalid_input("invalid hash")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
