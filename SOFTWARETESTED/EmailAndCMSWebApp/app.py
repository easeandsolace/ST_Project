# his script is a Flask web application designed to accept CSV file uploads, process these files concurrently, and allow users to download the processed results. It demonstrates the integration of Flask for web handling, WTForms for form handling, Pandas for data manipulation, and Python's multiprocessing and threading modules for concurrent processing.

import os
import logging
import threading
import multiprocessing
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, send_file, url_for, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
import Email_and_cms

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOADED_DATA_DEST'] = 'uploads'

# Set up basic logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class UploadForm(FlaskForm):

    csv_file = FileField('CSV File', validators=[FileRequired(), FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Upload')

# Global variable to store the processing state
processing_done = False
output_filename = None

def process_file_and_update_progress(filename):
    try:
        global processing_done, output_filename
        logging.info(f"Processing file: {filename}")

        # Now let's process the file using your current script code
        # Split the DataFrame into smaller DataFrames, save them to CSV files, and store their names
        input_df = pd.read_csv(filename)
        urls_per_file = len(input_df) // multiprocessing.cpu_count() + 1
        input_file_names = []
        for i, group in input_df.groupby(np.arange(len(input_df)) // urls_per_file):
            file_name = f'input_file_{i}.csv'
            group.to_csv(file_name, index=False)
            input_file_names.append(file_name)

        # Process all files and get results
        results = []
        with multiprocessing.Pool() as pool:
            results = pool.map(Email_and_cms.process_csv_file, input_file_names)

        # Convert results into a DataFrame and save to CSV
        results_df = pd.concat(results, ignore_index=True)
        output_filename = 'merged_output.csv'
        results_df.to_csv(output_filename, index=False)

        # At this point, processing is complete so we set processing_done to True
        processing_done = True
        logging.info("Processing completed...")
    except Exception as e:
        logging.error(f'GLOBAL TRY-EXCEPT ERROR ; {e}')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    if form.validate_on_submit():
        csv_file = form.csv_file.data
        filename = os.path.join(app.config['UPLOADED_DATA_DEST'], csv_file.filename)
        csv_file.save(filename)

        logging.info(f"File saved to: {filename}")

        threading.Thread(target=process_file_and_update_progress, args=(filename,)).start()
        return redirect(url_for('progress'))
    return render_template('index.html', form=form)

@app.route('/progress')
def progress():
    return render_template('progress.html')

@app.route('/is_done')
def is_done():
    global processing_done
    return {'done': processing_done}

@app.route('/download')
def download():
    global output_filename
    if output_filename is not None:
        return send_file(output_filename, as_attachment=True)
    else:
        return {'error': 'No file to download'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
