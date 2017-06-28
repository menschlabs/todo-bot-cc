from app import Todo, User, db


def processMessage(text, sender):
    try:
        user = User.query.filter(User.userid == sender).one()
        if text.startswith("LIST"):
            return getTodos(user)
        #if user.todo:
        #    print todo
        #else:
        #    return
    except:
        user = User(userid=sender)
        db.session.add(user)
        db.session.commit()
        return "Welcome to the Todo BOT!"


def getTodos(user):
    output = ""
    if user.todo:
        for todo in user.todo:
            output += "#%d %s" % (todo.id, todo.todo)
    else:
        output = "Your todo list looks empty!"
    return output


if __name__ == '__main__':
    processMessage("Hello", "abcde1")
