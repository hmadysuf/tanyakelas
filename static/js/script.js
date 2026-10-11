
document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("message");
    const sendButton = document.getElementById("sendButton");
    const chatbox = document.getElementById("chatbox");
    const suggestionsContainer = document.getElementById("suggestions");

    let isSending = false;


    // =====================================================
    // SEND MESSAGE
    // =====================================================

    async function sendMessage() {

        if (isSending) return;

        const message = input.value.trim();

        if (!message) return;

        isSending = true;

        addMessage(message, "user");

        input.value = "";

        // Hilangkan rekomendasi sebelumnya saat pertanyaan dikirim.
        suggestionsContainer.innerHTML = "";

        sendButton.disabled = true;
        sendButton.innerHTML = "⋯";

        const thinkingId = showThinking();

        try {

            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: message
                })
            });

            if (!response.ok) {
                throw new Error("HTTP Error: " + response.status);
            }

            const data = await response.json();

            // Simulasi jeda agar chatbot terasa sedang memproses.
            const delay = Math.floor(Math.random() * 301) + 500;

            await new Promise(resolve => setTimeout(resolve, delay));

            removeThinking(thinkingId);

            addMessage(
                data.response || "Maaf, jawaban belum tersedia.",
                "bot"
            );

            addInfo(
                data.intent || "unknown",
                Number(data.confidence) || 0
            );

            // Tampilkan rekomendasi lanjutan dari Flask.
            renderSuggestions(data.suggestions || []);

        } catch (error) {

            console.error("Error:", error);

            removeThinking(thinkingId);

            addMessage(
                "Terjadi kesalahan saat menghubungi server.",
                "bot"
            );

            renderSuggestions([
                {
                    label: "Coba lagi",
                    message: message
                },
                {
                    label: "Jadwal UTS",
                    message: "Kapan jadwal UTS?"
                }
            ]);

        } finally {

            sendButton.disabled = false;
            sendButton.innerHTML = "➤";

            isSending = false;

            input.focus();
        }
    }


    // =====================================================
    // RENDER RECOMMENDATIONS
    // =====================================================

    function renderSuggestions(suggestions) {

        suggestionsContainer.innerHTML = "";

        if (!Array.isArray(suggestions) || suggestions.length === 0) {
            return;
        }

        suggestions.forEach(function (item) {

            const button = document.createElement("button");

            button.type = "button";
            button.className = "suggestion";
            button.dataset.message = item.message;
            button.textContent = item.label;

            suggestionsContainer.appendChild(button);
        });

        scrollChat();
    }


    // =====================================================
    // CLICK RECOMMENDATION
    // =====================================================

    suggestionsContainer.addEventListener("click", function (event) {

        const button = event.target.closest(".suggestion");

        if (!button || isSending) return;

        input.value = button.dataset.message || "";

        sendMessage();
    });


    // =====================================================
    // SHOW THINKING
    // =====================================================

    function showThinking() {

        const id = "thinking-" + Date.now();

        const row = document.createElement("div");
        row.classList.add("message-row", "bot-row");
        row.id = id;

        const bubble = document.createElement("div");
        bubble.classList.add(
            "message",
            "bot-message",
            "thinking-message"
        );

        const content = document.createElement("div");
        content.classList.add("thinking-content");

        const text = document.createElement("span");
        text.innerText = "Sedang berpikir";

        const dots = document.createElement("span");
        dots.classList.add("thinking-dots");

        dots.innerHTML =
            "<span>•</span>" +
            "<span>•</span>" +
            "<span>•</span>";

        content.appendChild(text);
        content.appendChild(dots);
        bubble.appendChild(content);
        row.appendChild(bubble);
        chatbox.appendChild(row);

        scrollChat();

        return id;
    }


    // =====================================================
    // REMOVE THINKING
    // =====================================================

    function removeThinking(id) {

        const thinking = document.getElementById(id);

        if (thinking) {
            thinking.remove();
        }
    }


    // =====================================================
    // ADD MESSAGE
    // =====================================================

    function addMessage(message, sender) {

        const row = document.createElement("div");
        row.classList.add("message-row");

        row.classList.add(
            sender === "user" ? "user-row" : "bot-row"
        );

        const bubble = document.createElement("div");
        bubble.classList.add("message");

        bubble.classList.add(
            sender === "user" ? "user-message" : "bot-message"
        );

        const text = document.createElement("div");
        text.classList.add("message-text");
        const taskLinkPrefix = "Daftar tugas kuliah: ";
        if (sender === "bot" && message.startsWith(taskLinkPrefix)) {
            const url = message.slice(taskLinkPrefix.length).trim();
            text.appendChild(document.createTextNode(taskLinkPrefix));

            const link = document.createElement("a");
            link.href = url;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = url;
            text.appendChild(link);
        } else {
            text.innerText = message;
        }

        const time = document.createElement("div");
        time.classList.add("message-time");
        time.innerText = getCurrentTime();

        bubble.appendChild(text);
        bubble.appendChild(time);
        row.appendChild(bubble);

        // Sisipkan pesan sebelum panel rekomendasi.
        chatbox.insertBefore(row, suggestionsContainer.parentElement);

        scrollChat();
    }


    // =====================================================
    // MODEL INFO
    // =====================================================

    function addInfo(intent, confidence) {

        const info = document.createElement("div");
        info.classList.add("model-info");

        const percent = (confidence * 100).toFixed(2);

        info.innerText =
            "Intent: " + intent +
            " • Confidence: " + percent + "%";

        chatbox.insertBefore(info, suggestionsContainer.parentElement);

        scrollChat();
    }


    // =====================================================
    // CURRENT TIME
    // =====================================================

    function getCurrentTime() {

        return new Date().toLocaleTimeString("id-ID", {
            hour: "2-digit",
            minute: "2-digit"
        });
    }


    // =====================================================
    // SCROLL CHAT
    // =====================================================

    function scrollChat() {
        chatbox.scrollTop = chatbox.scrollHeight;
    }


    // =====================================================
    // SEND BUTTON
    // =====================================================

    sendButton.addEventListener("click", sendMessage);


    // =====================================================
    // ENTER KEY
    // =====================================================

    input.addEventListener("keydown", function (event) {

        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });

    input.focus();

});
