let preguntando = false;

document.addEventListener('DOMContentLoaded', function() {
    scrollToBottom();
});

function scrollToBottom() {
    const body = document.getElementById('chatBody');
    setTimeout(() => {
        body.scrollTop = body.scrollHeight;
    }, 100);
}

function addMessage(content, type = 'bot') {
    const body = document.getElementById('chatBody');
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${type}-bubble animate-in`;
    bubble.innerHTML = `
        <div class="chat-avatar ${type === 'bot' ? 'bot-avatar' : 'user-avatar'}">
            <i class="bi bi-${type === 'bot' ? 'cpu-fill' : 'person-fill'}"></i>
        </div>
        <div class="chat-content ${type === 'user' ? 'user-content' : ''}">
            ${content}
        </div>
    `;
    body.appendChild(bubble);
    scrollToBottom();
    return bubble;
}

function mostrarSugerencias() {
    const panel = document.getElementById('sugerenciasPanel');
    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    scrollToBottom();
}

function cerrarSugerencias() {
    document.getElementById('sugerenciasPanel').style.display = 'none';
}

function usarSugerencia(btn) {
    document.getElementById('chatInput').value = btn.textContent;
    cerrarSugerencias();
    enviarPregunta();
}

function showTyping() {
    document.getElementById('chatLoading').style.display = 'flex';
    document.getElementById('chatInputContainer').style.display = 'none';
}

function hideTyping() {
    document.getElementById('chatLoading').style.display = 'none';
    document.getElementById('chatInputContainer').style.display = 'block';
}

async function enviarPregunta() {
    if (preguntando) return;

    const input = document.getElementById('chatInput');
    const pregunta = input.value.trim();
    if (!pregunta) return;

    preguntando = true;
    input.value = '';

    addMessage(`<p class="mb-0">${pregunta}</p>`, 'user');

    showTyping();

    try {
        const response = await fetch('/api/asistente/preguntar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pregunta })
        });

        const data = await response.json();
        hideTyping();

        let respuestaHtml = '';

        if (data.tiene_respuesta) {
            const confianza = data.confianza || 0;
            let badgeClass = 'bg-success';
            let badgeText = 'Alta confianza';
            if (confianza < 50) { badgeClass = 'bg-warning text-dark'; badgeText = 'Confianza media'; }
            if (confianza < 30) { badgeClass = 'bg-secondary'; badgeText = 'Confianza baja'; }

            respuestaHtml = `
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <p class="mb-0" style="line-height: 1.7;">${data.respuesta}</p>
                </div>
                <div class="d-flex gap-2 mt-3">
                    <span class="badge ${badgeClass}">${badgeText} (${confianza}%)</span>
                    ${data.categoria ? `<span class="badge bg-primary">${data.categoria}</span>` : ''}
                </div>
            `;
        } else {
            respuestaHtml = `
                <div class="d-flex align-items-start gap-2 mb-2">
                    <i class="bi bi-info-circle text-warning mt-1 flex-shrink-0"></i>
                    <p class="mb-0">${data.respuesta}</p>
                </div>
                <div class="mt-3">
                    <p class="small text-muted mb-2">Prueba con estas preguntas:</p>
                    <div class="d-flex flex-wrap gap-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="usarSugerenciaText('¿Qué es un CONPES?')">¿Qué es un CONPES?</button>
                        <button class="btn btn-sm btn-outline-primary" onclick="usarSugerenciaText('¿Cómo funciona el sistema de salud?')">¿Cómo funciona el sistema de salud?</button>
                        <button class="btn btn-sm btn-outline-primary" onclick="usarSugerenciaText('¿Qué políticas existen para jóvenes?')">¿Qué políticas existen para jóvenes?</button>
                    </div>
                </div>
            `;
        }

        addMessage(respuestaHtml, 'bot');

    } catch (error) {
        hideTyping();
        addMessage(`
            <div class="alert alert-danger mb-0 py-2">
                <i class="bi bi-exclamation-triangle me-2"></i>Error de conexión. Intenta de nuevo.
            </div>
        `, 'bot');
    }

    preguntando = false;
    input.focus();
}

function usarSugerenciaText(texto) {
    document.getElementById('chatInput').value = texto;
    enviarPregunta();
}
