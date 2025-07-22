from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import json

app = Flask(__name__)

# --- Load Model and necessary files at startup ---
try:
    model = joblib.load('model/salary_prediction_model.joblib')
    feature_columns = joblib.load('model/feature_columns.joblib')
    categorical_values = joblib.load('model/categorical_values.joblib')
    print("✅ Model and supporting files loaded successfully.")
    
    # Load dataset for visualizations
    df = pd.read_csv('indian_employee_salary_dataset.csv')
    df.rename(columns={'Monthly Salary (INR)': 'Salary'}, inplace=True)
    
    # --- Prepare Data for Charts ---
    # Chart 1: Average Salary by Job Title (Top 10)
    avg_salary_by_job = df.groupby('Job Title')['Salary'].mean().sort_values(ascending=False).head(10)
    chart1_data = {
        "labels": avg_salary_by_job.index.tolist(),
        "data": avg_salary_by_job.values.tolist()
    }

    # Chart 2: Education Level Distribution
    education_distribution = df['Education'].value_counts()
    chart2_data = {
        "labels": education_distribution.index.tolist(),
        "data": education_distribution.values.tolist()
    }
    
except Exception as e:
    print(f"❌ Error loading files: {e}. Please run model_training.py first.")
    model = None
    chart1_data = {}
    chart2_data = {}

@app.route('/', methods=['GET'])
def home():
    if model is None:
        return "Model not found. Please run model_training.py first.", 500
    return render_template('index.html', 
                           categorical_values=categorical_values,
                           chart1_data=json.dumps(chart1_data),
                           chart2_data=json.dumps(chart2_data))

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model is not loaded.'}), 500

    try:
        data = request.get_json(force=True)
        input_data = pd.DataFrame([data], columns=feature_columns)
        
        for col in ['Age', 'Experience']:
            input_data[col] = pd.to_numeric(input_data[col], errors='coerce')
        
        if input_data.isnull().values.any():
            return jsonify({'error': 'Please enter valid numbers for Age and Experience.'}), 400

        prediction = model.predict(input_data)[0]
        
        lower_bound = prediction * 0.90
        upper_bound = prediction * 1.10

        return jsonify({
            'prediction': f'₹{prediction:,.0f} per month',
            'range': f'₹{lower_bound:,.0f} to ₹{upper_bound:,.0f}',
            'raw_prediction': prediction # For the report
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)