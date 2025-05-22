// public/js/formValidator.js

document.addEventListener('DOMContentLoaded', () => {

    // --- Validação e Máscara de Telefone ---
    document.querySelectorAll('.js-phone-mask').forEach(input => {
        const errorMessageDiv = document.getElementById(input.dataset.errorTarget);

        input.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, ''); // Remove tudo que não é dígito
            let formattedValue = '';

            if (value.length > 0) {
                formattedValue = '(' + value.substring(0, 2);
            }
            if (value.length > 2) {
                formattedValue += ') ' + value.substring(2, 11);
            }
            e.target.value = formattedValue;

            validatePhone(input, errorMessageDiv); // Validação visual enquanto digita
        });

        // Validação no blur (ao sair do campo) para garantir que o erro apareça se não preenchido corretamente
        input.addEventListener('blur', () => {
            validatePhone(input, errorMessageDiv);
        });

        function validatePhone(inputElement, errorElement) {
            const numeroLimpo = inputElement.value.replace(/\D/g, '');
            if (numeroLimpo.length === 10 || numeroLimpo.length === 11) {
                errorElement.textContent = '';
                return true;
            } else {
                errorElement.textContent = 'Telefone deve ter 10 ou 11 dígitos (incluindo DDD).';
                return false;
            }
        }
    });

    // --- Validação de Tipo de Arquivo ---
    document.querySelectorAll('.js-file-validator').forEach(input => {
        const errorMessageDiv = document.getElementById(input.dataset.errorTarget);
        const allowedExtensions = input.dataset.allowedExtensions ? input.dataset.allowedExtensions.split(',') : [];

        input.addEventListener('change', () => {
            validateFile(input, errorMessageDiv, allowedExtensions);
        });

        function validateFile(inputElement, errorElement, extensions) {
            const file = inputElement.files[0];
            if (file) {
                const fileName = file.name;
                const fileExtension = fileName.split('.').pop().toLowerCase();

                if (extensions.includes(fileExtension)) {
                    errorElement.textContent = '';
                    return true;
                } else {
                    errorElement.textContent = `Apenas arquivos ${extensions.join(', ').toUpperCase()} são permitidos.`;
                    inputElement.value = ''; // Limpa a seleção do arquivo
                    return false;
                }
            } else {
                errorElement.textContent = '';
                return true;
            }
        }
    });

    // --- Validação de Formulário Geral (no submit) ---
    // Este script valida todos os formulários que possuem um id, e espera campos específicos
    document.querySelectorAll('.js-validated-form').forEach(form => {
        form.addEventListener('submit', function (event) {
            let isFormValid = true;

            // Valida todos os campos de telefone com a classe '.js-phone-mask' neste formulário
            form.querySelectorAll('.js-phone-mask').forEach(input => {
                const errorMessageDiv = document.getElementById(input.dataset.errorTarget);
                if (!validatePhone(input, errorMessageDiv)) {
                    isFormValid = false;
                }
            });

            // Valida todos os campos de arquivo com a classe '.js-file-validator' neste formulário
            form.querySelectorAll('.js-file-validator').forEach(input => {
                const errorMessageDiv = document.getElementById(input.dataset.errorTarget);
                const allowedExtensions = input.dataset.allowedExtensions ? input.dataset.allowedExtensions.split(',') : [];
                if (!validateFile(input, errorMessageDiv, allowedExtensions)) {
                    isFormValid = false;
                }
            });

            if (!isFormValid) {
                event.preventDefault(); // Impede o envio se houver erros de validação
            }
        });
    });

});
