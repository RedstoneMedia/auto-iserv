from Cryptodome.Cipher import AES
from Cryptodome import Random
import hashlib
from autoIserv.Session import Session


def encrypt(raw, key):
    BS = 16
    pad = lambda s: s + (BS - len(s) % BS) * bytes(chr(BS - len(s) % BS), encoding="utf-8")
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return iv + cipher.encrypt(raw)


def decrypt(enc, key):
    BS = 16
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    enc = enc
    iv = enc[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')


def load_credential_file(credential_file_path : str, key : str):
    key = key.encode(encoding="utf-8")
    key = hashlib.sha256(key).digest()
    file = open(credential_file_path, mode="rb")
    username, password = decrypt(file.read(), key).split("\n")
    password = password.replace("\n", "")
    file.close()
    return username, password


def create_credential_file(username : str, password : str, key : str, credential_file_path : str):
    key = key.encode(encoding="utf-8")
    key = hashlib.sha256(key).digest()
    file = open(credential_file_path, mode="wb")
    file.write(encrypt(bytes(username, encoding="utf-8") + bytes("\n", encoding="utf-8") + bytes(password, encoding="utf-8"), key))
    file.close()


def login(credential_file_path : str, key : str, *args, **kwargs) -> Session:
    print("[*] Loading credentials")
    username, password = load_credential_file(credential_file_path, key)
    session = Session(username, password, *args, **kwargs)
    return session
