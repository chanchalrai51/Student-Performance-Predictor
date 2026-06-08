# 🎓 Student Performance Predictor

A Machine Learning based web application that predicts a student's End-Semester Marks using academic and behavioral factors.

The system uses a Random Forest Regressor trained on student performance data and provides:

- Predicted End-Semester Marks
- Total Marks Calculation
- Grade Prediction
- Responsive Frontend UI

---

## 📌 Features

- Machine Learning powered prediction
- Flask REST API backend
- Random Forest Regression model
- Real-time predictions
- Grade calculation based on academic rules
- Responsive user interface

---

## 🛠️ Tech Stack

### Frontend
- HTML
- CSS
- JavaScript
- Chart.js

### Backend
- Flask
- Flask-CORS

### Machine Learning
- Scikit-Learn
- Pandas
- NumPy
- Random Forest Regressor

---

## 📂 Project Structure

```text
Student-Performance-Predictor/
│
├── backend/
│   ├── app.py
│   ├── train_model.py
│   ├── requirements.txt
│   ├── student_performance_dataset.csv
│   ├── model.pkl
│   └── scaler.pkl
│
├── frontend/
│   ├── html/
│   ├── css/
│   └── js/
│
└── README.md
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/chanchalrai51/Student-Performance-Predictor.git

cd Student-Performance-Predictor
```

### Create Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🤖 Train the Model

Run:

```bash
python train_model.py
```

This generates:

```text
model.pkl
scaler.pkl
```

---

## ▶️ Run Backend Server

```bash
python app.py
```

Backend runs at:

```text
http://localhost:5000
```

Available endpoints:

```text
GET  /
GET  /health
POST /predict
```

---

## 🌐 Run Frontend

Open:

```text
frontend/html/index.html
```

or use VS Code Live Server:

1. Open project in VS Code
2. Right-click `index.html`
3. Click **Open with Live Server**

---

## 🎯 Output

The application provides:

- Predicted End-Semester Marks
- Total Marks
- Final Grade

### Grade Scale

| Grade | Marks |
|---------|---------|
| O | 90-100 |
| E | 80-89 |
| A | 70-79 |
| B | 60-69 |
| C | 50-59 |
| D | 40-49 |
| F | Below 40 |

---

## API Example

### POST `/predict`

```json
{
  "attendance": 85,
  "study_hours": 5,
  "previous_cgpa": 8.2,
  "internal_marks": 24,
  "midsem_marks": 16,
  "backlogs": 0,
  "assignment_completion": 90,
  "class_participation": 4,
  "age": 20,
  "sex": "Male",
  "extra_curricular": "Yes",
  "late_night_entry": 2
}
```

---

## Future Improvements

- User Authentication
- Database Integration
- Cloud Deployment
- Enhanced Dataset Collection
- Multiple ML Model Comparison
- Performance Tracking Dashboard

---

## Author

**Chanchal Rai**

GitHub: https://github.com/chanchalrai51

---

## License

This project is licensed under the MIT License.
