import psycopg2
from psycopg2 import sql

# Parámetros de conexión
DB_PARAMS = {
    "dbname": "ranpubackenddatabase",
    "user": "ranpubackenddatabase_user",
    "password": "pKqQl2aSzKeFiqvsR5pUEUFipbWWcgox",
    "host": "dpg-ctgraj0gph6c73ck0ppg-a.oregon-postgres.render.com",
    "port": 5432
}

# Función para ejecutar un SELECT en la base de datos
def execute_select(query):
    try:
        # Conectarse a la base de datos
        connection = psycopg2.connect(**DB_PARAMS)
        cursor = connection.cursor()
        
        # Ejecutar la consulta
        cursor.execute(query)
        
        # Obtener los resultados
        rows = cursor.fetchall()
        
        # Imprimir resultados
        for row in rows:
            print(row)
        
    except Exception as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        # Cerrar la conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Consulta a ejecutar (modificar según tu necesidad)
query = "SELECT * FROM estados_impresoras LIMIT 10;"  # Reemplaza 'tu_tabla' con el nombre de tu tabla

# Ejecutar la consulta
if __name__ == "__main__":
    execute_select(query)
