import pandas as pd
import numpy as np
from scipy.stats import kurtosis

# Function to calculate LSD (Least Significant Difference) at 0.05 confidence level
def calculate_lsd(trait_data):
    return 1.96 * trait_data.std() / np.sqrt(len(trait_data))

# Function to calculate standard error
def calculate_se(trait_data):
    return trait_data.std() / np.sqrt(len(trait_data))

# Load the CSV file
file_path = 'Your_File.csv'  # Replace this with your CSV file path
data = pd.read_csv(file_path)

# Prepare a DataFrame for storing results
results = pd.DataFrame(columns=['Trait', 'Mean', 'Std Error', 'Min', 'Max', 'CV%', 'Kurtosis', 'LSD (0.05)'])

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
    
    # Append results to the DataFrame
    results = results.append({
        'Trait': column,
        'Mean': mean_val,
        'Std Error': se_val,
        'Min': min_val,
        'Max': max_val,
        'CV%': cv_val,
        'Kurtosis': kurt_val,
        'LSD (0.05)': lsd_val
    }, ignore_index=True)

# Save results to a new CSV file
results.to_csv('statistical_results.csv', index=False)
print("Statistics calculated and saved to 'statistical_results.csv'")
