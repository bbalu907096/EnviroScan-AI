import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

# -------------------------------
# 1. Load Raw Dataset
# -------------------------------
df = pd.read_csv("data/merged_realtime_data.csv")
print("🔹 Raw shape:", df.shape)

# -------------------------------
# 2. Handle Missing Values
# -------------------------------
print("🔹 Missing values before:\n", df.isnull().sum())

# Drop duplicates
df = df.drop_duplicates()

# Fill missing numerical values with median
num_cols = df.select_dtypes(include=[np.number]).columns
for col in num_cols:
    df[col] = df[col].fillna(df[col].median())

# -------------------------------
# 3. Feature Engineering
# -------------------------------
df["temp_humidity_index"] = df["temperature"] * df["humidity"] / 100
df["pollution_wind_ratio"] = (df["pm2_5"] + df["pm10"] + df["no2"] + df["so2"] + df["o3"] + df["co"]) / (df["wind_speed"] + 0.1)

if "aqi" in df.columns:
    df["aqi_category"] = pd.cut(
        df["aqi"],
        bins=[0, 50, 100, 150, 200, 300, 500],
        labels=["Good", "Moderate", "Unhealthy Sensitive", "Unhealthy", "Very Unhealthy", "Hazardous"]
    )

# -------------------------------
# 4. Encode Categorical Variables (excluding location_id)
# -------------------------------
cat_cols = df.select_dtypes(include=["object", "category"]).columns
cat_cols = [col for col in cat_cols if col != "location_id"]
le = LabelEncoder()
for col in cat_cols:
    df[col] = df[col].astype(str)
    df[col] = le.fit_transform(df[col])

# -------------------------------
# 5. Normalize/Standardize Numerical Features (excluding location_id, latitude, longitude)
# -------------------------------
scaler = StandardScaler()
num_cols = df.select_dtypes(include=[np.number]).columns
num_cols = [col for col in num_cols if col not in ["location_id", "latitude", "longitude"]]
df[num_cols] = scaler.fit_transform(df[num_cols])

# -------------------------------
# 6. Feature Selection (drop highly correlated)
# -------------------------------
corr_matrix = df.corr().abs()
upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > 0.9)]
to_drop = [col for col in to_drop if col != "location_id"]
df = df.drop(columns=to_drop)
print("🔹 Dropped due to high correlation:", to_drop)

# -------------------------------
# 7. Save Cleaned Features
# -------------------------------
df.to_csv("data/cleaned_features.csv", index=False)
print("✅ Cleaned + Feature-engineered dataset saved as data/cleaned_features.csv")
