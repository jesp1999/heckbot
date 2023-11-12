import os
from datetime import datetime, timedelta
from typing import Optional

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

SECRET_KEY = os.getenv('HECKBOT_SECRET_KEY')


def encrypt(username: str, expiry: str) -> tuple[bytes, bytes]:
    message = f"{username}:{expiry}".encode()
    iv = os.urandom(16)
    cipher = Cipher(
        algorithms.AES(
            SECRET_KEY.encode()
        ), modes.CFB(iv), backend=default_backend()
    )
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message) + encryptor.finalize()
    return ciphertext, iv


def decrypt(ciphertext: str, iv: str) -> Optional[str]:
    cipher = Cipher(
        algorithms.AES(
            SECRET_KEY.encode()
        ), modes.CFB(iv.encode()), backend=default_backend()
    )
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(
        ciphertext.encode()
    ) + decryptor.finalize()
    decoded_data = decrypted_data.decode()
    username, timestamp = decoded_data.split(':')
    timestamp = datetime.fromisoformat(timestamp)
    if datetime.utcnow() < timestamp + timedelta(seconds=300):
        return username
    return None
