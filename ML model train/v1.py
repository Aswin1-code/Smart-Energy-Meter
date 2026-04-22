import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# ==============================
# 1. LOAD DATASET
# ==============================
df = pd.read_csv(r"E:\pendrive\code\Smart Energy meter\Smart-Energy-Meter\Dataset\final_Energy_dataset.csv")

print("✅ Dataset loaded")
print(df.head())

# ==============================
# 2. FEATURE SELECTION
# ==============================
features = ['power', 'hour_of_day']
target = 'energy'

X = df[features]
y = df[target]

# ==============================
# 3. TRAIN / TEST SPLIT
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

# ==============================
# 4. MODEL TRAINING
# ==============================
model = LinearRegression()
model.fit(X_train, y_train)

# ==============================
# 5. PREDICTION
# ==============================
y_pred = model.predict(X_test)

# ==============================
# 6. EVALUATION
# ==============================
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n📊 MODEL PERFORMANCE")
print("----------------------")
print("MAE:", mae)
print("R2 Score:", r2)

# ==============================
# 7. TEST SAMPLE PREDICTION
# ==============================
sample = pd.DataFrame([[100, 19]], columns=['power', 'hour_of_day'])
prediction = model.predict(sample)

print("\n🔮 SAMPLE PREDICTION")
print("----------------------")
print("Energy (kWh):", prediction[0])

# ==============================
# 8. SAVE MODEL
# ==============================
joblib.dump(model, "energy_model.pkl")

print("\n✅ Model saved as energy_model.pkl")