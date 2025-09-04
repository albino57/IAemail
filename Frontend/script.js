async function analyzeEmail() {
    const emailText = document.getElementById('emailText').value;
    const resultDiv = document.getElementById('result');
    const categorySpan = document.getElementById('category');
    const responseP = document.getElementById('response');

    // Limpa resultados anteriores e mostra loading.
    categorySpan.textContent = '';
    responseP.textContent = 'Analisando...';
    resultDiv.classList.remove('hidden');

    try { //Envia o texto para o backend
        const response = await fetch('https://rafaelalbinoia-iaemail-huggingface.hf.space/analyze', {
            method: 'POST',     //Método HTTP POST (para enviar dados).
            headers: {
                'Content-Type': 'application/json', //Avisa que está mandando JSON.
            },
            body: JSON.stringify({ text: emailText }) //Transforma o texto em JSON.
        });

        const data = await response.json(); //Transforma a resposta JSON em um objeto JS e espera com o 'await' a resposta.

        if (response.ok) { //Se a resposta for ok, atualiza.
            categorySpan.textContent = data.category;
            responseP.textContent = data.response;
        } else {
            throw new Error(data.error || 'Erro na análise');
        }

    } catch (error) {
        console.error('Erro:', error);
        categorySpan.textContent = 'Erro';
        responseP.textContent = 'Não foi possível analisar o e-mail. Tente novamente.';
    }
}

//↓↓Função que carrega TXT/PDF e envia para o backend processar↓↓
async function handleFileUpload(files) {
    if (files.length === 0) return;
    const file = files[0];

    //Prepara o FormData
    const formData = new FormData();
    formData.append('file', file);

    //Mostra estado de "carregando" para o usuário
    const resultDiv = document.getElementById('result');
    const categorySpan = document.getElementById('category');
    const responseP = document.getElementById('response');
    
    resultDiv.classList.remove('hidden');
    categorySpan.textContent = 'Analisando...';
    responseP.textContent = 'Processando seu arquivo...';

    try {
        //Envia o arquivo para o backend processar
        const response = await fetch('https://rafaelalbinoia-iaemail-huggingface.hf.space/analyze_file', {
            method: 'POST',
            body: formData   // Não setar 'Content-Type'! O browser faz isso automaticamente.
        });
        const data = await response.json();

        //Atualiza a interface com a resposta
        if (response.ok) {
            if (data.text) {
                // Se veio só o texto extraído (PDF/TXT)
                document.getElementById('emailText').value = data.text;
                categorySpan.textContent = 'Texto extraído!';
                responseP.textContent = 'Edite se necessário e clique em "Enviar E-mail".';
            } else if (data.category && data.response) {
                // Se já veio análise completa (formato antigo)
                categorySpan.textContent = data.category;
                responseP.textContent = data.response;
            }
        } else {
            throw new Error(data.error || 'Erro na análise do arquivo.');
        }
    } catch (error) {
        console.error('Erro no upload:', error);
        categorySpan.textContent = 'Erro';
        responseP.textContent = 'Falha ao processar o arquivo.';
    }
    
    document.getElementById('fileInput').value = ''; //Permite recarregar o mesmo arquivo
    document.getElementById('enviarBtn').disabled = false; //Caso carregue algum arquivo, garante que o botão fique liberado.
    document.getElementById('apagarBtn').disabled = false;
}

//↓↓↓-Código da função de desabilitar/habilitar botões-↓↓↓
const botaoApagar = document.getElementById('apagarBtn');
const textarea = document.getElementById('emailText');
const enviarBtn = document.getElementById('enviarBtn');
const resultDiv = document.getElementById('result'); //permite fazer hidden da div id="result" no HTML

botaoApagar.addEventListener('click', function() {
    textarea.value = '';
    enviarBtn.disabled = true;
    botaoApagar.disabled = true;
    resultDiv.classList.add('hidden'); //faz hidden (Oculta) da div id="result" no HTML
});

textarea.addEventListener('input', function() { // Função que desativa os botões 'enviar mensagem' e 'apagar' (X)

    if (textarea.value.trim() !== ''){
        enviarBtn.disabled = false;
        botaoApagar.disabled = false;
    }
    else {
        enviarBtn.disabled = true;
        botaoApagar.disabled = true;
    }
});