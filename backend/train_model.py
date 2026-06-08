import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import pickle
import json

# Load dataset
df = pd.read_csv('student_performance_dataset.csv')

# Features and target
X = df.drop('Endsem_Marks', axis=1)
y = df['Endsem_Marks']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Dictionary to store models and their metrics
models = {}
metrics = {}

# 1. Random Forest
print("Training Random Forest...")
rf_model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=15)
rf_model.fit(X_train_scaled, y_train)
rf_train_pred = rf_model.predict(X_train_scaled)
rf_test_pred = rf_model.predict(X_test_scaled)

models['RandomForest'] = rf_model
metrics['RandomForest'] = {
    'r2_train': float(r2_score(y_train, rf_train_pred)),
    'r2_test': float(r2_score(y_test, rf_test_pred)),
    'mae': float(mean_absolute_error(y_test, rf_test_pred)),
    'rmse': float(np.sqrt(mean_squared_error(y_test, rf_test_pred)))
}

# 2. Gradient Boosting
print("Training Gradient Boosting...")
gb_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
gb_model.fit(X_train_scaled, y_train)
gb_train_pred = gb_model.predict(X_train_scaled)
gb_test_pred = gb_model.predict(X_test_scaled)

models['GradientBoosting'] = gb_model
metrics['GradientBoosting'] = {
    'r2_train': float(r2_score(y_train, gb_train_pred)),
    'r2_test': float(r2_score(y_test, gb_test_pred)),
    'mae': float(mean_absolute_error(y_test, gb_test_pred)),
    'rmse': float(np.sqrt(mean_squared_error(y_test, gb_test_pred)))
}

# 3. Linear Regression
print("Training Linear Regression...")
lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)
lr_train_pred = lr_model.predict(X_train_scaled)
lr_test_pred = lr_model.predict(X_test_scaled)

models['LinearRegression'] = lr_model
metrics['LinearRegression'] = {
    'r2_train': float(r2_score(y_train, lr_train_pred)),
    'r2_test': float(r2_score(y_test, lr_test_pred)),
    'mae': float(mean_absolute_error(y_test, lr_test_pred)),
    'rmse': float(np.sqrt(mean_squared_error(y_test, lr_test_pred)))
}

# 4. Ridge Regression
print("Training Ridge Regression...")
ridge_model = Ridge(alpha=1.0)
ridge_model.fit(X_train_scaled, y_train)
ridge_train_pred = ridge_model.predict(X_train_scaled)
ridge_test_pred = ridge_model.predict(X_test_scaled)

models['Ridge'] = ridge_model
metrics['Ridge'] = {
    'r2_train': float(r2_score(y_train, ridge_train_pred)),
    'r2_test': float(r2_score(y_test, ridge_test_pred)),
    'mae': float(mean_absolute_error(y_test, ridge_test_pred)),
    'rmse': float(np.sqrt(mean_squared_error(y_test, ridge_test_pred)))
}

# 5. Support Vector Regression
print("Training Support Vector Regression...")
svr_model = SVR(kernel='rbf', gamma='scale')
svr_model.fit(X_train_scaled, y_train)
svr_train_pred = svr_model.predict(X_train_scaled)
svr_test_pred = svr_model.predict(X_test_scaled)

models['SVR'] = svr_model
metrics['SVR'] = {
    'r2_train': float(r2_score(y_train, svr_train_pred)),
    'r2_test': float(r2_score(y_test, svr_test_pred)),
    'mae': float(mean_absolute_error(y_test, svr_test_pred)),
    'rmse': float(np.sqrt(mean_squared_error(y_test, svr_test_pred)))
}

# Print metrics
print("\n" + "="*70)
print("MODEL PERFORMANCE COMPARISON")
print("="*70)
for model_name, model_metrics in metrics.items():
    print(f"\n{model_name}:")
    print(f"  Train R² Score: {model_metrics['r2_train']:.4f}")
    print(f"  Test R² Score:  {model_metrics['r2_test']:.4f}")
    print(f"  MAE:            {model_metrics['mae']:.4f}")
    print(f"  RMSE:           {model_metrics['rmse']:.4f}")

# Find best model
# Uncomment this line if you want model.pkl to use the best model by test R^2:
# best_model_name = max(metrics, key=lambda x: metrics[x]['r2_test'])

# Keep Random Forest as default because SHAP explanations are fast and stable for tree models.
best_model_name = "RandomForest"
# print("Best model type:", type(models[best_model_name]))
print(f"\n✅ Best Model (by Test R²): {best_model_name}")
print("="*70)

# Save all models
for model_name, model in models.items():
    with open(f'{model_name.lower()}_model.pkl', 'wb') as f:
        pickle.dump(model, f)

# Save metrics
with open('model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

# Save default model and scaler
with open('model.pkl', 'wb') as f:
    pickle.dump(models[best_model_name], f)

with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

print("\n✅ All models saved successfully!")
print("Files created:")
print("  - model.pkl (best model)")
print("  - scaler.pkl")
for model_name in models.keys():
    print(f"  - {model_name.lower()}_model.pkl")
print("  - model_metrics.json")
