# Import pandas for tabular data handling (DataFrame operations)
import pandas as pd

# Import numpy for numerical operations and array transformations
import numpy as np


# ==========================================================
# 1. LOAD CSV FILE
# ==========================================================
def load_csv(file_path):
    """
    Reads a CSV file and returns a pandas DataFrame.
    """
    # pd.read_csv loads the CSV into a structured table (rows x columns)
    df = pd.read_csv(file_path)
    
    # Return the loaded DataFrame for further processing
    return df


# ==========================================================
# 2. CLEAN DATA
# ==========================================================
def clean_data(df):
    """
    Cleans dataset by removing duplicates and handling missing values.
    """
    # Create a copy to avoid modifying original data (good practice)
    df = df.copy()

    # Remove duplicate rows to avoid biasing the model with repeated data
    df.drop_duplicates(inplace=True)

    # Fill missing numeric values with median of each column
    # Median is robust against outliers compared to mean
    df.fillna(df.median(numeric_only=True), inplace=True)

    # Return cleaned DataFrame
    return df


# ==========================================================
# 3. FEATURE ENGINEERING
# ==========================================================
def add_features(df):
    """
    Creates additional meaningful features from existing columns.
    """
    # Copy DataFrame to avoid unintended side effects
    df = df.copy()

    # Create a combined performance score
    # Weighted sum gives importance to previous marks, internal marks, attendance
    df["performance_index"] = (
        0.4 * df["prev_sem_marks"] +   # Previous semester has highest weight
        0.3 * df["internal_marks"] +   # Internal marks moderate importance
        0.3 * df["attendance"]         # Attendance also contributes
    )

    # Create study efficiency feature
    # Measures marks achieved per hour of study
    # +1 avoids division by zero when study_hours = 0
    df["study_efficiency"] = df["internal_marks"] / (df["study_hours"] + 1)

    # Return DataFrame with new features
    return df


# ==========================================================
# 4. CONVERT DATAFRAME TO NUMPY
# ==========================================================
def to_numpy(df, target_column="final_marks"):
    """
    Converts DataFrame into NumPy arrays for model input.
    """
    # X contains all columns except target (features)
    X = df.drop(columns=[target_column]).values

    # y contains the target values (what model should predict)
    # If target column not present, return None
    y = df[target_column].values if target_column in df else None

    # Return feature matrix and target vector
    return X, y


# ==========================================================
# 5. NORMALIZATION (TRAIN TIME)
# ==========================================================
def normalize_fit(X):
    """
    Normalizes features and computes mean & std for future use.
    """
    # Compute mean of each feature column
    mean = X.mean(axis=0)

    # Compute standard deviation of each feature column
    std = X.std(axis=0)

    # Replace zero std with 1 to avoid division by zero
    # This happens when a column has constant values
    std[std == 0] = 1

    # Apply normalization formula: (X - mean) / std
    X_norm = (X - mean) / std

    # Return normalized data along with parameters (needed later)
    return X_norm, mean, std


# ==========================================================
# 6. NORMALIZATION (INFERENCE TIME)
# ==========================================================
def normalize_transform(X, mean, std):
    """
    Applies previously computed normalization to new data.
    """
    # Again ensure no division by zero
    std = np.where(std == 0, 1, std)

    # Apply same scaling used during training
    return (X - mean) / std


# ==========================================================
# 7. FULL TRAINING DATA PREPARATION
# ==========================================================
def prepare_training_data(file_path):
    """
    Complete pipeline: load → clean → feature → normalize → numpy
    """
    # Step 1: Load raw CSV data
    df = load_csv(file_path)

    # Step 2: Clean the dataset
    df = clean_data(df)

    # Step 3: Add engineered features
    df = add_features(df)

    # Step 4: Convert to NumPy arrays
    X, y = to_numpy(df)

    # Step 5: Normalize features and store scaling parameters
    X, mean, std = normalize_fit(X)

    # Return everything required for model training
    return X, y, mean, std


# ==========================================================
# 8. SINGLE INPUT PREPARATION (FOR PREDICTION)
# ==========================================================
def prepare_single_input(data_dict, mean, std):
    """
    Converts a single student's data into normalized NumPy format.
    """

    # Compute performance index using same formula as training
    perf_index = (
        0.4 * data_dict["prev_sem_marks"] +
        0.3 * data_dict["internal_marks"] +
        0.3 * data_dict["attendance"]
    )

    # Compute study efficiency feature
    study_eff = data_dict["internal_marks"] / (data_dict["study_hours"] + 1)

    # Create NumPy array in SAME ORDER as training features
    arr = np.array([[
        data_dict["attendance"],
        data_dict["prev_sem_marks"],
        data_dict["internal_marks"],
        data_dict["study_hours"],
        perf_index,
        study_eff
    ]])

    # Apply normalization using training mean and std
    arr = normalize_transform(arr, mean, std)

    # Return model-ready input
    return arr
