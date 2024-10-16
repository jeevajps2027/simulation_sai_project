import plotly.graph_objs as go
import plotly.offline as pyo
from django.shortcuts import render
import numpy as np
import pandas as pd
from app.models import MeasurementData, X_Bar_R_Chart
from django.utils import timezone
from datetime import datetime
from django.db.models import Q

def calculate_control_limits(x_bars, ranges, sample_size):
    # Define constants for different sample sizes
    control_chart_constants = {
        2: {"A2": 1.880, "D3": 0, "D4": 3.267},
        3: {"A2": 1.023, "D3": 0, "D4": 2.574},
        4: {"A2": 0.729, "D3": 0, "D4": 2.282},
        5: {"A2": 0.577, "D3": 0, "D4": 2.114},
    }
    
    # Fetch the constants for the given sample size
    if sample_size not in control_chart_constants:
        raise ValueError(f"Sample size {sample_size} is not supported.")
    
    A2 = control_chart_constants[sample_size]["A2"]
    D3 = control_chart_constants[sample_size]["D3"]
    D4 = control_chart_constants[sample_size]["D4"]
    
    # Mean of X-bars and Ranges
    x_bar = np.mean(x_bars)
    r_bar = np.mean(ranges)

    # Control Limits for X-bar and Range
    UCLx = x_bar + A2 * r_bar
    LCLx = x_bar - A2 * r_bar
    UCLr = D4 * r_bar
    LCLr = D3 * r_bar

    return x_bar, r_bar, UCLx, LCLx, UCLr, LCLr

def calculate_cp_cpk(x_bars, usl, lsl):
    x_bar = np.mean(x_bars)
    sigma = np.std(x_bars, ddof=1)  # Standard deviation of the sample
    
    cp = (usl - lsl) / (6 * sigma)
    cpk = min((usl - x_bar) / (3 * sigma), (x_bar - lsl) / (3 * sigma))
    
    return cp, cpk
