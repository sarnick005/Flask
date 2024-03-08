from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,DateField
# from wtforms.fields.html5 import DateField


class NewTaskForm(FlaskForm):
    title = StringField(label="Title: ")
    description = StringField(label="Description: ")
    due_date = DateField("Due Date")  
    submit = SubmitField("Add Task")

