import openai
import requests
import mysql.connector
import json
import os
import re
import ftplib

openai.api_key = "<api_key_openai>"
client = openai
board_id = "uXjVKGRsnZ4"

# Connect with MySQL database
db_host = "
db_port = "3306"
db_name =  ""
db_user =  ""
db_password =  ""

PA_FTP = ""
PA_FTPUSER = ""
PA_COD = ''

# Remove HTML tags from text
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

# Obtener tags de Miro
url_encuesta = "https://api.miro.com/v2/boards/uXjVKGRsnZ4"+board_id+"%3D/items?limit=50&tag_id="
# Encuesta Si o No han hecho
id_si = "3458764600757981880"
id_no = "3458764600757981331"

texto_descripciones = ""

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": ""
}


# Add descriptions, images urls, id's to the Database
# Crea una conexión con la base de datos
conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,password=db_password)

# Crea un cursor para ejecutar comandos SQL
cur = conn.cursor()

# Ejecuta una consulta SQL
sql = "SELECT descripcio FROM teclaCOMIC WHERE tema = '99999'"
cur.execute(sql)

# Obtiene los resultados de la consulta
results_database = cur.fetchall()
if results_database:
    for row in results_database:
        if row[0] != "Escribe aquí tu respuesta...":
            texto_descripciones = texto_descripciones + str(row[0])

#print(texto_descripciones)
conn.commit()
# Cierra la conexión con la base de datos
cur.close()
conn.close()

# Palabras más usadas

completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": "Eres un excelente asistente que analiza textos."},
    {"role": "user", "content": "Dime cuales son las 6 palabras más usadas y con más de 5 caracteres en este texto:"+texto_descripciones+".La respuesta tiene que empezar con 'Las palabras más utilizadas en las descripciones son:'. Después un salto de linea en formato html y después el listado de palabras."}
  ]
)

print(completion.choices[0].message.content)

# Actualizamos el Miro con las palabras más usadas
url = "https://api.miro.com/v2/boards/uXjVKGRsnZ4%3D/shapes/3458764600766788959"

payload = { "data": { "content": completion.choices[0].message.content } }

response = requests.patch(url, json=payload, headers=headers)


#response = requests.get(url, headers=headers)
