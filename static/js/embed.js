(function () {
    const currentScript = document.currentScript;
    const apiKey = new URL(currentScript.src).searchParams.get('api_key');

    // API key kontrolü
    if (!apiKey) {
        console.error('API key bulunamadı! Lütfen geçerli bir API key sağlayın.');
        return;
    }


    let chatbotContainer = document.createElement("div");
    chatbotContainer.id = "chatbot-container";
    chatbotContainer.innerHTML = `
        <style>
            #chatbot-container {
                position: fixed;
                z-index: 9999;
                bottom: 20px;
                right: 20px;
                width: 300px;
                height: 400px;
                background: white;
                border: 1px solid #ccc;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                transition: all 0.3s ease;
                overflow: hidden;
            }
            
            #chatbot-container.minimized {
                height: 40px;
                width: 150px;
            }
            
            #chatbot-header {
                background: #0078ff;
                color: white;
                padding: 10px;
                text-align: center;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-size: 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                cursor: pointer;
            }
            
            .minimize-btn {
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .minimize-btn:hover {
                background: rgba(255,255,255,0.3);
            }
            
            #chatbot-messages {
                flex-grow: 1;
                overflow-y: auto;
                padding: 10px;
                font-size: 14px;
            }
            
            #chatbot-input-container {
                display: flex;
                padding: 5px;
                border-top: 1px solid #ccc;
            }
            
            #chatbot-input {
                flex-grow: 1;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            
            #chatbot-send {
                background: #0078ff;
                color: white;
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                border-radius: 5px;
                margin-left: 5px;
            }
        </style>
        <div id="chatbot-header">
            <span>TAIS Destek</span>
            <span class="minimize-btn">−</span>
        </div>
        <div id="chatbot-messages"></div>
        <div id="chatbot-input-container">
            <input type="text" id="chatbot-input" placeholder="Mesajınızı yazın...">
            <button id="chatbot-send">Gönder</button>
        </div>
    `;

    document.body.appendChild(chatbotContainer);

    // Minimize fonksiyonelliği
    const minimizeButton = chatbotContainer.querySelector('.minimize-btn');
    let isMinimized = localStorage.getItem('chatbotMinimized') === 'true';

    function toggleMinimize() {
        isMinimized = !isMinimized;
        chatbotContainer.classList.toggle('minimized', isMinimized);
        minimizeButton.textContent = isMinimized ? '+' : '−';
        localStorage.setItem('chatbotMinimized', isMinimized);
    }

    minimizeButton.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleMinimize();
    });

    // Başlangıç durumu
    if(isMinimized) {
        chatbotContainer.classList.add('minimized');
        minimizeButton.textContent = '+';
    }

    // Header'a tıklama ile toggle
    chatbotContainer.querySelector('#chatbot-header').addEventListener('click', () => {
        if(isMinimized) toggleMinimize();
    });

    // Mesaj gönderme fonksiyonelliği (mevcut kodunuz)
    let input = document.getElementById("chatbot-input");
    let sendButton = document.getElementById("chatbot-send");
    let messagesDiv = document.getElementById("chatbot-messages");

    function sendMessage() {
        if(isMinimized) return; // Minimize durumunda mesaj gönderimi engelle
        
        let message = input.value.trim();
        let session_id = localStorage.getItem("chatbot_session_id");

        if (!message) return;

        messagesDiv.innerHTML += `<div><b>Sen:</b> ${message}</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        input.value = "";

        console.log("API Key:", apiKey);

        fetch(`http://tais.teknolikya.com.tr/chatbot/api/chatbot/${apiKey}/`, {  
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message, session_id: session_id })
        })
        .then(response => response.json())
        .then(data => {
            messagesDiv.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            if (data.session_id) {
                localStorage.setItem("chatbot_session_id", data.session_id);
            }
        })
        .catch(error => {
            console.error("Hata:", error);
        });
    }

    sendButton.onclick = sendMessage;
    input.addEventListener("keypress", function (e) {
        if (e.key === "Enter") sendMessage();
    });
})();