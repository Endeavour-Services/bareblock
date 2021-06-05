import json
import traceback

from ed25519.keys import SigningKey, VerifyingKey

from . import gpg_utils
from .utils import eprint, merkley_helper, hashfunc
from .block import BlockHandler, generate_message
from .exceptions import *
from .udp_utils import Client
from .constants import *
import os
import random
import threading
import time


public_key_ed255 = []


def load():
    files = os.listdir(SIGNATURE_DIR)
    all_recipents = []
    # load public keys of all nodes
    for filename in files:
        root_file_path = os.path.join(SIGNATURE_DIR, filename)
        if os.path.isfile(root_file_path):
            with open(root_file_path, 'rb') as f:
                if not root_file_path.endswith('.ed25519'):
                    try:
                        key_data = f.read()
                        gpg_utils.gpg.import_keys(key_data)
                        eprint(f'were able to import {filename}')
                        all_recipents.append(
                            os.path.basename(filename).strip(".key"))
                    except:
                        eprint(f'trouble loading {filename}')
                else:
                    # loading ed25519 signature for all available nodes
                    public_key_ed255.append(VerifyingKey(f.read()))
    return all_recipents


def verify_message(sigature, hash):
    for key in public_key_ed255:
        try:
            key.verify(sigature, hash, encoding='hex')
            return True
        except:
            pass
    raise BlockSignFailed()


def integrity_check_fail_send(transaction_channel, all_recipents):
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


def run_for_message(recv, handler):
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

            if (verify_message(message['signature'], message['merkleRoot'].encode())):
                eprint("block sign verified")

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
                    # eprint("transaction recieved", transaction_encoded_to_verify)
                    transaction_encoded_to_verify_obj = json.loads(
                        transaction_encoded_to_verify)
                    if (verify_message(transaction_encoded_to_verify_obj['signature'], transaction_encoded_to_verify_obj['hash'].encode())):
                        eprint("transaction sign verified")

                else:
                    eprint("transaction failed")
            else:
                raise BlockSignFailed()
        else:
            raise MerkleyHashFailed()


def main():
    all_recipents = load()
    transaction_channel = Client(TRANSACTION_PORT)
    recv_channel = Client(TRANSACTION_PORT)
    transaction_sender = threading.Thread(
        target=integrity_check_fail_send, args=(transaction_channel, all_recipents))
    transaction_sender.start()
    handler = BlockHandler(transaction_channel, all_recipents)
    while True:
        eprint("waiting for receive")
        # using select and different channels would  be better choice
        # for now going with same channel and type identifier
        recv, addr = recv_channel.recvfrom()
        try:
            run_for_message(recv, handler)
        except Exception as e:
            eprint(
                f"message from {addr} loading into block failed with error {e}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
