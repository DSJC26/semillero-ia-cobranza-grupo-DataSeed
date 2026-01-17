const chatWindow = document.getElementById("chat-window");
const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// ID fijo de sesión para pruebas
const SESSION_ID = "demo-session-1";

// URL del backend (local); luego la cambiarás a la de Railway
const API_URL = "https://semillero-ia-cobranza-grupo-dataseed-production.up.railway.app/api/chat";

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = "message " + sender;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";
  sendBtn.disabled = true;

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: SESSION_ID, message: text }),
    });

    const data = await res.json();
    if (data.reply) {
      addMessage(data.reply, "bot");
    } else if (data.error) {
      addMessage("Error: " + data.error, "bot");
    } else {
      addMessage("Error en la respuesta del servidor.", "bot");
    }
  } catch (e) {
    addMessage("No se pudo conectar con el backend.", "bot");
  } finally {
    sendBtn.disabled = false;
  }
}

sendBtn.addEventListener("click", sendMessage);
input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});

// Mensaje inicial del bot
addMessage(
  "Hola, soy AsistenteDataSeed de Netlife. ¿Cuál es tu ID o cédula para revisar tu caso?",
  "bot"
);
