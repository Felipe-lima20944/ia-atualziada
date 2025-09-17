document.addEventListener('DOMContentLoaded', () => {

    const chatForm = document.getElementById('chat-form');
    const mensagemInput = document.getElementById('mensagem-input');
    const arquivosInput = document.getElementById('arquivos-input');
    const anexarBtn = document.getElementById('anexar-btn');
    const conversaMensagens = document.getElementById('conversa-mensagens');
    const conversaList = document.getElementById('conversa-list');
    const chatTitle = document.getElementById('chat-title');
    const conversaIdInput = document.getElementById('conversa-id');
    const novaConversaBtn = document.getElementById('nova-conversa-btn');
    const personalidadeSelect = document.getElementById('personalidade-select');
    const placeholderMessage = document.getElementById('placeholder-message');

    let isFetchingResponse = false;
    let currentConversationId = null;

    // Função para carregar personalidades
    async function carregarPersonalidades() {
        try {
            const response = await fetch('/api/personalidades/');
            const data = await response.json();
            if (data.personalidades) {
                personalidadeSelect.innerHTML = data.personalidades.map(p =>
                    `<option value="${p.nome}" data-foto="${p.foto_ia_url}">${p.nome}</option>`
                ).join('');
            }
        } catch (error) {
            console.error('Erro ao carregar personalidades:', error);
        }
    }

    // Função para carregar lista de conversas
    async function carregarConversas() {
        try {
            const response = await fetch('/api/conversas/');
            const data = await response.json();
            conversaList.innerHTML = '';
            if (data.conversas) {
                data.conversas.forEach(conversa => {
                    const li = document.createElement('li');
                    li.className = 'chat-list-item';
                    li.dataset.conversaId = conversa.id;
                    li.innerHTML = `<strong>${conversa.titulo}</strong><br><small class="text-muted">${conversa.modificado_em.split('T')[0]}</small>`;
                    li.addEventListener('click', () => carregarConversa(conversa.id));
                    conversaList.appendChild(li);
                });
            }
        } catch (error) {
            console.error('Erro ao carregar conversas:', error);
        }
    }

    // Função para carregar mensagens de uma conversa específica
    async function carregarConversa(conversaId) {
        placeholderMessage.style.display = 'none';
        conversaMensagens.innerHTML = '';

        document.querySelectorAll('.chat-list-item').forEach(el => el.classList.remove('active'));
        const activeItem = document.querySelector(`.chat-list-item[data-conversa-id="${conversaId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }

        try {
            const response = await fetch(`/api/conversas/${conversaId}/`);
            const data = await response.json();

            chatTitle.textContent = data.titulo;
            conversaIdInput.value = data.conversa_id;
            currentConversationId = data.conversa_id;
            personalidadeSelect.value = data.personalidade_id;

            data.mensagens.forEach(mensagem => {
                adicionarMensagemNaUI(mensagem.texto_html, mensagem.papel, mensagem.tipo_conteudo, mensagem.dados_conteudo, mensagem.id);
            });

            conversaMensagens.scrollTop = conversaMensagens.scrollHeight;
        } catch (error) {
            console.error('Erro ao carregar conversa:', error);
        }
    }

    // Função para adicionar uma mensagem à UI
    function adicionarMensagemNaUI(texto, papel, tipo, dados, mensagemId = null) {
        const mensagemDiv = document.createElement('div');
        mensagemDiv.className = `message ${papel === 'user' ? 'message-user' : 'message-assistant'}`;

        if (tipo === 'text') {
            mensagemDiv.innerHTML = texto;
        } else if (tipo === 'image' && dados) {
            mensagemDiv.innerHTML = `<p>${texto}</p><img src="${dados}" alt="Imagem gerada" style="max-width: 100%; border-radius: 8px;">`;
        } else if (tipo === 'file' && texto) {
            mensagemDiv.innerHTML = `<p>${texto}</p>`;
        } else {
            mensagemDiv.innerHTML = `<p>${texto}</p>`;
        }

        if (papel === 'assistant' && mensagemId) {
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'feedback-buttons';
            feedbackDiv.innerHTML = `
                <button class="feedback-like-btn" data-id="${mensagemId}" data-feedback="true">👍</button>
                <button class="feedback-dislike-btn" data-id="${mensagemId}" data-feedback="false">👎</button>
            `;
            mensagemDiv.appendChild(feedbackDiv);
        }

        conversaMensagens.appendChild(mensagemDiv);
        conversaMensagens.scrollTop = conversaMensagens.scrollHeight;

        if (papel === 'assistant' && mensagemId) {
            setupFeedbackListeners();
        }
    }

    // Função para configurar os listeners de feedback
    function setupFeedbackListeners() {
        document.querySelectorAll('.feedback-like-btn, .feedback-dislike-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const btn = event.currentTarget;
                const mensagemId = btn.dataset.id;
                const feedback = btn.dataset.feedback === 'true';

                btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                try {
                    await fetch(`/api/feedback/${mensagemId}/`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        },
                        body: JSON.stringify({ feedback: feedback })
                    });
                    console.log('Feedback enviado com sucesso.');
                } catch (error) {
                    console.error('Erro ao enviar feedback:', error);
                }
            });
        });
    }

    // Adiciona uma mensagem de "digitando"
    function adicionarMensagemCarregando() {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-message';
        loadingDiv.className = 'message message-assistant loading-dots';
        loadingDiv.innerHTML = '<span></span><span></span><span></span>';
        conversaMensagens.appendChild(loadingDiv);
        conversaMensagens.scrollTop = conversaMensagens.scrollHeight;
    }

    // Remove a mensagem de "digitando"
    function removerMensagemCarregando() {
        const loadingDiv = document.getElementById('loading-message');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    // Submissão do formulário de chat
    chatForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (isFetchingResponse) {
            return;
        }

        const mensagemTexto = mensagemInput.value.trim();
        const arquivos = arquivosInput.files;

        if (!mensagemTexto && arquivos.length === 0) {
            return;
        }
        
        isFetchingResponse = true;
        placeholderMessage.style.display = 'none';

        adicionarMensagemNaUI(mensagemTexto, 'user', 'text');
        if (arquivos.length > 0) {
            const fileNames = Array.from(arquivos).map(f => f.name).join(', ');
            adicionarMensagemNaUI(`Arquivo(s) anexado(s): ${fileNames}`, 'user', 'file');
        }

        adicionarMensagemCarregando();

        const formData = new FormData(chatForm);

        try {
            const response = await fetch('/chat/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                // A requisição falhou, mas a resposta não é JSON.
                // Exiba a resposta completa para depuração.
                console.error('Resposta de erro não-JSON:', errorText);
                throw new Error(`Ocorreu um erro no servidor. Status: ${response.status}`);
            }

            const data = await response.json();

            removerMensagemCarregando();

            adicionarMensagemNaUI(data.resposta, 'assistant', 'text', null, data.mensagem_id);

            if (data.titulo && chatTitle.textContent === 'Bem-vindo!') {
                chatTitle.textContent = data.titulo;
            }

            conversaIdInput.value = data.conversa_id;
            currentConversationId = data.conversa_id;
            carregarConversas();
        } catch (error) {
            removerMensagemCarregando();
            console.error('Erro na requisição:', error);
            // Melhorar a mensagem de erro para o usuário final
            const userError = error.message.includes("Unexpected token") ? 
                              "Erro de comunicação com o servidor. Tente novamente." : 
                              error.message;
            adicionarMensagemNaUI(`Desculpe, houve um erro ao processar sua solicitação: ${userError}`, 'assistant', 'text');
        } finally {
            mensagemInput.value = '';
            arquivosInput.value = '';
            isFetchingResponse = false;
        }
    });

    anexarBtn.addEventListener('click', () => {
        arquivosInput.click();
    });

    novaConversaBtn.addEventListener('click', () => {
        chatTitle.textContent = "Nova Conversa";
        conversaIdInput.value = "";
        currentConversationId = null;
        conversaMensagens.innerHTML = '';
        placeholderMessage.style.display = 'block';

        document.querySelectorAll('.chat-list-item').forEach(el => el.classList.remove('active'));
    });

    function getCSRFToken() {
        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfTokenElement) {
            return csrfTokenElement.value;
        }
        console.error("CSRF token não encontrado. Certifique-se de que {% csrf_token %} está no seu formulário.");
        return null;
    }

    carregarConversas();
    carregarPersonalidades();
});