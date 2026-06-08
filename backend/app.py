"""
Student Performance Prediction API
Flask backend for ML-based academic performance prediction
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os
import shap

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Global variables for model and scaler
model = None
scaler = None
explainer = None
all_models = {}
model_metrics = {}

# Load model and scaler on startup
def load_models():
    global model, scaler, explainer, all_models, model_metrics
    import json
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

        # Load all trained models
        model_files = ['randomforest_model.pkl', 'gradientboosting_model.pkl',
                      'linearregression_model.pkl', 'ridge_model.pkl', 'svr_model.pkl']
        for model_file in model_files:
            if os.path.exists(model_file):
                with open(model_file, 'rb') as f:
                    model_name = model_file.replace('_model.pkl', '')
                    all_models[model_name] = pickle.load(f)

        # Load model metrics
        if os.path.exists('model_metrics.json'):
            with open('model_metrics.json', 'r') as f:
                metrics_data = json.load(f)
                model_metrics = {k.lower().replace(' ', ''): v for k, v in metrics_data.items()}

        # Initialize SHAP explainer
        try:
            explainer = shap.TreeExplainer(model)
            print("✅ SHAP explainer initialized successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize SHAP explainer: {str(e)}")
            explainer = None

        print("✅ Model and scaler loaded successfully")
        if all_models:
            print(f"✅ Loaded {len(all_models)} additional models for comparison")
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
    Prediction endpoint with confidence scores
    """
    if not model or not scaler:
        return jsonify({
            "success": False,
            "error": "Model not loaded. Please run train_model.py first!"
        }), 500

    try:
        data = request.json

        if not data:
            return jsonify({
                "success": False,
                "error": "No data provided"
            }), 400

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

        sex_mapping = {'Male': 0, 'Female': 1, 'Other': 2}
        sex_numeric = sex_mapping.get(data['sex'], 0)

        extra_curricular_mapping = {'Yes': 1, 'No': 0}
        extra_curricular_numeric = extra_curricular_mapping.get(data['extra_curricular'], 0)

        features = [
            float(data['attendance']),
            float(data['study_hours']),
            float(data['previous_cgpa']),
            float(data['internal_marks']),
            float(data['midsem_marks']),
            int(data['backlogs']),
            float(data['assignment_completion']),
            int(data['class_participation']),
            int(data['age']),
            sex_numeric,
            extra_curricular_numeric,
            int(data['late_night_entry'])
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

        features_scaled = scaler.transform([features])

        # Main prediction
        predicted_endsem = model.predict(features_scaled)[0]
        predicted_endsem = max(0, min(50, predicted_endsem))

        # Calculate confidence score based on ensemble predictions
        confidence = calculate_confidence_score(features_scaled)

        # Calculate total marks
        total_marks = float(data['midsem_marks']) + float(data['internal_marks']) + predicted_endsem

        # Calculate grade
        grade = calculate_grade(total_marks)

        response = {
            "success": True,
            "predicted_endsem_marks": round(predicted_endsem, 2),
            "total_marks": round(total_marks, 2),
            "grade": grade,
            "confidence_score": confidence,
            "confidence_level": get_confidence_level(confidence),
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

def calculate_confidence_score(features_scaled):
    """
    Calculate prediction confidence based on ensemble agreement
    """
    if not all_models:
        return 0.85

    predictions = []
    try:
        predictions.append(float(model.predict(features_scaled)[0]))

        for trained_model in all_models.values():
            predictions.append(float(trained_model.predict(features_scaled)[0]))

        mean_pred = np.mean(predictions)
        std_pred = np.std(predictions)

        variance_score = 1.0 - (std_pred / (mean_pred + 1e-6))
        confidence = max(0.5, min(0.99, (variance_score + 0.85) / 2))

        return round(confidence, 3)
    except:
        return 0.85

def get_confidence_level(confidence_score):
    """
    Convert confidence score to readable level
    """
    if confidence_score >= 0.90:
        return "Very High"
    elif confidence_score >= 0.80:
        return "High"
    elif confidence_score >= 0.70:
        return "Medium"
    elif confidence_score >= 0.60:
        return "Low"
    else:
        return "Very Low"

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

@app.route('/explain', methods=['POST'])
def explain():
    """
    SHAP explanation endpoint - explains feature contributions to prediction
    """
    if not model or not scaler or not explainer:
        return jsonify({
            "success": False,
            "error": "Model or explainer not loaded"
        }), 500

    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

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
                "error": f"Missing fields: {', '.join(missing_fields)}"
            }), 400

        sex_mapping = {'Male': 0, 'Female': 1, 'Other': 2}
        sex_numeric = sex_mapping.get(data['sex'], 0)
        extra_curricular_mapping = {'Yes': 1, 'No': 0}
        extra_curricular_numeric = extra_curricular_mapping.get(data['extra_curricular'], 0)

        features = [
            float(data['attendance']),
            float(data['study_hours']),
            float(data['previous_cgpa']),
            float(data['internal_marks']),
            float(data['midsem_marks']),
            int(data['backlogs']),
            float(data['assignment_completion']),
            int(data['class_participation']),
            int(data['age']),
            sex_numeric,
            extra_curricular_numeric,
            int(data['late_night_entry'])
        ]

        features_scaled = scaler.transform([features])
        shap_values = explainer.shap_values(features_scaled)

        feature_names = [
            'Attendance', 'Study Hours', 'Previous CGPA', 'Internal Marks',
            'Midsem Marks', 'Backlogs', 'Assignment Completion',
            'Class Participation', 'Age', 'Gender', 'Extra-Curricular',
            'Late Night Entry'
        ]

        explanations = []
        for i, name in enumerate(feature_names):
            explanations.append({
                "feature": name,
                "value": features[i],
                "shap_value": float(shap_values[i]),
                "impact": "Positive" if shap_values[i] > 0 else "Negative"
            })

        explanations.sort(key=lambda x: abs(x['shap_value']), reverse=True)

        return jsonify({
            "success": True,
            "explanations": explanations,
            "base_value": float(explainer.expected_value)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Explanation error: {str(e)}"
        }), 500

