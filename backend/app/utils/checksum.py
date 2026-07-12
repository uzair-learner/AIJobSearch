import hashlib


def file_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
