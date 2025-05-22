// public/js/accessibility.js

document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    const decreaseButton = document.getElementById('decreaseFontSize');
    const increaseButton = document.getElementById('increaseFontSize');
    const resetButton = document.getElementById('resetFontSize');

    // Certifique-se de que os botões existem antes de adicionar event listeners
    if (!decreaseButton || !increaseButton || !resetButton) {
        console.warn("Botões de acessibilidade não encontrados no DOM. Verifique seu HTML.");
        return; // Sai da função se os botões não estiverem lá
    }

    const fontSizes = ['font-size-small', 'font-size-normal', 'font-size-large', 'font-size-x-large'];
    let currentFontSizeIndex = 1; // Começa no tamanho normal (índice 1)

    function applyFontSize() {
        fontSizes.forEach(cls => body.classList.remove(cls));
        body.classList.add(fontSizes[currentFontSizeIndex]);
        localStorage.setItem('fontSizePreference', currentFontSizeIndex);
    }

    const savedSizeIndex = localStorage.getItem('fontSizePreference');
    if (savedSizeIndex !== null) {
        currentFontSizeIndex = parseInt(savedSizeIndex);
    }
    applyFontSize(); // Aplica o tamanho inicial ao carregar a página

    decreaseButton.addEventListener('click', () => {
        if (currentFontSizeIndex > 0) {
            currentFontSizeIndex--;
            applyFontSize();
        }
    });

    increaseButton.addEventListener('click', () => {
        if (currentFontSizeIndex < fontSizes.length - 1) {
            currentFontSizeIndex++;
            applyFontSize();
        }
    });

    resetButton.addEventListener('click', () => {
        currentFontSizeIndex = 1; // Volta para o tamanho normal
        applyFontSize();
    });
});
