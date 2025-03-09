document.getElementById("chat-toggle").addEventListener("click", function() {
    document.querySelector(".chatbot").style.display = "flex";
});

document.getElementById("close-btn").addEventListener("click", function() {
    document.querySelector(".chatbot").style.display = "none";
});

document.getElementById("send-btn").addEventListener("click", function() {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    let chatBody = document.getElementById("chat-body");
    
    let userMessage = document.createElement("p");
    userMessage.classList.add("user-message");
    userMessage.textContent = userInput;
    
    chatBody.appendChild(userMessage);

    // Simulated bot response
    setTimeout(() => {
        let botMessage = document.createElement("p");
        botMessage.classList.add("bot-message");
        botMessage.textContent = "I'm just a simple chatbot!";
        
        chatBody.appendChild(botMessage);
        chatBody.scrollTop = chatBody.scrollHeight;
    }, 1000);

    document.getElementById("user-input").value = "";
});
