import json
import traceback

from . import gpg_utils
from .block import generate_message, hashfunc
from .udp_utils import Client
import os
import random
import sys
import threading
from merklelib import MerkleTree
import time

BLOCK_PORT = 8080
TRANSACTION_PORT = 8081
SIGNATURE_DIR = '/export'
files = os.listdir(SIGNATURE_DIR)


def eprint(*args):
    print(*args, file=sys.stderr)


eprint(files)

all_recipents = []


def load():
    # load public keys of all nodes
    for filename in files:
        root_file_path = os.path.join(SIGNATURE_DIR, filename)
        if os.path.isfile(root_file_path):
            with open(root_file_path) as f:
                try:
                    key_data = f.read()
                    gpg_utils.gpg.import_keys(key_data)
                    eprint(f'were able to import {filename}')
                    all_recipents.append(
                        os.path.basename(filename).strip(".key"))
                except:
                    eprint(f'trouble loading {filename}')


load()
transaction_channel = Client(TRANSACTION_PORT)
recv_channel = Client(TRANSACTION_PORT)


class MessageHashFailed(Exception):
    def __init__(self, *args: object) -> None:
        eprint("message hash failed")
        super().__init__("rejected (transaction hash)")


class MerkleyHashFailedFailed(Exception):
    def __init__(self, *args: object) -> None:
        eprint("block merkley hash failed")
        super().__init__("rejected (integrity)")


def send_messages_randomly():
    rand = random.Random()
    while True:
        eprint('starting sending message')
        randomnode = rand.randint(0, 9)
        recipent = f"node{randomnode}@dothttp.dev"
        generated_message = generate_message(
            gpg_utils.node_id, recipent)
        crypt_obj = gpg_utils.gpg.encrypt(
            generated_message, always_trust=True, recipients=all_recipents)
        enc_message = crypt_obj.data
        transaction_channel.sendto(enc_message)
        time.sleep(10)


transaction_sender = threading.Thread(target=send_messages_randomly)
transaction_sender.start()
TRANSACTION_PACK_BLOCK_LIMIT = 2


def merkley_helper(transactions):
    return MerkleTree([json.dumps(tran) for tran in transactions], hashfunc)


class BlockHandler:
    def __init__(self) -> None:
        self.transactions = []

    def add_transaction(self, message):
        self.transactions.append(message)
        if len(self.transactions) == TRANSACTION_PACK_BLOCK_LIMIT:
            eprint(f"transactions met limit {TRANSACTION_PACK_BLOCK_LIMIT}")
            tree = merkley_helper(self.transactions)
            block = {
                'merkleRoot': tree.merkle_root,
                'transactions': self.transactions,
                'signature': gpg_utils.gpg.sign(tree.merkle_root).data.decode(),
                'type': 'block'
            }
            b_unencrypted = json.dumps(block)
            b_encrypted = gpg_utils.gpg.encrypt(
                b_unencrypted, always_trust=True, recipients=all_recipents)
            transaction_channel.sendto(b_encrypted.data)
            self.transactions = []


handler = BlockHandler()

while True:
    eprint("waiting for recive")
    # using select and different channels would  be better choice
    # for now going with same channel and type identifier
    recv, addr = recv_channel.recvfrom()
    try:
        decrypted = gpg_utils.gpg.decrypt(
            recv, passphrase=gpg_utils.passphrase).data
        if decrypted == b'':
            raise Exception("rejected (authenticity)")
        message = json.loads(decrypted)
        if (message['type'] == 'message'):
            # transaction validation to add into block
            hash_of_message = message['hash']
            transaction = message['transaction']
            if hashfunc(transaction.encode()) == hash_of_message:
                handler.add_transaction(message)
            else:
                raise MessageHashFailed()
        else:
            merkleRootHash = message['merkleRoot']
            generated_merkle_hash = merkley_helper(
                message['transactions'])
            if (merkleRootHash == generated_merkle_hash.merkle_root):
                eprint("block hash verified")

                # verify random trasaction of block
                random_transaction_int = random.randint(
                    0, len(message['transactions'])-1)
                random_transaction = message['transactions'][random_transaction_int]
                transaction_encoded_to_verify = json.dumps(
                    random_transaction).encode()
                proof = generated_merkle_hash.get_proof(
                    transaction_encoded_to_verify)
                if generated_merkle_hash.verify_leaf_inclusion(transaction_encoded_to_verify, proof):
                    eprint('transaction verified')
                else:
                    eprint("transaction failed")
            else:
                raise MerkleyHashFailedFailed()
    except Exception as e:
        eprint(f"message from {addr} loading into block failed with error {e}")
        traceback.print_exc()
