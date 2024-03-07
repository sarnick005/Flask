import os
from flask import Flask, render_template, redirect, url_for
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


if __name__ == "__main__":
    app.run(debug=True)
