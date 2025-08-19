import streamlit as st
import requests as r
from Authentication import login as login_user, register as register_user,cross_check # <-- rename to avoid clash
from pymongo import MongoClient

client= MongoClient("mongodb://localhost:27017/")
db = client["expense_tracker_and_Secure_vault"]
notes_collection = db["user"]

st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="centered")

base_url = "http://127.0.0.1:5000/"
base_url2="http://127.0.0.1:5001/"

# ---- session state init ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "selected_feature" not in st.session_state:
    st.session_state.selected_feature = None
if "authentication" not in st.session_state:
    st.session_state.authentication = False
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "username" not in st.session_state:
    st.session_state.username = ""




# if "expenses" not in st.session_state:
#     res=r.get(base_url+"expenses/all")
#     if res.status_code==200:

#         data1=res.json()
#         st.session_state.vault_notes =list(data1)
#     else:
#         st.session_state.vault_notes =[]        

# --- Auth UI ---
def auth_page():
    st.title("Welcome to Secure expense manager")

    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login", key="login_button"):
                success, message = login_user(login_username, login_password)
                if success:
                    st.success(message)
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.page = "dashboard"
                    st.session_state.update_mode=False

                    st.rerun()
                else:
                    st.error(message)

        with tab2:
            signup_username = st.text_input("Username", key="signup_username")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            secure_pass = st.text_input("Create Secure vault password: ", type="password", key="secure_pass")

            if st.button("Sign Up", key="signup_button"):
                if signup_password != signup_confirm_password:
                    st.error("Passwords do not match!")
                else:
                    success, message = register_user(signup_username, signup_password, secure_pass)
                    if success:
                        st.success(message)
                        st.session_state.logged_in = True
                        st.session_state.username = signup_username
                        st.session_state.page = "dashboard"
                        st.session_state.update_mode=False
                        st.rerun()
                    else:
                        st.error(message)
    else:
        dashboard()


# --- Dashboard menu ---
def dashboard():
    st.title("📊 Dashboard")
    st.write(f"Hello, **{st.session_state['username']}**! You are logged in.")

    choice = st.sidebar.radio("Navigate", ["Home", "Expense Tracker", "Secure Vault"])
    st.session_state.page = choice

    if choice == "Home":
        st.info("Choose a feature from the sidebar.")
    elif choice == "Expense Tracker":
        expense_tracker()
    elif choice == "Secure Vault":
        secure_vault()

    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()


# --- Expense Tracker ---

def load_expenses():
    payload={"username":st.session_state.username}
    response = r.get(base_url + "expenses/all",json=payload)
    if response.status_code == 200:
        try:
            st.session_state.expenses = list(response.json())   # no list()
            # debug
            
        except Exception as e:
           
            st.session_state.expenses = []
    else:
        st.session_state.expenses = []

def expense_tracker():
    st.header("💰 Expense Tracker")
    if "expenses" not in st.session_state:
        load_expenses()
        
    operation = st.selectbox("Select an operation", ["", "Add Expense", "View Expenses", "View expense of a date"])
    if operation == "Add Expense":
        expense_type = st.selectbox(
            "Select expense type:",
            [" ", "Medicines", "Grocery", "Bills", "Entertainment", "Other Expense"]
        )
        amount = st.text_input("Enter amount:")
        details = ""
        if expense_type == "Other Expense":
            details = st.text_input("Enter expense details:")

        if st.button("Add Expense"):
            if expense_type.strip() and amount.strip():
                if expense_type=="Other Expense":
                     payload = {"category": details, "amount": amount,"user":st.session_state.username}

                else:
                    
                    payload = {"category": expense_type, "amount": amount,"user":st.session_state.username}

                try:
                    response = r.post(base_url + "create_expense", json=payload)
                    if response.status_code == 200:
                        st.success(response.text)
                    else:
                        st.warning("No response from backend server")
                except Exception as e:
                    st.error(f"Error connecting to backend: {e}")

               

    elif operation == "View Expenses":
        st.subheader("💰 Your Expenses")
        load_expenses()
        if "expenses" in st.session_state and st.session_state.expenses:
            j=1
            for i in list(st.session_state.expenses):
                with st.expander(f"Expense {j}: {i.get('category')}"):
                    st.write(f"**Category:** {i.get('category')}")
                    st.write(f"**Amount:** ₹{i.get('amount')}")
                    st.write(f"**Date:** {i.get('date')}")
                    b1=st.button("🗑️Delete",key="delete"+str(i))
                    if b1:
                        pay={"exp_id":i.get("exp_id")}
                        response=r.delete(base_url+"delete_expense",json=pay)
                        if response.status_code==200:
                            st.success("expense deleted successfully")
                            load_expenses()
                        else:
                            st.error("error while deleting") 


                    if st.button("✏️ Edit", key=f"edit_{i.get('exp_id')}"):
                        st.session_state.editing_note = i.get("exp_id")
                        
                    if st.session_state.get("editing_note") == i.get("exp_id"):        
                        
                        
                        cat=st.text_input("Enter the category to be updated")
                        am=st.text_input("Enter amount to be updated")
                        if cat and am:
                            pay={"category":cat,"amount":am,"exp_id":i.get("exp_id")}  
                            response=r.put(base_url+"update_expense",json=pay)
                            if response.status_code==200:
                                st.success("Expense Updated Successfully")
                                load_expenses()
                                st.session_state.editing_note = None
                            else:
                                st.error("Error while updating")    
                        else:
                            st.info("Enter both the fields",icon="🚨")        
                j+=1
                    
        else:
            st.info("No expenses found.")


    elif operation=="View expense of a date":
        inp=st.text_input("Enter a date in the format YYYY-MM-DD")
        if inp:
            payload={"date":inp,"username":st.session_state.username}
            try:
                response=r.get(base_url+"view_by_date",params=payload)
                if response.status_code==200:
                    my=list(response.json())
                    total=0
                    j=1
                    for i in my:
                        
                        with st.expander(f"Expense {j}: {i.get('category')}"):
                            st.write(f"**Category:** {i.get('category')}")
                            st.write(f"**Amount:** ₹{i.get('amount')}")
                            st.write(f"**Date:** {i.get('date')}")
                            total=total+i["amount"]
                            b1=st.button("🗑️Delete",key="delete"+str(i))
                            if b1:
                                pay={"exp_id":i.get("exp_id")}
                                response=r.delete(base_url+"delete_expense",json=pay)
                                if response.status_code==200:
                                    st.success("Expense deleted successfully")
                                    load_expenses()
                                else:
                                    st.error("Error while deleting") 


                            if st.button("✏️ Edit", key=f"edit_{i.get('exp_id')}"):
                                st.session_state.editing_note = i.get("exp_id")
                                
                            if st.session_state.get("editing_note") == i.get("exp_id"):        
                                
                                
                                cat=st.text_input("Enter the category to be updated")
                                am=st.text_input("Enter amount to be updated")
                                if cat and am:
                                    pay={"category":cat,"amount":am,"exp_id":i.get("exp_id")}  
                                    response=r.put(base_url+"update_expense",json=pay)
                                    if response.status_code==200:
                                        st.success("Expense updated successfully")
                                        load_expenses()
                                        st.session_state.editing_note = None
                                    else:
                                        st.error("Error while updating")    
                                else:
                                    st.info("Enter both the fields",icon="🚨")
                        j+=1        
                    #st.success(response.text)
                    st.write(f"Total Spent : ₹{total}")
                else:
                    st.warning(response.text)
            except Exception as e:
                st.warning(e)  



