const express = require('express');
const app = express();
const path = require('path');
const bodyParser = require('body-parser');
const session = require('express-session'); // Para gerenciar sessões
const flash = require('connect-flash');     // Para mensagens flash
const axios = require('axios'); // Importe o axios
const multer = require('multer'); // Importe o Multer

const port = 3000;
const pythonBackendUrl = 'http://172.31.19.161:5000'

// Configura o EJS como o template engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views')); // Define a pasta de templates

// Middleware para servir arquivos estáticos da pasta 'public'
app.use(express.static(path.join(__dirname, 'public')));

// Middleware para processar dados de formulário url-encoded
app.use(bodyParser.urlencoded({ extended: true }));

// Configura a sessão
app.use(session({
    secret: 'suaChaveSecretaMuitoSegura', // Use uma string forte e única
    resave: false,
    saveUninitialized: true,
    cookie: { maxAge: 60000 * 30} // Exemplo: sessão dura 1 minuto
}));

// Inicializa o connect-flash
app.use(flash());

// Middleware para disponibilizar as mensagens flash para os templates EJS
app.use((req, res, next) => {
    // 'messages' é o nome da variável que estará disponível em seus templates EJS
    res.locals.messages = req.flash('info'); // Você pode ter diferentes tipos de mensagens (info, error, success)
    console.log('Mensagens Flash recuperadas (res.locals.messages):', res.locals.messages); // Adicione esta linha
    next();
});

// Configuração do Multer
// Usa memoryStorage para armazenar o arquivo em buffer, ideal para converter para base64
const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 5 * 1024 * 1024 }, // Limite de 5MB por arquivo (ajuste conforme necessário)
    fileFilter: (req, file, cb) => {
        // Aceita apenas PDF, JPG e JPEG
        const allowedMimes = ['application/pdf', 'image/jpeg', 'image/jpg'];
        if (allowedMimes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('Tipo de arquivo inválido. Apenas PDF, JPG e JPEG são permitidos.'), false);
        }
    }
});

// Middleware para verificar se o usuário está autenticado
function isAuthenticated(req, res, next) {
    if (req.session.pythonResponseData) {
        return next();
    }
    req.flash('info', 'Por favor, faça login para acessar esta página.');
    res.redirect('/');
}

// Rota para exibir o formulário de login
app.get('/', (req, res) => {
    // Renderiza o template 'login.ejs' e passa as mensagens flash para ele
    res.render('login');
});

// Rota para processar o login (ação do formulário)
// Rota para processar o login (ação do formulário)
app.post('/valida/0', async (req, res) => { // Marque a função como 'async'
    const { user, pass } = req.body; // Pega os dados do formulário
    try {
        // Faz a requisição POST para o seu backend Python
        const response = await axios.post(`${pythonBackendUrl}/valida/0`, {
            user: user, // Nome do campo esperado pelo seu backend Python para o CNPJ
            pass: pass  // Nome do campo esperado pelo seu backend Python para a senha
        });
        if (response.status === 200 && response.data.code === 200 && response.data.mensagem === 'ok') { // Exemplo: se o Python retornar { success: true }
            req.flash('info', 'Login bem-sucedido! Bem-vindo(a).');
            req.session.pythonResponseData = response.data;
            console.log(req.session.pythonResponseData)
            // Redirecione para uma página de sucesso ou dashboard
            res.redirect('/servicos'); // Você precisaria criar essa rota e template
        } else {
            // Se o backend Python indicar falha no login
            const errorMessage = response.data.mensagem || 'CNPJ ou senha inválidos.';
            req.flash('info', errorMessage);
            res.redirect('/'); // Redireciona de volta para a página de login
        }
    } catch (error) {
        console.error('Erro ao conectar ou processar a resposta do backend Python:', error.message);

        // Se o erro for uma resposta de erro HTTP do Python (ex: 401 Unauthorized)
        if (error.response) {
            console.error('Dados do erro do backend:', error.response.data);
            const pythonErrorMessage = error.response.data.message || 'Erro de autenticação no servidor.';
            req.flash('info', pythonErrorMessage);
        } else if (error.request) {
            // A requisição foi feita, mas nenhuma resposta foi recebida
            req.flash('info', 'Não foi possível conectar ao servidor de autenticação.');
        } else {
            // Algo aconteceu na configuração da requisição que disparou um erro
            req.flash('info', 'Ocorreu um erro inesperado ao tentar fazer login.');
        }
        res.redirect('/'); // Redireciona de volta para a página de login
    }
});

