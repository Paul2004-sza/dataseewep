from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime


class PDFGenerator:
    @staticmethod
    def generate_analysis_report(summary_stats, visualizations, output_path=None):
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    font-size: 10px;
                }}
                h1 {{
                    color: #2c3e50;
                }}
                h2 {{
                    color: #3498db;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 5px;
                }}
                .summary-grid {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }}
                .summary-card {{
                    flex: 1 1 48%;
                    border: 1px solid #ccc;
                    padding: 10px;
                    font-size: 9px;
                    margin-bottom: 10px;
                }}
                .summary-card table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .summary-card td {{
                    padding: 2px 5px;
                    border-bottom: 1px solid #eee;
                }}
                .section {{
                    margin-bottom: 30px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 6px;
                    text-align: left;
                    font-size: 9px;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 10px auto;
                }}
                .footer {{
                    margin-top: 50px;
                    font-size: 0.8em;
                    color: #7f8c8d;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <h1>Data Analysis Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="section">
                <h2>Dataset Summary</h2>
                <p><strong>Shape:</strong> {summary_stats['shape'][0]} rows × {summary_stats['shape'][1]} columns</p>
            </div>

            <div class="section">
                <h2>Summary Statistics</h2>
                <p><em>Showing performance.</em></p>
                <div class="summary-grid">
        """

        # Render each column's stats as a card
        for i, (col, stats) in enumerate(summary_stats['describe'].items()):
            if i >= 40:
                html_content += """
                    <div style="width: 100%; text-align:center; font-style:italic; margin-top: 10px;">
                        ... (remaining columns omitted for performance) ...
                    </div>
                """
                break
            html_content += f"""
                    <div class="summary-card">
                        <strong>{col}</strong>
                        <table>
                            <tr><td>Count</td><td>{stats.get('count', 'N/A')}</td></tr>
                            <tr><td>Mean</td><td>{stats.get('mean', 'N/A')}</td></tr>
                            <tr><td>Std</td><td>{stats.get('std', 'N/A')}</td></tr>
                            <tr><td>Min</td><td>{stats.get('min', 'N/A')}</td></tr>
                            <tr><td>25%</td><td>{stats.get('25%', 'N/A')}</td></tr>
                            <tr><td>50%</td><td>{stats.get('50%', 'N/A')}</td></tr>
                            <tr><td>75%</td><td>{stats.get('75%', 'N/A')}</td></tr>
                            <tr><td>Max</td><td>{stats.get('max', 'N/A')}</td></tr>
                        </table>
                    </div>
            """

        html_content += """
                </div>
            </div>

            <div class="section">
                <h2>Missing Values</h2>
                <table>
                    <tr>
                        <th>Column</th>
                        <th>Missing Values</th>
                    </tr>
        """

        # Add missing values
        for col, count in summary_stats['missing_values'].items():
            html_content += f"""
                    <tr>
                        <td>{col}</td>
                        <td>{count}</td>
                    </tr>
            """

        html_content += """
                </table>
            </div>

            <div class="section">
                <h2>Data Visualizations</h2>
        """

        # Add visualizations
        for name, img_data in visualizations.items():
            html_content += f"""
                <div>
                    <img src="data:image/png;base64,{img_data}" alt="{name}">
                </div>
            """

        html_content += """
            </div>

            <div class="footer">
                <p>Report generated by Data Analysis App</p>
            </div>
        </body>
        </html>
        """

        # Generate PDF
        pdf_bytes = BytesIO()
        pisa.CreatePDF(html_content, dest=pdf_bytes)

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes.getvalue())

        return pdf_bytes.getvalue()

    @staticmethod
    def generate_prediction_report(model_info, metrics, visualizations, output_path=None):
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prediction Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 20px;
                    table-layout: fixed;
                    word-wrap: break-word;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                    font-size: 10px;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                    max-width: 120px;
                }}
                th {{ background-color: #f2f2f2; }}
                img {{ max-width: 100%; height: auto; display: block; margin: 10px auto; }}
                .section {{ margin-bottom: 30px; }}
                .footer {{ margin-top: 50px; font-size: 0.8em; color: #7f8c8d; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>Prediction Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <div class="section">
                <h2>Model Information</h2>
                <table>
                    <tr>
                        <th>Model Type</th>
                        <td>{model_info['model_type']}</td>
                    </tr>
                    <tr>
                        <th>Target Column</th>
                        <td>{model_info['target_column']}</td>
                    </tr>
                    <tr>
                        <th>Training Date</th>
                        <td>{model_info['training_date']}</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>Model Metrics</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Mean Squared Error (MSE)</td>
                        <td>{metrics['mse']:.4f}</td>
                    </tr>
                    <tr>
                        <td>Root Mean Squared Error (RMSE)</td>
                        <td>{metrics['rmse']:.4f}</td>
                    </tr>
                    <tr>
                        <td>R-squared (R²)</td>
                        <td>{metrics['r2']:.4f}</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>Model Visualizations</h2>
        """

        # Add visualizations
        for name, img_data in visualizations.items():
            html_content += f"""
                <div>
                    <img src="data:image/png;base64,{img_data}" alt="{name}">
                </div>
            """

        html_content += """
            </div>

            <div class="footer">
                <p>Report generated by Data Analysis App</p>
            </div>
        </body>
        </html>
        """

        # Generate PDF
        pdf_bytes = BytesIO()
        pisa.CreatePDF(html_content, dest=pdf_bytes)

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes.getvalue())

        return pdf_bytes.getvalue()