from app import Todo, User, db

def processMessage(text, userid):
    if text == "LIST":
        print text
        user = db.session.query().filter_by(userid=userid).one()
        if user:
            output = ""
            if len(user.todo) == 0:
                return "The list looks empty!"
            for todo in user.todo:
                output += todo.todo
            return output
        else:
            print "In else"
            user = User(userid=userid)
            db.session.add(user)
            db.session.commit()
            return "The list looks empty!"
