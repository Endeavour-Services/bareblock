import json
import uuid
from .run import BlockHandler, load, integrity_check_fail_send, run_for_message
import traceback
from .udp_utils import Client
from .constants import *
import threading
import random
from .utils import eprint, hashfunc
from . import gpg_utils
from .block import generate_message
import time


class MaliBlockHandler(BlockHandler):
    def get_merkley_root_hash(self):
        return ''


def authenticity_fail_check_send(transaction_channel, _all_recipents):
    rand = random.Random()
    while True:
        eprint('starting sending message')
        randomnode = rand.randint(0, 9)
        recipent = f"node{randomnode}@dothttp.dev"
        generated_message = generate_message(
            gpg_utils.node_id, recipent)
        transaction_channel.sendto(generated_message.encode())
        time.sleep(10)


def modify_hash_to_transaction_fail(sender, reciever):
    transaction = json.dumps({
        'id': str(uuid.uuid4()),
        'from': sender,
        'to': reciever,
        'amount': random.choice(range(1, 100)),
        'timestamp': int(round(time.time() * 1000))
    })
    return json.dumps({
        'hash': hashfunc(transaction.encode())+"hai",
        'transaction': transaction,
        'signature': gpg_utils.private_key_ed255.sign(transaction, encoding='hex'),
        'type': 'message'
    })


def transaction_fail_send(transaction_channel, all_recipents):
    rand = random.Random()
    while True:
        eprint('starting sending message')
        randomnode = rand.randint(0, 9)
        recipent = f"node{randomnode}@dothttp.dev"
        generated_message = modify_hash_to_transaction_fail(
            gpg_utils.node_id, recipent)
        crypt_obj = gpg_utils.gpg.encrypt(
            generated_message, always_trust=True, recipients=all_recipents)
        enc_message = crypt_obj.data
        transaction_channel.sendto(enc_message)
        time.sleep(10)


def main2():
    all_recipents = load()
    transaction_channel = Client(TRANSACTION_PORT)
    recv_channel = Client(TRANSACTION_PORT)
    #
    transaction_sender = threading.Thread(
        target=authenticity_fail_check_send, args=(transaction_channel, all_recipents))
    transaction_sender.start()
    transaction_sender = threading.Thread(
        target=integrity_check_fail_send, args=(transaction_channel, all_recipents))
    transaction_sender.start()

    transaction_sender = threading.Thread(
        target=transaction_fail_send, args=(transaction_channel, all_recipents))
    transaction_sender.start()

    handler = BlockHandler(transaction_channel, all_recipents)
    mali_handler = MaliBlockHandler(transaction_channel, all_recipents)
    while True:
        eprint("waiting for receive")
        # using select and different channels would  be better choice
        # for now going with same channel and type identifier
        recv, addr = recv_channel.recvfrom()
        try:
            run_for_message(recv, handler)
            run_for_message(recv, mali_handler)
        except Exception as e:
            eprint(
                f"message from {addr} loading into block failed with error {e}")
            traceback.print_exc()


if __name__ == "__main__":
    main2()
