# 🏦 Loan Prediction System (ML + Flask + SQL)

## 📌 Overview

The **Loan Prediction System** is an end-to-end Machine Learning application that predicts whether a loan application will be approved or rejected based on user financial and demographic data.

This project demonstrates the complete ML lifecycle, including data preprocessing, model training, backend API development, database integration, and frontend interaction.

---

## 🚀 Key Features

* 🔍 Predict loan approval status (Approved / Rejected)
* 📊 Display probability scores for predictions
* ✅ Input validation and error handling
* 💾 Store prediction history in SQL database
* 🌐 RESTful API using Flask
* 💻 Interactive frontend using HTML, CSS, and JavaScript

---

## 🧠 Machine Learning Pipeline

* **Algorithm:** Random Forest Classifier
* **Data Preprocessing:**

  * Label Encoding for categorical features
  * Feature Scaling using StandardScaler
  * 
* **Model Evaluation:**

  * Accuracy Score
  * Confusion Matrix
  * Classification Report

---

## 🛠️ Tech Stack

| Layer    | Technologies Used           |
| -------- | --------------------------- |
| Frontend | HTML, CSS, JavaScript       |
| Backend  | Python, Flask               |
| ML Model | Scikit-learn, Pandas, NumPy |
| Database | SQL (MySQL / SQLite)        |

---

## 📂 Project Structure

```bash id="y9b7qq"
loan-prediction/
│
├── model/
│   ├── model.pkl
│   ├── scaler.pkl
│   ├── marital_le.pkl
│   └── education_le.pkl
│
├── templates/
│   └── index.html
│
├── static/
│   └── main.js
│
├── app.py
├── model.py
├── db.py
├── requirements.txt
└── README.md
```

---

## 🔄 System Workflow

1. User inputs financial details via frontend
2. Data is sent to Flask backend API
3. Backend validates and preprocesses input
4. Model predicts loan approval and probability
5. Result is returned to UI
6. Prediction is optionally stored in database

---

## ▶️ How to Run Locally

### 1. Clone the Repository

```bash id="d7drs1"
git clone https://github.com/your-username/loan-prediction.git
```

### 2. Navigate to Project Directory

```bash id="iy43g3"
cd loan-prediction
```

### 3. Install Dependencies

```bash id="jshkp9"
pip install -r requirements.txt
```

### 4. Run the Application

```bash id="s9k2ja"
python app.py
```

### 5. Open in Browser

```bash id="bws93t"
http://127.0.0.1:5000/
```

---

## 📊 Sample Prediction Output

```json id="yv5lzk"
{
  "label": "Approved",
  "prob_approved": 0.87,
  "prob_rejected": 0.13
}
```

---

## 📸 Screenshots

<img width="1876" height="906" alt="image" src="https://github.com/user-attachments/assets/75f02256-b775-4d17-9155-6b99a8c5c843" />


## 📈 Future Enhancements

* 🔐 User authentication system
* ☁️ Cloud deployment (Render / AWS)
* 📊 Dashboard with analytics and charts
* ⚙️ Hyperparameter tuning for better accuracy

---

## 🧩 Key Learnings

* Building end-to-end ML applications
* Integrating ML models with web frameworks
* Working with REST APIs and databases
* Handling real-world data validation

---

## 👤 Author

Sadiya Kazi

---

## ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on GitHub!
