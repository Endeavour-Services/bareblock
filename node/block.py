import json
import random
import time
import uuid
from . import gpg_utils
from .constants import *

from .utils import hashfunc, merkley_helper, eprint


def generate_message(sender, reciever):
    transaction = json.dumps({
        'id': str(uuid.uuid4()),
        'from': sender,
        'to': reciever,
        'amount': random.choice(range(1, 100)),
        'timestamp': int(round(time.time() * 1000))
    })
    return json.dumps({
        'hash': hashfunc(transaction.encode()),
        'transaction': transaction,
        'type': 'message'
    })


class BlockHandler:
    def __init__(self, transaction_channel, all_recipents) -> None:
        self.transactions = []
        self.transaction_channel = transaction_channel
        self.all_recipents = all_recipents

    def add_transaction(self, message):
        self.transactions.append(message)
        if len(self.transactions) == TRANSACTION_PACK_BLOCK_LIMIT:
            self.generate_and_send_block()

    def generate_and_send_block(self):
        eprint(f"transactions met limit {TRANSACTION_PACK_BLOCK_LIMIT}")
        merkle_root_hash = self.get_merkley_root_hash()
        block = {
            'merkleRoot': merkle_root_hash,
            'transactions': self.transactions,
            'signature': gpg_utils.gpg.sign(merkle_root_hash).data.decode(),
            'type': 'block'
        }
        b_unencrypted = json.dumps(block)
        b_encrypted = gpg_utils.gpg.encrypt(
            b_unencrypted, always_trust=True, recipients=self.all_recipents)
        self.transaction_channel.sendto(b_encrypted.data)
        self.transactions = []

    def get_merkley_root_hash(self):
        tree = merkley_helper(self.transactions)
        merkle_root_hash = tree.merkle_root
        return merkle_root_hash
