
import os
import re
import pandas as pd
import joblib

from dotenv import load_dotenv
from groq import Groq

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"))

MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
TFIDF_PATH = os.path.join(BASE_DIR, "model", "tfidf.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")

# Konfigurasi Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Model klasifikasi lokal
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(TFIDF_PATH)

# Dataset lokal
df = pd.read_csv(DATASET_PATH)

# Validasi struktur dataset
required_columns = {"text", "intent", "response"}
if not required_columns.issubset(df.columns):
    raise ValueError(
        "dataset.csv harus memiliki kolom text, intent, response"
    )


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_nim(user_input):
    """Pencarian NIM secara lokal."""

    text = clean_text(user_input)

    stop_words = {
        "berapa", "nim", "dari", "nya", "bisa", "minta",
        "tolong", "saya", "ingin", "mohon", "cari",
        "mahasiswa", "siapa", "nama", "adalah", "untuk"
    }

    name_words = [
        word for word in text.split()
        if word not in stop_words
    ]

    if not name_words:
        return None

    nim_df = df[df["intent"] == "cek_nim"]

    for _, row in nim_df.iterrows():
        training_text = clean_text(row["text"])

        if all(word in training_text for word in name_words):
            return str(row["response"])

    return None


def get_local_response(intent):
    """Jawaban cadangan dari dataset lokal."""

    responses = df.loc[
        df["intent"] == intent, "response"
    ].dropna()

    if not responses.empty:
        return str(responses.iloc[0])

    return "Maaf, informasi tersebut belum tersedia."


def get_context(intent):
    """
    Mengambil fakta dari dataset lokal untuk diberikan ke AI.
    Batasi jumlah baris agar konteks tidak terlalu besar.
    """

    rows = df.loc[
        df["intent"] == intent, ["text", "response"]
    ].dropna().head(15)

    if rows.empty:
        return ""

    context = []

    for _, row in rows.iterrows():
        context.append(
            f"Pertanyaan referensi: {row['text']}\n"
            f"Informasi lokal: {row['response']}"
        )

    return "\n\n".join(context)


def ask_groq(user_input, intent, context):
    """Menghasilkan jawaban berdasarkan konteks dataset lokal."""

    if client is None:
        raise RuntimeError("GROQ_API_KEY belum dikonfigurasi.")

    if not context.strip():
        return None

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                            "Kamu adalah Tanyabot, asisten akademik yang menjawab "
        "dalam bahasa Indonesia secara jelas, langsung, dan ringkas. "

        "Jika pengguna menanyakan definisi atau konsep umum, "
        "seperti data mining, metode simpleks, statistik, "
        "atau pemrograman, jelaskan langsung berdasarkan "
        "pengetahuan umum yang relevan. "

        "JANGAN menulis disclaimer seperti 'informasi belum tersedia "
        "dalam DATA LOKAL', 'informasi tidak tersedia di database', "
        "atau kalimat sejenis untuk pertanyaan konsep umum. "

        "Untuk pertanyaan khusus Universitas Pamulang, mahasiswa, "
        "NIM, dosen, jadwal, tagihan, SKS, dan aturan akademik, "
        "gunakan hanya data lokal yang diberikan. "
        "Jika data spesifik tersebut tidak tersedia, sampaikan "
        "secara singkat bahwa informasi belum tersedia. "

        "Jangan mengarang data akademik atau data pribadi. "
        "Berikan jawaban langsung tanpa menjelaskan proses internal "
        "atau keterbatasan sumber data jika tidak diperlukan."
                )
            },
            {
                "role": "user",
                "content": (
                    f"INTENT TERDETEKSI: {intent}\n\n"
                    f"DATA LOKAL:\n{context}\n\n"
                    f"PERTANYAAN PENGGUNA:\n{user_input}\n\n"
                    "Jawab berdasarkan data lokal di atas."
                )
            }
        ],
        temperature=0.1,
        max_tokens=400,
        timeout=30
    )

    answer = completion.choices[0].message.content

    if not answer or not answer.strip():
        return None

    return answer.strip()

def is_nim_question(user_input):
    text = clean_text(user_input)

    nim_keywords = [
        "nim",
        "nomor induk mahasiswa",
        "nomor mahasiswa"
    ]

    return any(keyword in text for keyword in nim_keywords)

