
from .utils import eprint



class BaseBareException(Exception):
    pass


class MessageHashFailed(BaseBareException):
    def __init__(self, *args: object) -> None:
        eprint("message hash failed")
        super().__init__("rejected (transaction hash)")


class MerkleyHashFailedFailed(BaseBareException):
    def __init__(self, *args: object) -> None:
        eprint("block merkley hash failed")
        super().__init__("rejected (integrity)")
