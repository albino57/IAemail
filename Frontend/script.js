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
        const response = await fetch('http://localhost:5000/analyze', {
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