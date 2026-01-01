import configparser
import time
import mysql.connector
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ENCRYPTED_CONFIG_FILE = 'config.encrypted'
SALT_SIZE = 16

def derive_key(password: bytes, salt: bytes) -> bytes:
    """Derives a cryptographic key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password))

def get_database_config(section_name, password_str: str):
    """
    Reads the encrypted config file, decrypts it in memory using the provided password,
    and returns the configuration for the requested section.
    """
    if not password_str:
        raise ValueError("Password is required to decrypt configuration.")

    if not os.path.exists(ENCRYPTED_CONFIG_FILE):
        raise FileNotFoundError(
            f"The encrypted config file '{ENCRYPTED_CONFIG_FILE}' was not found. "
            f"Please run encrypt_config.py to create it."
        )

    try:
        # 1. Read the salt and the encrypted data
        with open(ENCRYPTED_CONFIG_FILE, 'rb') as f:
            salt = f.read(SALT_SIZE)
            encrypted_data = f.read()
        
        # 2. Derive the key from the provided password and the salt
        key = derive_key(password_str.encode('utf-8'), salt)
        
        # 3. Decrypt the data
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        
        # 4. Parse the decrypted data (which is in INI format)
        config = configparser.ConfigParser()
        config.read_string(decrypted_data.decode('utf-8'))
        
        return config[section_name]

    except FileNotFoundError:
        raise
    except Exception as e:
        # This can happen if the password is wrong, the file is corrupt, etc.
        raise Exception(f"Failed to decrypt or parse config file. Check password or file integrity. Error: {e}")


def connect_to_database(config, max_retries=3, retry_delay=5):
    """
    Connects to the database using the provided configuration dictionary.
    """
    retries = 0
    conn = None
    host = config["host"]
    user = config["user"]
    password = config["password"]
    database = config["database"]

    while retries < max_retries:
        try:
            conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
            if conn.is_connected():
                print("Connected to the database!")
                return conn
        except mysql.connector.Error as e:
            print(f"Failed to connect to the database: {e}")
            retries += 1
            time.sleep(retry_delay)

    print(f"Unable to connect to the database after {max_retries} retries.")
    return None
