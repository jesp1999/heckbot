import os
from datetime import datetime
from datetime import timedelta
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers import modes

SECRET_KEY = os.getenv('HECKBOT_SECRET_KEY', '').encode()


def encrypt(username: str, expiry: str) -> tuple[bytes, bytes]:
    message = f'{username}:{expiry}'.encode()
    iv = os.urandom(16)
    cipher = Cipher(
        algorithms.AES(
            SECRET_KEY,
        ), modes.CFB(iv), backend=default_backend(),
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message) + encryptor.finalize()
    return ciphertext, iv


def decrypt(ciphertext: bytes, iv: bytes) -> Optional[str]:
    cipher = Cipher(
        algorithms.AES(
            SECRET_KEY
        ), modes.CFB(iv), backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(
        ciphertext
    ) + decryptor.finalize()
    decoded_data = decrypted_data.decode()
    username, timestamp = decoded_data.split(':')
    timestamp = datetime.fromisoformat(timestamp)
    if datetime.utcnow() < timestamp + timedelta(seconds=300):
        return username
    return None
