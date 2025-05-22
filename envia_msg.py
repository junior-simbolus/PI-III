import requests
from flask import Flask, jsonify, request, render_template, session, redirect, flash
from flask_cors import CORS
from flask_session import Session
from werkzeug.utils import secure_filename
from fdb import Error
import uuid
import funcoes
import os

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = ""
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(app)
CORS(app)
url_send = "https://app.whatsgw.com.br/api/WhatsGw/Send"
user_db = "sysdba"
password_db = "masterkey"
name_db = "nome e caminho do banco"

header = {
    "Content-Type": "application/json"
}

@app.route('/')
def index():
    return render_template("login.html")
#    return render_template("index_services.html")

@app.route('/enviaTexto/<apikey>/<conta>/<Fone>/<id>/<Texto>', methods=["POST"])
def enviaTexto(apikey, conta, Fone, ID, Texto):
    dataTexto = {
        "apikey": apikey,
        "phone_number": conta,
        "contact_phone_number": "55"+Fone,
        "message_custom_id": ID,
        "message_type": "text",
        "message_body": Texto
        }
    print (dataTexto)
    response = requests.post(url_send, headers=header, json=dataTexto)
    return response.status_code, response.json()

@app.route('/enviaTexto2/', methods=["POST"])
def enviaTexto2():
    dados = request.get_json()
    apikey = dados.get('apikey')
    conta = dados.get('conta')
    Fone = dados.get('Fone')
    Texto = dados.get('Texto')
    ID = dados.get('id')
    dataTexto = {
        "apikey": apikey,
        "phone_number": conta,
        "contact_phone_number": "55"+Fone,
        "message_custom_id": ID,
        "message_type": "text",
        "message_body": Texto
        }
    print (dataTexto)
    response = requests.post(url_send, headers=header, json=dataTexto)
    return response.json()

@app.route('/enviaArquivo/<apikey>/<conta>/<Fone>/<id>/<Texto>/<nome_arquivo>/<encoded>/<tipo>/<tipo2>', methods=["POST"])
def enviaArquivo(apikey, conta, Fone, ID, Texto, nome_arquivo, encoded, tipo, tipo2):
    dataImagem = {
        "apikey": apikey,
        "phone_number": conta,
        "contact_phone_number": "55"+Fone,
        "message_custom_id": ID,
        "message_type": tipo2,
        "check_status": "1",
        "message_body_mimetype": tipo,
        "message_body_filename": nome_arquivo,
        "message_caption": Texto,
        "message_body": encoded
        }
    print (dataImagem)
    response = requests.post(url_send, headers=header, json=dataImagem)
    return response.status_code, response.json()

@app.route('/enviaArquivo2/', methods=["POST"])
def enviaArquivo2():
    dados = request.get_json()
    apikey = dados.get('apikey')
    conta = dados.get('conta')
    Fone = dados.get('Fone')
    Texto = dados.get('Texto')
    tipo2 = dados.get('tipo2')
    tipo = dados.get('tipo')
    encoded = dados.get('encoded')
    nome_arquivo = dados.get('nome_arquivo')
    ID = dados.get('id')
    dataImagem = {
        "apikey": apikey,
        "phone_number": conta,
        "contact_phone_number": "55"+Fone,
        "message_custom_id": ID,
        "message_type": tipo2,
        "check_status": "1",
        "message_body_mimetype": tipo,
        "message_body_filename": nome_arquivo,
        "message_caption": Texto,
        "message_body": encoded
        }
    print (dataImagem)
    response = requests.post(url_send, headers=header, json=dataImagem)
    return response.json()

@app.route('/documentacao/<tipo>', methods=["POST", "GET"])
def documentacao(tipo):
   if tipo == '1':
      return render_template("index_services.html")
   else:
      return jsonify('index_services.html')

@app.route('/servicos')
def servicos():
    dados = request.get_json()
    nome_cliente = dados['nome_cliente']
    idCli = dados['idCli']
    sessao = dados['token']
    cnpj = dados['cnpj']
    apikey = dados['apikey']
    conta = dados['conta']

    return render_template("servicos.html", nome_cliente=nome_cliente, idCli=idCli,
                                  sessao=sessao, cnpj=cnpj, apikey=apikey, conta=conta)