@app.route('/compare-models', methods=['POST'])
def compare_models():
    """
    Compare predictions across multiple models
    """
    if not all_models or not scaler:
        return jsonify({
            "success": False,
            "error": "Models not loaded for comparison"
        }), 500

    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

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
                "error": f"Missing fields: {', '.join(missing_fields)}"
            }), 400

        sex_mapping = {'Male': 0, 'Female': 1, 'Other': 2}
        sex_numeric = sex_mapping.get(data['sex'], 0)
        extra_curricular_mapping = {'Yes': 1, 'No': 0}
        extra_curricular_numeric = extra_curricular_mapping.get(data['extra_curricular'], 0)

        features = [
            float(data['attendance']),
            float(data['study_hours']),
            float(data['previous_cgpa']),
            float(data['internal_marks']),
            float(data['midsem_marks']),
            int(data['backlogs']),
            float(data['assignment_completion']),
            int(data['class_participation']),
            int(data['age']),
            sex_numeric,
            extra_curricular_numeric,
            int(data['late_night_entry'])
        ]

        features_scaled = scaler.transform([features])

        comparisons = []
        model_names_map = {
            'randomforest': 'Random Forest',
            'gradientboosting': 'Gradient Boosting',
            'linearregression': 'Linear Regression',
            'ridge': 'Ridge Regression',
            'svr': 'Support Vector Regression'
        }

        for model_key, trained_model in all_models.items():
            prediction = float(trained_model.predict(features_scaled)[0])
            prediction = max(0, min(50, prediction))

            metrics_key = model_key
            model_metrics_data = model_metrics.get(metrics_key, {})

            comparisons.append({
                "model_name": model_names_map.get(model_key, model_key),
                "prediction": round(prediction, 2),
                "r2_score": model_metrics_data.get('r2_test', 0),
                "mae": model_metrics_data.get('mae', 0),
                "rmse": model_metrics_data.get('rmse', 0)
            })

        comparisons.sort(key=lambda x: x['r2_score'], reverse=True)

        return jsonify({
            "success": True,
            "comparisons": comparisons,
            "best_model": comparisons[0] if comparisons else None
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Comparison error: {str(e)}"
        }), 500

