import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

def obtener_datos():
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='99Techno.99',
            database='mydb'
        )
        cursor = connection.cursor()

        # Ejecutar consulta
        query = "SELECT * FROM `Ordenes de producción`"
        cursor.execute(query)

        # Obtener resultados
        resultados = cursor.fetchall()

        # Convertir resultados a DataFrame
        columnas = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(resultados, columns=columnas)

        return df
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def graficar_datos(df):
    # Graficar los datos (ejemplo de gráfico de barras)
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df.groupby('Fecha')['Cantidad Producida'].sum().plot(kind='bar')
    plt.title('Cantidad Producida por Fecha')
    plt.xlabel('Fecha')
    plt.ylabel('Cantidad Producida')
    plt.show()

if __name__ == "__main__":
    datos = obtener_datos()
    graficar_datos(datos)

