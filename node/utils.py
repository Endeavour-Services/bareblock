import hashlib
import threading

readlock = threading.Lock()
writelock = threading.Lock()


def get_hash(data):
    if type(data) != bytes:
        # wierd hack
        # be warned
        data = data.encode('utf-8')
    gfg = hashlib.sha3_256()
    gfg.update(data)
    return gfg.hexdigest()


empty_hash = get_hash('')


class BlockList():

    def __init__(self) -> None:
        self.blocks = []
        self.block_map = {}

        self.last_hash = empty_hash

    def add(self, value, hash, sign_hash):
        readlock.acquire()
        self.blocks.append({"hash": hash, "value": value, "sign": sign_hash})
        self.block_map[hash] = {
            "messages": value, "sign_hash": sign_hash, "prev_hash": self.last_hash}
        self.last_hash = hash
        readlock.release()

    def all_blocks(self):
        return list(self.block_map.keys())
