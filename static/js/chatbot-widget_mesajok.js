window.ChatbotWidget = (function() {
    const createWidget = (config) => {
        const widgetHTML = `
        <div id="chatbot-widget" style="
            position: fixed;
            ${config.position === 'bottom-right' ? 
                'bottom: 20px; right: 20px' : 'bottom: 20px; left: 20px'};
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            font-family: Arial, sans-serif;
            z-index: 9999;
        ">
            <div style="
                background: ${config.primaryColor};
                color: white;
                padding: 15px;
                border-radius: 15px 15px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <h3 style="margin: 0;">${config.welcomeMessage}</h3>
                <button id="chatbot-close" style="
                    background: none;
                    border: none;
                    color: white;
                    cursor: pointer;
                    font-size: 1.2em;
                ">×</button>
            </div>

            <div id="chatbot-messages" style="
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background: #f9f9f9;
            "></div>

            <div style="
                padding: 15px;
                background: white;
                border-top: 1px solid #eee;
            ">
                <div style="display: flex; gap: 10px;">
                    <input 
                        type="text" 
                        id="chatbot-input" 
                        placeholder="Mesajınızı yazın..."
                        style="
                            flex: 1;
                            padding: 10px;
                            border: 1px solid #ddd;
                            border-radius: 5px;
                            outline: none;
                        "
                    >
                    <button 
                        id="chatbot-send" 
                        style="
                            padding: 10px 15px;
                            background: ${config.primaryColor};
                            color: white;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                        "
                    >Gönder</button>
                </div>
            </div>
        </div>
        `;

        document.body.insertAdjacentHTML('beforeend', widgetHTML);

        // Event Listeners
        const closeBtn = document.getElementById('chatbot-close');
        const sendBtn = document.getElementById('chatbot-send');
        const input = document.getElementById('chatbot-input');
        const messagesContainer = document.getElementById('chatbot-messages');

        closeBtn.addEventListener('click', () => {
            document.getElementById('chatbot-widget').remove();
        });

        const addMessage = (message, isUser = false) => {
            const messageDiv = document.createElement('div');
            messageDiv.style.marginBottom = '10px';
            messageDiv.style.padding = '8px 12px';
            messageDiv.style.borderRadius = '10px';
            messageDiv.style.background = isUser ? config.primaryColor : '#f1f1f1';
            messageDiv.style.color = isUser ? 'white' : '#333';
            messageDiv.style.alignSelf = isUser ? 'flex-end' : 'flex-start';
            messageDiv.style.maxWidth = '80%';
            messageDiv.textContent = message;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        };

        sendBtn.addEventListener('click', async () => {
            const message = input.value.trim();
            if (!message) return;

            addMessage(message, true);
            input.value = '';

            // API Request
            try {
                const response = await fetch('http://localhost:8000/chatbot/api/chatbot/01a075bc-20c3-4784-8f99-c8090cc6a4ae/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-API-KEY': config.apiKey
                    },
                    body: JSON.stringify({ message })
                });

                const data = await response.json();
                addMessage(data.response);
            } catch (error) {
                addMessage('Hata oluştu. Lütfen tekrar deneyin.');
            }
        });

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendBtn.click();
            }
        });
    };

    return {
        init: createWidget
    };
})();