import os
from flask import Flask, render_template, redirect, url_for, request
import mysql.connector
from forms import NewTaskForm
from config import DB_PASSWORD, SECRET_KEY
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=DB_PASSWORD,
    database="todo_flask",
)

# HOME ROUTE

@app.route("/")
@app.route("/home")
def home():
    try:
        mycursor = mydb.cursor()
        query = "SELECT * FROM todo_table"
        mycursor.execute(query)
        allTodos = mycursor.fetchall()
        mycursor.close()
        return render_template("home.html", todos=allTodos)
    except Exception as e:
        return f"An error occurred: {str(e)}"

# CREATE TASK ROUTE

@app.route("/new_task", methods=["GET", "POST"])
def new_task():
    form = NewTaskForm()
    if form.validate_on_submit():
        id = os.urandom(16).hex()
        current_date = datetime.now()
        created_at = current_date.strftime("%Y-%m-%d")
        title = form.title.data
        description = form.description.data
        due_date = form.due_date.data
        status = False
        mycursor = mydb.cursor()
        insert_query = "INSERT INTO todo_table (id, title, description, created_at, due_date, status) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (id, title, description, created_at, due_date, status)
        mycursor.execute(insert_query, data)
        mydb.commit()
        mycursor.close()
        return redirect(url_for("home"))

    return render_template("new.html", form=form)

# EDIT TASK ROUTE
@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    form = NewTaskForm()
    mycursor = mydb.cursor()
    select_query = "SELECT * FROM todo_table WHERE id = %s"
    mycursor.execute(select_query, (task_id,))
    todo_data = mycursor.fetchone()
    if todo_data:
        if request.method == "POST" and form.validate_on_submit():
            title = request.form["title"]
            description = request.form["description"]
            due_date = request.form["due_date"]
            update_query = "UPDATE todo_table SET title = %s, description = %s, due_date = %s WHERE id = %s"
            update_data = (title, description, due_date, task_id)
            mycursor.execute(update_query, update_data)
            mydb.commit()
            return redirect(url_for("home"))
        form.title.data = todo_data[1]
        form.description.data = todo_data[2]
        form.due_date.data = todo_data[4]

        return render_template("edit.html", form=form)
    else:
        return "Todo with ID {} not found".format(task_id), 404

# DESTROY TASK ROUTE
@app.route("/delete_task/<task_id>", methods=["POST"])
def delete_task(task_id):
    mycursor = mydb.cursor()
    select_query = "SELECT * FROM todo_table WHERE id = %s"
    mycursor.execute(select_query, (task_id,))
    todo_data = mycursor.fetchone()

    if todo_data:
        if request.method == "POST":
            delete_query = "DELETE FROM todo_table WHERE id = %s"
            mycursor.execute(delete_query, (task_id,))
            mydb.commit()
            return redirect(url_for("home"))
    else:
        return "Todo with ID {} not found".format(task_id), 404

# STATUS CHANGE ROUTE
@app.route("/status_task/<task_id>", methods=["POST"])
def status_task(task_id):
    mycursor = mydb.cursor()
    select_query = "SELECT * FROM todo_table WHERE id = %s"
    mycursor.execute(select_query, (task_id,))
    todo_data = mycursor.fetchone()
    if todo_data:
        current_status = todo_data[5]
        new_status = 0 if current_status else 1
        update_query = "UPDATE todo_table SET status = %s WHERE id = %s"
        mycursor.execute(update_query, (new_status, task_id))
        mydb.commit()
        return redirect(url_for("home"))
    else:
        return "Todo with ID {} not found".format(task_id), 404


if __name__ == "__main__":
    app.run(debug=True)
