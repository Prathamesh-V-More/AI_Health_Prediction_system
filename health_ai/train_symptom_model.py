"""
Train symptom-based disease prediction model.
Uses the Kaggle Disease Symptom dataset (built-in synthetic data if not available).
Run: python train_symptom_model.py
Saves: models_saved/symptom_model.pkl
"""
import os
import pickle
import sys

print("Training symptom-based disease prediction model...")

# Try to import sklearn
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    import numpy as np
except ImportError:
    print("Installing scikit-learn and numpy...")
    os.system("pip install scikit-learn numpy")
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    import numpy as np

# ── Load dataset ───────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "dataset.csv")

if os.path.exists(DATA_PATH):
    import csv
    print(f"Loading dataset from {DATA_PATH}...")
    rows = []
    with open(DATA_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f"Loaded {len(rows)} records.")
else:
    print("No dataset found. Generating synthetic training data...")
    print("For better accuracy, download: kaggle datasets download -d kaushil268/disease-prediction-using-machine-learning")

    # Synthetic training data based on known symptom-disease relationships
    SYNTHETIC_DATA = [
        # (disease, [symptoms])
        ("Fungal infection",    ["itching","skin_rash","nodal_skin_eruptions","dischromic_patches"]),
        ("Fungal infection",    ["itching","skin_rash","nodal_skin_eruptions"]),
        ("Allergy",             ["continuous_sneezing","shivering","chills","watering_from_eyes","runny_nose"]),
        ("Allergy",             ["continuous_sneezing","chills","watering_from_eyes","redness_of_eyes"]),
        ("GERD",                ["acidity","ulcers_on_tongue","vomiting","indigestion","chest_pain"]),
        ("GERD",                ["acidity","indigestion","stomach_pain","vomiting"]),
        ("Diabetes",            ["polyuria","fatigue","weight_loss","excessive_hunger","irregular_sugar_level"]),
        ("Diabetes",            ["polyuria","fatigue","weight_loss","blurred_and_distorted_vision"]),
        ("Tuberculosis",        ["fatigue","weight_loss","high_fever","sweating","chills","cough","blood_in_sputum"]),
        ("Tuberculosis",        ["cough","high_fever","fatigue","weight_loss","night_sweats"]),
        ("Dengue",              ["high_fever","headache","nausea","vomiting","muscle_pain","joint_pain","redness_of_eyes"]),
        ("Dengue",              ["high_fever","headache","pain_behind_the_eyes","muscle_pain","skin_rash"]),
        ("Malaria",             ["high_fever","chills","sweating","headache","nausea","vomiting"]),
        ("Malaria",             ["chills","high_fever","sweating","headache","fatigue"]),
        ("Pneumonia",           ["cough","high_fever","breathlessness","chest_pain","rusty_sputum"]),
        ("Pneumonia",           ["cough","high_fever","breathlessness","fatigue","phlegm"]),
        ("Hypothyroidism",      ["fatigue","weight_gain","cold_hands_and_feets","mood_swings","lethargy","enlarged_thyroid"]),
        ("Hypothyroidism",      ["fatigue","weight_gain","depression","brittle_nails","enlarged_thyroid"]),
        ("Heart attack",        ["chest_pain","fast_heart_rate","sweating","breathlessness","vomiting"]),
        ("Heart attack",        ["chest_pain","sweating","breathlessness","nausea","fatigue"]),
        ("Jaundice",            ["yellowish_skin","dark_urine","nausea","loss_of_appetite","fatigue","yellowing_of_eyes"]),
        ("Jaundice",            ["yellowish_skin","yellowing_of_eyes","dark_urine","abdominal_pain"]),
        ("Migraine",            ["headache","nausea","vomiting","blurred_and_distorted_vision","visual_disturbances"]),
        ("Migraine",            ["headache","nausea","sensitivity_to_light","vomiting"]),
        ("Common Cold",         ["continuous_sneezing","cough","fatigue","mild_fever","runny_nose","congestion"]),
        ("Common Cold",         ["cough","runny_nose","congestion","mild_fever","throat_irritation"]),
        ("Urinary tract infection",["burning_micturition","bladder_discomfort","foul_smell_of_urine","continuous_feel_of_urine"]),
        ("Urinary tract infection",["burning_micturition","dark_urine","bladder_discomfort","fatigue"]),
        ("Psoriasis",           ["skin_rash","joint_pain","skin_peeling","silver_like_dusting","small_dents_in_nails"]),
        ("Psoriasis",           ["skin_rash","skin_peeling","inflammatory_nails","joint_pain"]),
        ("Acne",                ["pus_filled_pimples","blackheads","skin_rash","scurring"]),
        ("Acne",                ["pus_filled_pimples","blackheads","skin_rash"]),
        ("Arthritis",           ["joint_pain","swelling_joints","movement_stiffness","painful_walking"]),
        ("Arthritis",           ["joint_pain","swelling_joints","stiff_neck","muscle_pain"]),
        ("Hypertension",        ["headache","chest_pain","dizziness","loss_of_balance","lack_of_concentration"]),
        ("Hypertension",        ["headache","dizziness","chest_pain","fatigue"]),
        ("Chicken pox",         ["skin_rash","high_fever","fatigue","loss_of_appetite","blister"]),
        ("Chicken pox",         ["skin_rash","itching","high_fever","blister","red_spots_over_body"]),
        ("Typhoid",             ["high_fever","headache","nausea","constipation","abdominal_pain","fatigue"]),
        ("Typhoid",             ["high_fever","fatigue","abdominal_pain","diarrhoea","vomiting"]),
        ("Hepatitis B",         ["fatigue","yellowish_skin","dark_urine","loss_of_appetite","abdominal_pain","yellowing_of_eyes"]),
        ("Hepatitis B",         ["fatigue","yellowish_skin","nausea","vomiting","joint_pain"]),
        ("Bronchial Asthma",    ["cough","breathlessness","chest_pain","fatigue","phlegm"]),
        ("Bronchial Asthma",    ["breathlessness","cough","chest_pain","wheezing"]),
        ("(vertigo) Paroxysmal Positional Vertigo",["dizziness","spinning_movements","loss_of_balance","unsteadiness","nausea"]),
        ("(vertigo) Paroxysmal Positional Vertigo",["dizziness","loss_of_balance","spinning_movements","headache"]),
        ("Hypoglycemia",        ["fatigue","anxiety","sweating","headache","excessive_hunger","fast_heart_rate"]),
        ("Hypoglycemia",        ["fatigue","sweating","excessive_hunger","dizziness","irritability"]),
        ("Gastroenteritis",     ["vomiting","diarrhoea","stomach_pain","dehydration","nausea"]),
        ("Gastroenteritis",     ["vomiting","diarrhoea","abdominal_pain","fatigue","nausea"]),
    ]

    # Build rows from synthetic data
    from ml.symptom_predict import ALL_SYMPTOMS
    rows = []
    for disease, symptoms in SYNTHETIC_DATA:
        row = {"prognosis": disease}
        for s in ALL_SYMPTOMS:
            row[s] = "1" if s in symptoms else "0"
        rows.append(row)
    # Duplicate for more training data
    rows = rows * 8
    print(f"Generated {len(rows)} synthetic training records.")

