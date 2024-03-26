from app import app 
from task_data.tasks import tasks_list 




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
