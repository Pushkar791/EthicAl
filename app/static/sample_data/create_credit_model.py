"""
Sample Credit Scoring Model Generator

This script generates a sample credit scoring model for demonstration purposes.
The model is trained on a CSV dataset that may contain biased features.
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

# Create directory for models if it doesn't exist
os.makedirs('models', exist_ok=True)

# Load sample data
df = pd.read_csv('credit_dataset.csv')

# Create a binary target variable (1 for good credit score, 0 for poor)
df['credit_approved'] = (df['credit_score'] >= 700).astype(int)

# Select features and target
X = df.drop(['credit_score', 'credit_approved', 'zip_code'], axis=1)
y = df['credit_approved']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define categorical and numerical features
categorical_features = ['gender', 'education']
numerical_features = ['age', 'income', 'months_employed', 'debt_to_income', 
                      'num_credit_cards', 'num_late_payments']

# Create preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features)
    ])

# Create pipeline with preprocessor and model
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
])

# Train the model
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, 'models/credit_scoring_model.joblib')

print("Model training completed and saved to models/credit_scoring_model.joblib")
print(f"Training accuracy: {model.score(X_train, y_train):.4f}")
print(f"Test accuracy: {model.score(X_test, y_test):.4f}")

# Create evaluation data to show potential bias
evaluation_data = {
    'Gender': ['Male', 'Female'],
    'Approval Rate': [
        sum(y_test[X_test['gender'] == 'male']) / sum(X_test['gender'] == 'male'),
        sum(y_test[X_test['gender'] == 'female']) / sum(X_test['gender'] == 'female')
    ]
}

# Display evaluation data
print("\nApproval Rates by Gender:")
for gender, rate in zip(evaluation_data['Gender'], evaluation_data['Approval Rate']):
    print(f"{gender}: {rate:.2%}")

print("\nNote: This is a deliberately simplified model for demonstration purposes.")
print("It may exhibit biases that would need to be addressed in real applications.") 