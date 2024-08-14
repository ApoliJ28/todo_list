from flask import Flask, render_template, request, url_for, redirect, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdj182321jDJSKADJ*213sd'
csrf = CSRFProtect(app)

#Create Data Base
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todolist.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class ListTask(db.Model):
    
    __tablename__ = 'list_task'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    creator: Mapped[str] = mapped_column(String(120), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    
    tasks = relationship("Task", back_populates="fk_tasklist")
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Task(db.Model):
    
    __tablename__ = 'task'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    priority_color: Mapped[str] = mapped_column(String(60), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    task_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('list_task.id'))
    fk_tasklist =relationship("ListTask", back_populates='tasks')


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/todo_list')
def  todo_list():
    task_lists = db.session.execute(db.select(ListTask)).scalars().all()
    
    return render_template('todolist.html', task_lists=task_lists)

@app.route("/task/<int:todolist_id>")
def task(todolist_id):
    todo_list = db.get_or_404(ListTask, todolist_id)
    list_name= todo_list.name
    
    list_id = todo_list.id
    
    tasks =db.session.execute(db.select(Task).where(Task.task_id == todo_list.id)).scalars().all()

    return render_template('task.html', tasks=tasks, list_name=list_name, list_id=list_id)

@app.route("/todo_list/add", methods=['POST', 'GET'])
def todolist_add():
    
    if request.method == 'POST':
        new_list_task = ListTask(
            creator=request.form.get('list_create_name'),
            name=request.form.get('list_name'),
            description=request.form.get('list_description'),
            created_at=datetime.now()
        )
        
        db.session.add(new_list_task)
        db.session.commit()
        
        return redirect(url_for('todo_list'))
    
    return render_template('add_todolist.html')

@app.route('/todo_list/delete/<int:todolist_id>')
def delete_todolist(todolist_id):
    list_task = db.get_or_404(ListTask, todolist_id)
    
    try:
        db.session.delete(list_task)
        db.session.commit()
    except Exception as e:
        print(f"Error en eliminar la lista, error: {e}")

    return redirect(url_for('todo_list'))

@app.route('/add_task', methods=['POST'])
def add_task():
    print('Hola mundo')
    if request.method == 'POST':
        
        name = request.form.get('task_name')
        id_list = request.form.get('list_id')

        # Añadir la nueva tarea a la base de datos
        new_task = Task(
            name=name,
            task_id=id_list,
            completed=False,
            priority_color=None
        )
        
        db.session.add(new_task)
        db.session.commit()

        # Devolver la tarea recién creada con su ID
        return redirect(url_for('task', todolist_id=id_list))

@app.route('/update_task_status/<int:task_id>', methods=['POST'])
def update_task_status(task_id):
    try:
        data = request.get_json()
        completed = data.get('completed')

        task = Task.query.get(task_id)
        if task is None:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        task.completed = completed
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/update_task_priority/<int:task_id>', methods=['POST'])
def update_task_priority(task_id):
    try:
        data = request.get_json()
        priority_color = data.get('priority_color')

        task = Task.query.get(task_id)
        if task is None:
            return jsonify({'success': False, 'error': 'Task not found'}), 404

        task.priority_color = priority_color
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/task/delete/<int:task_id>')
def delete_task(task_id):
    task = db.get_or_404(Task, task_id)
    
    try:
        db.session.delete(task)
        db.session.commit()
    except Exception as e:
        print(f"Error en eliminar la lista, error: {e}")

    return redirect(url_for('task', todolist_id=task.task_id))


if __name__ == '__main__':
    app.run()
