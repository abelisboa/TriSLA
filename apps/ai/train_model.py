import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Create a simple SLA prediction model
X = np.array([[5.0, 1], [10.0, 1], [15.0, 1], [20.0, 0], [25.0, 0], [30.0, 0]])
y = np.array([1, 1, 0, 0, 0, 0])  # 1 = ACCEPT, 0 = REJECT

model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)

# Save the model
joblib.dump(model, 'modelo_sla.pkl')
print("Model saved as modelo_sla.pkl")