def is_general_question(user_input):
    """Mendeteksi pertanyaan pengetahuan umum."""

    text = clean_text(user_input)

    general_patterns = [
        r"\bapa itu\b",
        r"\bapa fungsi\b",
        r"\bapa kegunaan\b",
        r"\bkegunaan\b",
        r"\bkegunaannya\b",
        r"\bmanfaat\b",
        r"\bjelaskan\b",
        r"\bpengertian\b",
        r"\bdefinisi\b",
        r"\bbagaimana cara kerja\b",
        r"\buntuk apa\b",
        r"\bapa yang dimaksud\b"
    ]

    return any(
        re.search(pattern, text)
        for pattern in general_patterns
    )

def get_response(user_input):
    cleaned_text = clean_text(user_input)

    if not cleaned_text:
        return {
            "response": "Silakan masukkan pertanyaan terlebih dahulu.",
            "intent": "unknown",
            "confidence": 0.0
        }

    # Klasifikasi intent tetap berjalan secara lokal.
    vector = vectorizer.transform([cleaned_text])
    probabilities = model.predict_proba(vector)[0]

    best_index = probabilities.argmax()
    intent = model.classes_[best_index]
    confidence = float(probabilities[best_index])

    # Pencarian NIM tetap lokal.
    # Jangan kirim nama atau NIM mahasiswa ke Groq.
    if intent == "cek_nim" and is_nim_question(user_input):
        nim = get_nim(user_input)

        if nim:
            response = f"Informasi NIM: {nim}"
        else:
            response = (
                "Maaf, nama mahasiswa tersebut tidak ditemukan "
                "dalam data lokal."
            )

        return {
            "response": response,
            "intent": "cek_nim",
            "confidence": confidence
        }

      # ==========================================
    # PERTANYAAN PENGETAHUAN UMUM
    # Jalankan sebelum pemeriksaan confidence
    # ==========================================

    if is_general_question(user_input):

        general_context = (
            "Jawab pertanyaan pengetahuan umum menggunakan "
            "pengetahuan umum yang relevan. "
            "Berikan jawaban langsung dalam bahasa Indonesia. "
            "Jangan membatasi jawaban hanya pada dataset lokal. "
            "Jangan mengarang informasi spesifik tentang kampus, "
            "mahasiswa, jadwal, tagihan, atau data pribadi. "
            "Jika pertanyaan meminta data spesifik kampus yang "
            "tidak tersedia, jelaskan bahwa data tersebut belum tersedia."
        )

        try:
            answer = ask_groq(
                user_input,
                "pertanyaan_umum",
                general_context
            )

            if answer:
                return {
                    "response": answer,
                    "intent": "pertanyaan_umum",
                    "confidence": confidence
                }

        except Exception as error:
            print(
                f"Groq API error: {type(error).__name__}"
            )

        return {
            "response": (
                "Maaf, saya belum dapat menjawab pertanyaan "
                "tersebut saat ini. Silakan coba kembali."
            ),
            "intent": "pertanyaan_umum",
            "confidence": confidence
        }


    # Pertanyaan dengan keyakinan klasifikasi rendah
    # tidak langsung dijawab oleh AI dengan fakta tebakan.
    if confidence < 0.40:
        return {
            "response": (
                "Maaf, saya belum memahami pertanyaan tersebut. "
                "Coba tanyakan tentang jadwal, dosen, kelas, SKS, "
                "tagihan, tugas, atau aturan kuliah."
            ),
            "intent": "unknown",
            "confidence": confidence
        }

    # Pertanyaan tentang tugas tetap menggunakan link
    # yang sudah ditangani oleh app.py.
    # Jawaban AI dipakai untuk intent lainnya.
    context = get_context(intent)

    if client is not None and context:
        try:
            answer = ask_groq(user_input, intent, context)

            if answer:
                return {
                    "response": answer,
                    "intent": intent,
                    "confidence": confidence
                }

        except Exception as error:
            # Catat error di terminal, jangan tampilkan API key
            # atau detail internal kepada pengguna.
            print(f"Groq API error: {type(error).__name__}")
            print(f"Detail: {error}")

    # Fallback jika API gagal atau tidak tersedia.
    return {
        "response": get_local_response(intent),
        "intent": intent,
        "confidence": confidence
    }


if __name__ == "__main__":
    print("=" * 50)
    print("       TANYABOT - GROQ AI + DATA LOKAL")
    print("=" * 50)
    print(f"Model: {GROQ_MODEL}")
    print(f"Groq API: {'Aktif' if client else 'Tidak dikonfigurasi'}")
    print("Ketik 'exit' untuk keluar.\n")

    while True:
        user_input = input("Anda: ")

        if user_input.strip().lower() == "exit":
            print("Bot: Terima kasih. Sampai jumpa.")
            break

        if not user_input.strip():
            continue

        result = get_response(user_input)

        print(f"Bot: {result['response']}")
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.2%}\n")
