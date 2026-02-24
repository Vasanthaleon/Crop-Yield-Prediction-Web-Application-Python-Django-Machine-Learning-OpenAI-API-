import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor

data = pd.read_csv("crop_yield.csv")

le_state = LabelEncoder()
le_crop = LabelEncoder()
le_season = LabelEncoder()

data['State'] = le_state.fit_transform(data['State'])
data['Crop'] = le_crop.fit_transform(data['Crop'])
data['Season'] = le_season.fit_transform(data['Season'])

X = data.drop('Yield', axis=1)
y = data['Yield']

model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X, y)

joblib.dump(model, "crop_yield_model.pkl")
joblib.dump(le_state, "state_encoder.pkl")
joblib.dump(le_crop, "crop_encoder.pkl")
joblib.dump(le_season, "season_encoder.pkl")

print("Model trained successfully")
