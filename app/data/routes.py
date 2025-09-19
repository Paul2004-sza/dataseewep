from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from app.data.models import DataFile, Analysis, Prediction
from app.utils.data_analysis import DataAnalyzer
from app.utils.ml_models import MLPredictor
from app.utils.pdf_generator import PDFGenerator
from app import db
import json
from io import BytesIO
import base64

data_bp = Blueprint('data', __name__, url_prefix='/data')


@data_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # Save file info to database
            data_file = DataFile(
                filename=filename,
                filepath=filepath,
                user_id=current_user.id
            )
            db.session.add(data_file)
            db.session.commit()

            flash('File successfully uploaded', 'success')
            return redirect(url_for('data.analyze', file_id=data_file.id))

    return render_template('data/upload.html')


@data_bp.route('/analyze/<int:file_id>', methods=['GET', 'POST'])
@login_required
def analyze(file_id):
    data_file = DataFile.query.get_or_404(file_id)

    if data_file.user_id != current_user.id:
        flash('You do not have permission to access this file', 'error')
        return redirect(url_for('main.home'))

    analyzer = DataAnalyzer(data_file.filepath)
    summary_stats = analyzer.get_summary_stats()

    if request.method == 'POST':
        selected_columns = request.form.getlist('columns')
        visualizations = analyzer.generate_visualizations(selected_columns)

        # Generate PDF preview
        pdf_bytes = PDFGenerator.generate_analysis_report(summary_stats, visualizations)

        # Save analysis to database
        analysis = Analysis(
            data_file_id=data_file.id,
            analysis_type='exploratory',
            parameters=json.dumps({'columns': selected_columns}),
            result_path=None  # We'll update this after saving the file
        )
        db.session.add(analysis)
        db.session.commit()

        # Save PDF to filesystem
        report_filename = f"analysis_report_{data_file.id}_{analysis.id}.pdf"
        report_path = os.path.join(current_app.config['UPLOAD_FOLDER'], report_filename)
        with open(report_path, 'wb') as f:
            f.write(pdf_bytes)

        # Update analysis record with report path
        analysis.result_path = report_path
        db.session.commit()

        return render_template('data/preview.html',
                               file_id=data_file.id,
                               analysis_id=analysis.id,
                               report_data=base64.b64encode(pdf_bytes).decode('utf-8'),
                               report_type='analysis')

    return render_template('data/analyze.html',
                           file_id=data_file.id,
                           columns=summary_stats['columns'],
                           summary_stats=summary_stats)


