
from flask import Flask, render_template, request, jsonify
from chatbot import get_response

app = Flask(__name__)


def get_suggestions(intent, user_input=""):
    """Menghasilkan rekomendasi berdasarkan topik percakapan."""

    text = user_input.lower()

    suggestions_map = {
        "cek_nim": [
            {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"},
            {"label": "Dosen mata kuliah", "message": "Siapa dosen Data Mining?"},
            {"label": "Informasi kelas", "message": "Saya berada di kelas berapa?"}
        ],
        "cek_dosen": [
            {"label": "Jadwal kuliah", "message": "Bagaimana jadwal kuliah saya?"},
            {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"},
            {"label": "Informasi tugas", "message": "Apa saja tugas kuliah saya?"}
        ],
        "cek_jadwal": [
            {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"},
            {"label": "Jadwal UAS", "message": "Kapan jadwal UAS?"},
            {"label": "Dosen mata kuliah", "message": "Siapa dosen Data Mining?"}
        ],
        "cek_jadwal_uts": [
            {"label": "Jadwal UAS", "message": "Kapan jadwal UAS?"},
            {"label": "Informasi tugas", "message": "Apa saja tugas kuliah saya?"},
            {"label": "Dosen mata kuliah", "message": "Siapa dosen Data Mining?"}
        ],
        "cek_jadwal_uas": [
            {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"},
            {"label": "Informasi tugas", "message": "Apa saja tugas kuliah saya?"},
            {"label": "Dosen mata kuliah", "message": "Siapa dosen Data Mining?"}
        ],
        "cek_tugas": [
            {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"},
            {"label": "Jadwal UAS", "message": "Kapan jadwal UAS?"},
            {"label": "Aturan presensi", "message": "Bagaimana aturan presensi kuliah?"}
        ],
        "cek_aturan": [
            {"label": "Aturan absensi", "message": "Berapa kali boleh tidak masuk kuliah?"},
            {"label": "Presensi e-learning", "message": "Bagaimana syarat presensi e-learning?"},
            {"label": "Informasi tugas", "message": "Apa saja tugas kuliah saya?"}
        ],
        "cek_kelas": [
            {"label": "Cek NIM", "message": "Bagaimana cara mengetahui NIM mahasiswa?"},
            {"label": "Dosen mata kuliah", "message": "Siapa dosen Data Mining?"},
            {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"}
        ],
        "cek_sks": [
            {"label": "Informasi kelas", "message": "Saya berada di kelas berapa?"},
            {"label": "Dosen mata kuliah", "message": "Siapa dosen Data Mining?"},
            {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"}
        ],
        "cek_tagihan": [
            {"label": "Informasi SKS", "message": "Berapa jumlah SKS saya?"},
            {"label": "Informasi kelas", "message": "Saya berada di kelas berapa?"},
            {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"}
        ],
        "cek_sistem": [
            {"label": "Informasi kelas", "message": "Saya berada di kelas berapa?"},
            {"label": "Informasi tugas", "message": "Apa saja tugas kuliah saya?"},
            {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"}
        ]
    }

    # Rekomendasi umum jika model belum memahami pertanyaan.
    default_suggestions = [
        {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"},
        {"label": "Dosen mata kuliah", "message": "Siapa dosen Data Mining?"},
        {"label": "Informasi tugas", "message": "Apa saja tugas kuliah saya?"}
    ]

    if intent == "cek_aturan":
        if any(word in text for word in ["elearning", "e-learning", "daring", "kuesioner"]):
            return [
                {"label": "Aturan absensi", "message": "Berapa kali boleh tidak masuk kuliah?"},
                {"label": "Jadwal UTS", "message": "Kapan jadwal UTS?"},
                {"label": "Informasi tugas", "message": "Apa saja tugas kuliah saya?"}
            ]

    return suggestions_map.get(intent, default_suggestions)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({
            "response": "Silakan masukkan pertanyaan terlebih dahulu.",
            "intent": "unknown",
            "confidence": 0,
            "suggestions": get_suggestions("unknown")
        })

    result = get_response(user_input)

    # Jika intent cek_tugas, tambahkan link tugas kuliah.
    if result.get("intent") == "cek_tugas":
        result["response"] = (
            "Daftar tugas kuliah: "
            "https://docs.google.com/spreadsheets/d/"
            "1IVxIbSN580NolyvbRJ3TJtnJE4Yjii4-Wmj50lIrP8c/edit?usp=sharing"
        )

    # Tambahkan rekomendasi berdasarkan intent dan pertanyaan pengguna.
    result["suggestions"] = get_suggestions(
        result.get("intent", "unknown"),
        user_input
    )

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
