import numpy as np
import matplotlib.pyplot as plt

# Step 1: Generate 500 random values between 0 and 500
# (You can replace this with your actual data)
data = np.random.randint(0, 500, 500)

# Step 2: Define the bin edges (0-19, 20-39, ..., 480-499)
bins = np.arange(0, 500, 20)

# Step 3: Plot the histogram
plt.hist(data, bins=bins, edgecolor='black')

# Step 4: Add titles and labels
plt.title("Histogram of Data with Bin Size of 20")
plt.xlabel("Value")
plt.ylabel("Frequency")

# Step 5: Show the plot
plt.show()
