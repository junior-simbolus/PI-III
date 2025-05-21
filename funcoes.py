import fdb
from fdb import Error
from PIL import Image
import base64
from io import BytesIO

# Primeiro, abre a imagem e a converte para um array de bytes
def converteimagem(strImagem):
   with Image.open(strImagem) as imagem:
      buffer = BytesIO()
      imagem.save(buffer, format="JPEG")
      array_bytes = buffer.getvalue()

   # Depois, converte o array de bytes para uma string Base64
   encoded = base64.b64encode(array_bytes).decode('utf-8')
   return encoded

def convertePDF(strpdf):
   with open(strpdf, "rb") as pdf_file:
      pdf_bytes = pdf_file.read()
      encoded = base64.b64encode(pdf_bytes).decode("utf-8")
   return encoded

def create_db_connection(user_name, user_password, db_name):
   connection = None
   try:
      connection = fdb.connect(user=user_name, password=user_password, dsn=db_name, charset="WIN1252")
   except Error as err:
       print(f"Error: '{err}'")
   return connection


def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except Error as err:
        return result, err
    return result, "ok"


def exec_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        msg = "OK"
    except Error as err:
        msg = err
    return msg

