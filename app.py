from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb
import requests
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "zr7gMW89PD2L3Uo4UgdCt9hMN8wGeex7WV9syxv3"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'registro2'

mysql = MySQL(app)


def crear_tabla():
    with app.app_context():
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    nombre VARCHAR(100),
                    apellido VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
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
        except Exception as e:
            print("ERROR AL CREAR TABLA:", e)




def email_existe(email):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE email=%s", (email,))
        resultado = cursor.fetchone()
        cursor.close()
        return bool(resultado)
    except Exception as e:
        print("Error verificando email:", e)
        return False




@app.route('/usuarios')
def obtener_usuarios():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
        usuario = cursor.fetchone()
        cursor.close()

        if not usuario:
            return render_template("sesion.html", error="Correo o contraseña incorrectos")

        if check_password_hash(usuario["password"], password):
            session["usuario"] = usuario["email"]
            session["nombre"] = usuario["nombre"]
            session["apellido"] = usuario["apellido"]
            return redirect(url_for("perfil"))
        else:
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
        objetivo = request.form.get("objetivos")
        alergias = request.form.get("alergias")
        intolerancias = request.form.get("intolerancias")
        dieta = request.form.get("dietas")
        no_gusta = request.form.get("no_gustan")

        if email_existe(email):
            return render_template("formulario.html", error="Ese email ya está registrado")

        try:
            hashed = generate_password_hash(password)

            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO usuarios
                (nombre, apellido, email, password, genero, experiencia, objetivo,
                alergias, intolerancias, dieta, no_gusta)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (nombre, apellido, email, hashed, genero, experiencia, objetivo,
                    alergias, intolerancias, dieta, no_gusta))

            mysql.connection.commit()
            cursor.close()

            session["usuario"] = email

            return redirect(url_for("perfil"))

        except Exception as e:
            print("ERROR AL INSERTAR USUARIO:", e)
            return render_template("formulario.html", error="Error al registrar usuario")

    return render_template("formulario.html")




@app.route("/perfil")
def perfil():
    if "usuario" not in session:
        return redirect(url_for("sesion"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE email=%s", (session["usuario"],))
    usuario = cursor.fetchone()
    cursor.close()

    return render_template("perfil.html", usuario=usuario)






@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("sesion"))
    return render_template("dashboard.html", usuario=session["usuario"])



@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("lobby"))




@app.route("/dieta", methods=["GET", "POST"])
def dieta():
    datos_usuario = None
    dieta_generada = None

    if request.method == "POST":
        edad = int(request.form["edad"])
        peso = float(request.form["peso"])
        altura = float(request.form["altura"])
        objetivo = request.form["objetivo"]

        session["nutri_datos"] = {
            "edad": edad,
            "peso": peso,
            "altura": altura,
            "objetivo": objetivo
        }

        datos_usuario = session["nutri_datos"]

        if objetivo == "bajar":
            dieta_generada = [
                "Desayuno: Avena con manzana",
                "Comida: Pollo con verduras",
                "Cena: Ensalada con atún",
                "Snack: Yogur"
            ]
        elif objetivo == "subir":
            dieta_generada = [
                "Desayuno: Huevos + pan integral",
                "Comida: Pasta con carne",
                "Cena: Sándwich de pavo",
                "Snack: Almendras"
            ]
        else:
            dieta_generada = [
                "Desayuno: Smoothie",
                "Comida: Arroz + pollo",
                "Cena: Wrap",
                "Snack: Gelatina"
            ]

    return render_template("dieta.html", datos=datos_usuario, dieta=dieta_generada)




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



@app.route("/recetas", methods=["GET", "POST"])
def recetas():
    resultados = []

    if request.method == "POST":
        busqueda = request.form.get("buscar")

        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            "api_key": "zr7gMW89PD2L3Uo4UgdCt9hMN8wGeex7WV9syxv3",
            "query": busqueda,
            "pageSize": 10
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            foods = data.get("foods", [])

            for item in foods:
                nutrientes = {n["nutrientName"]: n["value"] for n in item.get("foodNutrients", [])}

                resultados.append({
                    "nombre": item.get("description"),
                    "ingredientes": item.get("ingredients"),
                    "descripcion": item.get("additionalDescriptions"),
                    "calorias": nutrientes.get("Energy"),
                    "proteinas": nutrientes.get("Protein"),
                    "grasas": nutrientes.get("Total lipid (fat)"),
                    "carbohidratos": nutrientes.get("Carbohydrate, by difference")
                })

    return render_template("recetas.html", resultados=resultados)



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



@app.route("/calculadora", methods=["GET", "POST"])
def calculadora():
    return render_template("calculadora.html")



@app.route("/info")
def info():
    return render_template("info.html")



if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)
