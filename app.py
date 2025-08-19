from flask import Flask,request
from storage import storage

app=Flask("my")

@app.route("/add_note",methods=["POST"])
def create_note():
    s=storage()
    data=request.json
    text=data.get("data")
    user=data.get("username")
    status=s.add_note(text,user)
    if status==True:
        return "note created successfully",200
    else:
        return "error while creating",500    


@app.route("/view_notes",methods=["GET"])
def view_note():
    s=storage()
    data=request.json
    user=data.get("username")
    status=s.print_notes(user)
    if status==None:
        return "no notes for now",500
    else:
        return status

@app.route("/update_note",methods=["PUT"])
def update_task():

    s=storage()
    data=request.json
    text=data.get("data")
    id=int(data.get("note_id"))
    status=s.update_note(id,text)
    if status==None:
        return "No notes to update",500
    elif status==True:
        return "note updated successfully",200
    elif status==False:
        return f"no note is present with id:{id}",500

@app.route("/delete_note",methods=["DELETE"])
def delete_note()    :
    s=storage()
    data=request.json
    id=int(data.get("note_id"))
    status=s.delete_note(id)
    if status==None:
        return "No notes to delete",500
    elif status==True:
        return "note deleted successfully",200
    elif status==False:
        return f"no note is present with id:{id}",500
    


if __name__ == '__main__':
    # ... (code to create .env file) ...
    app.run(port=5001,debug=True)
