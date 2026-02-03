import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
import joblib
import time
import numpy as np


# --- 1. FUNCTION: LOAD AND CLEAN DATA ---
def load_and_clean_data(filepath="ad.data"):
    print("\n[1/6] Loading and cleaning data...")
    start_time = time.time()

    try:
        # low_memory=False prevents warnings due to mixed types (numbers and '?')
        df = pd.read_csv(filepath, header=None, low_memory=False)
    except FileNotFoundError:
        print(f"ERROR: File '{filepath}' not found. Please download it first.")
        return None

    # Rename the last column (1558) to 'label'
    df.rename(columns={1558: "label"}, inplace=True)

    # Handle missing values ("?")
    # Replace "?" with NaN and then drop those rows
    # Using regex replacement is faster than iterating with a for-loop
    df = df.replace(to_replace='[?]', value=np.nan, regex=True)

    initial_len = len(df)
    df.dropna(inplace=True)
    final_len = len(df)

    # Convert feature columns to numeric (float)
    # Exclude the label column (last one)
    feature_cols = df.columns[:-1]
    df[feature_cols] = df[feature_cols].apply(pd.to_numeric)

    print(f"   -> Removed {initial_len - final_len} rows containing errors/missing values.")
    print(f"   -> Processing time: {time.time() - start_time:.2f} seconds.")
    return df


# --- 2. FUNCTION: PREPARE DATA ---
def prepare_data(df):
    print("\n[2/6] Splitting Train/Test sets...")

    # Convert label: "ad." -> 1, "nonad." -> 0
    df["label"] = df["label"].apply(lambda x: 1 if str(x).strip() == "ad." else 0)

    # Separate Features (X) and Target (y)
    X = df.drop("label", axis=1).values
    y = df["label"].values

    # Split data (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test


# --- 3. FUNCTION: TRAIN MODEL ---
def train_model(X_train, y_train):
    print("\n[3/6] Training Random Forest Classifier...")
    # n_estimators=100: Create 100 decision trees
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    return clf


# --- 4. FUNCTION: EVALUATE MODEL (CROSS-VALIDATION) ---
def evaluate_model(clf, X_train, y_train, X_test, y_test):
    print("\n[4/6] Evaluating model performance...")

    # 1. Score on Test Set
    score = clf.score(X_test, y_test)
    print(f"   -> Test Set Accuracy: {score * 100:.2f}%")

    # 2. Cross-Validation (5-Fold)
    print("   -> Running 5-Fold Cross-Validation...")
    cv_scores = cross_val_score(clf, X_train, y_train, cv=5)

    # 3. Create a DataFrame for the Cross-Validation Report
    table_data = []
    for i, s in enumerate(cv_scores):
        table_data.append({
            "Fold": f"Run {i + 1}",
            "Accuracy": s,
            "Formatted": f"{s * 100:.2f}%"
        })

    mean_score = cv_scores.mean()
    std_score = cv_scores.std()

    # Add Average row
    table_data.append({
        "Fold": "AVERAGE",
        "Accuracy": mean_score,
        "Formatted": f"{mean_score * 100:.2f}% (+/- {std_score * 100:.2f}%)"
    })

    df_cv_report = pd.DataFrame(table_data)

    # Print the table to console
    print("\n" + "=" * 40)
    print("CROSS-VALIDATION REPORT")
    print("=" * 40)
    print(df_cv_report[["Fold", "Formatted"]].to_string(index=False))
    print("=" * 40)

    # Export to CSV
    output_filename = "cross_validation_report.csv"
    df_cv_report.to_csv(output_filename, index=False)
    print(f"   -> Report exported to: '{output_filename}'")

    return cv_scores, mean_score, std_score


# --- 5. FUNCTION: GENERATE DETAILED REPORT ---
def detailed_report(clf, X_test, y_test):
    print("\n[5/6] Generating detailed classification report...")
    y_pred = clf.predict(X_test)

    print("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=["Non-Ad", "Ad"]))

    return y_pred


# --- 6. FUNCTION: VISUALIZE RESULTS ---
def visualize_results(clf, y_test, y_pred, cv_scores, cv_mean):
    print("\n[6/6] Visualizing results...")

    # Setup the figure with 2 subplots (Bar Chart + Confusion Matrix)
    plt.figure(figsize=(14, 6))

    # --- CHART 1: Cross-Validation Results ---
    plt.subplot(1, 2, 1)
    folds = [f"Run {i + 1}" for i in range(len(cv_scores))]
    bars = plt.bar(folds, cv_scores, color='#4e79a7', alpha=0.8)

    # Add mean line
    plt.axhline(cv_mean, color='red', linestyle='--', linewidth=2, label=f'Average: {cv_mean * 100:.2f}%')

    # Add text labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height * 100:.1f}%', ha='center', va='bottom')

    plt.ylim(0.8, 1.0)  # Zoom in Y-axis
    plt.ylabel('Accuracy')
    plt.title('Cross-Validation Scores (5-Folds)')
    plt.legend(loc='lower right')
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # --- CHART 2: Confusion Matrix ---
    plt.subplot(1, 2, 2)
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=["Non-Ad (Predicted)", "Ad (Predicted)"],
                yticklabels=["Non-Ad (Actual)", "Ad (Actual)"])
    plt.title('Confusion Matrix')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')

    plt.tight_layout()
    plt.show()

    # --- CHART 3: Feature Importance (Separate Figure) ---
    plt.figure(figsize=(10, 6))
    importances = clf.feature_importances_
    # Get Top 10 features
    indices = np.argsort(importances)[::-1][:10]

    plt.title("Top 10 Most Important Features")
    plt.bar(range(10), importances[indices], align="center", color='green')
    plt.xticks(range(10), indices)
    plt.xlabel("Feature Index")
    plt.ylabel("Importance Score")
    plt.tight_layout()
    plt.show()


# --- MAIN FUNCTION ---
def main():
    # 1. Load Data
    df = load_and_clean_data("ad.data")
    if df is None: return

    # 2. Prepare Data
    X_train, X_test, y_train, y_test = prepare_data(df)

    # 3. Train Model
    clf = train_model(X_train, y_train)

    # 4. Evaluate (Cross Validation & Export Table)
    cv_scores, cv_mean, cv_std = evaluate_model(clf, X_train, y_train, X_test, y_test)

    # 5. Detailed Report
    y_pred = detailed_report(clf, X_test, y_test)

    # 6. Visualize
    visualize_results(clf, y_test, y_pred, cv_scores, cv_mean)

    # 7. Save Model
    print("\nSaving model...")
    joblib.dump(clf, 'ad_blocker_model.joblib')
    print("--> COMPLETED! Model saved successfully.")


if __name__ == "__main__":
    main()