import hashlib
import time
import random
import json
import uuid


def hashfunc(value):
    return hashlib.sha256(value).hexdigest()



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