@app.route('/valida/<tipo>', methods=["POST", "GET"])
def valida(tipo):
   try:
     if tipo == '0':
       dados = request.get_json()
       cnpj = dados['user']
       senha = dados['pass']
     else:
       cnpj = request.form.get('user')
       senha = request.form.get('pass')

     conexao = funcoes.create_db_connection(user_db, password_db, name_db)
     sql = "select cli_senha_web, cli_razao, cli_codigo, cli_banco_caminho, cli_banco_senha, cli_banco_usuario, "
     sql = sql + "cli_apikey, cli_conta from clientes where cli_status = 0 and cli_cnpj = '"+cnpj+"'"
     cursor, msg = funcoes.read_query(conexao, sql)
     conexao.close()
     if cursor:
        if cursor[0][0] != senha:
           if tipo == '1':
              flash("Usuário ou senha inválido!")
              retorno = {"mensagem": "Usuário ou senha inválido", "code": 400}
              return render_template("login.html", retorno=retorno)
           else:
              retorno = {"mensagem": "usuário ou senha inválido", "code": 400}
        else:
           banco = cursor[0][3]
           usuario = cursor[0][5]
           senha = cursor[0][4]
           apikey = ""
           conta = ""
           if cursor[0][6] and cursor[0][6] != "":
              apikey = cursor[0][6]
              conta = cursor[0][7]
           elif banco != "":
              sql = "SELECT IWA_APIKEY, IWA_TELEFONE FROM INSTANCIASWA"
              conexao2 = funcoes.create_db_connection(usuario, senha, banco)
              instancia, msg = funcoes.read_query(conexao2, sql)
              conexao2.close()
              apikey = instancia[0][0]
              conta = instancia[0][1]

           session["cnpj"] = cnpj
           session["idcli"] = cursor[0][2]
           session["nome_cliente"] = cursor[0][1]
           session["uid"] = uuid.uuid4()
           retorno = {"mensagem": "ok",
                      "idcli": cursor[0][2],
                      "nome_cliente": cursor[0][1],
                      "cnpj": cnpj,
                      "code": 200,
                      "token": session.get("uid"),
                      "apikey": apikey,
                      "conta": conta
                      }
           if tipo == '1':
              return render_template("servicos.html", nome_cliente=cursor[0][1], idCli=cursor[0][2], Mensagem=None,
                                  sessao=session.get("uid"), retorno=retorno, cnpj=cnpj)
     else:
        retorno = {"mensagem": "cnpj inválido!", "code": 400}
        if tipo == '1':
          flash("CNPJ ou senha inválido!")
          return render_template("login.html", retorno=retorno)
   except Error as err:
     retorno = {"mensagem": err, "code": 400}
   print(retorno)
   return jsonify(retorno)

@app.route("/logoff/<sessao>")
def logoff(sessao):
    session["idCli"] = None
    session["cnpj"] = None
    session["nome_cliente"] = None
    session["uid"] = None
    session["apikey"] = None
    session["conta"] = None
    return redirect("/")


@app.route("/mensagem/<idCli>/<nome_cliente>/<cnpj>")
def mensagem(idCli, nome_cliente, cnpj):
   return render_template("mensagem.html", idCli=idCli, nome_cliente=nome_cliente, cnpj=cnpj)


