from functools import wraps
from flask import redirect, url_for
from flask_login import current_user
from . import application

def relevantsMap(classid):
    relevants = application.getClazzDetails(classid)
    relevantsList = relevants.getRelevants()
    clazzRelevants = {}
    for relevant in relevantsList:
        #print(relevant.read)
        usergroup_name = relevant.usergroup
        #print(usergroup_name)
        clazzRelevants[usergroup_name] = {
            "read": relevant.read,
            "create": relevant.create,
            "delete": relevant.delete,
            "search": relevant.search,
            "edit": relevant.edit
        }
    return clazzRelevants
def verify_relevant(typeRelevant):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            classid = kwargs.get('classid')
            clazzRelevants = relevantsMap(classid)
            if not current_user.is_authenticated or not current_user.usergroup:
                return redirect(url_for('application.index'))
            
            userGroup = current_user.usergroup
            #print(userGroup)
            #print(clazzRelevants.get(userGroup, {}).get(typeRelevant))
            if clazzRelevants.get(userGroup, {}).get(typeRelevant) == False  or not current_user.usergroup:
                return redirect(url_for('application.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator