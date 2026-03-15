const askButton = document.getElementById("askButton");
const promptInput = document.getElementById("prompt");
const chatHistory = document.querySelector(".chat-history");


askButton.addEventListener("click", async () => {
    const message = promptInput.value.trim();

    if (message) {

        addMessage(message, "user-message");
        promptInput.value = "";


        const loadingDiv = document.createElement("div");
        loadingDiv.classList.add("message", "bot-message", "loading-indicator");

        loadingDiv.innerHTML = `<span class="spinner"></span> Το AI σκέφτεται...`;
        chatHistory.appendChild(loadingDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;


        try {
            const response = await fetch("http://127.0.0.1:9000/callAI", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    prompt: message
                })
            });

            const result = await response.json();


            loadingDiv.remove();


            addMessage(result.answer, "bot-message");

        } catch (error) {
            console.error("Σφάλμα κατά την επικοινωνία με το AI:", error);


            loadingDiv.remove();

            addMessage("Υπήρξε ένα σφάλμα σύνδεσης με το backend. Δοκίμασε ξανά.", "bot-message");
        }
    }
});

promptInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        askButton.click();
    }
});

function addMessage(text, className) {
    const welcomeScreen = document.getElementById("welcomeScreen");
    if (welcomeScreen) {
        welcomeScreen.remove();
    }

    const messageElement = document.createElement("div");
    messageElement.classList.add("message", className);
    messageElement.textContent = text;
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}