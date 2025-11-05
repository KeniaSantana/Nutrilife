from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/sesion")
def sesion():
    return render_template("sesion.html")

@app.route("/formulario")
def registro():
    return render_template("formulario.html")

@app.route("/dieta")
def dieta():
    return render_template("dieta.html")

@app.route("/horarioC")
def horario():
    return render_template("horarioC.html")

@app.route("/recetas")
def recetas():
    return render_template("recetas.html")

@app.route("/acerca")
def acerca():
    return render_template("acerca.html")

@app.route("/ejercicio")
def ejercicio():
    return render_template("ejercicio.html")

if __name__ == "__main__":
    app.run(debug=True)
