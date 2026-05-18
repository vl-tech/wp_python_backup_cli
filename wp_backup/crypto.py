from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken

KEY_FILE = Path.home() / '.wp_backup.key'


def get_or_create_key() -> bytes:
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    KEY_FILE.chmod(0o600)
    print(f"Encryption key created: {KEY_FILE}")
    print("Back up this file — without it, stored passwords cannot be recovered.")
    return key


def encrypt(plaintext: str) -> str:
    return Fernet(get_or_create_key()).encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    return Fernet(get_or_create_key()).decrypt(ciphertext.encode()).decode()


def is_encrypted(value: str) -> bool:
    try:
        Fernet(get_or_create_key()).decrypt(value.encode())
        return True
    except (InvalidToken, Exception):
        return False
