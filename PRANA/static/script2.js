document.getElementById("chat-toggle").addEventListener("click", function () {
  document.querySelector(".chatbot").style.display = "flex";
});

document.getElementById("close-btn").addEventListener("click", function () {
  document.querySelector(".chatbot").style.display = "none";
});

document.getElementById("send-btn").addEventListener("click", function () {
  let userInput = document.getElementById("user-input").value.trim();
  if (userInput === "") return;

  let chatBody = document.getElementById("chat-body");

  // Display user message
  let userMessage = document.createElement("div");
  userMessage.classList.add("message", "user-message");
  userMessage.textContent = userInput;
  chatBody.appendChild(userMessage);

  // Create a loading message while waiting for response
  let loadingMessage = document.createElement("div");
  loadingMessage.classList.add("message", "bot-message");
  loadingMessage.textContent = "Thinking...";
  chatBody.appendChild(loadingMessage);

  // Auto-scroll to bottom
  chatBody.scrollTop = chatBody.scrollHeight;

  // Call Gemini AI API
  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: userInput }),
  })
    .then((response) => response.json())
    .then((data) => {
      // Remove the "Thinking..." message
      loadingMessage.remove();

      // Display bot response
      let botMessage = document.createElement("div");
      botMessage.classList.add("message", "bot-message");
      botMessage.textContent = data.response;
      chatBody.appendChild(botMessage);

      // Auto-scroll to latest message
      chatBody.scrollTop = chatBody.scrollHeight;
    })
    .catch((error) => {
      console.error("Error:", error);
      loadingMessage.textContent = "Error getting response!";
    });

  // Clear user input field
  document.getElementById("user-input").value = "";
});


