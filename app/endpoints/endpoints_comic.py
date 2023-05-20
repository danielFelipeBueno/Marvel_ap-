from fastapi import APIRouter, status
from datetime import datetime

import hashlib
import time
import httpx
import pyodbc

connection_string = "Driver={SQL Server};Server=localhost\SQLEXPRESS03;Database=bd_marvel_bk;Trusted_Connection=True;"



router = APIRouter()

@router.get(
    path='/comics',
    status_code=status.HTTP_200_OK
)
async def get_comics(
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
    
    url='https://gateway.marvel.com:443/v1/public/comics?apikey='+pubkey+'&hash='+hash_md5+'&ts='+ts+'&limit='+str(limit)+'&offset='+str(skip)

    response = httpx.get(url)
    if response.status_code == 200:
        body = response.json()
        for comic in body['data']['results']:
            titulo = comic['title']
            descripcion_variante = comic['variantDescription']
            description_comic = comic['description']
            fecha = comic['modified']
            codigo_isbn = comic['isbn']
            codigo_barras = comic['upc']
            formato = comic['format']
            paginas_comic = comic['pageCount']
            identificador_url = comic['resourceURI']
            imagen_comic = comic['thumbnail']['path']+comic['thumbnail']['extension']
            query = f"INSERT INTO comic (titulo, descripcion_variante, description_comic, fecha_modificacion, codigo_isbn, codigo_barras, formato, paginas_comic, identificador_url, imagen_comic) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            date_format = "%Y-%m-%dT%H:%M:%S%z"
            try:
                fecha_modificacion = datetime.strptime(fecha, date_format)
            except Exception as e:
                print(str(e))
            try:
                cursor.execute(query,(
                    titulo,
                    descripcion_variante,
                    description_comic,
                    fecha_modificacion,
                    codigo_isbn,
                    codigo_barras,
                    formato,
                    paginas_comic,
                    identificador_url,
                    imagen_comic
                ))
            except pyodbc.Error as e:
                print(f"Error al ejecutar la consulta: {str(e)}")
        conn.commit()
        cursor.close()
        conn.close()
        return {"message":"Datos guardados en la base de datos"}
    else:
        return {'error':'Error en la solicitud'}
    
