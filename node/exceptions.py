
from .utils import eprint



class BaseBareException(Exception):
    pass


class MessageHashFailed(BaseBareException):
    def __init__(self, *args: object) -> None:
        eprint("message hash failed")
        super().__init__("rejected (transaction hash)")


class MerkleyHashFailed(BaseBareException):
    def __init__(self, *args: object) -> None:
        eprint("block merkley hash failed")
        super().__init__("rejected (integrity)")

class BlockSignFailed(BaseBareException):
    def __init__(self, *args: object) -> None:
        eprint("block signature failed")
        super().__init__("rejected (integrity)")

class TransactionSignFailed(BaseBareException):
    def __init__(self, *args: object) -> None:
        eprint("transaction signature failed")
        super().__init__("rejected (integrity)")