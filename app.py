from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)


@app.route("/")
def inicio():
    return render_template("inicio.html")

@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/dieta")
def dieta():
    return render_template("dieta.html")

@app.route("/acerca")
def acerca():
    return render_template("acerca.html")

@app.route("/horario")
def horario():
    return render_template("horario.html")

@app.route("/recetas")
def recetas():
    return render_template("recetas.html")


@app.route("/acerca")
def acerca():
    return render_template("acerca.html")


if __name__ == "__main__":
    app.run(debug=True)