import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

from backend.data_preparation import prepare_training_data, prepare_single_input

# ==========================================================
# 1. TRAIN AI MODEL
# ==========================================================
def train_model(csv_file_path, model_save_path="backend/student_model.pkl"):
    """
    Trains a Random Forest Regressor using the prepared data and saves it.
    """
    print(f"Loading and preparing data from: {csv_file_path}...")
    try:
        X, y, mean, std = prepare_training_data(csv_file_path)
    except FileNotFoundError:
        print(f"Error: Could not find {csv_file_path}. Please provide a valid dataset.")
        return None, None, None
        
    if y is None:
        print("Error: Target column 'final_marks' not found in dataset.")
        return None, None, None

    print("Splitting dataset into training and testing sets...")
    # 80% for training, 20% for testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest AI Model...")
    # Initialize model
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    
    # Train model
    model.fit(X_train, y_train)

    print("Evaluating model...")
    # Predict on test data
    predictions = model.predict(X_test)
    
    # Calculate error metrics
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    
    print("\n" + "="*30)
    print(" MODEL TRAINING RESULTS")
    print("="*30)
    print(f"Mean Squared Error: {mse:.2f}")
    print(f"R2 Score (Accuracy): {r2:.4f}")
    print("="*30 + "\n")

    # Save the model and normalization parameters for later inference
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump({"model": model, "mean": mean, "std": std}, model_save_path)
    print(f"Model successfully saved to {model_save_path}")

    return model, mean, std

# ==========================================================
# 2. PREDICT PERFORMANCE (INFERENCE)
# ==========================================================
def predict_student_performance(student_data, model_save_path="backend/student_model.pkl"):
    """
    Loads the trained model and predicts the final marks for a new student.
    
    student_data format:
    {
        "attendance": 85,
        "prev_sem_marks": 78,
        "internal_marks": 25,
        "study_hours": 4
    }
    """
    if not os.path.exists(model_save_path):
        print(f"Error: Model not found at {model_save_path}. Please train the model first.")
        return None

    # Load model and normalization parameters
    saved_data = joblib.load(model_save_path)
    model = saved_data["model"]
    mean = saved_data["mean"]
    std = saved_data["std"]

    # Process and normalize input data
    processed_input = prepare_single_input(student_data, mean, std)

    # Predict
    prediction = model.predict(processed_input)
    
    return prediction[0]

# ==========================================================
# 3. EXAMPLE USAGE / TEST SCRIPT
# ==========================================================
if __name__ == "__main__":
    # Note: To run this, you need a CSV file named 'students_dataset.csv' 
    # with columns: attendance, prev_sem_marks, internal_marks, study_hours, final_marks
    
    dataset_path = "students_dataset.csv"
    
    # Check if dataset exists before trying to train
    if os.path.exists(dataset_path):
        # 1. Train the model
        train_model(dataset_path)
        
        # 2. Test prediction
        sample_student = {
            "attendance": 92,
            "prev_sem_marks": 85,
            "internal_marks": 28,
            "study_hours": 5
        }
        
        predicted_marks = predict_student_performance(sample_student)
        if predicted_marks is not None:
            print(f"\nAI Prediction for Sample Student:")
            print(f"Predicted Final Marks: {predicted_marks:.2f}")
    else:
        print(f"Dataset '{dataset_path}' not found. Cannot run training example.")
        print("\nTo use this model:")
        print("1. Create a dataset with columns: attendance, prev_sem_marks, internal_marks, study_hours, final_marks")
        print("2. Run train_model('your_dataset.csv')")
        print("3. Use predict_student_performance(student_dict) to get predictions")
