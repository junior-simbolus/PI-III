import requests
from flask import Flask, jsonify, request, render_template, session, redirect, flash
from flask_cors import CORS
from flask_session import Session
import fdb
from fdb import Error
import uuid

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = ""
Session(app)
CORS(app)
url_send = "https://app.whatsgw.com.br/api/WhatsGw/Send"
user_db = "sysdba"
password_db = "masterkey"
name_db = "simbolussi.ddns.com.br/3050:C:\\Simbolus\\Banco\\bSimbolus_Gestor.fdb"

header = {
    "Content-Type": "application/json"
}

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
    response = requests.post(url_send, headers=header, json=dataTexto)
    return response.status_code, response.json()

@app.route('/enviaTexto/<apikey>/<conta>/<Fone>/<id>/<Texto>/<nome_rquivo>/<encoded>/<tipo>/<tipo2>', methods=["POST"])
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

@app.route('/documentacao/<tipo>', methods=["POST", "GET"])
def documentacao(tipo):
   if tipo == '1':
      return render_template("index_services.html")
   else:
     return jsonify('index_services.html')

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

     conexao = create_db_connection(user_db, password_db, name_db)
     sql = "select cli_senha_web, cli_razao, cli_codigo from clientes where cli_status = 0 and cli_cnpj = '"+cnpj+"'"
     cursor, msg = read_query(conexao, sql)
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
           print('ok')
           session["cnpj"] = cnpj
           session["idcli"] = cursor[0][2]
           session["nome_cliente"] = cursor[0][1]
           session["uid"] = uuid.uuid4()
           retorno = {"mensagem": "ok",
                      "idcli": cursor[0][2],
                      "nome_cliente": cursor[0][1],
                      "cnpj": cnpj,
                      "code": 200,
                      "token": session.get("uid")}
           if tipo == '1':
              return render_template("servicos.html", nome_cliente=cursor[0][1], idCli=cursor[0][2], Mensagem=None,
                                  sessao=session.get("uid"), retorno=retorno)
     else:
        print('teste')
        retorno = {"mensagem": "cnpj inválido!", "code": 400}
        if tipo == '1':
          flash("CNPJ ou senha inválido!")
          return render_template("login.html", retorno=retorno)
   except Error as err:
     retorno = {"mensagem": err, "code": 400}
   return jsonify(retorno)

@app.route("/logoff/<sessao>")
def logoff(sessao):
    session["idCli"] = None
    session["cnpj"] = None
    session["nome_cliente"] = None
    session["uid"] = None
    return redirect("/")

app.run(host='192.168.2.190')
#  serve(app, host="192.168.2.190", port=5000)
