import pymongo
from cryptography.fernet import Fernet

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Change if using cloud MongoDB
db = client["expense_tracker_and_Secure_vault"]
collection = db["user"]

# Key file
key_file = "users_secret.key"

try:
    with open(key_file, "rb") as f:
        key = f.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)

cipher = Fernet(key)

def encrypt_text(text):
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(text):
    return cipher.decrypt(text.encode()).decode()


def register(username, password, secure):
    enc_username = encrypt_text(username)
    enc_password = encrypt_text(password)
    enc_secure = encrypt_text(secure)
    # Check if username already exists
    if collection.find_one({"username": enc_username}):
        return False, "Username already exists"

    # Insert user
    collection.insert_one({
        "username": enc_username,
        "password": enc_password,
        "secure" : enc_secure
    })
    return True, "Registered Successfully"


def login(username, password):
    # Get all users from DB
    users = collection.find()
    for user in users:
        if decrypt_text(user["username"]) == username and decrypt_text(user["password"]) == password:
            return True, "Login Successfully"

    return False, "Invalid username or password"



def cross_check(username,s_pass):
    users=collection.find()
    for user in users:
        if decrypt_text(user["username"])==username and decrypt_text(user["secure"])==s_pass:
            return True
    return False    
