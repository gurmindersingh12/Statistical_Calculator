from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import pandas as pd
import numpy as np
from scipy.stats import kurtosis, t
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import os

app = Flask(__name__)

# Function to calculate LSD (Least Significant Difference) using ANOVA
def calculate_lsd_anova(data, trait, alpha=0.05):
    # Perform ANOVA with trait as the response, ENV and REP as factors
    model = ols(f'{trait} ~ C(ENV) + C(REP)', data=data).fit()
    anova_table = anova_lm(model)
    
    # Extract MSE (Mean Square Error) and degrees of freedom for error
    mse = anova_table['mean_sq'][-1]  # Last row in ANOVA table is the residual/error
    df_error = anova_table['df'][-1]
    
    # Calculate t-critical value for the given confidence level
    t_critical = t.ppf(1 - alpha / 2, df_error)
    
    # LSD calculation
    lsd = t_critical * np.sqrt(2 * mse / data['TRT'].nunique())  # TRT is treatment count per ENV
    return lsd, mse, df_error, t_critical  # Return additional values for table

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
    file_path = os.path.join('static/uploads', file.filename)
    file.save(file_path)

    # Load the CSV file and perform calculations
    data = pd.read_csv(file_path)
    results_list = []  # Create an empty list to store results

    # Loop through each environment and calculate statistics for each trait
    for env, env_data in data.groupby('ENV'):
        for column in ['DTH', 'GFD', 'PHT', 'TNS', 'TGW', 'KA', 'KW', 'KL', 'KC', 'KLW', 'KPS', 'GWS']:
            # Convert column to numeric, forcing non-numeric values to NaN, and drop NaN values
            trait_data = pd.to_numeric(env_data[column], errors='coerce').dropna()
            
            if len(trait_data) == 0:
                # Skip if no valid data points in the column
                continue

            # Calculate basic statistics
            mean_val = trait_data.mean()
            sd_val = trait_data.std()
            n_val = len(trait_data)
            se_val = calculate_se(trait_data)
            min_val = trait_data.min()
            max_val = trait_data.max()
            cv_val = (sd_val / mean_val) * 100 if mean_val != 0 else None  # Avoid division by zero
            kurt_val = kurtosis(trait_data, fisher=True)  # Fisher's definition of kurtosis

            # Calculate LSD using ANOVA
            lsd_val, mse_val, df_error, t_critical = calculate_lsd_anova(env_data, column)
            
            # Append each result as a dictionary
            results_list.append({
                'Environment': env,
                'Trait': column,
                'Mean': mean_val,
                'Standard Deviation (SD)': sd_val,
                'Sample Size (n)': n_val,
                'Standard Error (SE)': se_val,
                'Min': min_val,
                'Max': max_val,
                'CV%': cv_val,
                'Kurtosis': kurt_val,
                'MSE': mse_val,
                'Degrees of Freedom (df)': df_error,
                't-Critical Value': t_critical,
                'LSD (0.05)': lsd_val
            })

    # Convert the list of dictionaries to a DataFrame
    results = pd.DataFrame(results_list)

    # Save the results to a new CSV file in the static/uploads directory
    results_file = os.path.join('static/uploads', 'detailed_statistical_results.csv')
    results.to_csv(results_file, index=False)

    return redirect(url_for('download_file', filename='detailed_statistical_results.csv'))

# Route to download the resulting CSV file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('static/uploads', filename)

if __name__ == '__main__':
    # Create an uploads folder inside static if it doesn't exist
    if not os.path.exists('static/uploads'):
        os.makedirs('static/uploads')
    app.run(debug=True)
