import hashlib
import time
import random
import json
import uuid
from merklelib import MerkleTree, beautify


def hashfunc(value):
    return hashlib.sha256(value).hexdigest()


def generate_message(sender, reciever):
    transaction = json.dumps({
        'id': uuid.uuid4(),
        'from': sender,
        'to': reciever,
        'amount': random.choice(range(1, 100)),
        'timestamp': int(round(time.time() * 1000))
    })
    return json.dumps({
        'hash': hashfunc(transaction.encode()),
        'transaction': transaction
    })


# working code

# print(int(round(time.time() * 1000)))

# transactions = []

# for i in range(0, 15):
#     transaction = {
#         'id': i,
#         'from': 'some from ' + str(i),
#         'to': 'some to ' + str(i),
#         'amount': random.choice(range(1, 100)),
#         'timestamp': int(round(time.time() * 1000))
#     }
#     json_object = json.dumps(transaction)
#     message = {
#         'hash': hashfunc(json_object.encode()),
#         'transaction': transaction
#     }
#     transactions.append(message)

# # build a Merkle tree for that transactions list
# tree = MerkleTree(transactions, hashfunc)

# block = {
#     'merkleRoot': tree.merkle_root,
#     'transactions': transactions,
#     'signature': 'Bsignature'
# }

# print(tree)

# beautify(tree)

# print(block)


# fullycommented


# SM===========> Camparing two Merkle Trees!!
# transactions1 = ['sm', 'ms', 'sm']
# transactions2 = ['sm', 'ms', 'sm']
# # transactions2 = ['sm', 'sm', 'ms']

# tree1 = MerkleTree(transactions1, hashfunc)
# tree2 = MerkleTree(transactions2, hashfunc)

# beautify(tree1)
# beautify(tree2)

# if tree1 == tree2:
#     print('They are consistent')
# else:
#     exit('They are different! - Rejected (integrity)')
