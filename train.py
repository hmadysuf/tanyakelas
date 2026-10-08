import os
import re
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
# from sklearn.svm import LinearSVC
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# =========================================================
# 1. LOAD DATASET
# =========================================================

DATASET = "dataset.csv"
MODEL_DIR = "model"

os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(DATASET)

print("=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print(f"Jumlah data : {len(df)}")
print(f"Jumlah intent : {df['intent'].nunique()}")

print("\nDistribusi Intent:")
print(df["intent"].value_counts())


# =========================================================
# 2. DATA CLEANING
# =========================================================

def clean_text(text):

    text = str(text).lower()

    # Hapus karakter selain huruf dan angka
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Hapus spasi berlebihan
    text = re.sub(r"\s+", " ", text)

    return text.strip()


df["clean_text"] = df["text"].apply(clean_text)


# =========================================================
# 3. INPUT DAN TARGET
# =========================================================

X = df["clean_text"]
y = df["intent"]


# =========================================================
# 4. TRAIN TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining data :", len(X_train))
print("Testing data  :", len(X_test))


# =========================================================
# 5. TF-IDF
# =========================================================

vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print("\nTF-IDF feature :", X_train_tfidf.shape)


# =========================================================
# 6. DEFINISI MODEL
# =========================================================

# models = {

#     "Naive Bayes": MultinomialNB(),

#     "Logistic Regression": LogisticRegression(
#         max_iter=1000
#     ),

#     "SVM": LinearSVC(
#         random_state=42
#     )
# }
models = {

    "Naive Bayes": MultinomialNB(),

    "Logistic Regression": LogisticRegression(
        max_iter=1000
    ),

    "SVM": CalibratedClassifierCV(
        estimator=LinearSVC(
            random_state=42
        ),
        cv=2
    )
}


# =========================================================
# 7. TRAINING DAN EVALUASI
# =========================================================

results = []

best_model = None
best_model_name = None
best_accuracy = 0


print("\n")
print("=" * 60)
print("MODEL EVALUATION")
print("=" * 60)


for name, model in models.items():

    print(f"\nTraining {name}...")

    model.fit(
        X_train_tfidf,
        y_train
    )

    y_pred = model.predict(
        X_test_tfidf
    )

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1
    })

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1-Score  : {f1:.4f}")

    # Simpan model terbaik
    if accuracy > best_accuracy:

        best_accuracy = accuracy
        best_model = model
        best_model_name = name


# =========================================================
# 8. HASIL PERBANDINGAN
# =========================================================

results_df = pd.DataFrame(results)

print("\n")
print("=" * 60)
print("COMPARISON RESULT")
print("=" * 60)

print(
    results_df.to_string(index=False)
)


# =========================================================
# 9. BEST MODEL
# =========================================================

print("\n")
print("=" * 60)
print("BEST MODEL")
print("=" * 60)

print(f"Model     : {best_model_name}")
print(f"Accuracy  : {best_accuracy:.4f}")


# =========================================================
# 10. CLASSIFICATION REPORT
# =========================================================

best_prediction = best_model.predict(
    X_test_tfidf
)

print("\n")
print("=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)

print(
    classification_report(
        y_test,
        best_prediction,
        zero_division=0
    )
)


# =========================================================
# 11. CONFUSION MATRIX
# =========================================================

print("\n")
print("=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

cm = confusion_matrix(
    y_test,
    best_prediction
)

print(cm)


# =========================================================
# 12. SAVE MODEL
# =========================================================

model_path = os.path.join(
    MODEL_DIR,
    "model.pkl"
)

tfidf_path = os.path.join(
    MODEL_DIR,
    "tfidf.pkl"
)

joblib.dump(
    best_model,
    model_path
)

joblib.dump(
    vectorizer,
    tfidf_path
)


print("\n")
print("=" * 60)
print("MODEL SAVED")
print("=" * 60)

print(f"Model  : {model_path}")
print(f"TF-IDF : {tfidf_path}")

print("\nTraining selesai.")