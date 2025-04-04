// Chatbot Script
(function () {
    let chatbotContainer = document.createElement("div");
    chatbotContainer.id = "chatbot-container";
    chatbotContainer.innerHTML = `
        <style>
            #chatbot-container {
                position: fixed;
                z-index: 9999; /* Yüksek değer */
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
            }
            #chatbot-header {
                background: #0078ff;
                color: white;
                padding: 10px;
                text-align: center;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-size: 16px;
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
        <div id="chatbot-header">Chatbot</div>
        <div id="chatbot-messages"></div>
        <div id="chatbot-input-container">
            <input type="text" id="chatbot-input" placeholder="Mesajınızı yazın...">
            <button id="chatbot-send">Gönder</button>
        </div>
    `;

    document.body.appendChild(chatbotContainer);

    let input = document.getElementById("chatbot-input");
    let sendButton = document.getElementById("chatbot-send");
    let messagesDiv = document.getElementById("chatbot-messages");

    
    function sendMessage() {
        let message = input.value.trim();
        let session_id = localStorage.getItem("chatbot_session_id");

        if (!message) return;

        messagesDiv.innerHTML += `<div><b>Sen:</b> ${message}</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        input.value = "";

        
        fetch("http://localhost:8000/chatbot/api/chatbot/01a075bc-20c3-4784-8f99-c8090cc6a4ae/", {  
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
