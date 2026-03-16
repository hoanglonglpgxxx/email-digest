import argparse
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

    df["label"] = df["label"].apply(lambda x: 1 if str(x).strip() == "ad." else 0)

    X = df.drop("label", axis=1).values
    y = df["label"].values

    # ✅ Giữ đúng như sách: default 75/25, không set random_state
    X_train, X_test, y_train, y_test = train_test_split(X, y)

    return X_train, X_test, y_train, y_test


# --- 3. FUNCTION: TRAIN MODEL ---
def train_model(X_train, y_train):
    print("\n[3/6] Training Random Forest Classifier...")

    # ✅ Giữ đúng như sách: không set n_estimators, không set random_state
    clf = RandomForestClassifier()
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


# --- DEMO RUNNER HELPERS ---
def run_pipeline(data_path="ad.data", do_visualize=True, do_save=True):
    """Run the full pipeline and return key artifacts for demo narration."""
    df = load_and_clean_data(data_path)
    if df is None:
        return None

    X_train, X_test, y_train, y_test = prepare_data(df)
    clf = train_model(X_train, y_train)
    cv_scores, cv_mean, cv_std = evaluate_model(clf, X_train, y_train, X_test, y_test)
    y_pred = detailed_report(clf, X_test, y_test)

    if do_visualize:
        visualize_results(clf, y_test, y_pred, cv_scores, cv_mean)

    if do_save:
        print("\nSaving model...")
        joblib.dump(clf, "original_dataset.joblib")
        print("--> COMPLETED! Model saved successfully.")

    return {
        "df": df,
        "clf": clf,
        "cv_scores": cv_scores,
        "cv_mean": cv_mean,
        "cv_std": cv_std,
        "y_pred": y_pred,
        "X_test": X_test,
        "y_test": y_test,
    }


def run_selected_steps(steps, data_path="ad.data", do_visualize=True, do_save=True):
    """Execute only the requested steps in order, useful for live demos."""
    ctx = {}

    for step in steps:
        if step == "load":
            ctx["df"] = load_and_clean_data(data_path)
            if ctx["df"] is None:
                return None
        elif step == "prepare":
            if "df" not in ctx:
                ctx["df"] = load_and_clean_data(data_path)
            ctx["X_train"], ctx["X_test"], ctx["y_train"], ctx["y_test"] = prepare_data(ctx["df"])
        elif step == "train":
            if "X_train" not in ctx:
                raise ValueError("Call prepare before train")
            ctx["clf"] = train_model(ctx["X_train"], ctx["y_train"])
        elif step == "evaluate":
            if "clf" not in ctx:
                raise ValueError("Call train before evaluate")
            ctx["cv_scores"], ctx["cv_mean"], ctx["cv_std"] = evaluate_model(
                ctx["clf"], ctx["X_train"], ctx["y_train"], ctx["X_test"], ctx["y_test"]
            )
        elif step == "report":
            if "clf" not in ctx or "X_test" not in ctx:
                raise ValueError("Call prepare/train before report")
            ctx["y_pred"] = detailed_report(ctx["clf"], ctx["X_test"], ctx["y_test"])
        elif step == "visualize":
            if "y_pred" not in ctx:
                raise ValueError("Call report before visualize")
            if do_visualize:
                visualize_results(ctx["clf"], ctx["y_test"], ctx["y_pred"], ctx["cv_scores"], ctx["cv_mean"])
        elif step == "save":
            if "clf" not in ctx:
                raise ValueError("Call train before save")
            if do_save:
                print("\nSaving model...")
                joblib.dump(ctx["clf"], "original_dataset.joblib")
                print("--> COMPLETED! Model saved successfully.")
        else:
            raise ValueError(f"Unknown step: {step}")

    return ctx


def parse_args():
    parser = argparse.ArgumentParser(description="Adblocker Random Forest demo runner")
    parser.add_argument("--data-path", default="ad.data", help="Path to dataset (default: ad.data in current folder)")
    parser.add_argument("--steps", nargs="+", default=["load", "prepare", "train", "evaluate", "report", "visualize", "save"],
                        choices=["load", "prepare", "train", "evaluate", "report", "visualize", "save"],
                        help="Ordered list of steps to run (default: full pipeline)")
    parser.add_argument("--no-visualize", action="store_true", help="Skip plotting (useful for headless runs)")
    parser.add_argument("--no-save", action="store_true", help="Skip saving the joblib model")
    return parser.parse_args()


def main():
    args = parse_args()
    run_selected_steps(
        steps=args.steps,
        data_path=args.data_path,
        do_visualize=not args.no_visualize,
        do_save=not args.no_save,
    )


if __name__ == "__main__":
    main()