from flask import Flask
from flask import render_template
from flask import redirect
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
import sqlite3
import re
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///info.db"
db = SQLAlchemy(app)

class messageDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.TEXT, unique = False, nullable = False)
    email = db.Column(db.TEXT, unique = False, nullable = False)
    message = db.Column(db.TEXT, unique = False, nullable = False)
class musicDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.TEXT, unique = False, nullable = True)
    locationName = db.Column(db.TEXT, unique = False, nullable = True)
    time = db.Column(db.TEXT, unique = False, nullable = True)
class commentDb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.TEXT, unique = False, nullable = False)
    content = db.Column(db.TEXT, unique = False, nullable = False)
    time = db.Column(db.TEXT, unique = False, nullable = False)
    musicId = db.Column(db.Integer, unique = False, nullable = False)

@app.route("/")
def main_page():
    return render_template("main.html")

@app.route("/searchKey", methods = ["POST"])
def searchKey():
    music = musicDb.query.all()
    key = request.form.get("name")
    database = sqlite3.connect("info.db")
    def regexp(y, x, search=re.search):
        return 1 if search(y, x) else 0
    database.create_function('regexp', 2, regexp)
    sql = '''SELECT title, locationName, time, id FROM music_db
            WHERE title REGEXP ? or locationName REGEXP ? or time REGEXP ?'''
    reg = re.escape(key)
    results = database.execute(sql, [reg, reg, reg])
    i = 0
    title = []
    name = []
    time = []
    id = []
    for result in results:
        title.append(result[0])
        name.append(result[1])
        time.append(result[2])
        id.append(result[3])
        i += 1
    information = [title, name, time, id]
    return render_template("search.html", music = music, key = key, information = information, length = len(title))
    database.close()

@app.route("/search")
def search_page():
    music = musicDb.query.all()
    return render_template("search.html", music = music)

@app.route("/index")
def info_page():
    info = request.args
    database = sqlite3.connect("info.db")
    sql = f'''SELECT location, price, onSales, id FROM music_db
            WHERE title = "{info["title"]}" and locationName = "{info["locationName"]}" and time = "{info["time"]}";'''
    results = database.execute(sql)
    for result in results:
        location = result[0]
        price = result[1]
        onSales = result[2]
        id = result[3]
    locationCity = location[0:3]

    sql = f'''SELECT name, content, time FROM comment_db
            WHERE musicId = {int(info["id"])}'''
    music = database.execute(sql)
    user_name = []
    content = []
    time = []
    for infos in music:
        user_name.append(infos[0])
        content.append(infos[1])
        time.append(infos[2])
    comment = [user_name, content, time]
    length = len(comment[0])

    sql = f'''SELECT 確定病例數 FROM covid
            WHERE covid.縣市 = "{locationCity}"'''
    covid = database.execute(sql)
    covid_num = 0
    for c in covid:
        covid_num += int(c[0])
    
    return render_template("index.html", info = info, location = location, price = price, onSales = onSales, covid_num = covid_num, comment = comment, id = id, length = length)

@app.route("/message", methods=["GET", "POST"])
def addMessage():
    info = request.args
    name = request.form.get("Message Name")
    content = request.form.get("Message Board")
    music_id = int(info["id"])
    time = str(datetime.now())
    if name != "" and content != "":
        p = commentDb(name = name, content = content, time = time, musicId = music_id)
        db.session.add(p)
        db.session.commit()
    return redirect(url_for("info_page", title = info["title"], locationName = info["locationName"], id = info["id"], time = info["time"]))

@app.route("/comment", methods=["GET", "POST"])
def addComment():
    info =request.args
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")
    if name != "" and email != "" and message != "":
        p = messageDb(name = name, email = email, message = message)
        db.session.add(p)
        db.session.commit()
    return redirect(url_for("info_page", title = info["title"], locationName = info["locationName"], id = info["id"], time = info["time"]))

if __name__ == "__main__":
    app.run()