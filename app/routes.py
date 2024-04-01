from flask import request, render_template, flash, redirect, url_for
from app import app, db 
from app.models import Task, User, check_password_hash
from .auth import basic_auth, token_auth
from datetime import datetime 
from flask import session



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
    
@app.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()


@app.route('/create_user', methods=['POST'])
def create_user_from_form():
    if not request.form:
        flash('Your submission must be in form data', 'error')
        return redirect(url_for('index'))

    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    missing_fields = [field for field in ['firstName', 'lastName', 'username', 'email', 'password'] if not request.form.get(field)]
    if missing_fields:
        flash(f"{' '.join(missing_fields)} must be in the request body", 'error')
        return redirect(url_for('index'))

    check_users = db.session.execute(select(User).where((User.username == username) | (User.email == email))).scalars().all()
    if check_users:
        flash("A user with that username and/or email already exists", 'error')
        return redirect(url_for('index'))

    
    new_user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
    flash('User created successfully', 'success')
    return redirect(url_for('index'))

@app.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def update_user(user_id):
    user = token_auth.current_user()
    if user.id != user_id:
        return {'error': 'Unauthorized'}, 401  
    
    data = request.json
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.set_password(data['password'])
    db.session.commit()
    return {'message': 'User updated successfully'}, 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
@token_auth.login_required
def delete_user(user_id):
    user = token_auth.current_user()
    if user.id != user_id:
        return {'error': 'Unauthorized'}, 401  
    
    db.session.delete(user)
    db.session.commit()
    return {'message': 'User deleted successfully'}, 200

# Task Routes
@app.route('/')
def index():
    return render_template('index.html')



# Rout to return all tasks 
@app.route('/tasks', methods=['GET'])
def get_tasks():
    select_stmt = db.select(Task)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Task.title.ilike(f"%{search}%"))
    completed = request.args.get('completed')
    if completed:
        completed = completed.lower() == 'true'
        select_stmt = select_stmt.where(Task.complete == completed)
    tasks = db.session.execute(select_stmt)
    task_dicts = [task.to_dict() for task in tasks.scalars().all()]
    return render_template('tasks.html', tasks=task_dicts)


@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if task:
        return task.to_dict()
    else:
        return {'error': f"A Task with the ID of {task_id} does not exist."}, 404

# Create Task 

@app.route('/tasks', methods=['POST'])
@token_auth.login_required
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
#Update Task
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_auth.login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    user = token_auth.current_user()
    if task.user_id != user.id:
        return {'error': 'Unauthorized'}, 401  
    
    data = request.json
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'completed' in data:
        task.completed = data['completed']
    if 'due_date' in data:
        task.due_date = datetime.fromisoformat(data['due_date'])
    db.session.commit()
    return {'message': 'Task updated successfully'}, 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_auth.login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    user = token_auth.current_user()
    if task.user_id != user.id:
        return {'error': 'Unauthorized'}, 401  
    
    db.session.delete(task)
    db.session.commit()
    return {'message': 'Task deleted successfully'}, 200

@app.route('/create_task', methods=['POST'])
def create_task_from_form():
    if 'token' not in session:
        flash('You must be logged in to create a task.', 'error')
        return redirect(url_for('index'))
    token = session['token']
    user = User.find_by_token(token)
    if not user:
        flash('Invalid or expired token. Please log in again.', 'error')
        return redirect(url_for('index'))  
    title = request.form.get('title')
    description = request.form.get('description')
    due_date_str = request.form.get('dueDate')
    due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None

    new_task = Task(title=title, description=description, due_date=due_date, user_id=user.id)
    
    flash('Task created successfully!', 'success')
    return redirect(url_for('user_home'))  

# Login 

@app.route('/login', methods=['POST'])
def login():
    if 'token' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('user_home'))
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id  
        session['token'] = user.get_token()['token']
        return redirect(url_for('user_home'))  
    else:
        flash('Invalid username or password.', 'error')
        return redirect(url_for('index'))  

@app.route('/userhome')
def user_home():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user_id = session['user_id']
    user = User.query.get(user_id)
    if not user:
        flash('No user found.', 'error')
        return redirect(url_for('index'))
    tasks = Task.query.filter_by(user_id=user.id).all()
    return render_template('userhome.html', tasks=tasks)