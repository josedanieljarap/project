from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import format_decimal, format_percentage, login_required

# Configure application
application = Flask(__name__)

# Custom filter
application.jinja_env.filters["dec"] = format_decimal
application.jinja_env.filters["per"] = format_percentage

# Configure session to use filesystem (instead of signed cookies)
application.config["SESSION_PERMANENT"] = False
application.config["SESSION_TYPE"] = "filesystem"
Session(application)

# Import SQLite database
db = SQL("sqlite:///mosquitos.db")

@application.route("/")
@login_required
def index():
    table_1 = db.execute("SELECT * FROM mortalidad")
    table_2 = db.execute("SELECT * FROM frecuencias_F1534C")
    table_3 = db.execute("SELECT * FROM frecuencias_V419L")
    return render_template("index.html", table_1=table_1, table_2=table_2, table_3=table_3, session=session)


@application.route("/sobre")
@login_required
def sobre():
    return render_template("/sobre.html")


@application.route("/editar", methods=["POST", "GET"])
@login_required
def editar():
    if request.method == "POST":
        if request.form.get("tabla") == "Tabla 1":
            return render_template("/editar1.html")
        elif request.form.get("tabla") == "Tabla 2":
            return render_template("/editar2.html")
        elif request.form.get("tabla") == "Tabla 3":
            return render_template("/editar3.html")
        else:
            return render_template("apology.html", mensaje="Debe especificar una tabla")
    else:
        return render_template("/editar.html")


@application.route("/editar1", methods=["POST"])
@login_required
def editar1():
    distrito = request.form.get("distrito").upper()
    try:
        total = int(request.form.get("total"))
    except:
        return render_template("apology.html", mensaje="el número total de mosquitos es inválido.")
    try:
        muertos = int(request.form.get("muertos"))
    except:
        return render_template("apology.html", mensaje="el número de mosquitos muertos es inválido.")
    sobrevivientes = total - muertos
    mortalidad = muertos / total * 100

    db.execute("INSERT INTO mortalidad \
        (poblacion, total, muertos, sobrevivientes, mortalidad) \
            VALUES(?, ?, ?, ?, ?)", distrito, total, muertos, sobrevivientes, mortalidad)

    return redirect("/")


@application.route("/editar2", methods=["POST"])
@login_required
def editar2():
    distrito = request.form.get("distrito").upper()
    id = db.execute("SELECT id FROM mortalidad WHERE poblacion = ?", distrito)
    if id == []:
        return render_template("apology.html", mensaje="debe especificar un distrito que esté en la Tabla 1.")
    else:
        id = id[0]["id"]
    try:
        n = int(request.form.get("n"))
    except:
        return render_template("apology.html", mensaje="el número N es inválido.")
    try:
        ff = int(request.form.get("ff"))
    except:
        return render_template("apology.html", mensaje="el número FF es inválido.")
    try:
        fc = int(request.form.get("fc"))
    except:
        return render_template("apology.html", mensaje="el número FC es inválido.")
    try:
        cc = int(request.form.get("cc"))
    except:
        return render_template("apology.html", mensaje="el número CC es inválido.")
    p = (fc + 2 * cc) / (2 * n)
    q = (fc + 2 * ff) / (2 * n)

    db.execute("INSERT INTO frecuencias_F1534C \
        (id, poblacion, N, FF, FC, CC, p, q) \
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)", id, distrito, n, ff, fc, cc, p, q)

    return redirect("/")


@application.route("/editar3", methods=["POST"])
@login_required
def editar3():
    distrito = request.form.get("distrito").upper()
    id = db.execute("SELECT id FROM mortalidad WHERE poblacion = ?", distrito)
    if id == []:
        return render_template("apology.html", mensaje="debe especificar un distrito que esté en la Tabla 1.")
    else:
        id = id[0]["id"]
    try:
        n = int(request.form.get("n"))
    except:
        return render_template("apology.html", mensaje="el número N es inválido.")
    try:
        vv = int(request.form.get("vv"))
    except:
        return render_template("apology.html", mensaje="el número VV es inválido.")
    try:
        vl = int(request.form.get("vl"))
    except:
        return render_template("apology.html", mensaje="el número VL es inválido.")
    try:
        ll = int(request.form.get("ll"))
    except:
        return render_template("apology.html", mensaje="el número LL es inválido.")
    p = (vl + 2 * ll) / (2 * n)
    q = (vl + 2 * vv) / (2 * n)

    db.execute("INSERT INTO frecuencias_V419L \
        (id, poblacion, N, VV, VL, LL, p, q) \
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)", id, distrito, n, vv, vl, ll, p, q)

    return redirect("/")


@application.route("/eliminar", methods=["GET", "POST"])
@login_required
def eliminar():
    if request.method == "POST":
        distrito = request.form.get("distrito").upper()
        tablas = request.form.getlist("tabla")
        for i in reversed(tablas):
            db.execute("DELETE FROM ? WHERE poblacion = ?", i, distrito)
        return redirect("/")
    else:
        return render_template("/eliminar.html")


@application.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", mensaje="debe proveer un nombre de usuario.")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", mensaje="debe proveer un password.")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").upper())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", mensaje="usuario y/o password inválido.")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["tipo"] = rows[0]["type"]

        print("oe causa")
        print(session)

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        print("oe causa")
        print(session)
        
        return render_template("login.html")


@application.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@application.route("/registrar", methods=["GET", "POST"])
def registrar():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username").upper()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        tipo = request.form.get("tipo")
        if not username:
            return render_template("apology.html", mensaje="debe proveer un nombre de usuario.")
        elif db.execute("SELECT * FROM users WHERE username = ?", username):
            return render_template("apology.html", mensaje="este usuario ya ha sido tomado.")
        elif not password:
            return render_template("apology.html", mensaje="debe proveer un password.")
        elif not confirmation:
            return render_template("apology.html", mensaje="debe escribir el password otra vez.")
        elif password != confirmation:
            return render_template("apology.html", mensaje="los passwords no son iguales.")
        elif not tipo:
            return render_template("apology.html", mensaje="debe indicar el tipo de cuenta.")
        else:
            hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash, type) VALUES(?, ?, ?)", username, hash, tipo)
            user_logged = db.execute("SELECT id FROM users WHERE username = ?", username)
            session["user_id"] = user_logged[0]["id"]
            session["tipo"] = tipo

            return redirect("/")
    else:
        return render_template("registrar.html")



@application.route("/contraseña", methods=["GET", "POST"])
def contraseña():
    """Register user"""
    if request.method == "POST":
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not password:
            return render_template("apology.html", mensaje="debe proveer un password.")
        elif not confirmation:
            return render_template("apology.html", mensaje="debe escribir el password otra vez.")
        elif password != confirmation:
            return render_template("apology.html", mensaje="los passwords no son iguales.")
        else:
            hash = generate_password_hash(password)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])
            return redirect("/")
    else:
        return render_template("contraseña.html")