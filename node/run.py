import json
from operator import add
import traceback
from . import gpg_utils
from .block import generate_message, hashfunc
from .udp_utils import Client
import os
import random
import threading
from merklelib import MerkleTree, beautify
import time

BLOCK_PORT = 8080
TRANSACTION_PORT = 8081
files = os.listdir('/export')

all_recipents = []


def load():
    # load public keys of all nodes
    for filename in files:
        if os.path.isfile(filename):
            with open(filename) as f:
                try:
                    key_data = f.read()
                    gpg_utils.gpg.import_keys(key_data)
                    print(f'were able to import {filename}')
                    all_recipents.append(os.path.basename(filename))
                except:
                    print(f'trouble loading {filename}')


load()
transaction_channel = Client(TRANSACTION_PORT)


class MessageHashFailed(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("message hash failed")


def send_messages_randomly():
    rand = random.Random()
    while True:
        time.sleep(10)
        print()
        randomnode = rand.randint(0, 9)
        recipent = f"node{randomnode}@dothttp.dev"
        encrypted_message = gpg_utils.gpg.encrypt(generate_message(
            gpg_utils.node_id, recipent), recipients=all_recipents)
        transaction_channel.sendto(encrypted_message)


transaction_sender = threading.Thread(target=send_messages_randomly)
transaction_sender.run()


class BlockHandler:
    def __init__(self) -> None:
        self.transactions = []

    def add_transaction(self, message):
        self.transactions.append(message)
        if len(self.transactions) == 15:
            tree = MerkleTree(self.transactions, hashfunc)
            block = {
                'merkleRoot': tree.merkle_root,
                'transactions': self.transactions,
                'signature': gpg_utils.gpg.sign(tree.merkle_root)
            }
            b_unencrypted = json.dumps(block)
            b_encrypted = gpg_utils.gpg.encrypt(
                b_unencrypted, recipients=all_recipents)
            transaction_channel.sendto(b_encrypted)
            self.transactions = []


handler = BlockHandler()

while True:
    recv, addr = transaction_channel.recvfrom()
    try:
        decrypted = gpg_utils.gpg.decrypt(
            recv, passphrase=gpg_utils.passphrase).data
        message = json.loads(decrypted)
        hash_of_message = message['hash']
        transaction = message['transaction']
        if hashfunc(transaction) == hash_of_message:
            handler.add_transaction(message)
        else:
            raise MessageHashFailed()
    except Exception as e:
        print(f"message from {addr} loading into block failed with error {e}")
        traceback.print_exc()
