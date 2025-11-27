from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb

app = Flask(__name__)
app.secret_key = "X6bcYYVWiKi2YFvG9dErDszBeJVsWRe0YFv"


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'registro'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)



def crear_tabla():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("USE registro;")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios(
                id INT PRIMARY KEY AUTO_INCREMENT,
                nombre VARCHAR(100),
                apellido VARCHAR(100),
                email VARCHAR(100),
                password VARCHAR(255),
                genero VARCHAR(20),
                experiencia VARCHAR(50),
                objetivo VARCHAR(100),
                alergias VARCHAR(255),
                intolerancias VARCHAR(255),
                dieta VARCHAR(100),
                no_gusta VARCHAR(255)
            )
        """)
        mysql.connection.commit()
        cursor.close()



def email_existe(email):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    cursor.close()
    return usuario is not None



def registrar_usuario(datos):
    try:
        cursor = mysql.connection.cursor()
        sql = """
            INSERT INTO usuarios 
            (nombre, apellido, email, password, genero, experiencia, objetivo, alergias, intolerancias, dieta, no_gusta)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, datos)
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print("ERROR AL REGISTRAR:", e)
        return False



@app.route('/usuarios')
def obtener_usuarios():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM usuarios")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)



@app.route("/")
def lobby():
    return render_template("lobby.html")


@app.route("/inicio")
def inicio():
    if not session.get("usuario"):
        return redirect(url_for("sesion"))
    return render_template("inicio.html")



@app.route("/sesion", methods=["GET", "POST"])
def sesion():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")


        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()

        if not usuario:
            return render_template("sesion.html", error="Correo o contraseña incorrectos")
        password_bd = usuario["password"]
        if password_bd == password:
            session["usuario"] = usuario["email"]
            session["nombre"] = usuario["nombre"]
            session["apellido"] = usuario["apellido"]
            

            return redirect(url_for("perfil"))

        return render_template("sesion.html", error="Correo o contraseña incorrectos")

    return render_template("sesion.html")





@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":

        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        email = request.form.get("email")
        password = request.form.get("password")
        genero = request.form.get("genero")
        experiencia = request.form.get("experiencia")
        objetivo = request.form.get("objetivo")
        alergias = request.form.get("alergias")
        intolerancias = request.form.get("intolerancias")
        dieta = request.form.get("dieta")
        no_gusta = request.form.get("no_gusta")

        if email_existe(email):
            return render_template("formulario.html", error="Ese email ya está registrado")

        hashed = generate_password_hash(password)

        exito = registrar_usuario((nombre, apellido, email, hashed, genero, experiencia,
                                objetivo, alergias, intolerancias, dieta, no_gusta))

        if exito:
            session["usuario"] = email
            return redirect(url_for("inicio"))

        return render_template("formulario.html", error="Error al registrar usuario")

    return render_template("formulario.html")


@app.route("/perfil")
def perfil():
    if "usuario" not in session:
        return redirect(url_for("sesion"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s", (session["usuario"],))
    usuario = cursor.fetchone()
    cursor.close()

    return render_template("perfil.html", usuario=usuario)


@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('sesion'))
    return render_template("dashboard.html", usuario=session['usuario'])



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("lobby"))


@app.route("/dieta", methods=["GET", "POST"])
def dieta():

    peso = 60
    altura = 165
    objetivo = "Bajar de peso"

    if objetivo == "Bajar de peso":
        desayuno = "Avena con fruta y nueces"
        comida = "Pollo a la plancha con verduras"
        cena = "Ensalada ligera con proteína"
        snack = "Yogurt griego o una manzana"
    elif objetivo == "Subir masa muscular":
        desayuno = "Huevos con avena y plátano"
        comida = "Carne magra con arroz y verduras"
        cena = "Atún con tortillas de maíz"
        snack = "Licenciado de proteína o frutos secos"
    else:
        desayuno = "Pan integral con huevo"
        comida = "Pechuga con pasta integral"
        cena = "Sándwich integral con jamón de pavo"
        snack = "Fruta o yogurt"

    hora_desayuno = "8:00 AM"
    hora_comida = "2:00 PM"
    hora_cena = "8:00 PM"

    return render_template(
        "dieta.html",
        peso=peso,
        altura=altura,
        objetivo=objetivo,
        desayuno=desayuno,
        comida=comida,
        cena=cena,
        snack=snack,
        hora_desayuno=hora_desayuno,
        hora_comida=hora_comida,
        hora_cena=hora_cena
    )



@app.route("/horarioC", methods=["GET", "POST"])
def horario():
    meta = 2000
    actual = 0
    porcentaje = 0
    meta_semanal = 14000
    actual_semanal = 0
    porcentaje_semanal = 0

    if request.method == "POST":
        try:
            meta = float(request.form.get("meta", meta))
            actual = float(request.form.get("actual", actual))
            porcentaje = min((actual / meta) * 100, 100) if meta > 0 else 0

            actual_semanal = float(request.form.get("actual_semanal", actual * 3))
            porcentaje_semanal = min((actual_semanal / meta_semanal) * 100, 100)
        except ValueError:
            pass

    return render_template(
        "horarioC.html",
        meta=int(meta),
        actual=int(actual),
        porcentaje=porcentaje,
        meta_semanal=int(meta_semanal),
        actual_semanal=int(actual_semanal),
        porcentaje_semanal=porcentaje_semanal
    )


@app.route("/recetas")
def recetas():
    return render_template("recetas.html")


@app.route("/acerca")
def acerca():
    return render_template("acerca.html")


@app.route("/ejercicio", methods=["GET", "POST"])
def ejercicio():
    porcentaje = 0
    if request.method == "POST":
        completado = int(request.form.get("completado", 0))
        total = int(request.form.get("total", 1))
        porcentaje = min(100, (completado / total) * 100)
    return render_template("ejercicio.html", porcentaje=porcentaje)



@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    resultado = None

    if request.method == 'POST':
        genero = request.form.get('genero')
        peso = float(request.form.get('peso'))
        altura = float(request.form.get('altura'))
        edad = int(request.form.get('edad'))

        imc_valor = round(peso / (altura * altura), 1)

        if imc_valor < 18:
            clasificacion = "Bajo peso"
            riesgo = "Riesgo bajo pero requiere vigilancia nutricional."
        elif imc_valor < 25:
            clasificacion = "Peso normal"
            riesgo = "Riesgo bajo, mantener hábitos saludables."
        elif imc_valor < 30:
            clasificacion = "Sobrepeso"
            riesgo = "Aumento del riesgo de enfermedades."
        elif imc_valor < 35:
            clasificacion = "Obesidad Grado I"
            riesgo = "Riesgo moderado, recomendable atención médica."
        elif imc_valor < 40:
            clasificacion = "Obesidad Grado II"
            riesgo = "Riesgo alto, seguimiento profesional necesario."
        else:
            clasificacion = "Obesidad Grado III"
            riesgo = "Riesgo muy alto, intervención médica inmediata."

        resultado = {
            "genero": genero,
            "edad": edad,
            "imc": imc_valor,
            "clasificacion": clasificacion,
            "riesgo": riesgo
        }

    return render_template("calculadora.html", resultado=resultado)


@app.route("/info")
def info():
    return render_template("info.html")

if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)
