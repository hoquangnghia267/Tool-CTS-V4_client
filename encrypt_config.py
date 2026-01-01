from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import base64
import os

# This script is a one-time tool for the developer to encrypt the configuration file.

# --- Configuration ---
INPUT_FILE = 'database_config.ini'
OUTPUT_FILE = 'config.encrypted'
SALT_SIZE = 16  # Size of the salt in bytes

def derive_key(password: bytes, salt: bytes) -> bytes:
    """Derives a cryptographic key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # Recommended number of iterations
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

def encrypt_file():
    """Encrypts the INPUT_FILE and saves it to the OUTPUT_FILE."""
    # 1. Check if the input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"Error: The input file '{INPUT_FILE}' was not found.")
        print("Please make sure the configuration file is in the same directory.")
        return

    # 2. Get password from the developer securely
    password_str = getpass.getpass(f"Enter a password to encrypt '{INPUT_FILE}': ")
    if not password_str:
        print("Password cannot be empty. Aborting.")
        return
    password = password_str.encode('utf-8')

    # 3. Read the plaintext content
    try:
        with open(INPUT_FILE, 'rb') as f:
            plaintext = f.read()
    except IOError as e:
        print(f"Error reading file '{INPUT_FILE}': {e}")
        return

    # 4. Generate a random salt
    salt = os.urandom(SALT_SIZE)

    # 5. Derive a key from the password and salt
    key = derive_key(password, salt)
    
    # 6. Encrypt the data
    f = Fernet(key)
    encrypted_data = f.encrypt(plaintext)

    # 7. Write the salt + encrypted data to the output file
    try:
        with open(OUTPUT_FILE, 'wb') as f:
            f.write(salt)
            f.write(encrypted_data)
    except IOError as e:
        print(f"Error writing to file '{OUTPUT_FILE}': {e}")
        return

    print("-" * 50)
    print(f"Success! '{INPUT_FILE}' has been encrypted to '{OUTPUT_FILE}'.")
    print("IMPORTANT:")
    print("1. Keep the password you just entered safe. You will need it in your application code.")
    print(f"2. You can now distribute '{OUTPUT_FILE}' with your application instead of '{INPUT_FILE}'.")
    print("-" * 50)


if __name__ == "__main__":
    encrypt_file()