def load_notes():
    
    payload={
        "username":st.session_state.username
    }
    response=r.get(base_url2+"view_notes",json=payload)
    if response.status_code==200:
        try:
            data=response.json()
            if data:
                st.session_state.vault_notes =list(data)
            else:    
                st.session_state.vault_notes =[]
        except:
    
            st.session_state.vault_notes =[]
    else:
        st.session_state.vault_notes =[]
# --- Secure Vault ---
def secure_vault():
    
    st.header("🔒 Secure Vault")
    password = st.text_input("Enter password:", type="password")
    if "vault_unlocked" not in st.session_state:
        st.session_state.vault_unlocked = False
    b1=st.button("Verify")
    if not st.session_state.vault_unlocked:
        if password:
            if b1:
                msg=cross_check(st.session_state.username,password)
                if msg==True:  # For demo, no real validation
                        
                    
                        st.success("Access Granted")
                        st.session_state.vault_unlocked=True
                        st.rerun()
                        # Add new note
                else:
                    st.error("Invalid Password")  
        else:
            st.info("Enter your password to unlock the vault.")                          
    else:
        if "vault_notes" not in st.session_state:
            load_notes()                                  
        new_note = st.text_area("Write a secure note:", key="new_note")
        mydict={"data":new_note,"username":st.session_state.username}
        b2=st.button("save note",key="add button")
        if b2:
            response=r.post(base_url2+"add_note",json=mydict)
            if response.status_code==200:
                st.success("Note saved!")
                load_notes()

            
            else:
                st.error("note not saved")    
        st.subheader("Your Notes")
        response=r.get(base_url2+"view_notes")
        if response.status_code==200:

            data=response.json()
            if data:

                st.session_state.vault_notes =data    
            else:
                st.session_state.vault_notes =[]

        #for i in st.session_state.vault_notes:
            #st.write(f"Id:{i["id"]},data:{i["data"]}")
        if st.session_state.vault_notes:
            j=1
            for i in st.session_state.vault_notes:
                short = i["data"] if len(i["data"]) <= 30 else i["data"][:30] + "..."
                with st.expander(f"Note {j}: {short}"):
                    st.write(i["data"])

                    # ---- EDIT BUTTON ----
                    if st.button("✏️ Edit", key=f"edit_{i['id']}"):
                        st.session_state.editing_note = i["id"]

                    # ---- DELETE BUTTON ----
                    if st.button("🗑️ Delete", key=f"delete_{i['id']}"):
                        pay = {"note_id": i["id"]}
                        response = r.delete(base_url2 + "delete_note", json=pay)
                        st.write(response.text)
                        load_notes()

                    # ---- EDIT MODE ----
                    if st.session_state.get("editing_note") == i["id"]:
                        up = st.text_input("Enter updated note:", value=i["data"], key=f"input_{i['id']}")
                        if st.button("Update", key=f"update_{i['id']}"):
                            if up.strip():
                                pay = {"note_id": i["id"], "data": up}
                                response = r.put(base_url2 + "update_note", json=pay)
                                
                                if response.status_code == 200:
                                    st.success("Updated successfully")
                                    st.session_state.editing_note = None
                                    load_notes()
                                else:
                                    st.error("Error while updating")
                            else:
                                st.warning("Please enter note to update")
                j+=1
        else:
            st.info("No notes yet.")                
       
                



# --- Main ---
if not st.session_state.logged_in:
    auth_page()
else:
    dashboard()