app.get('/servicos', isAuthenticated, (req, res) => {
    const userData = req.session.pythonResponseData;
    res.render('servicos', {
        idCli: userData.idcli,
        nome_cliente: userData.nome_cliente,
        cnpj: userData.cnpj,
        sessao: userData.token,
        apikey: userData.apikey,
        conta: userData.conta,
        banco: userData.banco,
        senha: userData.senha,
        usuario: userData.usuario
    });
});

app.get('/documentacao', isAuthenticated, (req, res) => {
    const userData = req.session.pythonResponseData;
    res.render('documentacao', {
        idCli: userData.idcli,
        nome_cliente: userData.nome_cliente,
        cnpj: userData.cnpj,
        sessao: userData.token,
        apikey: userData.apikey,
        conta: userData.conta,
        banco: userData.banco,
        senha: userData.senha,
        usuario: userData.usuario
});
});

app.get('/mensagem', isAuthenticated, (req, res) => {
   const userData = req.session.pythonResponseData; // Correto: userData

    // É uma boa prática verificar se userData existe antes de tentar acessar suas propriedades
    if (!userData) {
        req.flash('info', 'Dados de sessão não encontrados. Por favor, faça login novamente.');
        return res.redirect('/'); // Redireciona para o login se não houver dados de sessão
    }

    res.render('mensagem', {
        idCli: userData.idcli,         // Corrigido para userData
        nome_cliente: userData.nome_cliente,
        cnpj: userData.cnpj,
        sessao: userData.token,        // Corrigido para userData
        apikey: userData.apikey,
        conta: userData.conta,
        banco: userData.banco,
        senha: userData.senha,
        usuario: userData.usuario
    });
});

app.get('/logoff', (req, res) => {
    // 1. Defina a mensagem flash ANTES de destruir a sessão
    //    Isso garante que req.flash() tenha acesso a req.session
    req.flash('info', 'Você foi desconectado com sucesso.');

    // 2. Destrói a sessão do usuário
    req.session.destroy(err => {
        if (err) {
            console.error('Erro ao fazer logoff:', err);
            // Se houver um erro na destruição, você pode querer sobrescrever a mensagem
            req.flash('info', 'Ocorreu um erro ao tentar fazer logoff. Por favor, tente novamente.');
        }
        // 3. Redireciona para a página de login após o logoff
        res.redirect('/');
    });
});