# ── Build feature matrix ───────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from ml.symptom_predict import ALL_SYMPTOMS

X, y = [], []
for row in rows:
    features = []
    for s in ALL_SYMPTOMS:
        val = row.get(s, "0")
        features.append(1 if str(val).strip() in ("1", "1.0", "True", "true") else 0)
    X.append(features)
    y.append(row.get("prognosis", row.get("Disease", "Unknown")).strip())

X = np.array(X)
y = np.array(y)

print(f"Features: {X.shape}, Classes: {len(set(y))}")

# ── Encode labels ──────────────────────────────────────────────
encoder = LabelEncoder()
y_enc   = encoder.fit_transform(y)

# ── Train ──────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42)

print("Training Random Forest model...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=2,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

acc = accuracy_score(y_test, model.predict(X_test))
print(f"Accuracy: {acc*100:.2f}%")

# ── Save ───────────────────────────────────────────────────────
os.makedirs("models_saved", exist_ok=True)
with open("models_saved/symptom_model.pkl", "wb") as f:
    pickle.dump(model, f)
with open("models_saved/symptom_encoder.pkl", "wb") as f:
    pickle.dump(encoder, f)

print("Model saved to models_saved/symptom_model.pkl")
print("Encoder saved to models_saved/symptom_encoder.pkl")
print("\nDiseases the model can predict:")
for d in sorted(set(y)):
    print(f"  - {d}")
