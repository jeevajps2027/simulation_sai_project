
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import urllib.parse
from django.shortcuts import render
from  app.models import MeasurementData

def spc(request):
    # Fetch data from the database
    measurements = MeasurementData.objects.all()
    
    # Convert to DataFrame and filter out non-numeric values
    data = pd.DataFrame(list(measurements.values('date', 'comp_sr_no')))
    data['comp_sr_no'] = pd.to_numeric(data['comp_sr_no'], errors='coerce')  # Convert to numeric, coerce errors to NaN
    
    # Drop rows with NaN (if any)
    data = data.dropna()

    # Convert date string to datetime object
    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d', errors='coerce')  # Adjust format as per your actual date format
    
    # Drop rows with NaN dates (if any)
    data = data.dropna(subset=['date'])

    # Calculate control limits
    if not data.empty:
        mean = data['comp_sr_no'].mean()
        std = data['comp_sr_no'].std()
        ucl = mean + 3 * std
        lcl = mean - 3 * std
    else:
        mean = std = ucl = lcl = 0  # Handle case when there is no valid data
    
    # Create the control chart
    plt.figure(figsize=(10, 6))
    plt.plot(data['date'], data['comp_sr_no'], marker='o', linestyle='-', color='b', label='Measurement')
    plt.axhline(mean, color='g', linestyle='--', label='Mean')
    plt.axhline(ucl, color='r', linestyle='--', label='UCL (Upper Control Limit)')
    plt.axhline(lcl, color='r', linestyle='--', label='LCL (Lower Control Limit)')
    plt.fill_between(data['date'], lcl, ucl, color='r', alpha=0.1)

    plt.title('Control Chart')
    plt.xlabel('Date')
    plt.ylabel('Component Serial Number')
    plt.legend()
    plt.grid(True)

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return render(request, 'app/spc.html', {'chart': uri})
