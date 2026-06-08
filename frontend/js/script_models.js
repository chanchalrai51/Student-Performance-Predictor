// Model Comparison Dashboard JS

const METRICS_URL = 'http://localhost:5000/model-metrics';
const COMPARE_URL = 'http://localhost:5000/compare-models';

let chartsCreated = false;

async function loadModelDashboard() {
    try {
        const response = await fetch(METRICS_URL);
        const data = await response.json();

        if (data.success && data.metrics) {
            displayMetricsTable(data.metrics);
            displayModelCards(data.metrics);
            createCharts(data.metrics);
        }
    } catch (error) {
        console.error('Error loading model dashboard:', error);
    }
}

function displayMetricsTable(metrics) {
    const tableBody = document.getElementById('metricsTableBody');
    let html = '';

    metrics.forEach(metric => {
        html += `
            <tr>
                <td><strong>${metric.model_name}</strong></td>
                <td>${(metric.r2_train).toFixed(4)}</td>
                <td><span class="highlight">${(metric.r2_test).toFixed(4)}</span></td>
                <td>${(metric.mae).toFixed(4)}</td>
                <td>${(metric.rmse).toFixed(4)}</td>
            </tr>
        `;
    });

    tableBody.innerHTML = html;
}

function displayModelCards(metrics) {
    const grid = document.getElementById('modelsGrid');
    let html = '';

    metrics.forEach(metric => {
        html += `
            <div class="model-card">
                <h4>${metric.model_name}</h4>
                <div class="model-metric">
                    <span class="metric-label">Train R²:</span>
                    <span class="metric-value">${(metric.r2_train).toFixed(4)}</span>
                </div>
                <div class="model-metric">
                    <span class="metric-label">Test R²:</span>
                    <span class="metric-value">${(metric.r2_test).toFixed(4)}</span>
                </div>
                <div class="model-metric">
                    <span class="metric-label">MAE:</span>
                    <span class="metric-value">${(metric.mae).toFixed(4)}</span>
                </div>
                <div class="model-metric">
                    <span class="metric-label">RMSE:</span>
                    <span class="metric-value">${(metric.rmse).toFixed(4)}</span>
                </div>
            </div>
        `;
    });

    grid.innerHTML = html;
}

function createCharts(metrics) {
    if (chartsCreated) return;

    // R² Score Chart
    const r2Ctx = document.getElementById('r2Chart');
    if (r2Ctx) {
        new Chart(r2Ctx, {
            type: 'bar',
            data: {
                labels: metrics.map(m => m.model_name),
                datasets: [
                    {
                        label: 'Train R²',
                        data: metrics.map(m => m.r2_train),
                        backgroundColor: 'rgba(102, 126, 234, 0.6)',
                        borderColor: 'rgba(102, 126, 234, 1)',
                        borderWidth: 2
                    },
                    {
                        label: 'Test R²',
                        data: metrics.map(m => m.r2_test),
                        backgroundColor: 'rgba(118, 75, 162, 0.6)',
                        borderColor: 'rgba(118, 75, 162, 1)',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(2);
                            }
                        }
                    }
                }
            }
        });
    }

    // Error Metrics Chart
    const errorCtx = document.getElementById('errorChart');
    if (errorCtx) {
        new Chart(errorCtx, {
            type: 'radar',
            data: {
                labels: ['MAE', 'RMSE'],
                datasets: metrics.map((metric, index) => ({
                    label: metric.model_name,
                    data: [metric.mae, metric.rmse],
                    borderColor: `hsl(${index * 60}, 70%, 50%)`,
                    backgroundColor: `hsla(${index * 60}, 70%, 50%, 0.2)`,
                    borderWidth: 2
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    chartsCreated = true;
}

async function compareOnModels() {
    const data = {
        attendance: parseFloat(document.getElementById('testAttendance').value),
        study_hours: parseFloat(document.getElementById('testStudyHours').value),
        previous_cgpa: parseFloat(document.getElementById('testCGPA').value),
        internal_marks: parseFloat(document.getElementById('testInternal').value),
        midsem_marks: parseFloat(document.getElementById('testMidsem').value),
        backlogs: parseInt(document.getElementById('testBacklogs').value),
        assignment_completion: parseFloat(document.getElementById('testAssignment').value),
        class_participation: parseInt(document.getElementById('testParticipation').value),
        age: parseInt(document.getElementById('testAge').value),
        sex: document.getElementById('testGender').value,
        extra_curricular: document.getElementById('testExtraCurricular').value,
        late_night_entry: parseInt(document.getElementById('testLateNight').value)
    };

    try {
        const response = await fetch(COMPARE_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success && result.comparisons) {
            displayComparisonResults(result.comparisons);
        }
    } catch (error) {
        console.error('Error comparing models:', error);
        document.getElementById('comparisonResults').innerHTML =
            '<p style="color: red;">Error loading comparison results</p>';
    }
}

function displayComparisonResults(comparisons) {
    const container = document.getElementById('comparisonResults');
    let html = '<div class="results-grid">';

    comparisons.forEach(comp => {
        html += `
            <div class="result-card">
                <h5>${comp.model_name}</h5>
                <div class="prediction-value">${comp.prediction.toFixed(2)}</div>
                <div class="prediction-max">/ 50 marks</div>
                <div class="metrics-small">
                    <div class="metric-row">
                        <span>Test R²:</span>
                        <strong>${(comp.r2_score).toFixed(4)}</strong>
                    </div>
                    <div class="metric-row">
                        <span>MAE:</span>
                        <strong>${(comp.mae).toFixed(4)}</strong>
                    </div>
                    <div class="metric-row">
                        <span>RMSE:</span>
                        <strong>${(comp.rmse).toFixed(4)}</strong>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}