@app.route("/enviaMsg/<tipo>/<idCli>/<nome_cliente>/<cnpj>", methods=["POST", "GET"])
def enviaMsg(tipo, idCli, nome_cliente, cnpj):
     if tipo == "1":
        Fone = request.form.get("fone")
        Mensagem = request.form.get('mensagem')
        file = request.files['file']
        Arquivo = ""
        if file:
            Arquivo = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], Arquivo)
            Arquivo = file_path
            file.save(file_path)
            print(file_path)
     else:
        dados = request.get_json()
        Fone = dados['fone']
        Mensagem = dados['mensagem']
        Arquivo = dados['arquivo']

     sql = "SELECT CLI_BANCO_CAMINHO, CLI_BANCO_SENHA, CLI_BANCO_USUARIO, CLI_APIKEY, CLI_CONTA "
     sql = sql + "FROM CLIENTES WHERE CLI_CODIGO = "+str(idCli)
     conexao = funcoes.create_db_connection(user_db, password_db, name_db)
     query, msg = funcoes.read_query(conexao, sql)
     conexao.close()
     gravar = False
     banco = ""
     usuario = ""
     senha = ""
     if query[0][3] and query[0][3] != "":
        apikey = query[0][3]
        conta = query[0][4]
     else:
        sql = "SELECT IWA_APIKEY, IWA_TELEFONE FROM INSTANCIASWA"
        conexao2 = funcoes.create_db_connection(query[0][2], query[0][1], query[0][0])
        instancia, msg = funcoes.read_query(conexao2, sql)
        conexao2.close()
        apikey = instancia[0][0]
        conta = instancia[0][1]
        banco = query[0][0]
        usuario = query[0][2]
        senha = query[0][1]
        gravar = True

     tipo = ""
     tipo2 = ""
     encoded = None
     if "jpg" in Arquivo:
        tipo = "image/jpeg"
        tipo2 = "image"
        encoded = funcoes.converteimagem(Arquivo)
     elif "pdf" in Arquivo:
        tipo = "application/pdf"
        tipo2 = "document"
        encoded = funcoes.convertePDF(Arquivo)
     elif Arquivo != "":
        tipo = "application/xml"
        tipo2 = "document"
        encoded = funcoes.convertePDF(Arquivo)
     nome_arquivo = ""
     if Arquivo != "":
        nome_arquivo = os.path.basename(Arquivo)
     Mensagem = "*"+nome_cliente+"*\n"+Mensagem
     Mensagem = Mensagem+"\n\n_Enviado pelo sistema Simbolus_"

     if Arquivo != "":
        retorno = enviaArquivo(apikey, conta, Fone, "0", Mensagem,
                               nome_arquivo, encoded, tipo, tipo2)
     else:
        retorno = enviaTexto(apikey, conta, Fone, "0", Mensagem)
     idRetorno = ""
     status = ""
     if retorno[0] == 200:
        idRetorno = retorno[1]['message_id']
        status = retorno[1]['phone_state']
        enviado = 1
     elif retorno[0] == 404:
        status = retorno[1]['result_message']
        enviado = -1

     if gravar:
        sql = "SELECT GEN_ID(GERA_ID_MENSAGEM_WSAPP, 1) FROM RDB$DATABASE"
        conexao2 = funcoes.create_db_connection(usuario, senha, banco)
        gen, msg = funcoes.read_query(conexao2, sql)
        conexao2.close()
        ID = gen[0][0]
        sql = "INSERT INTO MENSAGEM_WSAPP (MWA_CODIGO, MWA_INCLUSAO, USU_INCLUSAO, "
        sql = sql + "MWA_ENVIAR_PARA, MWA_LOCAL, MWA_DOCUMENTO, MWA_ENVIADO, "
        sql = sql + "MWA_ARQUIVO1, MWA_MENSAGEM, MWA_APIKEY, MWA_INSTANCIA, "
        sql = sql + "MWA_EMPRESA, MWA_CNPJ, MWA_RETORNO, MWA_ID, MWA_DATA_ENVIO) "
        sql = sql + "VALUES ("+str(ID)+", CURRENT_TIMESTAMP, "
        sql = sql + "0, '"+Fone+"', 'WEB', 'WEB', "+str(enviado)+", '"+nome_arquivo+"', '"+Mensagem
        sql = sql + "', '"+apikey+"', '"+conta+"', '"+nome_cliente+"', '"+cnpj+"', '"
        sql = sql + status+"', '"+str(idRetorno)+"', CURRENT_TIMESTAMP);"
        print(sql)
        conexao2 = funcoes.create_db_connection(usuario, senha, banco)
        msg = funcoes.exec_query(conexao2, sql)
        print(msg)
        conexao2.close()

     print(retorno[0])
     print(retorno[1])
     flash("Mensagem enviada com sucesso!")
     return render_template("mensagem.html", idCli=idCli, nome_cliente=nome_cliente, retorno=retorno, cnpj=cnpj)


app.run(host='192.168.2.190')
#  serve(app, host="192.168.2.190", port=5000)
