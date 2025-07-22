document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('prediction-form');
    const resultContainer = document.getElementById('result-container');
    const errorAlert = document.getElementById('error-alert');
    const predictButton = document.getElementById('predict-button');
    const buttonText = document.getElementById('button-text');
    const buttonSpinner = document.getElementById('button-spinner');
    const downloadBtn = document.getElementById('download-report');
    let predictionData = {}; // Store prediction data for PDF report

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        buttonText.textContent = 'Predicting...';
        buttonSpinner.classList.remove('d-none');
        predictButton.disabled = true;
        resultContainer.classList.add('d-none');
        errorAlert.classList.add('d-none');

        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        predictionData.inputs = data; // Store user inputs for the report

        fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                errorAlert.textContent = 'Error: ' + data.error;
                errorAlert.classList.remove('d-none');
            } else {
                predictionData.prediction = data; // Store results for the report
                document.getElementById('prediction-value').textContent = data.prediction;
                document.getElementById('range-value').textContent = data.range;
                resultContainer.classList.remove('d-none');
            }
        })
        .catch(error => {
            errorAlert.textContent = 'An unexpected error occurred. Please check the console.';
            errorAlert.classList.remove('d-none');
        })
        .finally(() => {
            buttonText.textContent = 'Predict Salary';
            buttonSpinner.classList.add('d-none');
            predictButton.disabled = false;
        });
    });

    // --- PDF Download Feature ---
    downloadBtn.addEventListener('click', function() {
        const { inputs, prediction } = predictionData;
        const reportContent = `
            <div style="font-family: Arial, sans-serif; padding: 2rem;">
                <h1 style="color: #1e2a38;">Salary Prediction Report</h1>
                <p><strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
                <hr>
                <h3 style="color: #333;">Input Details</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f2f2f2;"><th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Feature</th><th style="padding: 8px; border: 1px solid #ddd; text-align: left;">Value</th></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;">Age</td><td style="padding: 8px; border: 1px solid #ddd;">${inputs.Age}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;">Gender</td><td style="padding: 8px; border: 1px solid #ddd;">${inputs.Gender}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;">Education</td><td style="padding: 8px; border: 1px solid #ddd;">${inputs.Education}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;">Job Title</td><td style="padding: 8px; border: 1px solid #ddd;">${inputs['Job Title']}</td></tr>
                    <tr><td style="padding: 8px; border: 1px solid #ddd;">Experience</td><td style="padding: 8px; border: 1px solid #ddd;">${inputs.Experience} years</td></tr>
                </table>
                <hr>
                <h3 style="color: #333;">Prediction Result</h3>
                <div style="background-color: #eef2ff; padding: 1rem; border-radius: 8px; text-align: center;">
                    <p style="font-size: 1.2rem; margin: 0;">Predicted Monthly Salary</p>
                    <p style="font-size: 2.5rem; font-weight: bold; color: #5e72e4; margin: 0;">${prediction.prediction}</p>
                    <p style="font-size: 1rem; color: #6c757d; margin-top: 5px;">Range: ${prediction.range}</p>
                </div>
            </div>
        `;
        document.getElementById('printable-report').innerHTML = reportContent;
        window.print();
    });

    // --- Chart.js Visualizations ---
    const jobTitleCtx = document.getElementById('jobTitleChart').getContext('2d');
    new Chart(jobTitleCtx, {
        type: 'bar',
        data: {
            labels: chart1Data.labels,
            datasets: [{
                label: 'Average Monthly Salary (₹)',
                data: chart1Data.data,
                backgroundColor: '#5e72e4',
            }]
        },
        options: { indexAxis: 'y', responsive: true }
    });

    const educationCtx = document.getElementById('educationChart').getContext('2d');
    new Chart(educationCtx, {
        type: 'pie',
        data: {
            labels: chart2Data.labels,
            datasets: [{
                label: 'Count',
                data: chart2Data.data,
                backgroundColor: ['#5e72e4', '#324cdd', '#8997ff', '#2c3e50', '#95a5a6'],
            }]
        },
        options: { responsive: true }
    });
});