import pandas as pd
import numpy as np

# Sample data (14 readings, 2 per subgroup, so total 7 groups)
data = {
    'X1': [15.003, 15.107, 15.152, 15.146, 15.147],
    'X2': [15.003, 15.107, 15.152, 15.146, 15.147],
    'X3': [14.913, 15.070, 15.107, 15.152, 15.146],
    'X4': [14.913, 15.070, 15.107, 15.152, 15.146],
    'X5': [15.003, 15.107, 15.152, 15.146, 15.147],
    'X6': [15.003, 15.107, 15.152, 15.146, 15.147],
    'X7': [15.003, 15.107, 15.152, 15.146, 15.147],
}

# Create DataFrame from the dictionary
df = pd.DataFrame(data)

# Step 1: Calculate X-bar (mean) and R (range) for each group
x_bar = df.mean(axis=0)  # Calculate mean for each column
r_bar = df.apply(np.ptp, axis=0)  # Range for each column (ptp - peak-to-peak)

# Step 2: Add Sum, X-bar, and R-bar as rows to the DataFrame
df.loc['Sum'] = df.sum()
df.loc['X̄ (Mean)'] = x_bar
df.loc['R̄ (Range)'] = r_bar

# Step 3: Overall X-bar and R-bar
overall_x_bar = x_bar.mean()
overall_r_bar = r_bar.mean()

# Add overall statistics as the last two rows
df['Overall X̄'] = [overall_x_bar] + [''] * (df.shape[0] - 1)
df['Overall R̄'] = [overall_r_bar] + [''] * (df.shape[0] - 1)

# Output the DataFrame as a table
print(df)