@app.route('/suggestions', methods=['POST'])
def get_suggestions():
    """
    Generate personalized improvement suggestions based on student data
    """
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        suggestions = []

        # Attendance suggestions
        if data.get('attendance', 0) < 75:
            suggestions.append({
                "category": "Attendance",
                "priority": "High",
                "suggestion": "Your attendance is below optimal. Aim for at least 75% to maintain consistent learning momentum.",
                "impact": "Could improve marks by 5-10%"
            })
        elif data.get('attendance', 0) < 85:
            suggestions.append({
                "category": "Attendance",
                "priority": "Medium",
                "suggestion": "Improve attendance above 85%. Regular class participation helps understand concepts better.",
                "impact": "Could improve marks by 2-5%"
            })

        # Study hours suggestions
        if data.get('study_hours', 0) < 3:
            suggestions.append({
                "category": "Study Hours",
                "priority": "High",
                "suggestion": "Increase daily study time to at least 3-4 hours for better concept clarity.",
                "impact": "Could improve marks by 8-15%"
            })
        elif data.get('study_hours', 0) < 5:
            suggestions.append({
                "category": "Study Hours",
                "priority": "Medium",
                "suggestion": "Consider increasing study time to 5+ hours daily for exam preparation.",
                "impact": "Could improve marks by 5-10%"
            })

        # Assignment completion
        if data.get('assignment_completion', 0) < 70:
            suggestions.append({
                "category": "Assignment Completion",
                "priority": "High",
                "suggestion": "Submit assignments regularly. This reinforces learning and builds consistency.",
                "impact": "Could improve marks by 3-8%"
            })

        # Class participation
        if data.get('class_participation', 1) <= 2:
            suggestions.append({
                "category": "Class Participation",
                "priority": "Medium",
                "suggestion": "Participate more actively in classes. Ask questions and engage with instructors.",
                "impact": "Could improve marks by 2-5%"
            })

        # Backlogs
        if data.get('backlogs', 0) > 0:
            suggestions.append({
                "category": "Backlogs",
                "priority": "High",
                "suggestion": "Focus on clearing your backlogs. These are crucial for overall academic progress.",
                "impact": "Could improve marks by 10-20%"
            })

        # Previous CGPA
        if data.get('previous_cgpa', 0) < 5.0:
            suggestions.append({
                "category": "Academic Strength",
                "priority": "High",
                "suggestion": "Strengthen fundamental concepts. Consider additional tutoring or study groups.",
                "impact": "Could improve marks by 15-25%"
            })

        # Behavioral suggestions
        if data.get('late_night_entry', 1) > 3:
            suggestions.append({
                "category": "Sleep Schedule",
                "priority": "High",
                "suggestion": "Maintain regular sleep schedule. Adequate rest improves focus and retention.",
                "impact": "Could improve marks by 5-10%"
            })

        if data.get('extra_curricular', 'No') == 'No':
            suggestions.append({
                "category": "Holistic Development",
                "priority": "Low",
                "suggestion": "Consider light extracurricular activities for stress relief and overall development.",
                "impact": "Indirect positive impact on studies"
            })

        # Sort by priority
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        suggestions.sort(key=lambda x: priority_order[x['priority']])

        # If no suggestions, provide positive feedback
        if not suggestions:
            suggestions.append({
                "category": "Overall Performance",
                "priority": "Low",
                "suggestion": "Great job! You're maintaining a good academic balance. Keep up the consistent effort!",
                "impact": "Maintain your current performance"
            })

        return jsonify({
            "success": True,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Suggestion generation error: {str(e)}"
        }), 500

@app.route('/model-metrics', methods=['GET'])
def get_model_metrics():
    """
    Get all model metrics for display
    """
    if not model_metrics:
        return jsonify({
            "success": False,
            "error": "Model metrics not available"
        }), 500

    model_names_map = {
        'RandomForest': 'Random Forest',
        'GradientBoosting': 'Gradient Boosting',
        'LinearRegression': 'Linear Regression',
        'Ridge': 'Ridge Regression',
        'SVR': 'Support Vector Regression'
    }

    metrics_list = []
    for model_name, metrics in model_metrics.items():
        display_name = model_names_map.get(model_name, model_name)
        metrics_list.append({
            "model_name": display_name,
            "r2_train": metrics.get('r2_train', 0),
            "r2_test": metrics.get('r2_test', 0),
            "mae": metrics.get('mae', 0),
            "rmse": metrics.get('rmse', 0)
        })

    metrics_list.sort(key=lambda x: x['r2_test'], reverse=True)

    return jsonify({
        "success": True,
        "metrics": metrics_list
    })

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