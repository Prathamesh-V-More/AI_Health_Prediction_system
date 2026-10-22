"""
Symptom-based disease prediction.
Uses a trained Random Forest / Decision Tree model on symptom data.
Falls back to rule-based prediction if model not available.
No numpy/tensorflow required for basic operation.
"""
import os
import json

MODEL_PATH   = os.path.join(os.path.dirname(__file__), "../models_saved/symptom_model.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "../models_saved/symptom_encoder.pkl")

# ── All 132 symptoms used in training ─────────────────────────
ALL_SYMPTOMS = [
    "itching","skin_rash","nodal_skin_eruptions","continuous_sneezing","shivering",
    "chills","joint_pain","stomach_pain","acidity","ulcers_on_tongue","muscle_wasting",
    "vomiting","burning_micturition","spotting_urination","fatigue","weight_gain",
    "anxiety","cold_hands_and_feets","mood_swings","weight_loss","restlessness",
    "lethargy","patches_in_throat","irregular_sugar_level","cough","high_fever",
    "sunken_eyes","breathlessness","sweating","dehydration","indigestion","headache",
    "yellowish_skin","dark_urine","nausea","loss_of_appetite","pain_behind_the_eyes",
    "back_pain","constipation","abdominal_pain","diarrhoea","mild_fever","yellow_urine",
    "yellowing_of_eyes","acute_liver_failure","fluid_overload","swelling_of_stomach",
    "swelled_lymph_nodes","malaise","blurred_and_distorted_vision","phlegm",
    "throat_irritation","redness_of_eyes","sinus_pressure","runny_nose","congestion",
    "chest_pain","weakness_in_limbs","fast_heart_rate","pain_during_bowel_movements",
    "pain_in_anal_region","bloody_stool","irritation_in_anus","neck_pain","dizziness",
    "cramps","bruising","obesity","swollen_legs","swollen_blood_vessels",
    "puffy_face_and_eyes","enlarged_thyroid","brittle_nails","swollen_extremeties",
    "excessive_hunger","extra_marital_contacts","drying_and_tingling_lips",
    "slurred_speech","knee_pain","hip_joint_pain","muscle_weakness","stiff_neck",
    "swelling_joints","movement_stiffness","spinning_movements","loss_of_balance",
    "unsteadiness","weakness_of_one_body_side","loss_of_smell","bladder_discomfort",
    "foul_smell_of_urine","continuous_feel_of_urine","passage_of_gases",
    "internal_itching","toxic_look_(typhos)","depression","irritability",
    "muscle_pain","altered_sensorium","red_spots_over_body","belly_pain",
    "abnormal_menstruation","dischromic_patches","watering_from_eyes",
    "increased_appetite","polyuria","family_history","mucoid_sputum",
    "rusty_sputum","lack_of_concentration","visual_disturbances",
    "receiving_blood_transfusion","receiving_unsterile_injections","coma",
    "stomach_bleeding","distention_of_abdomen","history_of_alcohol_consumption",
    "fluid_overload.1","blood_in_sputum","prominent_veins_on_calf","palpitations",
    "painful_walking","pus_filled_pimples","blackheads","scurring","skin_peeling",
    "silver_like_dusting","small_dents_in_nails","inflammatory_nails","blister",
    "red_sore_around_nose","yellow_crust_ooze"
]

# ── Disease info ───────────────────────────────────────────────
DISEASE_INFO = {
    "Fungal infection":        {"severity":"Mild",     "rec":"Use antifungal cream. Keep area dry. Consult a dermatologist."},
    "Allergy":                 {"severity":"Mild",     "rec":"Avoid allergens. Take antihistamines. See a doctor if severe."},
    "GERD":                    {"severity":"Moderate", "rec":"Avoid spicy food. Take antacids. Consult a gastroenterologist."},
    "Chronic cholestasis":     {"severity":"Severe",   "rec":"Urgent liver function tests needed. See a hepatologist."},
    "Drug Reaction":           {"severity":"Moderate", "rec":"Stop the suspected drug immediately. Consult your doctor."},
    "Peptic ulcer disease":    {"severity":"Moderate", "rec":"Avoid NSAIDs and alcohol. Take prescribed antacids."},
    "AIDS":                    {"severity":"Critical",  "rec":"Immediate medical care required. Start antiretroviral therapy."},
    "Diabetes":                {"severity":"Severe",   "rec":"Monitor blood sugar. Follow diabetic diet. Consult endocrinologist."},
    "Gastroenteritis":         {"severity":"Moderate", "rec":"Stay hydrated. Rest. See a doctor if symptoms persist."},
    "Bronchial Asthma":        {"severity":"Severe",   "rec":"Use prescribed inhaler. Avoid triggers. See a pulmonologist."},
    "Hypertension":            {"severity":"Severe",   "rec":"Reduce salt intake. Exercise regularly. Take prescribed medication."},
    "Migraine":                {"severity":"Moderate", "rec":"Rest in dark room. Take pain relievers. Consult a neurologist."},
    "Cervical spondylosis":    {"severity":"Moderate", "rec":"Physiotherapy recommended. Avoid heavy lifting. See an orthopedist."},
    "Paralysis (brain hemorrhage)": {"severity":"Critical","rec":"EMERGENCY: Call ambulance immediately."},
    "Jaundice":                {"severity":"Severe",   "rec":"Urgent liver tests needed. Avoid alcohol. See a hepatologist."},
    "Malaria":                 {"severity":"Severe",   "rec":"Antimalarial medication required. See a doctor immediately."},
    "Chicken pox":             {"severity":"Moderate", "rec":"Rest, stay hydrated. Avoid scratching. Consult a doctor."},
    "Dengue":                  {"severity":"Severe",   "rec":"Urgent medical care. Monitor platelet count. Stay hydrated."},
    "Typhoid":                 {"severity":"Severe",   "rec":"Antibiotics required. Rest and hydration. See a doctor."},
    "hepatitis A":             {"severity":"Moderate", "rec":"Rest, avoid alcohol. Supportive care. Consult a doctor."},
    "Hepatitis B":             {"severity":"Severe",   "rec":"Antiviral treatment may be needed. See a hepatologist."},
    "Hepatitis C":             {"severity":"Severe",   "rec":"Antiviral treatment available. See a hepatologist urgently."},
    "Hepatitis D":             {"severity":"Severe",   "rec":"Requires Hepatitis B treatment. See a hepatologist."},
    "Hepatitis E":             {"severity":"Moderate", "rec":"Rest and hydration. Avoid alcohol. Consult a doctor."},
    "Alcoholic hepatitis":     {"severity":"Severe",   "rec":"Stop alcohol immediately. Urgent liver care needed."},
    "Tuberculosis":            {"severity":"Severe",   "rec":"Long-term antibiotics required. See a pulmonologist."},
    "Common Cold":             {"severity":"Mild",     "rec":"Rest, stay hydrated. Take OTC cold medicine if needed."},
    "Pneumonia":               {"severity":"Severe",   "rec":"Antibiotics required. Rest. See a doctor immediately."},
    "Dimorphic hemmorhoids(piles)": {"severity":"Moderate","rec":"High fiber diet. Sitz baths. Consult a proctologist."},
    "Heart attack":            {"severity":"Critical",  "rec":"EMERGENCY: Call ambulance immediately. Chew aspirin if available."},
    "Varicose veins":          {"severity":"Mild",     "rec":"Elevate legs. Compression stockings. See a vascular surgeon."},
    "Hypothyroidism":          {"severity":"Moderate", "rec":"Thyroid hormone replacement therapy. See an endocrinologist."},
    "Hyperthyroidism":         {"severity":"Moderate", "rec":"Antithyroid medication. See an endocrinologist."},
    "Hypoglycemia":            {"severity":"Severe",   "rec":"Eat sugar immediately. Monitor blood glucose. See a doctor."},
    "Osteoarthritis":          {"severity":"Moderate", "rec":"Physiotherapy. Pain management. See an orthopedist."},
    "Arthritis":               {"severity":"Moderate", "rec":"Anti-inflammatory medication. Physiotherapy. See a rheumatologist."},
    "(vertigo) Paroxysmal Positional Vertigo": {"severity":"Moderate","rec":"Epley maneuver. See an ENT specialist."},
    "Acne":                    {"severity":"Mild",     "rec":"Gentle cleansers. Topical treatments. See a dermatologist."},
    "Urinary tract infection": {"severity":"Moderate", "rec":"Antibiotics required. Drink plenty of water. See a doctor."},
    "Psoriasis":               {"severity":"Moderate", "rec":"Topical treatments. See a dermatologist."},
    "Impetigo":                {"severity":"Mild",     "rec":"Antibiotic cream. Keep area clean. See a doctor."},
}

# ── Rule-based fallback ────────────────────────────────────────
SYMPTOM_DISEASE_RULES = {
    frozenset(["itching","skin_rash","nodal_skin_eruptions"]):          "Fungal infection",
    frozenset(["continuous_sneezing","shivering","chills","watering_from_eyes"]): "Allergy",
    frozenset(["acidity","ulcers_on_tongue","vomiting","indigestion"]): "GERD",
    frozenset(["fatigue","weight_loss","high_fever","sweating","chills"]): "Tuberculosis",
    frozenset(["high_fever","headache","nausea","vomiting","muscle_pain"]): "Dengue",
    frozenset(["high_fever","chills","sweating","headache","nausea"]):   "Malaria",
    frozenset(["cough","high_fever","breathlessness","chest_pain"]):     "Pneumonia",
    frozenset(["fatigue","weight_gain","cold_hands_and_feets","mood_swings"]): "Hypothyroidism",
    frozenset(["chest_pain","fast_heart_rate","sweating","breathlessness"]): "Heart attack",
    frozenset(["yellowish_skin","dark_urine","nausea","loss_of_appetite"]): "Jaundice",
    frozenset(["headache","nausea","vomiting","blurred_and_distorted_vision"]): "Migraine",
    frozenset(["polyuria","fatigue","weight_loss","excessive_hunger"]):  "Diabetes",
    frozenset(["skin_rash","joint_pain","fatigue","high_fever"]):        "Chicken pox",
    frozenset(["continuous_sneezing","cough","fatigue","mild_fever"]):   "Common Cold",
    frozenset(["burning_micturition","bladder_discomfort","foul_smell_of_urine"]): "Urinary tract infection",
    frozenset(["skin_rash","patches_in_throat","joint_pain","fatigue"]): "Psoriasis",
    frozenset(["pus_filled_pimples","blackheads","skin_rash"]):          "Acne",
    frozenset(["back_pain","neck_pain","dizziness","weakness_in_limbs"]): "Cervical spondylosis",
    frozenset(["joint_pain","swelling_joints","movement_stiffness"]):    "Arthritis",
    frozenset(["dizziness","spinning_movements","loss_of_balance","unsteadiness"]): "(vertigo) Paroxysmal Positional Vertigo",
}

_model   = None
_encoder = None
_loaded  = False


def _load_model():
    global _model, _encoder, _loaded
    if _loaded:
        return
    _loaded = True
    try:
        import pickle
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                _model = pickle.load(f)
        if os.path.exists(ENCODER_PATH):
            with open(ENCODER_PATH, "rb") as f:
                _encoder = pickle.load(f)
    except Exception as e:
        print(f"[ML] Symptom model load warning: {e}")


def _rule_based_predict(symptoms_list):
    """Match symptoms against rules, return best matching disease."""
    symptom_set = set(symptoms_list)
    best_match  = None
    best_score  = 0

    for rule_symptoms, disease in SYMPTOM_DISEASE_RULES.items():
        score = len(rule_symptoms & symptom_set)
        if score > best_score:
            best_score = score
            best_match = disease

    if best_match and best_score >= 2:
        confidence = min(60 + best_score * 5, 88)
        return best_match, confidence

    # Generic fallback based on dominant symptom
    if "chest_pain" in symptom_set or "fast_heart_rate" in symptom_set:
        return "Heart attack", 72
    if "high_fever" in symptom_set and "cough" in symptom_set:
        return "Pneumonia", 70
    if "fatigue" in symptom_set and "weight_loss" in symptom_set:
        return "Tuberculosis", 68
    if "yellowish_skin" in symptom_set or "dark_urine" in symptom_set:
        return "Jaundice", 71
    if "skin_rash" in symptom_set or "itching" in symptom_set:
        return "Fungal infection", 65
    if "headache" in symptom_set and "nausea" in symptom_set:
        return "Migraine", 66
    if "joint_pain" in symptom_set:
        return "Arthritis", 64
    if "cough" in symptom_set:
        return "Common Cold", 62

    return "Common Cold", 55


def predict_from_symptoms(symptoms_list):
    """
    Main prediction function.
    symptoms_list: list of symptom strings from ALL_SYMPTOMS
    Returns dict with disease, confidence, severity, recommendation.
    """
    if not symptoms_list:
        return {
            "valid": False,
            "error": "Please select at least 2 symptoms."
        }

    if len(symptoms_list) < 2:
        return {
            "valid": False,
            "error": "Please select at least 2 symptoms for accurate prediction."
        }

    _load_model()

    if _model is not None:
        try:
            import numpy as np
            # Build feature vector
            feature_vec = [1 if s in symptoms_list else 0 for s in ALL_SYMPTOMS]
            X = np.array(feature_vec).reshape(1, -1)
            pred = _model.predict(X)[0]
            proba = _model.predict_proba(X)[0]
            confidence = round(float(max(proba)) * 100, 2)
            if _encoder is not None:
                disease = _encoder.inverse_transform([pred])[0]
            else:
                disease = str(pred)
        except Exception as e:
            print(f"[ML] Prediction error: {e}")
            disease, confidence = _rule_based_predict(symptoms_list)
    else:
        disease, confidence = _rule_based_predict(symptoms_list)

    info = DISEASE_INFO.get(disease, {
        "severity": "Unknown",
        "rec": "Please consult a doctor for proper diagnosis."
    })

    return {
        "valid":          True,
        "disease":        disease,
        "confidence":     confidence,
        "severity":       info["severity"],
        "recommendation": info["rec"],
        "symptoms_used":  symptoms_list,
    }


def get_symptom_categories():
    """Return symptoms grouped by category for the UI form."""
    return {
        "General": [
            "fatigue","weight_loss","weight_gain","fever","high_fever","mild_fever",
            "chills","sweating","dehydration","malaise","lethargy","restlessness",
            "anxiety","mood_swings","depression","irritability"
        ],
        "Head & Neurological": [
            "headache","dizziness","loss_of_balance","unsteadiness","spinning_movements",
            "blurred_and_distorted_vision","visual_disturbances","loss_of_smell",
            "slurred_speech","altered_sensorium","coma","weakness_of_one_body_side",
            "lack_of_concentration","pain_behind_the_eyes"
        ],
        "Respiratory": [
            "cough","breathlessness","chest_pain","phlegm","blood_in_sputum",
            "rusty_sputum","mucoid_sputum","throat_irritation","congestion",
            "runny_nose","sinus_pressure","continuous_sneezing"
        ],
        "Digestive": [
            "nausea","vomiting","indigestion","acidity","stomach_pain","abdominal_pain",
            "belly_pain","diarrhoea","constipation","loss_of_appetite","passage_of_gases",
            "swelling_of_stomach","distention_of_abdomen","stomach_bleeding",
            "ulcers_on_tongue","pain_during_bowel_movements","bloody_stool"
        ],
        "Skin": [
            "itching","skin_rash","nodal_skin_eruptions","yellowish_skin","patches_in_throat",
            "dischromic_patches","red_spots_over_body","pus_filled_pimples","blackheads",
            "skin_peeling","silver_like_dusting","blister","red_sore_around_nose",
            "yellow_crust_ooze","bruising","inflammatory_nails","brittle_nails"
        ],
        "Musculoskeletal": [
            "joint_pain","muscle_pain","muscle_weakness","muscle_wasting","back_pain",
            "neck_pain","knee_pain","hip_joint_pain","swelling_joints","stiff_neck",
            "movement_stiffness","cramps","weakness_in_limbs","painful_walking"
        ],
        "Urinary": [
            "burning_micturition","spotting_urination","bladder_discomfort",
            "foul_smell_of_urine","continuous_feel_of_urine","yellow_urine","dark_urine",
            "polyuria"
        ],
        "Eyes & ENT": [
            "redness_of_eyes","watering_from_eyes","yellowing_of_eyes",
            "puffy_face_and_eyes","sunken_eyes"
        ],
        "Cardiovascular": [
            "fast_heart_rate","palpitations","chest_pain","swollen_blood_vessels",
            "prominent_veins_on_calf","swollen_legs","swollen_extremeties"
        ],
        "Other": [
            "excessive_hunger","irregular_sugar_level","increased_appetite",
            "enlarged_thyroid","obesity","family_history","cold_hands_and_feets",
            "swelled_lymph_nodes","abnormal_menstruation","extra_marital_contacts"
        ],
    }
