// ==========================================
// PREDICT & RESULT PAGE JAVASCRIPT
// ==========================================

// API Configuration
const API_URL = 'http://localhost:5000/predict';

// Mobile menu toggle
function toggleMobileMenu() {
    const navLinks = document.getElementById('navLinks');
    navLinks.classList.toggle('active');
}

// Validation ranges
const VALIDATION_RULES = {
    attendance: { min: 0, max: 100, name: 'Attendance' },
    study_hours: { min: 0, max: 12, name: 'Study Hours' },
    previous_cgpa: { min: 0, max: 10, name: 'Previous CGPA' },
    internal_marks: { min: 0, max: 30, name: 'Internal Marks' },
    midsem_marks: { min: 0, max: 20, name: 'Mid-Semester Marks' },
    backlogs: { min: 0, max: 5, name: 'Backlogs' },
    assignment_completion: { min: 0, max: 100, name: 'Assignment Completion' },
    class_participation: { min: 1, max: 5, name: 'Class Participation' },
    age: { min: 17, max: 30, name: 'Age' },
    late_night_entry: { min: 1, max: 5, name: 'Late Night Entry' }
};

// Show popup message
function showPopup(message) {
    // Create popup if it doesn't exist
    let popup = document.getElementById('validationPopup');
    if (!popup) {
        popup = document.createElement('div');
        popup.id = 'validationPopup';
        popup.className = 'popup-overlay';
        popup.innerHTML = `
            <div class="popup-content">
                <h3>⚠️ Validation Error</h3>
                <p id="popupMessage"></p>
                <button class="popup-btn" onclick="closePopup()">OK</button>
            </div>
        `;
        document.body.appendChild(popup);
    }
    
    document.getElementById('popupMessage').textContent = message;
    popup.classList.add('show');
}

function closePopup() {
    const popup = document.getElementById('validationPopup');
    if (popup) {
        popup.classList.remove('show');
    }
}

// Validate input values
function validateInputs(formData) {
    for (let [fieldName, rules] of Object.entries(VALIDATION_RULES)) {
        const value = formData.get(fieldName);
        
        if (!value && value !== 0 && value !== '0') {
            showPopup(`Please fill in ${rules.name}`);
            return false;
        }
        
        const numValue = parseFloat(value);
        
        if (isNaN(numValue)) {
            showPopup(`${rules.name} must be a valid number`);
            return false;
        }
        
        if (numValue < rules.min || numValue > rules.max) {
            showPopup(`${rules.name} must be between ${rules.min} and ${rules.max}`);
            return false;
        }
    }
    
    // Validate dropdown fields
    const sex = formData.get('sex');
    const extraCurricular = formData.get('extra_curricular');
    
    if (!sex || sex === '') {
        showPopup('Please select Gender');
        return false;
    }
    
    if (!extraCurricular || extraCurricular === '') {
        showPopup('Please select Extra-Curricular Activities');
        return false;
    }
    
    return true;
}

