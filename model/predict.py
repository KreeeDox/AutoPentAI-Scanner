# LAB-ONLY: Model prediction (V-FINAL - Robust Confidence v2)
import joblib; import pandas as pd; import os; import numpy as np

def get_prediction(feature_df):
    model_filename = 'model/autopenta_model.pkl'
    print(f"\n[PREDICT FINAL v2] Attempting prediction using features:\n{feature_df.to_string()}")
    try: 
        if not os.path.exists(model_filename): print(f"[ERROR] Model file not found at {model_filename}."); return "Error", 0.0
        print(f"[PREDICT FINAL v2] Loading model from {model_filename}...")
        model = joblib.load(model_filename)
        print("[PREDICT FINAL v2] Model loaded successfully.")
    except Exception as e: print(f"[ERROR] Error loading model {model_filename}: {e}"); return "Error", 0.0

    features_ordered = ['critical_risk_count', 'high_risk_count', 'medium_risk_count', 'nikto_vuln_count']
    try: 
        if not all(col in feature_df.columns for col in features_ordered): missing = [col for col in features_ordered if col not in feature_df.columns]; print(f"[ERROR] Input missing columns: {missing}"); return "Error", 0.0
        feature_df_ordered = feature_df[features_ordered] 
        print("[PREDICT FINAL v2] Feature data prepared.")
    except Exception as e: print(f"[ERROR] Error preparing features: {e}"); return "Error", 0.0

    try:
        if feature_df_ordered.empty: print("[ERROR] Input feature data empty."); return "Error", 0.0

        print("[PREDICT FINAL v2] Performing model.predict...")
        prediction = model.predict(feature_df_ordered)
        print(f"[PREDICT FINAL v2] Raw prediction: {prediction}")

        print("[PREDICT FINAL v2] Performing model.predict_proba...")
        probability = model.predict_proba(feature_df_ordered)
        print(f"[PREDICT FINAL v2] Raw probabilities: {probability}")
        print(f"[PREDICT FINAL v2] Model classes: {model.classes_}") 

        if len(prediction) == 0 or len(probability) == 0: print("[ERROR] Model returned empty result."); return "Error", 0.0

        prediction_label = prediction[0]

        # --- ROBUST CONFIDENCE CALCULATION v2 ---
        # Get the probability scores for the single prediction
        probabilities_for_prediction = probability[0] 
        # Get the list of class names from the model
        model_classes = list(model.classes_)

        # Find the index (position) of our predicted label within the class list
        try:
             predicted_class_index = model_classes.index(prediction_label)
             # Get the probability score AT THAT SPECIFIC INDEX
             prediction_confidence = probabilities_for_prediction[predicted_class_index] * 100
             print(f"[PREDICT FINAL v2] Confidence for '{prediction_label}' (index {predicted_class_index}): {prediction_confidence:.2f}%")
        except ValueError:
             # This should NOT happen if predict() worked, but just in case...
             print(f"[ERROR] Predicted label '{prediction_label}' not in model classes: {model_classes}. Using max probability.")
             prediction_confidence = np.max(probabilities_for_prediction) * 100 
        except IndexError:
             print(f"[ERROR] Index {predicted_class_index} out of bounds for probabilities array. Using max probability.")
             prediction_confidence = np.max(probabilities_for_prediction) * 100
        except Exception as e_conf:
             print(f"[ERROR] calculating confidence: {e_conf}. Using max probability.")
             prediction_confidence = np.max(probabilities_for_prediction) * 100 
        # --- END ROBUST ---

        print(f"FINAL Prediction: {prediction_label} (Confidence: {prediction_confidence:.2f}%)")
        return prediction_label, prediction_confidence
    except Exception as e:
        print(f"[ERROR] during prediction phase: {e}")
        return "Error", 0.0
