async function analyzeEmail() {
    const emailText = document.getElementById('emailText').value;
    const resultDiv = document.getElementById('result');
    const categorySpan = document.getElementById('category');
    const responseP = document.getElementById('response');

    // Limpa resultados anteriores e mostra loading
    categorySpan.textContent = '';
    responseP.textContent = 'Analisando...';
    resultDiv.classList.remove('hidden');

    try {
        const response = await fetch('http://localhost:5000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: emailText })
        });

        const data = await response.json();

        if (response.ok) {
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