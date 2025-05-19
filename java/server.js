// server.js
const express = require('express');
const app = express();
const path = require('path');

// Servir arquivos estáticos do front-end
app.use(express.static(path.join(__dirname, 'public')));

// Rodar o servidor Node.js
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Servidor Node rodando em http://localhost:${PORT}`);
});
