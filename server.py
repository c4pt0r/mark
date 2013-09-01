from flask import Flask, request, jsonify, make_response, render_template, redirect
import json
import hashlib
import pymongo
import uuid
import time
from functools import wraps
app = Flask(__name__)

conn = pymongo.Connection("localhost", 27017)
db = conn.Mark

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.cookies.get("email") is None:
            return json.dumps({"ret":-1, "msg": "login required"})
        return f(*args, **kwargs)
    return decorated_function

def login_page_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.cookies.get("email") is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def args(key, value = None):
    if request.form.get(key, value) != value:
        return request.form.get(key, value)
    if request.args.get(key, value) != value:
        return request.args.get(key, value)
    return value

def get_email_from_token(token):
    if token is None: return None
    u = db.user.find_one({"token": token})
    if u != None:
        return u["email"]
    return None

def record_match_rank(keyword, record_obj):
    tags = record_obj["tags"]
    title = record_obj["title"]
    url = record_obj["url"]
    point = 0
    for tag in tags:
        if keyword in tag:
            point += 5
    if keyword in title:
        point += 3
    if keyword in url:
        point += 1
    return point

def to_dict(mongo_obj):
    del mongo_obj['_id']
    return mongo_obj

######### user handlers ##############
@app.route("/user/register", methods=["GET", "POST"])
def register():
    username = args("email")
    password = args("password")
    if username != None and password != None and db.User.find_one({"email": username}) == None:
        token = hashlib.md5(str(uuid.uuid1())).hexdigest()
        db.user.insert({"email": username,
                        "password": hashlib.md5(password).hexdigest(),
                        "token": token })
        return json.dumps({"ret":0, "token": token, "email": username})
    else:
        return json.dumps({"ret":-1, "msg": "email exists"})

@app.route("/user/login", methods=["GET","POST"])
def login():
    username = args("email")
    password = args("password")
    if password != None:
        password = hashlib.md5(password).hexdigest()
    if username and password:
        u = db.user.find_one({"email": username, "password": password})
        if u != None:
            ret = json.dumps({"ret":0, "token": u["token"], "email": username})
            resp = make_response(ret)
            resp.set_cookie("email", username)
            return resp
    return json.dumps({"ret":-1, "msg": "password error"})

@app.route("/user/logout")
@login_required
def logout():
    ret = json.dumps({"ret":0})
    resp = make_response(ret)
    resp.set_cookie("email", "", expires=0)
    return resp

########## end of user handlers #########

########## record handlers ##########
db.record.save({"auto_incr_id":0})

@app.route("/record/list")
@login_required
def record_list():
    email = request.cookies.get('email')
    query = {"email":email}
    if args("tags") != None:
        tags = args("tags")
        tags = [tag.rstrip().lstrip() for tag in tags.split(",")]
        tags = list(set(tags))
        query["tags"] = {"$in": tags}
    ret = []
    for r in db.record.find(query, {"email":0}):
        ret.append(to_dict(r))
    return json.dumps(ret)

@app.route("/record/add", methods=["POST", "GET"])
def record_add():
    email = request.cookies.get('email')
    if email is None:
        email = get_email_from_token(args("token"))
    if email is None:
        return json.dumps({"ret":-1, "msg": "need login or token"})

    title = args("title")
    url   = args("url", "")
    tags  = args("tags", "")
    ts    = int(time.time())
    datetime = time.strftime("%Y%m%d", time.localtime())
    hash = hashlib.md5(url + datetime).hexdigest()
    item = db.record.find_one({"hash":hash, "email":email}, {"id":1, "tags":1})
    if item  != None:
        return json.dumps({"ret":0, "id":item["id"], "tags": item["tags"]})
    if title != None:
        tags = [tag.rstrip().lstrip() for tag in tags.split(",")]
        tags = list(set(tags))
        id = db.record.find_and_modify(update = {"$inc":{"auto_incr_id": 1}}, new = True).get("auto_incr_id")
        db.record.insert({"id" : id,
                          "title": title,
                          "url": url,
                          "tags": tags,
                          "ts": ts,
                          "hash" : hash,
                          "email": email})
        return json.dumps({"ret":0, "id":id})
    return json.dumps({"ret":-2})

@app.route("/record/update", methods=["POST", "GET"])
def record_update():
    email = request.cookies.get('email')
    if email is None:
        email = get_email_from_token(args("token"))
    if email is None:
        return json.dumps({"ret":-1, "msg": "need login or token"})

    title = args("title")
    url   = args("url", "")
    tags  = args("tags", "")
    tags = list(set([tag.rstrip().lstrip() for tag in tags.split(",")]))
    try:
        id = int(args("id"))
    except:
        return json.dumps({"ret":-2, "msg": "id invalid"})
    db.record.find_and_modify(query= {"id":id},update = {"$set": {"title":title, "tags":tags}})
    return json.dumps({"ret":0, "id":id})

@app.route("/record/search")
@login_required
def record_search():
    keyword = args("s")
    email = request.cookies.get('email')
    ret = []
    for r in db.record.find({"email":email}, {"ts":1, "title":1, "url":1, "tags":1}):
        point = record_match_rank(keyword, r)
        if point > 0:
            r["rank"] = point
            ret.append(to_dict(r))
    return json.dumps(ret)

############### pages ####################
@app.route("/home")
@login_page_required
def home_handler():
    email = request.cookies.get("email")
    return render_template("home.html", email=email)

@app.route("/login")
def login_page_handler():
    return render_template("login.html")

@app.route("/register")
def register_page_handler():
    return render_template("register.html")

if __name__ == "__main__":
    app.debug = True
    app.run()
