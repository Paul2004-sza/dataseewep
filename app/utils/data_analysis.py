import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import json


class DataAnalyzer:
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

    def get_summary_stats(self):
        return {
            'describe': self.df.describe().to_dict(),
            'dtypes': self.df.dtypes.astype(str).to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'shape': self.df.shape,
            'columns': list(self.df.columns)
        }

    def generate_visualizations(self, columns):
        visualizations = {}

        for col in columns:
            if col not in self.df.columns:
                continue

            # Determine plot type based on data type
            if np.issubdtype(self.df[col].dtype, np.number):
                # Numeric data - histogram and boxplot
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

                # Histogram
                sns.histplot(self.df[col], kde=True, ax=ax1)
                ax1.set_title(f'Histogram of {col}')

                # Boxplot
                sns.boxplot(y=self.df[col], ax=ax2)
                ax2.set_title(f'Boxplot of {col}')

                plt.tight_layout()

                # Save to base64
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                plt.close()
                visualizations[f'{col}_distribution'] = base64.b64encode(buf.getvalue()).decode('utf-8')

            else:
                # Categorical data - bar plot
                plt.figure(figsize=(10, 6))
                sns.countplot(y=self.df[col], order=self.df[col].value_counts().index)
                plt.title(f'Distribution of {col}')
                plt.tight_layout()

                # Save to base64
                buf = BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight')
                plt.close()
                visualizations[f'{col}_distribution'] = base64.b64encode(buf.getvalue()).decode('utf-8')

        # Correlation heatmap if multiple numeric columns
        numeric_cols = self.df.select_dtypes(include=np.number).columns
        if len(numeric_cols) > 1:
            plt.figure(figsize=(10, 8))
            sns.heatmap(self.df[numeric_cols].corr(), annot=True, cmap='coolwarm', center=0)
            plt.title('Correlation Heatmap')
            plt.tight_layout()

            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            plt.close()
            visualizations['correlation_heatmap'] = base64.b64encode(buf.getvalue()).decode('utf-8')

        return visualizations