import requests

# URL de la API de autenticación (WSAA) en homologación
url_wsaa = 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms'

# Ruta al archivo TRA firmado (.sig)
path_to_signed_tra = 'C:/Users/Usuario/Desktop/Gian/RV Grafica py/nuevo_entorno/PY/TRA.xml.sig'

# Leer el archivo binario (archivo firmado TRA.xml.sig)
with open(path_to_signed_tra, 'rb') as f:
    signed_tra = f.read()

# Headers de la solicitud HTTP
headers = {
    'Content-Type': 'application/octet-stream'  # Indicamos que enviamos un archivo binario
}

# Enviar la solicitud POST a la API de AFIP
response = requests.post(url_wsaa, data=signed_tra, headers=headers)

# Verificar la respuesta de AFIP
if response.status_code == 200:
    print("Solicitud exitosa. Respuesta de AFIP obtenida.")
    # Aquí deberías recibir un XML con el Token y el Sign
    print("Respuesta de AFIP:", response.text)
    # Guardar la respuesta en un archivo si es necesario
    with open('respuesta_token_sign.xml', 'w') as f:
        f.write(response.text)
else:
    print(f"Error: Código de estado {response.status_code}")
    print("Respuesta de AFIP:", response.text)
