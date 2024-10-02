from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
from scipy.stats import kurtosis
import os

app = Flask(__name__)

# Function to calculate LSD (Least Significant Difference) at 0.05 confidence level
def calculate_lsd(trait_data):
    return 1.96 * trait_data.std() / np.sqrt(len(trait_data))

# Function to calculate standard error
def calculate_se(trait_data):
    return trait_data.std() / np.sqrt(len(trait_data))

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle CSV upload and calculate statistics
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    # Save the file to the server
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    # Load the CSV file and perform calculations
    data = pd.read_csv(file_path)
    results_list = []  # Create an empty list to store results

    # Loop through each trait column and calculate statistics
    for column in data.columns[1:]:  # Exclude 'Genotype' column
        trait_data = data[column]
        mean_val = trait_data.mean()
        se_val = calculate_se(trait_data)
        min_val = trait_data.min()
        max_val = trait_data.max()
        cv_val = (trait_data.std() / mean_val) * 100  # Coefficient of variation
        kurt_val = kurtosis(trait_data, fisher=True)  # Fisher's definition of kurtosis
        lsd_val = calculate_lsd(trait_data)
        
        # Append each result as a dictionary
        results_list.append({
            'Trait': column,
            'Mean': mean_val,
            'Std Error': se_val,
            'Min': min_val,
            'Max': max_val,
            'CV%': cv_val,
            'Kurtosis': kurt_val,
            'LSD (0.05)': lsd_val
        })

    # Convert the list of dictionaries to a DataFrame
    results = pd.DataFrame(results_list)

    # Save the results to a new CSV file
    results_file = os.path.join('uploads', 'statistical_results.csv')
    results.to_csv(results_file, index=False)

    return redirect(url_for('download_file', filename='statistical_results.csv'))

# Route to download the resulting CSV file
@app.route('/download/<filename>')
def download_file(filename):
    return redirect(url_for('static', filename=f'uploads/{filename}'))

if __name__ == '__main__':
    # Create an uploads folder if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
