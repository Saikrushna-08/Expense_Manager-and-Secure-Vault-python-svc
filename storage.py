# storage.py

from bson.objectid import ObjectId

def add_expense(collection, expense_data):
    """Adds a new expense to the MongoDB collection."""
    result = collection.insert_one(expense_data)
    return str(result.inserted_id)



def get_all_expenses(collection,user):
    """Retrieves all expenses from the MongoDB collection."""
    expenses = list(collection.find({ "username":user}, {"_id": 0}))
    # Convert ObjectId to string for JSON serialization
    if expenses:
        
        return expenses
    else:
        return None
    
def get_expense_by_id(collection,expense_id):
    """Finds and returns a single expense by its ID."""
    try:
        
        expense = collection.find_one({'exp_id':expense_id},{"_id":0})
        if expense:
            
            return expense
    except Exception:
        return None

def update_expense(collection, expense_id, updated_data):
    """Updates an existing expense in the collection."""
    try:
        result = collection.update_one({'exp_id':expense_id}, {"$set":{"category":updated_data["category"],"amount":updated_data["amount"]}})
        return result.modified_count > 0
    except Exception:
        return False

def delete_expense(collection, expense_id):
    """Deletes an expense from the collection by its ID."""
    try:
        result = collection.delete_one({'exp_id':expense_id})
        return result.deleted_count > 0
    except Exception:
        return False

def get_by_date(collection,date,user):
    try:
        result=list(collection.find({"date":date,"username":user},{"_id":0}))
        if result:    
            return result
    except Exception:
        return False    