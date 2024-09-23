import numpy as np
import matplotlib.pyplot as plt
import io
import urllib, base64
from django.shortcuts import render

def xBarRchart(request):
    # Data points
    data = [
        [14.9833, 15.0017],
        [15.00, 15.02],
        [15.0017, 14.999]
    ]  # Grouped into subgroups of 2

    # Control limits and nominal values
    nominal = 15.00
    usl = 15.01  # Upper Specification Limit
    lsl = 14.99  # Lower Specification Limit

    # Calculate X-bar (average of each subgroup)
    x_bars = [np.mean(group) for group in data]

    # Calculate R (range of each subgroup)
    ranges = [np.max(group) - np.min(group) for group in data]

    # Calculate the overall average for X-bar and R
    x_bar_overall = np.mean(x_bars)
    r_overall = np.mean(ranges)

    # Generate X-bar chart
    plt.figure(figsize=(10, 6))
    
    # Plot X-bar chart
    plt.subplot(2, 1, 1)
    plt.plot(x_bars, marker='o', color='blue', linestyle='-', label='X-bar (Means)')
    plt.axhline(y=usl, color='red', linestyle='--', label='USL (15.01)')
    plt.axhline(y=lsl, color='red', linestyle='--', label='LSL (14.99)')
    plt.axhline(y=nominal, color='green', linestyle='-', label='Nominal (15.00)')
    plt.axhline(y=x_bar_overall, color='purple', linestyle='-', label=f'X-bar Overall Mean: {x_bar_overall:.5f}')
    plt.title('X-bar Chart')
    plt.ylabel('X-bar')
    plt.legend(loc='upper right')
    plt.grid(True)

    # Plot R (Range) chart
    plt.subplot(2, 1, 2)
    plt.plot(ranges, marker='o', color='blue', linestyle='-', label='Range (R)')
    plt.axhline(y=r_overall, color='purple', linestyle='-', label=f'R Overall Mean: {r_overall:.5f}')
    plt.title('R (Range) Chart')
    plt.xlabel('Subgroup')
    plt.ylabel('Range (R)')
    plt.legend(loc='upper right')
    plt.grid(True)

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Encode the image to base64
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    # Pass the image to the template
    context = {'chart': uri}
    return render(request, 'app/spc/xBarRchart.html', context)
