import openai
import requests
import mysql.connector
import json
import os
import re
import ftplib

openai.api_key = "<aqui clave openai>"
client = openai
board_id = "<aqui id del board de Miro>"
image_displacement_x = 996
image_displacement_y = 1085

# Connect with MySQL database
db_host = "<url bbdd mysql>"
db_port = "<puerto bbdd>"
db_name =  "<nombre bbdd>"
db_user =  "<nombre usuario bbdd>"
db_password =  "<pwd bbdd>"

PA_FTP = "<direccion servidor ftp>"
PA_FTPUSER = "<usuario ftp>"
PA_COD = '<codigo ftp>'

# Remove HTML tags from text
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)

# Images from the Miro board
url = "https://api.miro.com/v2/boards/"+board_id+"=/images"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer <token Miro developer>"
}

# Generate images from text description in a shape from users
# Note 1
list_notes = ["3458764600732344372", "3458764600733064841", "3458764600733345470", "3458764600733488492","3458764600733488572","3458764600733607113","3458764600733607536","3458764600733607540","3458764600733607544","3458764600733607548","3458764600733607552","3458764600733607556","3458764600751531396","3458764600751531400","3458764600751531404","3458764600751531408","3458764600751531412","3458764600751531416"]
list_descriptions = []
list_urls = []
index = 0
index_x = 0
index_y = 0
for x in list_notes:
    url_note = "https://api.miro.com/v2/boards/"+board_id+"%3D/shapes/"+x
    response = requests.get(url_note, headers=headers).json()
    text_description = remove_tags(response["data"]["content"])
    list_descriptions.append(text_description)
    print(text_description)

    if text_description != "Escribe aquí tu respuesta...":
        response_image = client.images.generate(
          model="dall-e-3",
          prompt="Create a realistic image based on this description:"+text_description,
          n=1,
          size="1024x1024"
        )
        print(response_image.data[0].url)
        payload = { "data": { "url": response_image.data[0].url },"position":{"x":3597+image_displacement_x*index_x,"y":1623+image_displacement_y*index_y},"geometry":{"width":449} }
        response = requests.post(url, json=payload, headers=headers)
        print(response)
        resinfografria = requests.get(response_image.data[0].url)

        creaName = str(list_notes[index]) + "_" + str(20000) + ".jpg"

        with open(creaName, 'wb') as f:
            f.write(resinfografria.content)

        ftp_server = ftplib.FTP(PA_FTP, PA_FTPUSER, PA_COD)
        file = open(creaName, 'rb')  # file to send
        # Read file in binary mode
        ftp_server.storbinary('STOR ' + creaName, file)
        ftp_server.quit()
        file.close()  # close file and FTP
        list_urls.append(creaName)
    else:
        print("No hay respuesta todavía para este usuario.")
        list_urls.append("-")
    index = index + 1
    if index>=6 and index<=11:
        if index == 6:
            index_x = 0
            index_y = 1
        else:
            index_x = index_x + 1
            index_y = 1
    elif index <= 5:
        index_y = 0
        index_x = index_x + 1
    elif index>=12 and index<=17:
        if index == 12:
            index_x = 0
            index_y = 2
        else:
            index_x = index_x + 1
            index_y = 2

# Add descriptions, images urls, id's to the Database
# Crea una conexión con la base de datos
conn = mysql.connector.connect(host=db_host, port=db_port, database=db_name, user=db_user,password=db_password)

# Crea un cursor para ejecutar comandos SQL
cur = conn.cursor()

# Insertamos el texto (descripción), la url de la imagen generada, la id(campo de texto de miro), y lo asociamos a EFDI con el tema=99999
num_imatges = len(list_notes)

for l in range(num_imatges-1):
    # Ejecuta una consulta SQL
    sql = "INSERT INTO teclaCOMIC (id,url, descripcio,tema) VALUES (%s,%s,%s,%s)"
    valores = (list_notes[l], list_urls[l], list_descriptions[l], 99999)
    cur.execute(sql, valores)
    conn.commit()

# Cierra la conexión con la base de datos
cur.close()
conn.close()
