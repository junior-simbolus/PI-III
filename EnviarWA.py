import time
import fdb
from fdb import Error
import locale
from PIL import Image
import base64
from io import BytesIO
import requests

user_db = "SYSDBA"
password_db = "masterkey"
#name_db = "SERVIDOR/3050:C:\\SISTEMA\\MOREIRA.gdb"
name_db = "127.0.0.1/3070:C:\\BANCOS\\NUTRI\\MATTAR.FDB"
url_send = "192.168.2.190:5000"

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


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

def verificarEnviar():
     sql = "SELECT MWA_CODIGO, MWA_ENVIAR_PARA, MWA_DOCUMENTO, MWA_ARQUIVO1, MWA_ARQUIVO2, "
     sql = sql + "MWA_MENSAGEM, MWA_APIKEY, MWA_INSTANCIA, MWA_EMPRESA FROM MENSAGEM_WSAPP WHERE MWA_ENVIADO = 0 ORDER BY MWA_CODIGO"
     conexao = create_db_connection(user_db, password_db, name_db)
     mensagens, msg = read_query(conexao, sql)
     conexao.close()

     for row in mensagens:
        try:
           ID = row[0]
           Fone = row[1]
           Arquivo1 = row[3]
           Arquivo2 = row[4]
           Mensagem = row[5]
           #apikey = row[6]
           apikey = '5a244df2-b3d0-4cbd-acd8-53346574db77'
           #conta = row[7]
           conta = '5514997792223'
           empresa = row[8]

           if "jpg" in Arquivo1:
             tipo = "image/jpeg"
             tipo2 = "image"
             encoded = converteimagem(Arquivo1)
           elif "pdf" in Arquivo1:
             tipo = "application/pdf"
             tipo2 = "document"
             encoded = convertePDF(Arquivo1)
           else:
             tipo = "application/xml"
             tipo2 = "document"
             encoded = convertePDF(Arquivo1)

           nome_arquivo = os.path.basename(Arquivo1)
           Mensagem = "*"+empresa+"*\n"+Mensagem

           dadosTexto={
               "apikey": apikey,
               "conta": conta,
               "Fone": Fone,
               "ID": ID,
               "Mensagem":Mensagem
           }
           dadosArquivo={
               "apikey": apikey,
               "conta": conta,
               "Fone": Fone,
               "ID": ID,
               "Mensagem": Mensagem,
               "nome_arquivo": nome_arquivo,
               "encoded": encoded,
               "tipo": tipo,
               "tipo2": tipo2
           }
           if Arquivo1 != "":
              retorno = requests.post(url_send+'/enviaArquivo', json=dadosArquivo)
           else:
              retorno = requests.post(url_send+'/enviaTexto', json=dadosTexto)

           print(retorno[0])
           print(retorno[1])
           if retorno[0] == 404:
              if retorno[1]['result'] == "fail":
                 status = retorno[1]['result_message']
                 sql = "UPDATE MENSAGEM_WSAPP SET MWA_ENVIADO = -1, MWA_DATA_ENVIO = CURRENT_TIMESTAMP, "
                 sql = sql + "MWA_RETORNO = '"+status+"' WHERE MWA_CODIGO = "+str(ID)
                 conexao = create_db_connection(user_db, password_db, name_db)
                 exec_query(conexao, sql)
                 conexao.close()
              else:
                  print("\nErro")
           elif retorno[0] == 200:
              idRetorno = retorno[1]['message_id']
              status = retorno[1]['phone_state']
              sql = "UPDATE MENSAGEM_WSAPP SET MWA_ENVIADO = 1, MWA_DATA_ENVIO = CURRENT_TIMESTAMP, "
              sql = sql + "MWA_ID = "+str(idRetorno)+", MWA_RETORNO = '"+status+"' WHERE MWA_CODIGO = "+str(ID)
              conexao = create_db_connection(user_db, password_db, name_db)
              exec_query(conexao, sql)
              conexao.close()
           else:
              status = retorno[1]['result_message']
              sql = "UPDATE MENSAGEM_WSAPP SET MWA_ENVIADO = -1, MWA_DATA_ENVIO = CURRENT_TIMESTAMP, "
              sql = sql + "MWA_RETORNO = '"+status+"' WHERE MWA_CODIGO = "+str(ID)
              conexao = create_db_connection(user_db, password_db, name_db)
              exec_query(conexao, sql)
              conexao.close()
        except Exception as e:
            print(f"Erro: {e}")
     time.sleep(10)


if __name__ == "__main__":
   while True:
      try:
         verificarEnviar()
      except Exception as e:
          print(f"Erro: {e}")