// Section navigation functions
function nextSection(sectionNum) {
    // Get current section
    const currentSection = document.querySelector('.form-section.active');
    const form = document.getElementById('predictionForm');
    const formData = new FormData(form);
    
    // Validate current section inputs
    const inputs = currentSection.querySelectorAll('input[required], select[required]');
    let isValid = true;
    
    for (let input of inputs) {
        const value = input.value;
        const fieldName = input.name;
        
        // Check if field is empty
        if (!value && value !== 0 && value !== '0') {
            showPopup(`Please fill in all required fields before proceeding`);
            input.focus();
            return;
        }
        
        // Validate range for number inputs
        if (input.type === 'number' && VALIDATION_RULES[fieldName]) {
            const numValue = parseFloat(value);
            const rules = VALIDATION_RULES[fieldName];
            
            if (numValue < rules.min || numValue > rules.max) {
                showPopup(`${rules.name} must be between ${rules.min} and ${rules.max}`);
                input.focus();
                return;
            }
        }
    }
    
    // Update sections
    document.querySelectorAll('.form-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`section${sectionNum}`).classList.add('active');
    
    // Update progress steps
    document.querySelectorAll('.step').forEach((step, index) => {
        if (index < sectionNum) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
    
    // If moving to review section, populate review data
    if (sectionNum === 3) {
        populateReviewData();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function prevSection(sectionNum) {
    // Update sections
    document.querySelectorAll('.form-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`section${sectionNum}`).classList.add('active');
    
    // Update progress steps
    document.querySelectorAll('.step').forEach((step, index) => {
        if (index < sectionNum) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Populate review data
function populateReviewData() {
    const form = document.getElementById('predictionForm');
    const formData = new FormData(form);
    
    const academicFields = {
        'attendance': 'Attendance (%)',
        'study_hours': 'Study Hours/Day',
        'previous_cgpa': 'Previous CGPA',
        'internal_marks': 'Internal Marks (/30)',
        'midsem_marks': 'Mid-Semester Marks (/20)',
        'backlogs': 'Backlogs',
        'assignment_completion': 'Assignment Completion (%)',
        'class_participation': 'Class Participation (1-5)'
    };
    
    const personalFields = {
        'age': 'Age',
        'sex': 'Gender',
        'extra_curricular': 'Extra-Curricular',
        'late_night_entry': 'Late-Night Entry (1-5)'
    };
    
    let html = `
        <div class="review-section">
            <h3>📚 Academic Information</h3>
            <div class="review-grid">
    `;
    
    for (let [key, label] of Object.entries(academicFields)) {
        const value = formData.get(key);
        html += `
            <div class="review-item">
                <div class="review-label">${label}</div>
                <div class="review-value">${value}</div>
            </div>
        `;
    }
    
    html += `
            </div>
        </div>
        <div class="review-section">
            <h3>👤 Personal Information</h3>
            <div class="review-grid">
    `;
    
    for (let [key, label] of Object.entries(personalFields)) {
        const value = formData.get(key);
        html += `
            <div class="review-item">
                <div class="review-label">${label}</div>
                <div class="review-value">${value}</div>
            </div>
        `;
    }
    
    html += `
            </div>
        </div>
    `;
    
    document.getElementById('reviewData').innerHTML = html;
}

// Form submission handler
if (document.getElementById('predictionForm')) {
    document.getElementById('predictionForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Get form data
        const formData = new FormData(e.target);
        
        // Validate all inputs before submission
        if (!validateInputs(formData)) {
            return;
        }
        
        // Show loading
        document.getElementById('loading').classList.add('show');
        document.querySelector('.btn-predict').disabled = true;
        
        // Prepare data object
        const data = {
            attendance: parseFloat(formData.get('attendance')),
            study_hours: parseFloat(formData.get('study_hours')),
            previous_cgpa: parseFloat(formData.get('previous_cgpa')),
            internal_marks: parseFloat(formData.get('internal_marks')),
            midsem_marks: parseFloat(formData.get('midsem_marks')),
            backlogs: parseInt(formData.get('backlogs')),
            assignment_completion: parseFloat(formData.get('assignment_completion')),
            class_participation: parseInt(formData.get('class_participation')),
            age: parseInt(formData.get('age')),
            sex: formData.get('sex'),
            extra_curricular: formData.get('extra_curricular'),
            late_night_entry: parseInt(formData.get('late_night_entry'))
        };
        
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            // Hide loading
            document.getElementById('loading').classList.remove('show');
            document.querySelector('.btn-predict').disabled = false;
            
            if (result.success) {
                // Store results in sessionStorage
                sessionStorage.setItem('predictionResults', JSON.stringify(result));
                sessionStorage.setItem('inputData', JSON.stringify(data));
                
                // Redirect to results page
                window.location.href = 'result.html';
            } else {
                showPopup(`Prediction failed: ${result.error || 'Unknown error'}`);
            }
        } catch (error) {
            document.getElementById('loading').classList.remove('show');
            document.querySelector('.btn-predict').disabled = false;
            
            showPopup(`Error: ${error.message}. Make sure the backend server is running on http://localhost:5000`);
        }
    });
}

// ==========================================
// RESULT PAGE FUNCTIONS
// ==========================================

function displayResults() {
    // Get data from sessionStorage
    const resultsData = sessionStorage.getItem('predictionResults');
    const inputData = sessionStorage.getItem('inputData');
    
    if (!resultsData || !inputData) {
        alert('No prediction data found. Please make a prediction first.');
        window.location.href = 'predict.html';
        return;
    }
    
    const results = JSON.parse(resultsData);
    const inputs = JSON.parse(inputData);
    
    // Display predicted marks
    document.getElementById('predictedMarks').textContent = results.predicted_endsem_marks.toFixed(2);
    
    // Display breakdown
    document.getElementById('midsemMarks').textContent = inputs.midsem_marks.toFixed(1);
    document.getElementById('internalMarks').textContent = inputs.internal_marks.toFixed(1);
    document.getElementById('endsemMarks').textContent = results.predicted_endsem_marks.toFixed(2);
    document.getElementById('totalMarks').textContent = results.total_marks.toFixed(2);
    
    // Display grade
    const gradeBadge = document.getElementById('gradeBadge');
    gradeBadge.textContent = results.grade;
    gradeBadge.className = 'grade-badge grade-' + results.grade;
    
    // Create contribution chart
    createContributionChart(inputs);
    
    // Populate input summary table
    populateInputSummary(inputs);
}

function createContributionChart(inputs) {
    const ctx = document.getElementById('contributionChart');
    if (!ctx) return;
    
    // Normalize values for visualization (0-100 scale)
    const chartData = {
        'Attendance': inputs.attendance,
        'Study Hours': (inputs.study_hours / 12) * 100,
        'Previous CGPA': (inputs.previous_cgpa / 10) * 100,
        'Internal Marks': (inputs.internal_marks / 30) * 100,
        'Midsem Marks': (inputs.midsem_marks / 20) * 100,
        'Assignment': inputs.assignment_completion,
        'Participation': (inputs.class_participation / 5) * 100,
        'Backlogs Impact': Math.max(0, 100 - (inputs.backlogs * 20))
    };
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(chartData),
            datasets: [{
                label: 'Performance Score (%)',
                data: Object.values(chartData),
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(72, 187, 120, 0.8)',
                    'rgba(66, 153, 225, 0.8)',
                    'rgba(237, 137, 54, 0.8)',
                    'rgba(246, 173, 85, 0.8)',
                    'rgba(156, 163, 175, 0.8)',
                    'rgba(252, 129, 129, 0.8)'
                ],
                borderColor: [
                    'rgba(102, 126, 234, 1)',
                    'rgba(118, 75, 162, 1)',
                    'rgba(72, 187, 120, 1)',
                    'rgba(66, 153, 225, 1)',
                    'rgba(237, 137, 54, 1)',
                    'rgba(246, 173, 85, 1)',
                    'rgba(156, 163, 175, 1)',
                    'rgba(252, 129, 129, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

function populateInputSummary(inputs) {
    const tableBody = document.getElementById('inputSummaryTable');
    if (!tableBody) return;
    
    const fields = [
        { name: 'Attendance', value: inputs.attendance + '%', category: 'Academic' },
        { name: 'Study Hours/Day', value: inputs.study_hours, category: 'Academic' },
        { name: 'Previous CGPA', value: inputs.previous_cgpa, category: 'Academic' },
        { name: 'Internal Marks', value: inputs.internal_marks + '/30', category: 'Academic' },
        { name: 'Mid-Semester Marks', value: inputs.midsem_marks + '/20', category: 'Academic' },
        { name: 'Backlogs', value: inputs.backlogs, category: 'Academic' },
        { name: 'Assignment Completion', value: inputs.assignment_completion + '%', category: 'Academic' },
        { name: 'Class Participation', value: inputs.class_participation + '/5', category: 'Academic' },
        { name: 'Age', value: inputs.age, category: 'Demographic' },
        { name: 'Gender', value: inputs.sex, category: 'Demographic' },
        { name: 'Extra-Curricular', value: inputs.extra_curricular, category: 'Behavioral' },
        { name: 'Late-Night Entry', value: inputs.late_night_entry + '/5', category: 'Behavioral' }
    ];
    
    let html = '';
    fields.forEach(field => {
        html += `
            <tr>
                <td><strong>${field.name}</strong></td>
                <td>${field.value}</td>
                <td><span style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem;">${field.category}</span></td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}