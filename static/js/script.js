document.addEventListener("DOMContentLoaded", function () {

    const input = document.getElementById("message");
    const sendButton = document.getElementById("sendButton");
    const chatbox = document.getElementById("chatbox");

    let isSending = false;


    // =====================================================
    // SEND MESSAGE
    // =====================================================

    async function sendMessage() {

        // Cegah request dikirim dua kali
        if (isSending) {
            return;
        }

        const message = input.value.trim();

        if (!message) {
            return;
        }

        isSending = true;

        // Tampilkan pesan user
        addMessage(message, "user");

        // Kosongkan input
        input.value = "";

        // Disable tombol
        sendButton.disabled = true;
        sendButton.innerHTML = "⋯";


        // =================================================
        // TAMPILKAN THINKING
        // =================================================

        const thinkingId = showThinking();


        try {

            // =================================================
            // REQUEST KE FLASK
            // =================================================

            const response = await fetch(
                "/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        message: message
                    })
                }
            );


            if (!response.ok) {

                throw new Error(
                    "HTTP Error: " + response.status
                );

            }


            const data = await response.json();


            // =================================================
            // DELAY THINKING 500 - 800 ms
            // =================================================

            const delay =
                Math.floor(
                    Math.random() * 301
                ) + 500;


            await new Promise(
                resolve =>
                    setTimeout(
                        resolve,
                        delay
                    )
            );


            // =================================================
            // HAPUS THINKING TERLEBIH DAHULU
            // =================================================

            removeThinking(thinkingId);


            // =================================================
            // TAMPILKAN JAWABAN
            // =================================================

            addMessage(
                data.response,
                "bot"
            );


            // =================================================
            // TAMPILKAN INFO MODEL
            // =================================================

            addInfo(
                data.intent,
                data.confidence
            );


        } catch (error) {

            console.error(
                "Error:",
                error
            );


            // Hapus thinking jika terjadi error
            removeThinking(
                thinkingId
            );


            addMessage(
                "Terjadi kesalahan saat menghubungi server.",
                "bot"
            );

        }


        // =================================================
        // AKTIFKAN KEMBALI INPUT
        // =================================================

        sendButton.disabled = false;

        sendButton.innerHTML = "➤";

        isSending = false;

        input.focus();

    }


    // =====================================================
    // SHOW THINKING
    // =====================================================

    function showThinking() {

        const id =
            "thinking-" + Date.now();


        const row =
            document.createElement("div");


        row.classList.add(
            "message-row",
            "bot-row"
        );


        row.id = id;


        const bubble =
            document.createElement("div");


        bubble.classList.add(
            "message",
            "bot-message",
            "thinking-message"
        );


        const content =
            document.createElement("div");


        content.classList.add(
            "thinking-content"
        );


        const text =
            document.createElement("span");


        text.innerText =
            "Sedang berpikir";


        const dots =
            document.createElement("span");


        dots.classList.add(
            "thinking-dots"
        );


        dots.innerHTML =
            "<span>•</span>" +
            "<span>•</span>" +
            "<span>•</span>";


        content.appendChild(
            text
        );


        content.appendChild(
            dots
        );


        bubble.appendChild(
            content
        );


        row.appendChild(
            bubble
        );


        chatbox.appendChild(
            row
        );


        scrollChat();


        return id;

    }


    // =====================================================
    // REMOVE THINKING
    // =====================================================

    function removeThinking(id) {

        const thinking =
            document.getElementById(id);


        if (thinking) {

            thinking.remove();

        }

    }


    // =====================================================
    // ADD MESSAGE
    // =====================================================

    function addMessage(
        message,
        sender
    ) {

        const row =
            document.createElement("div");


        row.classList.add(
            "message-row"
        );


        if (sender === "user") {

            row.classList.add(
                "user-row"
            );

        } else {

            row.classList.add(
                "bot-row"
            );

        }


        const bubble =
            document.createElement("div");


        bubble.classList.add(
            "message"
        );


        if (sender === "user") {

            bubble.classList.add(
                "user-message"
            );

        } else {

            bubble.classList.add(
                "bot-message"
            );

        }


        const text =
            document.createElement("div");


        text.classList.add(
            "message-text"
        );


        text.innerText =
            message;


        const time =
            document.createElement("div");


        time.classList.add(
            "message-time"
        );


        time.innerText =
            getCurrentTime();


        bubble.appendChild(
            text
        );


        bubble.appendChild(
            time
        );


        row.appendChild(
            bubble
        );


        chatbox.appendChild(
            row
        );


        scrollChat();

    }


    // =====================================================
    // MODEL INFO
    // =====================================================

    function addInfo(
        intent,
        confidence
    ) {

        const info =
            document.createElement("div");


        info.classList.add(
            "model-info"
        );


        const percent =
            (
                confidence * 100
            ).toFixed(2);


        info.innerText =
            "Intent: " +
            intent +
            " • Confidence: " +
            percent +
            "%";


        chatbox.appendChild(
            info
        );


        scrollChat();

    }


    // =====================================================
    // CURRENT TIME
    // =====================================================

    function getCurrentTime() {

        const now =
            new Date();


        return now.toLocaleTimeString(
            "id-ID",
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        );

    }


    // =====================================================
    // SCROLL CHAT
    // =====================================================

    function scrollChat() {

        chatbox.scrollTop =
            chatbox.scrollHeight;

    }


    // =====================================================
    // BUTTON CLICK
    // =====================================================

    sendButton.addEventListener(
        "click",
        sendMessage
    );


    // =====================================================
    // ENTER
    // =====================================================

    input.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter"
            ) {

                event.preventDefault();

                sendMessage();

            }

        }
    );


    // Fokus input
    input.focus();

});