// Rota para processar o envio de mensagem/arquivo
// 'upload.single('file')' é o middleware do Multer que processa o campo de arquivo 'file'
app.post('/enviaMsg', isAuthenticated, upload.single('file'), async (req, res) => {
    const { fone, mensagem } = req.body;
    const file = req.file; // O arquivo será processado pelo Multer e estará aqui
    const userData = req.session.pythonResponseData; // Tenta recuperar os dados da sessão
    console.log(userData)
    // Recupera a apikey (token) da sessão
    const apikey = userData.apikey;
    const conta = userData.conta;
    const idCli = userData.idcli;
    const nome_cliente = userData.nome_cliente;
    const cnpj = userData.cnpj;
    const usuario = userData.usuario;
    const senha = userData.senha;
    const banco = userData.banco;

    let apiUrl = ''; // URL do endpoint na sua API Python
    let payload = {
        apikey: apikey,
        conta: conta,
        Fone: fone,
        id: '',
        idCli: idCli,
        cnpj: cnpj,
        nome_cliente: nome_cliente,
        banco: banco,
        usuario: usuario,
        senha: senha         // Usando o idCli como identificador do cliente para a mensagem
    };

    try {
        if (file) {
            // Se houver um arquivo, converte o buffer do arquivo para Base64
            const encodedFile = file.buffer.toString('base64');
            const fileName = file.originalname;
            const fileMimeType = file.mimetype; // ex: 'image/jpeg', 'application/pdf'

            // Determine o tipo2 com base no mimetype
            let tipo2 = '';
            if (fileMimeType.startsWith('image/')) {
                tipo2 = 'image';
            } else if (fileMimeType.startsWith('application/pdf')) {
                tipo2 = 'document';
            } else {
                // Caso não seja um tipo esperado, você pode tratar o erro ou enviar como documento padrão
                tipo2 = 'document'; // Ou erro
            }

            // A mensagem de texto pode ser o "caption" do arquivo
            payload.Texto = '*'+nome_cliente+'*\n\n'+mensagem+'\n\n_Enviado pelo sistema Simbolus_';
            payload.nome_arquivo = fileName;
            payload.encoded = encodedFile;
            payload.tipo = fileMimeType;
            payload.tipo2 = tipo2;

            apiUrl = `${pythonBackendUrl}/enviaArquivo2`; // Endpoint para envio de arquivo
            console.log('Enviando arquivo para Python:', { ...payload, encoded: '[BASE64 OMITIDO]' });

        } else {
            // Se não houver arquivo, envia apenas a mensagem de texto
            if (!mensagem) {
                req.flash('info', 'Por favor, forneça uma mensagem ou um arquivo para enviar.');
                return res.redirect(`/mensagem`);
            }
            payload.Texto = '*'+nome_cliente+'*\n\n'+mensagem+'\n\n_Enviado pelo sistema Simbolus_';
            apiUrl = `${pythonBackendUrl}/enviaTexto2`; // Endpoint para envio de texto
            console.log('Enviando texto para Python:', payload);
        }
        console.log(payload)
        const response = await axios.post(apiUrl, payload);
        console.log(response.status)
        console.log(response.data)
        if (response.status === 200 && response.data.result === 'success') {
            req.flash('info', response.data.mensagem || 'Mensagem enviada com sucesso!');
        } else {
            req.flash('info', response.data.mensagem || 'Erro ao enviar mensagem para o WhatsApp.');
        }
        res.redirect(`/servicos`); // Redireciona de volta para a página de serviços

    } catch (error) {
        console.error('Erro na rota /enviaMsg:', error.message);
        if (error.response) {
            console.error('Resposta de erro do backend:', error.response.data);
            req.flash('info', `Erro do servidor: ${error.response.data.mensagem || error.response.statusText}`);
        } else if (error.request) {
            req.flash('info', 'Não foi possível conectar ao servidor Python.');
        } else if (error instanceof multer.MulterError) {
            // Erros específicos do Multer, como limite de tamanho de arquivo
            if (error.code === 'LIMIT_FILE_SIZE') {
                req.flash('info', 'O arquivo é muito grande. Tamanho máximo permitido é 5MB.');
            } else if (error.code === 'LIMIT_UNEXPECTED_FILE') {
                req.flash('info', 'Nome do campo de arquivo incorreto ou muitos arquivos.');
            } else {
                req.flash('info', `Erro no upload do arquivo: ${error.message}`);
            }
        } else {
            req.flash('info', `Ocorreu um erro inesperado: ${error.message}`);
        }
        res.redirect(`/mensagem`); // Redireciona de volta para o formulário com erro
    }
});

// Inicia o servidor
app.listen(port, () => {
    console.log(`Servidor rodando em http://localhost:${port}`);
    console.log('Pressione Ctrl+C para parar o servidor.');
});
