import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import json


class MLPredictor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = self._load_data()

    def _load_data(self):
        if self.file_path.endswith('.csv'):
            return pd.read_csv(self.file_path)
        elif self.file_path.endswith('.xlsx'):
            return pd.read_excel(self.file_path)
        else:
            raise ValueError("Unsupported file format")

    def prepare_data(self, target_column, test_size=0.2, random_state=42):
        if target_column not in self.df.columns:
            raise ValueError(f"Target column {target_column} not found in data")

        # Drop rows with missing target values
        self.df = self.df.dropna(subset=[target_column])

        # Separate features and target
        X = self.df.drop(columns=[target_column])
        y = self.df[target_column]

        # Convert categorical variables to dummy variables
        X = pd.get_dummies(X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        return X_train, X_test, y_train, y_test

    def train_model(self, model_type, X_train, y_train, **kwargs):
        if model_type == 'linear_regression':
            model = LinearRegression(**kwargs)
        elif model_type == 'decision_tree':
            model = DecisionTreeRegressor(**kwargs)
        elif model_type == 'random_forest':
            model = RandomForestRegressor(**kwargs)
        elif model_type == 'xgboost':
            model = XGBRegressor(**kwargs)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        model.fit(X_train, y_train)
        return model

    def evaluate_model(self, model, X_test, y_test):
        y_pred = model.predict(X_test)

        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'r2': r2_score(y_test, y_pred)
        }

        return metrics, y_pred

    def generate_visualizations(self, model, X_test, y_test, y_pred, target_column):
        visualizations = {}

        # Actual vs Predicted plot
        plt.figure(figsize=(10, 6))
        plt.scatter(y_test, y_pred, alpha=0.5)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title(f'Actual vs Predicted {target_column}')

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        visualizations['actual_vs_predicted'] = base64.b64encode(buf.getvalue()).decode('utf-8')

        # Feature importance if available
        if hasattr(model, 'feature_importances_'):
            plt.figure(figsize=(10, 6))
            feature_imp = pd.Series(model.feature_importances_, index=X_test.columns)
            feature_imp.nlargest(10).plot(kind='barh')
            plt.title('Top 10 Feature Importance')

            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close()
            visualizations['feature_importance'] = base64.b64encode(buf.getvalue()).decode('utf-8')

        return visualizations