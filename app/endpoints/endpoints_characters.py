from fastapi import APIRouter, status
from datetime import datetime

import hashlib
import time
import httpx
import pyodbc

connection_string = "Driver={SQL Server};Server=localhost\SQLEXPRESS03;Database=bd_marvel_bk;Trusted_Connection=True;"



router = APIRouter()

@router.get(
    path='/characters',
    status_code=status.HTTP_200_OK
)
async def get_characters(
    limit: int,
    skip: int,
):
    try:
        conn = pyodbc.connect(connection_string)
    except pyodbc.Error as ex:
        print("Error al establecer la conexión:")
        print(ex)
    cursor = conn.cursor()
    pubkey = "c6c6a92acd0265ef34418784174ca0d5"
    pvtkey = "e5b6623296a93f16e90f4706642e3f2e194aee0b"
    ts = str(int(time.time()))
    message = ts + pvtkey + pubkey
    hash_md5 = hashlib.md5(message.encode()).hexdigest()
    
    url='https://gateway.marvel.com:443/v1/public/characters?apikey='+pubkey+'&hash='+hash_md5+'&ts='+ts+'&limit='+str(limit)+'&offset='+str(skip)
    
    response = httpx.get(url)
    if response.status_code == 200:
        body = response.json()
        for character in body['data']['results']:
            nombre_personaje =character['name']
            descripcion = character['description']
            modificado = character['modified']
            identificador_url = character['resourceURI']
            imagen = character['thumbnail']['path']+character['thumbnail']['extension']
            
            query = f"INSERT INTO personaje (nombre_personaje, descripcion, modificado,identificador_url,imagen) VALUES (?, ?, ?, ?, ?)"
            date_format = "%Y-%m-%dT%H:%M:%S%z"
            datetime_obj = datetime.strptime(modificado, date_format)
            try:
                cursor.execute(query, (nombre_personaje,descripcion ,datetime_obj,identificador_url,imagen))            
            except pyodbc.Error as e:
                print(f"Error al ejecutar la consulta: {str(e)}")
        conn.commit()
        cursor.close()
        conn.close()

        return {"message":"Datos guardados en la base de datos"}
    else:
        return {'error':'Error en la solicitud'}