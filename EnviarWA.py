import time
import locale
import requests
import funcoes

user_db = "SYSDBA"
password_db = "masterkey"
#name_db = "SERVIDOR/3050:C:\\SISTEMA\\MOREIRA.gdb"
name_db = "127.0.0.1/3070:C:\\BANCOS\\NUTRI\\M,A.FDB"
url_send = "192.168.2.190:5000"

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def verificarEnviar():
     sql = "SELECT MWA_CODIGO, MWA_ENVIAR_PARA, MWA_DOCUMENTO, MWA_ARQUIVO1, MWA_ARQUIVO2, "
     sql = sql + "MWA_MENSAGEM, MWA_APIKEY, MWA_INSTANCIA, MWA_EMPRESA FROM MENSAGEM_WSAPP WHERE MWA_ENVIADO = 0 ORDER BY MWA_CODIGO"
     conexao = funcoes.create_db_connection(user_db, password_db, name_db)
     mensagens, msg = funcoes.read_query(conexao, sql)
     conexao.close()

     for row in mensagens:
        try:
           ID = row[0]
           Fone = row[1]
           Arquivo1 = row[3]
           Arquivo2 = row[4]
           Mensagem = row[5]
           apikey = row[6]
           conta = row[7]
           empresa = row[8]

           if "jpg" in Arquivo1:
             tipo = "image/jpeg"
             tipo2 = "image"
             encoded = funcoes.converteimagem(Arquivo1)
           elif "pdf" in Arquivo1:
             tipo = "application/pdf"
             tipo2 = "document"
             encoded = funcoes.convertePDF(Arquivo1)
           else:
             tipo = "application/xml"
             tipo2 = "document"
             encoded = funcoes.convertePDF(Arquivo1)

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
                 conexao = funcoes.create_db_connection(user_db, password_db, name_db)
                 funcoes.exec_query(conexao, sql)
                 conexao.close()
              else:
                  print("\nErro")
           elif retorno[0] == 200:
              idRetorno = retorno[1]['message_id']
              status = retorno[1]['phone_state']
              sql = "UPDATE MENSAGEM_WSAPP SET MWA_ENVIADO = 1, MWA_DATA_ENVIO = CURRENT_TIMESTAMP, "
              sql = sql + "MWA_ID = "+str(idRetorno)+", MWA_RETORNO = '"+status+"' WHERE MWA_CODIGO = "+str(ID)
              conexao = funcoes.create_db_connection(user_db, password_db, name_db)
              funcoes.exec_query(conexao, sql)
              conexao.close()
           else:
              status = retorno[1]['result_message']
              sql = "UPDATE MENSAGEM_WSAPP SET MWA_ENVIADO = -1, MWA_DATA_ENVIO = CURRENT_TIMESTAMP, "
              sql = sql + "MWA_RETORNO = '"+status+"' WHERE MWA_CODIGO = "+str(ID)
              conexao = funcoes.create_db_connection(user_db, password_db, name_db)
              funcoes.exec_query(conexao, sql)
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