@data_bp.route('/predict/<int:file_id>', methods=['GET', 'POST'])
@login_required
def predict(file_id):
    data_file = DataFile.query.get_or_404(file_id)

    if data_file.user_id != current_user.id:
        flash('You do not have permission to access this file', 'error')
        return redirect(url_for('main.home'))

    analyzer = DataAnalyzer(data_file.filepath)
    summary_stats = analyzer.get_summary_stats()
    numeric_cols = [col for col, dtype in summary_stats['dtypes'].items() if 'float' in dtype or 'int' in dtype]

    if request.method == 'POST':
        target_column = request.form.get('target_column')
        model_type = request.form.get('model_type')

        # Prepare and train model
        ml_predictor = MLPredictor(data_file.filepath)
        X_train, X_test, y_train, y_test = ml_predictor.prepare_data(target_column)
        model = ml_predictor.train_model(model_type, X_train, y_train)
        metrics, y_pred = ml_predictor.evaluate_model(model, X_test, y_test)
        visualizations = ml_predictor.generate_visualizations(model, X_test, y_test, y_pred, target_column)

        # Generate PDF preview
        model_info = {
            'model_type': model_type,
            'target_column': target_column,
            'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        pdf_bytes = PDFGenerator.generate_prediction_report(model_info, metrics, visualizations)

        # Save prediction to database
        prediction = Prediction(
            data_file_id=data_file.id,
            model_type=model_type,
            target_column=target_column,
            parameters=json.dumps({'test_size': 0.2}),
            metrics=json.dumps(metrics),
            result_path=None  # We'll update this after saving the file
        )
        db.session.add(prediction)
        db.session.commit()

        # Save PDF to filesystem
        report_filename = f"prediction_report_{data_file.id}_{prediction.id}.pdf"
        report_path = os.path.join(current_app.config['UPLOAD_FOLDER'], report_filename)
        with open(report_path, 'wb') as f:
            f.write(pdf_bytes)

        # Update prediction record with report path
        prediction.result_path = report_path
        db.session.commit()

        return render_template('data/preview.html',
                               file_id=data_file.id,
                               prediction_id=prediction.id,
                               report_data=base64.b64encode(pdf_bytes).decode('utf-8'),
                               report_type='prediction')

    return render_template('data/predict.html',
                           file_id=data_file.id,
                           numeric_cols=numeric_cols)


@data_bp.route('/download/<report_type>/<int:report_id>')
@login_required
def download(report_type, report_id):
    if report_type == 'analysis':
        report = Analysis.query.get_or_404(report_id)
    elif report_type == 'prediction':
        report = Prediction.query.get_or_404(report_id)
    else:
        flash('Invalid report type', 'error')
        return redirect(url_for('main.home'))

    # Verify ownership
    if report.data_file.user_id != current_user.id:
        flash('You do not have permission to download this report', 'error')
        return redirect(url_for('main.home'))

    return send_file(report.result_path, as_attachment=True)


@data_bp.route('/dashboard')
@login_required
def dashboard():
    data_files = DataFile.query.filter_by(user_id=current_user.id).order_by(DataFile.uploaded_at.desc()).all()
    return render_template('data/dashboard.html', data_files=data_files)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

#adding
@data_bp.route('/view_file/<int:file_id>')
@login_required
def view_file(file_id):
    data_file = DataFile.query.get_or_404(file_id)

    if data_file.user_id != current_user.id:
        flash("You do not have permission to access this file", "error")
        return redirect(url_for('main.home'))

    return send_file(data_file.filepath)


@data_bp.route('/view_report/<report_type>/<int:report_id>')
@login_required
def view_report(report_type, report_id):
    if report_type == 'analysis':
        report = Analysis.query.get_or_404(report_id)
        template_type = 'analysis'
    elif report_type == 'prediction':
        report = Prediction.query.get_or_404(report_id)
        template_type = 'prediction'
    else:
        flash('Invalid report type', 'error')
        return redirect(url_for('main.home'))

    if report.data_file.user_id != current_user.id:
        flash("You do not have permission to access this report", "error")
        return redirect(url_for('main.home'))

    with open(report.result_path, 'rb') as f:
        pdf_bytes = f.read()

    return render_template('data/preview.html',
                           file_id=report.data_file.id,
                           report_type=template_type,
                           analysis_id=report.id if template_type == 'analysis' else None,
                           prediction_id=report.id if template_type == 'prediction' else None,
                           report_data=base64.b64encode(pdf_bytes).decode('utf-8'))
# Delete a data file and all its reports
@data_bp.route('/delete_file/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    data_file = DataFile.query.get_or_404(file_id)

    if data_file.user_id != current_user.id:
        flash("You do not have permission to delete this file", "error")
        return redirect(url_for('data.dashboard'))

    # Delete associated analyses
    for analysis in data_file.analyses:
        if analysis.result_path and os.path.exists(analysis.result_path):
            os.remove(analysis.result_path)
        db.session.delete(analysis)

    # Delete associated predictions
    for prediction in data_file.predictions:
        if prediction.result_path and os.path.exists(prediction.result_path):
            os.remove(prediction.result_path)
        db.session.delete(prediction)

    # Delete the file from filesystem
    if os.path.exists(data_file.filepath):
        os.remove(data_file.filepath)

    db.session.delete(data_file)
    db.session.commit()
    flash("File and associated reports deleted successfully", "success")
    return redirect(url_for('data.dashboard'))


# Delete a single report
@data_bp.route('/delete_report/<report_type>/<int:report_id>', methods=['POST'])
@login_required
def delete_report(report_type, report_id):
    if report_type == 'analysis':
        report = Analysis.query.get_or_404(report_id)
    elif report_type == 'prediction':
        report = Prediction.query.get_or_404(report_id)
    else:
        flash("Invalid report type", "error")
        return redirect(url_for('data.dashboard'))

    if report.data_file.user_id != current_user.id:
        flash("You do not have permission to delete this report", "error")
        return redirect(url_for('data.dashboard'))

    if report.result_path and os.path.exists(report.result_path):
        os.remove(report.result_path)

    db.session.delete(report)
    db.session.commit()
    flash("Report deleted successfully", "success")
    return redirect(url_for('data.dashboard'))
