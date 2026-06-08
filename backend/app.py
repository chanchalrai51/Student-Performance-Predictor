"""
Student Performance Prediction API
Flask backend for ML-based academic performance prediction
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Global variables for model and scaler
model = None
scaler = None

# Load model and scaler on startup
def load_models():
    global model, scaler
    try:
        model_path = 'model.pkl'
        scaler_path = 'scaler.pkl'
        
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            print("⚠️  Model files not found!")
            print("Please run 'python train_model.py' first to generate model.pkl and scaler.pkl")
            return False
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        print("✅ Model and scaler loaded successfully")
        return True
    
    except Exception as e:
        print(f"❌ Error loading models: {str(e)}")
        return False

# API Routes

@app.route('/')
def home():
    """
    Home endpoint - API information
    """
    return jsonify({
        "message": "Student Performance Prediction API",
        "version": "1.0",
        "status": "running" if model and scaler else "model not loaded",
        "endpoints": {
            "/": "API information (this page)",
            "/predict": "POST - Make prediction",
            "/health": "GET - Health check"
        },
        "specifications": {
            "input_features": 12,
            "ml_output": "End-Semester Marks (0-50)",
            "total_calculation": "Mid-Sem (30) + Internal (20) + End-Sem (50) = 100",
            "grade_scale": {
                "O": "90-100",
                "E": "80-89",
                "A": "70-79",
                "B": "60-69",
                "C": "50-59",
                "D": "40-49",
                "F": "<40"
            }
        },
        "note": "Grade is calculated using fixed academic rules, NOT predicted by ML"
    })

@app.route('/health')
def health():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Prediction endpoint
    Accepts student data and returns predicted end-semester marks, total marks, and grade
    """
    if not model or not scaler:
        return jsonify({
            "success": False,
            "error": "Model not loaded. Please run train_model.py first!"
        }), 500
    
    try:
        # Get JSON data from request
        data = request.json
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400
        
        # Validate required fields
        required_fields = [
            'attendance', 'study_hours', 'previous_cgpa', 'internal_marks',
            'midsem_marks', 'backlogs', 'assignment_completion', 
            'class_participation', 'age', 'sex', 'extra_curricular', 
            'late_night_entry'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "success": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400
        
        # Convert categorical variables to numeric
        sex_mapping = {'Male': 0, 'Female': 1, 'Other': 2}
        sex_numeric = sex_mapping.get(data['sex'], 0)
        
        extra_curricular_mapping = {'Yes': 1, 'No': 0}
        extra_curricular_numeric = extra_curricular_mapping.get(data['extra_curricular'], 0)
        
        # Extract and prepare features in correct order
        # Order must match the training data column order
        features = [
            float(data['attendance']),                    # Attendance (0-100)
            float(data['study_hours']),                   # Study Hours (0-12)
            float(data['previous_cgpa']),                 # Previous CGPA (0-10)
            float(data['internal_marks']),                # Internal Marks (0-20)
            float(data['midsem_marks']),                  # Midsem Marks (0-30)
            int(data['backlogs']),                        # Backlogs (0-5+)
            float(data['assignment_completion']),         # Assignment Completion (0-100)
            int(data['class_participation']),             # Class Participation (1-5)
            int(data['age']),                             # Age (17-30)
            sex_numeric,                                  # Sex (0/1/2)
            extra_curricular_numeric,                     # Extra-Curricular (0/1)
            int(data['late_night_entry'])                 # Late Night Entry (1-5)
        ]
        
        # Validate feature ranges
        if not (0 <= features[0] <= 100):
            return jsonify({"success": False, "error": "Attendance must be between 0-100"}), 400
        if not (0 <= features[1] <= 12):
            return jsonify({"success": False, "error": "Study hours must be between 0-12"}), 400
        if not (0 <= features[2] <= 10):
            return jsonify({"success": False, "error": "Previous CGPA must be between 0-10"}), 400
        if not (0 <= features[3] <= 30):
            return jsonify({"success": False, "error": "Internal marks must be between 0-30"}), 400
        if not (0 <= features[4] <= 20):
            return jsonify({"success": False, "error": "Midsem marks must be between 0-20"}), 400
        
        # Scale features
        features_scaled = scaler.transform([features])
        
        # Make prediction
        predicted_endsem = model.predict(features_scaled)[0]
        
        # Clip to valid range (0-50)
        predicted_endsem = max(0, min(50, predicted_endsem))
        
        # Calculate total marks
        # Total = Mid-Sem (20) + Internal (30) + End-Sem (50) = 100
        total_marks = float(data['midsem_marks']) + float(data['internal_marks']) + predicted_endsem
        
        # Calculate grade based on total marks (Fixed academic rules)
        grade = calculate_grade(total_marks)
        
        # Prepare response
        response = {
            "success": True,
            "predicted_endsem_marks": round(predicted_endsem, 2),
            "total_marks": round(total_marks, 2),
            "grade": grade,
            "breakdown": {
                "midsem_marks": float(data['midsem_marks']),
                "internal_marks": float(data['internal_marks']),
                "endsem_marks": round(predicted_endsem, 2)
            },
            "grade_info": get_grade_info(grade),
            "note": "Grade is calculated using fixed academic rules, NOT predicted by ML"
        }
        
        return jsonify(response)
    
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Invalid data format: {str(e)}"
        }), 400
    
    except KeyError as e:
        return jsonify({
            "success": False,
            "error": f"Missing required field: {str(e)}"
        }), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Prediction error: {str(e)}"
        }), 500

def calculate_grade(total_marks):
    """
    Calculate grade based on total marks using fixed academic rules
    """
    if total_marks >= 90:
        return 'O'
    elif total_marks >= 80:
        return 'E'
    elif total_marks >= 70:
        return 'A'
    elif total_marks >= 60:
        return 'B'
    elif total_marks >= 50:
        return 'C'
    elif total_marks >= 40:
        return 'D'
    else:
        return 'F'

def get_grade_info(grade):
    """
    Get additional information about the grade
    """
    grade_info = {
        'O': {'description': 'Outstanding', 'range': '90-100'},
        'E': {'description': 'Excellent', 'range': '80-89'},
        'A': {'description': 'Very Good', 'range': '70-79'},
        'B': {'description': 'Good', 'range': '60-69'},
        'C': {'description': 'Average', 'range': '50-59'},
        'D': {'description': 'Below Average', 'range': '40-49'},
        'F': {'description': 'Fail', 'range': '<40'}
    }
    return grade_info.get(grade, {'description': 'Unknown', 'range': 'N/A'})

# Error handlers

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

# Main execution
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎓 STUDENT PERFORMANCE PREDICTION API")
    print("="*70)
    
    # Load models
    if load_models():
        print("\n✅ Backend ready!")
        print("📡 Server starting on http://localhost:5000")
        print("📝 API Documentation: http://localhost:5000")
        print("\n💡 Next steps:")
        print("   1. Open index.html in your browser")
        print("   2. Navigate to the prediction page")
        print("   3. Enter student details and get predictions!")
        print("\n" + "="*70 + "\n")
        
        # Run Flask app
        app.run(debug=True, port=5000, host='0.0.0.0')
    else:
        print("\n❌ Failed to load models!")
        print("Please run: python train_model.py")
        print("\n" + "="*70 + "\n")