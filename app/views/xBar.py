
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render
import numpy as np

def xBar(request):
    # Data points
    data = [14.9833, 15.0017, 15.00, 15.02, 15.0017, 14.999]
    
    # Control limits and nominal values
    nominal = 15.00
    usl = 15.01  # Upper Specification Limit (USL)
    lsl = 14.99  # Lower Specification Limit (LSL)
    
    # Calculate the average (mean) of the data
    x_bar = np.mean(data)
    
    # Generate the X-bar chart
    plt.figure(figsize=(10, 6))
    plt.plot(data, marker='o', color='blue', linestyle='-', label='Data')
    
    # Plot control limits and nominal value
    plt.axhline(y=usl, color='red', linestyle='--', label='USL (15.01)')
    plt.axhline(y=lsl, color='red', linestyle='--', label='LSL (14.99)')
    plt.axhline(y=nominal, color='green', linestyle='-', label='Nominal (15.00)')
    plt.axhline(y=x_bar, color='purple', linestyle='-', label=f'X-bar (Mean: {x_bar:.5f})')
    
    # Labeling the chart
    plt.title('X-bar Control Chart')
    plt.xlabel('Sample Number')
    plt.ylabel('Measurement')
    plt.legend(loc='upper right')
    
    # Save the plot to a bytes buffer instead of a file
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Encode the image to base64 so that it can be embedded in the HTML
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)
    
    # Pass the image URI to the template
    context = {'chart': uri}
    return render(request, 'app/spc/xBar.html', context)
