# app.py

from flask import Flask, request, jsonify
from storage import add_expense, get_all_expenses, delete_expense, update_expense, get_expense_by_id,get_by_date
from views import format_expenses_list, format_single_expense, format_total_expenses, format_response
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson import ObjectId
from cryptography.fernet import Fernet


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# MongoDB connection setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient("mongodb://localhost:27017/")
db = client["expense_tracker_and_Secure_vault"]
expenses_collection = db["expenses"]

# Make sure you have REMOVED the line that creates the index on "id"
# expenses_collection.create_index("id", unique=True) <-- This should be gone

# ... (other routes remain the same) ...
def get_next_id():
    next_id=expenses_collection.find_one(sort=[("exp_id",-1)])
    return int(next_id["exp_id"])+1 if next_id else 1


@app.route('/create_expense', methods=['POST'])
def create_expense():
    """Adds a new expense with the current date/time."""
    try:
        # Change these two lines only
        data = request.json if request.json else request.get_json(force=True)
        category = data['category']
        amount = float(data['amount'])
        user=data["user"]
        if amount<=0:
            raise ValueError
        
        current_date = datetime.now().strftime('%Y-%m-%d')
    except KeyError:
        return format_response('Error: Missing form data (category or amount).', 'error', 400)
    except ValueError:
        return format_response('Error: Amount must be a positive number', 'error', 400)

    new_expense_data = {
        "username":user,
        'exp_id':get_next_id(),
        'category': category,
        'amount': amount,
        'date': current_date
    }
    inserted_id = add_expense(expenses_collection, new_expense_data)
    if inserted_id:
        return "expense added successfully",200
    

@app.route('/view_expenses', methods=['GET'])
def view_expense():
    data=int(request.json.get("exp_id"))
    status=get_expense_by_id(expenses_collection,data)
    if status!=None:
        return status,200
    
@app.route('/expenses/all', methods=['GET'])
def view_all():
    user=request.json.get("username")
    status=get_all_expenses(expenses_collection,user)
    if status !=None:
        return status,200
    else:
        return "no expenses "


@app.route('/update_expense', methods=['PUT'])
def update_expense_route():
    try:
        data = request.json if request.json else request.get_json(force=True)
        updated_data = {}
        exp_id=int(data.get("exp_id"))
        if data.get("category"):
            updated_data['category'] = data['category']
        if data.get("amount"):
            updated_data['amount'] = float(data['amount'])
    except ValueError:
        return format_response('Error: Amount must be a number.', 'error', 400)

    if not updated_data:
        return format_response('No valid fields to update.', 'error', 400)
    
    success = update_expense(expenses_collection, exp_id, updated_data)
    if success:
        return f"successfully updated expense with id :{exp_id}"
    return format_response('Expense not found or not updated.', 'error', 404)


@app.route("/view_by_date",methods=["GET"])
def get_with_date():

    date=request.args.get("date")
    user=request.args.get("username")
    #date=data.get("date")
    if date:
        success=get_by_date(expenses_collection,date,user)
        if success:
            return success,200
        else:
            return "no expenses or no expense for that date",500


@app.route("/delete_expense",methods=["DELETE"])
def delete():
    data=request.json
    exp_id=int(data.get("exp_id"))
    if exp_id:
        success=delete_expense(expenses_collection,exp_id)
        if success:
            return f'expense with id {exp_id} deleted successfully',200
        else:
            return f"there is no expense to delete or expense with id:{exp_id} dows not exist",500





if __name__ == '__main__':
    # ... (code to create .env file) ...
    app.run(port=5000,debug=True)
