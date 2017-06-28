from app import Todo, User, db

db.drop_all()
db.create_all()

admin = User(userid='admin')
guest = User(userid='guest')

admin_todo = Todo(todo="Do this by 10PM", done=False, user= admin)
user_todo = Todo(todo="Let's do this", done=False, user= guest)
db.session.add(admin)  # This will also add admin_address to the session.
db.session.add(guest)  # This will also add guest_address to the session.
db.session.commit()

print User.query.all()
for i in Todo.query.all():
    print i.todo
print Todo.query.all()
