from flask import request, render_template
from app import app 
from task_data.tasks import tasks_list 

import datetime 
current_time = datetime.datetime.now()
formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S')

# Task Routes
@app.route('/')
def index():
    return render_template('index.html')



# Rout to return all tasks 
@app.route('/tasks')
def get_tasks():
    tasks = tasks_list 
    return tasks 

# Rout to return task by id

@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    tasks = tasks_list
    for task in tasks:
        if task['id'] == task_id:
            return task
    return  {'error': f"A Task with the ID of {task_id} does not exist."}, 404

# Create Task 

@app.route('/tasks', methods=['POST'])
def create_task():
    if not request.is_json:
        return {'error': 'Your Task submission must be of json type'}, 400
    data = request.json
    required_fields = ['title', 'description', 'dueDate']
    missing_fields = []

    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request "}, 400
    
    title = data.get('title')
    description = data.get('description')
    dueDate = data.get('dueDate')

    new_task = {
        'id': len(tasks_list) + 1,
        'title': title,
        'description': description,
        'completed': False,
        'dueDate': dueDate,
        'createdAt': formatted_time,
    }

    #Needs to be a DB today
    tasks_list.append(new_task)

    return new_task, 201