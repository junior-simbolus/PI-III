import requests
from flask import Flask, jsonify, request, render_template, session, redirect, flash
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)
Session(app)
CORS(app)

url_send = "https://app.whatsgw.com.br/api/WhatsGw/Send"

header = {
    "Content-Type": "application/json"
}

@app.route('/')
def index():
    return render_template("index_services.html")

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

app.run(host='192.168.2.190')
