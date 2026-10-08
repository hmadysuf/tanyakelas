import os
import re
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
TFIDF_PATH = os.path.join(BASE_DIR, "model", "tfidf.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(TFIDF_PATH)
df = pd.read_csv(DATASET_PATH)


def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_nim(user_input):
    """
    Mencari NIM berdasarkan nama mahasiswa
    """

    text = clean_text(user_input)

    # Hapus kata-kata umum
    stop_words = [
        "berapa",
        "nim",
        "dari",
        "nya",
        "bisa",
        "minta",
        "tolong",
        "saya",
        "ingin",
        "mohon",
        "cari",
        "mahasiswa"
    ]

    words = text.split()

    name_words = [
        word for word in words
        if word not in stop_words
    ]

    if not name_words:
        return None

    # Dataset hanya diambil dari intent cek_nim
    nim_df = df[df["intent"] == "cek_nim"].copy()

    # Cari berdasarkan teks training
    for _, row in nim_df.iterrows():

        training_text = clean_text(row["text"])

        # Cek apakah semua kata nama ada di training text
        if all(word in training_text for word in name_words):

            return row["response"]

    return None


def get_response(user_input):

    cleaned_text = clean_text(user_input)

    vector = vectorizer.transform([cleaned_text])

    probabilities = model.predict_proba(vector)[0]

    best_index = probabilities.argmax()

    intent = model.classes_[best_index]

    confidence = float(probabilities[best_index])

    # ==========================================
    # KHUSUS CEK NIM
    # ==========================================

    if intent == "cek_nim":

        nim = get_nim(user_input)

        if nim:

            return {
                "response": f"NIM mahasiswa tersebut adalah {nim}",
                "intent": "cek_nim",
                "confidence": confidence
            }

        return {
            "response": "Maaf, nama mahasiswa tersebut tidak ditemukan.",
            "intent": "cek_nim",
            "confidence": confidence
        }

    # ==========================================
    # INTENT LAIN
    # ==========================================

    if confidence < 0.30:

        return {
            "response": "Maaf, saya belum memahami pertanyaan tersebut.",
            "intent": "unknown",
            "confidence": confidence
        }

    responses = df[df["intent"] == intent]["response"]

    if len(responses) == 0:

        return {
            "response": "Maaf, jawaban belum tersedia.",
            "intent": intent,
            "confidence": confidence
        }

    response = responses.iloc[0]

    return {
        "response": response,
        "intent": intent,
        "confidence": confidence
    }

if __name__ == "__main__":
    print("=" * 50)
    print("        TANYABOT - CHATBOT DATA MINING")
    print("=" * 50)
    print("Ketik 'exit' untuk keluar.")
    print()

    while True:
        user_input = input("Anda : ")

        if user_input.lower() == "exit":
            print("Bot  : Terima kasih. Sampai jumpa.")
            break

        if not user_input.strip():
            continue

        result = get_response(user_input)

        print(f"Bot  : {result['response']}")
        print(f"Intent     : {result['intent']}")
        print(f"Confidence : {result['confidence']:.2%}")
        print()