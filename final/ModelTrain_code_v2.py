import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler

import joblib

# ==============================
# 1. LOAD DATASET
# ==============================
df = pd.read_csv(r"E:\pendrive\code\Smart Energy meter\Smart-Energy-Meter\final\dataset\energyDataset.csv")

print("✅ Dataset Loaded")
print(df.head())

# ==============================
# 2. FEATURES & TARGET
# ==============================
X = df[['power', 'hour_of_day']]
y = df['energy']

# ==============================
# 3. FEATURE SCALING
# ==============================
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ==============================
# 4. TRAIN-TEST SPLIT
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42
)

# ==============================
# 5. TRAIN MODEL
# ==============================
model = LinearRegression()
model.fit(X_train, y_train)

# ==============================
# 6. PREDICTION
# ==============================
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n📊 MODEL PERFORMANCE")
print("----------------------")
print("MAE:", mae)
print("R2 Score:", r2)

# ==============================
# 7. SAMPLE CHECK
# ==============================
sample = np.array([[100, 19]])
sample_scaled = scaler.transform(sample)
pred = model.predict(sample_scaled)[0]

print("\n🔮 SAMPLE TEST")
print("----------------------")
print("Power: 100W")
print("Hour: 19")
print("Energy (kWh):", pred)

# ==============================
# 8. SAVE MODEL + SCALER
# ==============================
joblib.dump(model, "energy_model.pkl")
joblib.dump(scaler, "scaler.pkl")

print("\n✅ Model saved: energy_model.pkl")
print("✅ Scaler saved: scaler.pkl")