from flask import Flask, jsonify, request
import mysql.connector
import json

# IMPORTANTE: En un entorno de producción, evita las conexiones de base de datos globales
# y utiliza un pool de conexiones o crea y cierra la conexión por cada solicitud.
# Para este ejemplo, mantendremos tu conexión global pero arreglaremos el uso del cursor.
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="Ju94714016*",
        database="LaLiga"
    )
except mysql.connector.Error as err:
    print(f"Error al conectar con MySQL: {err}")
    # En una aplicación real, deberías manejar esto de forma más elegante
    mydb = None

app = Flask(__name__)


@app.route('/')
def root():
    # Mensaje de bienvenida
    return 'Bienvenido Raul'


def sql_call(numero_temporada):
    # Verifica si la conexión a la base de datos es válida
    if not mydb:
        return None

    # CORRECCIÓN CRÍTICA: Usa un cursor local dentro de un bloque 'with'.
    # Esto cierra automáticamente el cursor después del bloque, liberando el buffer de resultados.
    # dictionary=True devuelve los resultados como diccionarios (nombre_columna: valor).
    try:
        # Abre la conexion con la DB
        with mydb.cursor(dictionary=True) as cursor:
            # Consulta SQL - NOTA: La interpolación con f-string es menos segura que las consultas parametrizadas
            cursor.execute(f"""
                SELECT 
                    el.Nombre_Equipo, (pn.penaltis_a_favor + pn.penaltis_en_contra)/2 as media
                FROM 
                    penaltis pn
                JOIN
                    equipos_liga el ON pn.ID_Liga = el.ID_Liga
                JOIN 
                    temporada_liga tl ON tl.ID_Temporada = el.ID_Temporada
                WHERE
                    tl.Temporada = '{numero_temporada}'
                ORDER BY
                    media DESC

            """)
            # Usa fetchall() para recuperar TODOS los resultados, asegurando que el buffer se limpie
            datos = cursor.fetchall()
            return datos

    except mysql.connector.Error as err:
        # Registra el error si la ejecución del SQL falla
        print(f"Error de base de datos durante la consulta: {err}")
        return None

# Endpoint GET: Devuelve una lista de diccionarios (equipos) para una temporada dada


@app.route("/Temporada/<numero_temporada>")
def get_temporada(numero_temporada):
    data = sql_call(numero_temporada)

    if data:
        return jsonify(data), 200
    else:
        # Devuelve un 404 (No encontrado) si no se encuentran datos
        mensaje_error = f"No se encontraron datos para la temporada {numero_temporada} o hubo un error en la base de datos."
        return jsonify({"error": mensaje_error}), 404


if __name__ == '__main__':
    app.run(debug=True)
