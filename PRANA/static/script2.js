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
  const userMessage = document.createElement("div");
  userMessage.classList.add("message", "fromMe");
  userMessage.textContent = userInput;
  chatBody.appendChild(userMessage);

  // Send message to Node.js server
  fetch("http://localhost:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userInput }),
  })
  .then((response) => response.json())
  .then((data) => {
      // Display bot response
      const botMessage = document.createElement("div");
      botMessage.classList.add("message", "fromThem");
      botMessage.textContent = data.response;
      chatBody.appendChild(botMessage);
      
      chatBody.scrollTop = chatBody.scrollHeight;
  })
  .catch((error) => console.error("Error:", error));

  document.getElementById("user-input").value = "";
});
