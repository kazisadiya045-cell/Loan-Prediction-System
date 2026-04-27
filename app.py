import os, sys, pickle, logging
import numpy as np
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# --- Load ML artifacts ---
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")

def _load(fname):
    path = os.path.join(MODEL_DIR, fname)
    if not os.path.exists(path):
        log.error(f"Missing: {path}. Run: python model/train_model.py")
        sys.exit(1)
    return pickle.load(open(path, "rb"))

model        = _load("model.pkl")
scaler       = _load("scaler.pkl")
marital_le   = _load("marital_le.pkl")
education_le = _load("education_le.pkl")
log.info("✅ Model loaded.")

# --- DB (optional) ---
try:
    from database.db import save_prediction, fetch_recent
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    log.warning("⚠️  No DB module found.")

VALID_MARITAL   = list(marital_le.classes_)
VALID_EDUCATION = list(education_le.classes_)

def validate(data):
    required = ["age","income","loan_amount","credit_score","employment_years","existing_loans","marital_status","education"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError(f"Missing: {missing}")

    age   = int(data["age"]);   income = float(data["income"])
    loan  = float(data["loan_amount"]); cs = int(data["credit_score"])
    emp   = int(data["employment_years"]); el = int(data["existing_loans"])
    ms    = data["marital_status"]; edu = data["education"]

    if not 18 <= age <= 100:    raise ValueError("Age must be 18–100.")
    if income <= 0:             raise ValueError("Income must be positive.")
    if loan <= 0:               raise ValueError("Loan amount must be positive.")
    if not 300 <= cs <= 850:    raise ValueError("Credit score must be 300–850.")
    if ms  not in VALID_MARITAL:   raise ValueError(f"marital_status must be one of {VALID_MARITAL}")
    if edu not in VALID_EDUCATION: raise ValueError(f"education must be one of {VALID_EDUCATION}")

    ms_enc  = int(marital_le.transform([ms])[0])
    edu_enc = int(education_le.transform([edu])[0])

    features = np.array([[age, income, loan, cs, emp, el, ms_enc, edu_enc]], dtype=float)
    clean    = dict(age=age, income=income, loan_amount=loan, credit_score=cs,
                    employment_years=emp, existing_loans=el, marital_status=ms, education=edu)
    return features, clean

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        features, clean = validate(data)
        fs   = scaler.transform(features)
        pred = int(model.predict(fs)[0])
        prob = model.predict_proba(fs)[0]
        return jsonify({
            "success": True,
            "prediction":    pred,
            "label":         "Approved" if pred == 1 else "Rejected",
            "prob_approved": round(float(prob[1]), 4),
            "prob_rejected": round(float(prob[0]), 4),
            "message": "🎉 Congratulations! Your loan has been approved!" if pred == 1
                       else "😔 We're sorry. Your loan was not approved.",
        }), 200
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception:
        log.exception("Error in /predict")
        return jsonify({"success": False, "error": "Internal server error."}), 500

@app.route("/save", methods=["POST"])
def save():
    if not DB_AVAILABLE:
        return jsonify({"success": False, "error": "Database not configured."}), 503
    try:
        data = request.get_json(force=True)
        features, clean = validate(data)
        pred = data.get("prediction")
        pa   = data.get("prob_approved")
        pr   = data.get("prob_rejected")
        if pred is None:
            fs   = scaler.transform(features)
            pred = int(model.predict(fs)[0])
            prob = model.predict_proba(fs)[0]
            pa, pr = round(float(prob[1]),4), round(float(prob[0]),4)
        row_id = save_prediction({**clean,
            "prediction": int(pred), "prediction_label": "Approved" if pred==1 else "Rejected",
            "prob_approved": float(pa), "prob_rejected": float(pr)})
        return (jsonify({"success": True,  "id": row_id}), 201) if row_id \
          else (jsonify({"success": False, "error": "DB insert failed."}), 500)
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception:
        log.exception("Error in /save")
        return jsonify({"success": False, "error": "Internal server error."}), 500

@app.route("/history")
def history():
    if not DB_AVAILABLE:
        return jsonify({"success": False, "data": []}), 200
    limit   = min(int(request.args.get("limit", 10)), 50)
    records = fetch_recent(limit)
    for r in records:
        for k,v in r.items():
            if hasattr(v,"isoformat"): r[k] = v.isoformat()
            elif hasattr(v,"__float__"): r[k] = float(v)
    return jsonify({"success": True, "data": records})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "db": DB_AVAILABLE})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)




@app.route("/predict", methods=["POST"])
def predict():
    try:
        age = float(request.form["age"])
        income = float(request.form["income"])
        loan_amount = float(request.form["loan_amount"])
        credit_score = float(request.form["credit_score"])
        employment_years = float(request.form["employment_years"])
        existing_loans = int(request.form["existing_loans"])
        marital_status = request.form["marital_status"]
        education = request.form["education"]

        # 🔥 Encoding
        marital_map = {"Single": 0, "Married": 1, "Divorced": 2}
        education_map = {"High School": 0, "Bachelor": 1, "Master": 2, "PhD": 3}

        marital_encoded = marital_map[marital_status]
        education_encoded = education_map[education]

        # 🔥 Feature array (correct order)
        features = np.array([[
            age, income, loan_amount, credit_score,
            employment_years, existing_loans,
            marital_encoded, education_encoded
        ]])

        prediction = model.predict(features)[0]

        prob = model.predict_proba(features)[0]
        prob_approved = float(prob[1])
        prob_rejected = float(prob[0])

        label = "Approved" if prediction == 1 else "Rejected"

        # 🔥 Save to DB (original values store karo)
        data = {
            "age": age,
            "income": income,
            "loan_amount": loan_amount,
            "credit_score": credit_score,
            "employment_years": employment_years,
            "existing_loans": existing_loans,
            "marital_status": marital_status,
            "education": education,
            "prediction": int(prediction),
            "prediction_label": label,
            "prob_approved": prob_approved,
            "prob_rejected": prob_rejected
        }

        save_prediction(data)

        return render_template("index.html", prediction_text=f"🎉 {label}")

    except Exception as e:
        return render_template("index.html", prediction_text=f"Error: {e}")