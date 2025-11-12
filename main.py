from flask import Flask, jsonify
import mysql.connector
import os

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))


@app.route('/')
def root():
    return 'Bienvenido Raul'


def sql_call(numero_temporada):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="Ju94714016*",
            database="LaLiga"
        )
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT 
                    el.Nombre_Equipo, 
                    (pn.penaltis_a_favor + pn.penaltis_en_contra)/2 AS media
                FROM 
                    penaltis pn
                JOIN
                    equipos_liga el ON pn.ID_Liga = el.ID_Liga
                JOIN 
                    temporada_liga tl ON tl.ID_Temporada = el.ID_Temporada
                WHERE
                    tl.Temporada = %s
                ORDER BY
                    media DESC
            """, (numero_temporada,))
            datos = cursor.fetchall()
        conn.close()
        return datos
    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return None


@app.route("/Temporada/<numero_temporada>")
def get_temporada(numero_temporada):
    data = sql_call(numero_temporada)
    if data:
        return jsonify(data), 200
    else:
        return jsonify({
            "error": f"No se encontraron datos o hubo un error para la temporada {numero_temporada}"
        }), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)
