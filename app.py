from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import requests 
import MySQLdb
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "zr7gMW89PD2L3Uo4UgdCt9hMN8wGeex7WV9syxv3"


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
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # Cursor tipo diccionario
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
    datos_usuario = None
    dieta_generada = None

    if request.method == "POST":
        edad = int(request.form["edad"])
        peso = float(request.form["peso"])
        altura = float(request.form["altura"])
        objetivo = request.form["objetivo"]

        # Guardar datos en sesión
        session["nutri_datos"] = {
            "edad": edad,
            "peso": peso,
            "altura": altura,
            "objetivo": objetivo
        }

        datos_usuario = session["nutri_datos"]

        # Dieta según objetivo
        if objetivo == "bajar":
            dieta_generada = [
                "Desayuno: Avena con manzana",
                "Comida: Pollo a la plancha con verduras",
                "Cena: Ensalada verde con atún",
                "Snack: Yogur griego"
            ]
        elif objetivo == "subir":
            dieta_generada = [
                "Desayuno: Huevos + pan integral",
                "Comida: Pasta con carne molida",
                "Cena: Sándwich de pavo",
                "Snack: Almendras"
            ]
        else:  
            dieta_generada = [
                "Desayuno: Smoothie de frutas",
                "Comida: Arroz + pollo + ensalada",
                "Cena: Wrap de vegetales",
                "Snack: Gelatina light"
            ]

    return render_template("dieta.html",
                            datos=datos_usuario,
                            dieta=dieta_generada)



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
                    "calorias": nutrientes.get("Energy", "N/A"),
                    "proteinas": nutrientes.get("Protein", "N/A"),
                    "grasas": nutrientes.get("Total lipid (fat)", "N/A"),
                    "carbohidratos": nutrientes.get("Carbohydrate, by difference", "N/A")
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



@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    tipo = request.args.get('tipo')
    resultado_imc = None
    resultado_tmb = None
    resultado_gct = None
    resultado_pi = None
    resultado_macros = None
    resultado_receta = None

    if request.method == 'POST':
        # Calculadora de IMC
        if tipo == 'imc':
            genero = request.form.get('genero')
            peso = float(request.form.get('peso'))
            altura = float(request.form.get('altura'))

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

            resultado_imc = {
                "imc": imc_valor,
                "clasificacion": clasificacion,
                "riesgo": riesgo
            }


        elif tipo == 'tmb':
            genero = request.form.get('genero')
            peso = float(request.form.get('peso'))
            altura = float(request.form.get('altura'))
            edad = int(request.form.get('edad'))

            if genero == 'Masculino':
                tmb_valor = round(66 + (13.7 * peso) + (5 * altura) - (6.8 * edad), 2)
            else:
                tmb_valor = round(655 + (9.6 * peso) + (1.8 * altura) - (4.7 * edad), 2)

            resultado_tmb = {"tmb": tmb_valor}

        elif tipo == 'gct':
            tmb = float(request.form.get('tmb'))
            actividad = float(request.form.get('actividad'))
            gct_valor = round(tmb * actividad, 2)
            resultado_gct = {"gct": gct_valor}


        elif tipo == 'pesoideal':
            altura = float(request.form.get('altura'))
            # Fórmula de Devine (ejemplo para peso ideal en kg)
            peso_ideal = round(50 + 0.9 * (altura - 152), 1)  # altura en cm
            resultado_pi = {"peso": peso_ideal}


        elif tipo == 'macros':
            calorias = float(request.form.get('calorias'))
            objetivo = request.form.get('objetivo')

            if objetivo == 'perdida':
                proteina = round(calorias * 0.3 / 4, 1)
                grasas = round(calorias * 0.25 / 9, 1)
                carbs = round(calorias * 0.45 / 4, 1)
            elif objetivo == 'ganancia':
                proteina = round(calorias * 0.25 / 4, 1)
                grasas = round(calorias * 0.25 / 9, 1)
                carbs = round(calorias * 0.5 / 4, 1)
            else:  
                proteina = round(calorias * 0.3 / 4, 1)
                grasas = round(calorias * 0.3 / 9, 1)
                carbs = round(calorias * 0.4 / 4, 1)

            resultado_macros = {
                "proteina": proteina,
                "grasas": grasas,
                "carbs": carbs
            }

        elif tipo == 'receta':
            ingredientes_texto = request.form.get('ingredientes')

            calorias = 0
            proteina = 0
            grasas = 0
            carbs = 0
            for linea in ingredientes_texto.splitlines():
            
                if 'arroz' in linea.lower():
                    calorias += 130
                    proteina += 2.5
                    grasas += 0.3
                    carbs += 28
                elif 'huevo' in linea.lower():
                    calorias += 70
                    proteina += 6
                    grasas += 5
                    carbs += 1
                elif 'pollo' in linea.lower():
                    calorias += 165
                    proteina += 31
                    grasas += 3.6
                    carbs += 0
            resultado_receta = {
                "calorias": calorias,
                "proteina": proteina,
                "grasas": grasas,
                "carbs": carbs
            }

    return render_template(
        "calculadora.html",
        resultado_imc=resultado_imc,
        resultado_tmb=resultado_tmb,
        resultado_gct=resultado_gct,
        resultado_pi=resultado_pi,
        resultado_macros=resultado_macros,
        resultado_receta=resultado_receta
    )


@app.route("/info")
def info():
    return render_template("info.html")

if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)
