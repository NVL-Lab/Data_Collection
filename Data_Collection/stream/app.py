# import pandas as pd
# import os
# import subprocess
# import requests
# from flask import Flask, render_template, request, redirect, url_for, jsonify

# app = Flask(__name__)
# # Define the upload folder path
# UPLOAD_FOLDER = 'uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # Function to start a script with its full path
# def run_script(script_path):
#     try:
#         process = subprocess.Popen(['python3', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         stdout, stderr = process.communicate()
#         if stderr:
#             return {"error": stderr.decode('utf-8')}
#         return {"output": stdout.decode('utf-8')}
#     except Exception as e:
#         return {"error": str(e)}

# # Endpoint to start the full experiment (run both camera and coordinates)
# @app.route('/run_tests', methods=['GET'])
# def run_tests():
#     linux_server_ip = 'http://192.168.1.18:3000/start_experiment'
#     message = ""
#     camera_output = ""
#     coordinates_output = ""
    
#     try:
#         # Send request to the Linux server to start the experiment
#         response = requests.get(linux_server_ip)

#         if response.status_code == 200:
#             message = response.json().get("message", "Experiment started successfully.")
#             camera_output = response.json().get("camera_output", "No camera output available.")
#             coordinates_output = response.json().get("coordinates_output", "No coordinates output available.")
#         else:
#             message = f"Error: {response.status_code}, {response.json()}"

#     except Exception as e:
#         message = f"Failed to connect to the Linux server: {e}"

#     return render_template('run_results.html', message=message, camera_output=camera_output, coordinates_output=coordinates_output)

# # Route for the main page
# @app.route('/')
# def index():
#     return render_template('index.html')

# # Dummy route for "Show Results" button
# @app.route('/show_results', methods=['GET', 'POST'])
# def show_results():
#     table_data = None
#     has_data = False  # A flag to indicate if valid data is present

#     if request.method == 'POST':
#         # Check if a file is uploaded
#         if 'file' not in request.files:
#             return render_template('show_results.html', table_data=None, has_data=has_data)

#         file = request.files['file']

#         if file.filename == '':
#             return render_template('show_results.html', table_data=None, has_data=has_data)

#         # Save the uploaded file
#         if file and file.filename.endswith('.parquet'):
#             file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#             file.save(file_path)

#             # Read the parquet file using pandas
#             try:
#                 df = pd.read_parquet(file_path)
#                 table_data = df
#                 has_data = not df.empty  # Update the flag if the DataFrame is not empty
#             except Exception as e:
#                 print(f"Error reading the parquet file: {e}")
#                 table_data = None
#                 has_data = False

#     return render_template('show_results.html', table_data=table_data, has_data=has_data)

# # Placeholder route for "Upload Files"
# @app.route('/upload')
# def upload():
#     return "<h2>Upload Page - Placeholder</h2>"

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=3001)

from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
import requests
import pandas as pd

app = Flask(__name__)

# Define the upload folder path
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to start a script with its full path
def run_script(script_path):
    try:
        process = subprocess.Popen(['python3', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            return {"error": stderr.decode('utf-8')}
        return {"output": stdout.decode('utf-8')}
    except Exception as e:
        return {"error": str(e)}

# Endpoint to start the full experiment (run both camera and coordinates)
@app.route('/run_tests', methods=['GET'])
def run_tests():
    linux_server_ip = 'http://172.24.51.182:3000/start_experiment'
    message = ""
    camera_output = ""
    coordinates_output = ""

    try:
        # Send request to the Linux server to start the experiment
        response = requests.get(linux_server_ip)

        if response.status_code == 200:
            message = response.json().get("message", "Experiment started successfully.")
            # Ensure that camera_output and coordinates_output are strings
            camera_output = response.json().get("camera_output", {})
            coordinates_output = response.json().get("coordinates_output", {})
            
            # Convert outputs to strings if they are dictionaries (to avoid 'split' errors in Jinja2)
            if isinstance(camera_output, dict):
                camera_output = str(camera_output)
            if isinstance(coordinates_output, dict):
                coordinates_output = str(coordinates_output)

        else:
            message = f"Error: {response.status_code}, {response.json()}"

    except Exception as e:
        message = f"Failed to connect to the Linux server: {e}"

    return render_template('run_results.html', message=message, camera_output=camera_output, coordinates_output=coordinates_output)
# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Handle the results display and user interaction
@app.route('/run_results', methods=['GET', 'POST'])
def run_results():
    if request.method == 'POST':
        if request.form['continue'] == 'no':
            return redirect(url_for('index'))  # Redirect to the main page if 'No'
        elif request.form['continue'] == 'yes':
            return redirect(url_for('index'))  # Or implement a way to restart the stream

    # When accessed via GET, show the results
    message = request.args.get('message', '')
    camera_output = request.args.get('camera_output', '')
    coordinates_output = request.args.get('coordinates_output', '')
    
    return render_template('run_results.html', message=message, camera_output=camera_output, coordinates_output=coordinates_output)

# Dummy route for "Show Results" button
@app.route('/show_results', methods=['GET', 'POST'])
def show_results():
    table_data = None
    has_data = False  # A flag to indicate if valid data is present

    if request.method == 'POST':
        # Check if a file is uploaded
        if 'file' not in request.files:
            return render_template('show_results.html', table_data=None, has_data=has_data)

        file = request.files['file']

        if file.filename == '':
            return render_template('show_results.html', table_data=None, has_data=has_data)

        # Save the uploaded file
        if file and file.filename.endswith('.parquet'):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Read the parquet file using pandas
            try:
                df = pd.read_parquet(file_path)
                table_data = df
                has_data = not df.empty  # Update the flag if the DataFrame is not empty
            except Exception as e:
                print(f"Error reading the parquet file: {e}")
                table_data = None
                has_data = False

    return render_template('show_results.html', table_data=table_data, has_data=has_data)

# Placeholder route for "Upload Files"
@app.route('/upload')
def upload():
    return "<h2>Upload Page - Placeholder</h2>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001)
