from pymongo import MongoClient
from cryptography.fernet import Fernet
from model import secure_manager as sm


class storage:
    
    # Load or generate encryption key
    try:
        with open("secret.key", "rb") as f:
            key = f.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as f:
            f.write(key)

    cipher = Fernet(key)

    def __init__(self):
        self.client= MongoClient("mongodb://localhost:27017/")
        self.db = self.client["expense_tracker_and_Secure_vault"]
        self.notes_collection = self.db["Notes"]

    def to_dict(self,ob):
        return {"id":ob.id,"data":ob.data,"username":ob.username}

    def get_next_id(self):
        next_id=self.notes_collection.find_one(sort=[("id",-1)])
        return next_id["id"]+1 if next_id else 1


    def add_note(self,data,user):
        if data:
            encrypted_data=storage.cipher.encrypt(data.encode()).decode()
            
            note=sm(self.get_next_id(),encrypted_data,user)
            self.notes_collection.insert_one(self.to_dict(note))
            return True
        return False

    def print_notes(self,user):
        notes=list(self.notes_collection.find({"username":user}, {"_id": 0}))
        if not notes:
            return None
        for note in notes:
            note["data"]=storage.cipher.decrypt(note["data"].encode()).decode()
        return notes

    def delete_note(self,id):
        result=self.notes_collection.delete_one({"id":id})   
        if result.deleted_count >0:
            return True
        else:
            return False
        
    def update_note(self,id,data):
        L=list(self.notes_collection.find())
        if L:


            encrypted_data=storage.cipher.encrypt(data.encode()).decode()
            result=self.notes_collection.update_one({"id":id},{"$set":{"data":encrypted_data}})
            if result.modified_count>0:
                return True
            else:
                return False
        else:
            return None
        



