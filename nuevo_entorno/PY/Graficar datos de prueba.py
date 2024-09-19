import mysql.connector
from mysql.connector import Error
import pandas as pd
import matplotlib.pyplot as plt

def obtener_datos():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Cambia esto según tu configuración
            user='root',
            password='99Techno.99',
            database='mydb'
        )
        
        if connection.is_connected():
            print("Conectado a MySQL Server versión", connection.get_server_info())
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM `Ordenes de producción`")  # Ajusta el nombre de la tabla según sea necesario
            datos = cursor.fetchall()
            return datos

    except Error as e:
        print("Error al conectar a MySQL", e)
        return None

    finally:
        if connection and connection.is_connected():
            connection.close()
            print("Conexión a MySQL cerrada")

def graficar_datos(datos):
    if datos is not None:
        df = pd.DataFrame(datos, columns=['OrdenProduccionID', 'Fecha', 'Estado', 'Cantidad Producida', 'ProductoID', 'EmpleadoID', 'Detalles'])
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        
        # Verifica los primeros datos
        print(df.head())
        print(df.dtypes)
        
        # Asegúrate de que 'Cantidad Producida' sea numérico
        df['Cantidad Producida'] = pd.to_numeric(df['Cantidad Producida'], errors='coerce')
        
        # Verifica si hay datos después de la conversión
        print(df['Cantidad Producida'].head())
        
        # Agrupación y gráfico
        grouped_data = df.groupby('Fecha')['Cantidad Producida'].sum()
        print(grouped_data.head())
        
        grouped_data.plot(kind='bar')
        plt.xlabel('Fecha')
        plt.ylabel('Cantidad Producida')
        plt.title('Cantidad Producida por Fecha')
        plt.show()
    else:
        print("No se pudieron obtener datos.")

datos = obtener_datos()
graficar_datos(datos)


