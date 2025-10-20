# LAB-ONLY: Model training (V-FINAL - Force Overwrite)
import pandas as pd; from sklearn.ensemble import RandomForestClassifier; import joblib; import os
def train():
    print("Starting model training (V-FINAL - Force Overwrite - Training on 100%)..."); 
    try: df = pd.read_csv('data/dataset.csv')
    except FileNotFoundError: print("Error: data/dataset.csv not found."); return
    features = ['critical_risk_count', 'high_risk_count', 'medium_risk_count', 'nikto_vuln_count']; 
    X = df[features]; y = df['risk_label']
    X_train = X; y_train = y 
    model = RandomForestClassifier(n_estimators=10, random_state=42); model.fit(X_train, y_train)
    model_filename = 'model/autopenta_model.pkl'; model_dir = os.path.dirname(model_filename)
    os.makedirs(model_dir, exist_ok=True) 
    if os.path.exists(model_filename):
        try: os.remove(model_filename); print(f"Removed old model file: {model_filename}")
        except OSError as e: print(f"Error removing old model file {model_filename}: {e}")
    try:
         joblib.dump(model, model_filename); 
         print(f"Model training complete. Saved new model to {model_filename}")
         accuracy = model.score(X_train, y_train); 
         print(f"Model accuracy on (full) training set: {accuracy * 100:.2f}%") # Should be 100%
    except Exception as e:
         print(f"ERROR saving model file {model_filename}: {e}")
if __name__ == "__main__": train()
