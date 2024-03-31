from flask import request, render_template
from app import app, db 
from app.models import Task, User


import datetime 
current_time = datetime.datetime.now()
formatted_time = current_time.strftime('%Y-%m-%dT%H:%M:%S')

# User Routes

@app.route('/users', methods=['POST'])
def create_user():
    if not request.is_json: 
        return {'error': 'Your content type must be application/json'}, 400
    data = request.json
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{','.join(missing_fields)} must be in the request body"}, 400
    
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    check_users = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_users:
        return {'error': "A user with that username and/or email already exists"}, 400
    
    new_user = User(first_name=first_name, last_name=last_name,  username=username, email=email, password=password)

    return new_user.to_dict(), 201
    

@app.route('/create_user', methods=['POST'])
def create_user_from_form():
    # Retrieve form data from request
    if not request.form:
        return {'error': 'Your submission must be of form type'}, 400
    data = request.form
    required_fields = ['firstName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{','.join(missing_fields)} cannot be left empty"}, 400
    
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    check_users = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_users:
        return {'error': "A user with that username and/or email already exists"}, 400
    
    new_user = User(first_name=first_name, last_name=last_name,  username=username, email=email, password=password)

    return new_user.to_dict(), 201

# Task Routes
@app.route('/')
def index():
    return render_template('index.html')



# Rout to return all tasks 
@app.route('/tasks', methods=['GET'])
def get_tasks():
    # Construct a select statement to select all tasks
    select_stmt = db.select(Task)

    # Check if there is a search query parameter
    search = request.args.get('search')
    if search:
        # Modify the select statement to filter tasks by title
        select_stmt = select_stmt.where(Task.title.ilike(f"%{search}%"))

    completed = request.args.get('completed')
    if completed:
        # Convert the completed parameter to a boolean
        completed = completed.lower() == 'true'
        # Modify the select statement to filter tasks by completion status
        select_stmt = select_stmt.where(Task.complete == completed)

    # Execute the select statement
    tasks = db.session.execute(select_stmt)

    # Extract individual rows and convert each task to a dictionary
    task_dicts = [task.to_dict() for task in tasks.scalars().all()]

    # Return the list of task dictionaries
    return render_template('tasks.html', tasks=task_dicts)

# Rout to return task by id

@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        return {'error': f"A Task with the ID of {task_id} does not exist."}, 404

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

    new_task = Task(title=title, description=description, due_date=dueDate)
    db.session.add(new_task)
    db.session.commit()

    return new_task.to_dict(), 201


# Route to mark task complete


@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    
    if not request.is_json:
        return {'error': 'Content-Type must be application/json'}, 400
    
    task = db.session.get(Task, task_id)
    
    if task is None:
        return {'error': f'Task with ID {task_id} not found'}, 404
    
    task.complete = True
    
    db.session.commit()
    
    return task.to_dict(), 200 

