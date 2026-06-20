# ===============================
# 1. Import Libraries
# ===============================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# ===============================
# 2. Load Dataset
# ===============================
df = pd.read_csv("diabetes_dataset.csv")

print("First 5 rows:\n", df.head())
print("\nDataset Info:\n", df.info())

# ===============================
# 3. Preprocessing
# ===============================

# Drop unnecessary columns
df = df.drop(['location', 'year'], axis=1)

# Encode categorical columns
le = LabelEncoder()
df['gender'] = le.fit_transform(df['gender'])
df['smoking_history'] = le.fit_transform(df['smoking_history'])

# ===============================
# 4. Feature Engineering (BMI Category)
# ===============================
def bmi_category(bmi):
    if bmi < 18.5:
        return 0   # Underweight
    elif bmi < 25:
        return 1   # Normal
    elif bmi < 30:
        return 2   # Overweight
    else:
        return 3   # Obese

df['bmi_category'] = df['bmi'].apply(bmi_category)

# ===============================
# 5. Feature Selection
# ===============================
X = df.drop("diabetes", axis=1)
y = df["diabetes"]

# ===============================
# 6. Train-Test Split
# ===============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ===============================
# 7. Feature Scaling
# ===============================
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# ===============================
# 8. Logistic Regression
# ===============================
lr_model = LogisticRegression(max_iter=1000)
lr_model.fit(X_train, y_train)

lr_pred = lr_model.predict(X_test)
lr_acc = accuracy_score(y_test, lr_pred)

print("\nLogistic Regression Accuracy:", lr_acc)
print(classification_report(y_test, lr_pred))

# ===============================
# 9. Decision Tree
# ===============================
dt_model = DecisionTreeClassifier(random_state=42)
dt_model.fit(X_train, y_train)

dt_pred = dt_model.predict(X_test)
dt_acc = accuracy_score(y_test, dt_pred)

print("\nDecision Tree Accuracy:", dt_acc)

# ===============================
# 10. Random Forest
# ===============================
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

rf_pred = rf_model.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)

print("\nRandom Forest Accuracy:", rf_acc)

# ===============================
# 11. Model Comparison
# ===============================
print("\n--- Model Comparison ---")
print("Logistic Regression:", lr_acc)
print("Decision Tree:", dt_acc)
print("Random Forest:", rf_acc)

# ===============================
# 12. Confusion Matrices
# ===============================
cm_lr = confusion_matrix(y_test, lr_pred)
cm_dt = confusion_matrix(y_test, dt_pred)
cm_rf = confusion_matrix(y_test, rf_pred)

print("\nLogistic Regression CM:\n", cm_lr)
print("\nDecision Tree CM:\n", cm_dt)
print("\nRandom Forest CM:\n", cm_rf)

# ===============================
# 13. Visualization
# ===============================
plt.figure(figsize=(15,4))

# LR
plt.subplot(1,3,1)
sns.heatmap(cm_lr, annot=True, fmt='d')
plt.title("Logistic Regression")

# DT
plt.subplot(1,3,2)
sns.heatmap(cm_dt, annot=True, fmt='d')
plt.title("Decision Tree")

# RF
plt.subplot(1,3,3)
sns.heatmap(cm_rf, annot=True, fmt='d')
plt.title("Random Forest")

plt.show()

# ===============================
# 14. Feature Importance (Logistic Regression)
# ===============================
coeff = pd.DataFrame({
    "Feature": X.columns,
    "Coefficient": lr_model.coef_[0]
})

print("\nFeature Importance:\n", coeff.sort_values(by="Coefficient", ascending=False))
