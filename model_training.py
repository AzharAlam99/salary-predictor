import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_squared_error
import joblib
import os

def train_and_save_model():
    """
    Loads, preprocesses, trains, evaluates, and saves the salary prediction model.
    """
    # --- 1. Data Loading and Cleaning ---
    try:
        df = pd.read_csv('indian_employee_salary_dataset.csv')
        print("✅ Dataset loaded successfully.")
    except FileNotFoundError:
        print("❌ Error: 'indian_employee_salary_dataset.csv' not found.")
        return

    df.dropna(inplace=True)
    df.rename(columns={'Experience (Years)': 'Experience', 'Monthly Salary (INR)': 'Salary'}, inplace=True)
    
    # --- 2. Feature Engineering ---
    X = df[['Age', 'Gender', 'Education', 'Job Title', 'Experience']]
    y = df['Salary']

    # --- 3. Preprocessing ---
    categorical_features = ['Gender', 'Education', 'Job Title']
    numerical_features = ['Age', 'Experience']

    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
            ('cat', categorical_transformer, categorical_features)
        ],
        remainder='passthrough'
    )

    # --- 4. Model Training and Selection ---
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=42, objective='reg:squarederror')
    }

    best_model_name = ''
    best_model_score = -np.inf
    best_model_pipeline = None

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("\n--- Model Evaluation ---")
    for name, model in models.items():
        pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('regressor', model)])
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"--- {name} ---")
        print(f"  R² Score: {r2:.4f}")
        print(f"  RMSE: ₹{rmse:,.2f}")
        
        if r2 > best_model_score:
            best_model_score = r2
            best_model_name = name
            best_model_pipeline = pipeline

    print(f"\n🏆 Best Model Selected: {best_model_name} with R² score of {best_model_score:.4f}")

    # --- 5. Saving Artifacts ---
    os.makedirs("model", exist_ok=True)
    joblib.dump(best_model_pipeline, 'model/salary_prediction_model.joblib')
    print("\n✅ Trained model pipeline saved.")
    
    feature_columns = list(X.columns)
    joblib.dump(feature_columns, 'model/feature_columns.joblib')
    print("✅ Feature columns saved.")
    
    categorical_values = {col: X[col].unique().tolist() for col in categorical_features}
    joblib.dump(categorical_values, 'model/categorical_values.joblib')
    print("✅ Categorical values for dropdowns saved.")

if __name__ == '__main__':
    train_and_save_model()