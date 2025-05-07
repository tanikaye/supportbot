console.log("Script loaded successfully");

function toggleChat() {
  const chatWidget = document.getElementById("chat-widget");
  chatWidget.style.display = chatWidget.style.display === "none" ? "block" : "none";
}

function appendMessage(sender, text) {
  const chatMessages = document.getElementById("chat-messages");
  const message = document.createElement("div");
  message.className = sender;
  message.textContent = text;
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function sendMessage() {
  const userInput = document.getElementById("user-input").value;
  if (!userInput) return;

  console.log("Sending message:", userInput);

  appendMessage("user", userInput);

  fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({
          message: userInput,
          business_id: 3
      })
  })
  .then(response => response.json())
  .then(data => {
      appendMessage("bot", data.reply);
  })
  .catch(error => {
      appendMessage("bot", "Error: Unable to connect to the server.");
      console.error("Error:", error);
  });

  document.getElementById("user-input").value = "";
}
