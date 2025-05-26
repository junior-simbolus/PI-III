Projeto Simbolus
Este projeto é composto por um frontend em React e um servidor backend em Python. Siga as instruções abaixo para configurar e rodar ambos.

Configuração do Frontend
1.	Criar arquivo de ambiente:
o	A partir do arquivo .env.example, crie um arquivo .env.
o	Certifique-se de que a porta 3000 do projeto esteja definida.
2.	Instalar dependências:
3.	cd frontend
npm install
4.	Iniciar a aplicação:
npm start

Configuração do Backend
1.	Abrir projeto no PyCharm:
o	Abra o projeto no PyCharm.
o	Ele solicitará a configuração de um interpretador Python. Selecione o interpretador Python instalado ou crie um ambiente virtual (virtua-lenv).
2.	Instalar dependências:
o	No PyCharm, vá para o menu File > Settings > Project: EnviarWA_PI > Python Interpreter.
o	Clique no ícone de mais (+) para adicionar pacotes.
	Digite Flask e clique em Install Package.
	Digite Flask-Session e clique em Install Package.
	Digite waitress e clique em Install Package.
3.	Atualizar o pip e instalar fdb:
o	No terminal do PyCharm, execute:
o	python.exe -m pip install --upgrade pip
pip install fdb
4.	Instalar pacotes no ambiente virtual (venv):
o	No terminal, repita o procedimento de instalação para os paco-tes flask, flask-session, e fdb.
5.	Configurar servidor para rodar:
o	No final do arquivo servidor_simbolus.py, certifique-se de que o ser-vidor esteja configurado corretamente:
o	if __name__ == "__main__":
o	    serve(app, host="192.168.2.190", port=5000)
    # app.run(debug=True)

6.	Rodar servidor fora do PyCharm:
o	Para rodar o servidor fora do PyCharm, abra um terminal e execute:
C:\Users\acdsj\PycharmProjects\EnviarWA_PI\venv\Scripts\python.exe C:\Users\acdsj\PycharmProjects\EnviarWA_PI\envia_msg.py

Para testar, você pode usar o link de acesso ao sistema

http://3.130.239.90:3000/
usuario: 15691951000121
senha: 123456

http://3.130.239.90:5000/
back-end rodando nesse link
métodos:
@app.route('/documentacao/<tipo>', methods=["POST", "GET"])
retorna os métodos para envio de mensagem
o parâmetro tipo tem que ser passado 0 para receber o retorno em json

@app.route('/valida/<tipo>', methods=["POST", "GET"])
valida o usuário para usar o serviço e retorna os dados como
banco de dados do cliente, id, nome, api e conta.
o parâmetro tipo deve ser igual a zero "0"

@app.route('/enviaTexto2/', methods=["POST"])
envia a mensagem de texto para o telefone informado no json

@app.route('/enviaArquivo2/', methods=["POST"])
envia a mensagem com anexo para o telefone informado no json