def xBarRchart(request): 
    if request.method == 'GET':
        # Fetch the x_bar_values and other fields
        x_bar_R_values = X_Bar_R_Chart.objects.all()
        part_model = X_Bar_R_Chart.objects.values_list('part_model', flat=True).distinct().get()

        fromDateStr = X_Bar_R_Chart.objects.values_list('formatted_from_date', flat=True).get()
        toDateStr = X_Bar_R_Chart.objects.values_list('formatted_to_date', flat=True).get()

        parameter_name = X_Bar_R_Chart.objects.values_list('parameter_name', flat=True).get()
        operator = X_Bar_R_Chart.objects.values_list('operator', flat=True).get()
        machine = X_Bar_R_Chart.objects.values_list('machine', flat=True).get()
        shift = X_Bar_R_Chart.objects.values_list('shift', flat=True).get()

        # Convert sample_size to an integer
        sample_size = int(X_Bar_R_Chart.objects.values_list('sample_size', flat=True).get())

        # Convert the date strings to datetime objects
        date_format_input = '%d-%m-%Y %I:%M:%S %p'
        from_datetime_naive = datetime.strptime(fromDateStr, date_format_input)
        to_datetime_naive = datetime.strptime(toDateStr, date_format_input)

        from_datetime = timezone.make_aware(from_datetime_naive, timezone.get_default_timezone())
        to_datetime = timezone.make_aware(to_datetime_naive, timezone.get_default_timezone())

        # Set up filter conditions
        filter_kwargs = {
            'date__range': (from_datetime, to_datetime),
            'part_model': part_model,
        }

        if parameter_name != "ALL":
            filter_kwargs['parameter_name'] = parameter_name

        if operator != "ALL":
            filter_kwargs['operator'] = operator

        if machine != "ALL":
            filter_kwargs['machine'] = machine

        if shift != "ALL":
            filter_kwargs['shift'] = shift

        # Fetch filtered data
        filtered_readings = list(MeasurementData.objects.filter(**filter_kwargs).values_list('readings', flat=True).order_by('id'))
        print("filtered_readings",filtered_readings)

        total_count = len(filtered_readings)
        print("Total readings count:", total_count)

          # Retrieve distinct usl and lsl values from MeasurementData
        usl_values = MeasurementData.objects.filter(**filter_kwargs).values_list('usl', flat=True).distinct()
        lsl_values = MeasurementData.objects.filter(**filter_kwargs).values_list('lsl', flat=True).distinct()

        # Convert the querysets to single values
        usl = usl_values.first() if usl_values else None
        lsl = lsl_values.first() if lsl_values else None

        print("usl",usl)
        print("lsl",lsl)

        # Divide readings into subgroups based on sample_size (converted to integer)
        subgroups = [filtered_readings[i:i + sample_size] for i in range(0, len(filtered_readings), sample_size)]
        subgroups_length = len(subgroups)
        print("sub group length:",subgroups_length)

        # Calculate X-bar and Range (R) for each subgroup
        x_bars = [np.mean(group) for group in subgroups]
        print("x_bars",x_bars)
        ranges = [max(group) - min(group) for group in subgroups]

        # Calculate control limits
        x_bar, r_bar, UCLx, LCLx, UCLr, LCLr = calculate_control_limits(x_bars, ranges, sample_size)
        cp, cpk = calculate_cp_cpk(x_bars, usl, lsl)

        # Print the calculated values in the terminal
        print(f"X-bar: {x_bar:.5f}, R-bar: {r_bar:.5f}")
        print(f"UCLx: {UCLx:.5f}, LCLx: {LCLx:.5f}")
        print(f"UCLr: {UCLr:.5f}, LCLr: {LCLr:.5f}")
        print(f"cp: {cp}, cpk: {cpk}")

      # Divide readings into subgroups based on sample_size (converted to integer)
        subgroups = [filtered_readings[i:i + sample_size] for i in range(0, len(filtered_readings), sample_size)]

        # Calculate X-bar and Range (R) for each subgroup
        x_bars = [np.mean(group) for group in subgroups]
        ranges = [max(group) - min(group) for group in subgroups]





        # Create a DataFrame for the readings
        df = pd.DataFrame(subgroups).transpose()  # Transpose to have rows for readings and columns for samples
       # Renaming columns to X1, X2, ..., X20 (or fewer if there are fewer subgroups)
        max_columns = 20
        df.columns = [f'X{i+1}' for i in range(min(len(df.columns), max_columns))]

        # If there are more than 20 columns, you may want to handle them appropriately
        if len(df.columns) > max_columns:
            print("Warning: More than 20 columns present. Additional columns will not be displayed.")


        # Calculate Sum, Mean, and Range
        df.loc['Sum'] = df.sum()


        df.loc['X̄ (Mean)'] = x_bars  # Use pre-calculated means
        df.loc['R̄ (Range)'] = ranges  # Use pre-calculated ranges

        # Create row labels dynamically
        row_labels = [f'Row {i+1}' for i in range(len(subgroups))] + ['Sum', 'X̄ (Mean)', 'R̄ (Range)']

        # Set the index to the created row labels
        if len(row_labels) == len(df.index):
            df.index = row_labels  # Set the index if lengths match
        else:
            print("Mismatch in length between row labels and DataFrame index.")
            

        # Convert the DataFrame to HTML for rendering in the template
        table_html = df.to_html(classes="table table-striped", index=True, header=True)

        # Inline CSS styles for table formatting
        style = """
        <style>
            table.table {
                font-size: 10px; /* Decrease font size */
                width: 100%; /* Set table width to fit the container */
                max-height : 20%;
            }
            table.table th, table.table td {
                padding: 2px; /* Adjust padding for smaller row height */
                max-width: 50px; /* Set a max column width */
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            table.table th {
                background-color: #f2f2f2; /* Optional: Light gray background for headers */
            }
        </style>
        """

        # Combine the style and table HTML
        table_html = style + table_html


        # Create X-bar chart
        xbar_trace = go.Scatter(
            x=list(range(1, len(x_bars) + 1)),
            y=x_bars,
            mode='lines+markers',
            name='X-bar'
        )

        # Add UCL and LCL lines to X-bar chart
        UCLx_trace = go.Scatter(x=list(range(1, len(x_bars) + 1)), y=[UCLx] * len(x_bars), mode='lines', name='UCLx', line=dict(color='red', dash='dash'))
        LCLx_trace = go.Scatter(x=list(range(1, len(x_bars) + 1)), y=[LCLx] * len(x_bars), mode='lines', name='LCLx', line=dict(color='red', dash='dash'))
        x_bar_trace = go.Scatter(x=list(range(1, len(x_bars) + 1)), y=[x_bar] * len(x_bars), mode='lines', name='X-bar Line', line=dict(color='green', width=2))

        # Create R chart
        r_trace = go.Scatter(
            x=list(range(1, len(ranges) + 1)),
            y=ranges,
            mode='lines+markers',
            name='Range (R)'
        )

        # Add UCL and LCL lines to R chart
        UCLr_trace = go.Scatter(x=list(range(1, len(ranges) + 1)), y=[UCLr] * len(ranges), mode='lines', name='UCLr', line=dict(color='blue', dash='dash'))
        LCLr_trace = go.Scatter(x=list(range(1, len(ranges) + 1)), y=[LCLr] * len(ranges), mode='lines', name='LCLr', line=dict(color='blue', dash='dash'))
        r_bar_trace = go.Scatter(x=list(range(1, len(ranges) + 1)), y=[r_bar] * len(ranges), mode='lines', name='R-bar Line', line=dict(color='purple', width=2))

        # Layout for X-bar chart with reduced height and minimal margins
        xbar_layout = go.Layout(
            title='X-bar Chart',
            xaxis=dict(title='Subgroup'),
            yaxis=dict(title='Value'),
            height=250,  # Set height to 250px to fit within 500px total
            margin=dict(l=40, r=20, t=40, b=40),  # Reduce margins to minimize white space
        )

        # Layout for R chart with reduced height and minimal margins
        r_layout = go.Layout(
            title='R Chart',
            xaxis=dict(title='Subgroup'),
            yaxis=dict(title='Value'),
            height=250,  # Set height to 250px to fit within 500px total
            margin=dict(l=40, r=20, t=40, b=40),  # Reduce margins to minimize white space
        )


        # Create the figures with the respective layouts and traces
        xbar_chart = go.Figure(data=[xbar_trace, UCLx_trace, LCLx_trace, x_bar_trace], layout=xbar_layout)
        r_chart = go.Figure(data=[r_trace, UCLr_trace, LCLr_trace, r_bar_trace], layout=r_layout)

        # Convert the charts to HTML
        xbar_chart_html = pyo.plot(xbar_chart, include_plotlyjs=False, output_type='div')
        r_chart_html = pyo.plot(r_chart, include_plotlyjs=False, output_type='div')

        # Pass the chart HTML and table HTML to the template
        context = {
            'xbar_chart': xbar_chart_html,
            'r_chart': r_chart_html,
            'table_html': table_html,  # Pass the Pandas table HTML
            'x_bar_R_values':x_bar_R_values,
            'subgroups_length': subgroups_length,
            'x_bar':x_bar,
            'r_bar':r_bar,
            'UCLx':UCLx,
            'LCLx':LCLx,
             'UCLr':UCLr,
            'LCLr':LCLr,
        }

    return render(request, 'app/spc/xBarRchart.html', context)


"""
1.df = pd.DataFrame(subgroups).transpose()  # Transpose to have rows for readings and columns for samples

        pd.DataFrame(subgroups): This creates a DataFrame from the list of subgroups. Each subgroup corresponds to a set of readings (e.g., a sample of data points).
        .transpose(): This method transposes the DataFrame, switching rows and columns. After this step, each row represents a sample (or reading) while each column represents a specific subgroup (e.g., X1, X2, ...).


2.df.columns = [f'X{i+1}' for i in range(len(df.columns))]  # Renaming columns to X1, X2, ...
        This line dynamically creates new column names for the DataFrame, assigning them labels like X1, X2, etc. This is useful for easily identifying each subgroup's data in the DataFrame.

"""