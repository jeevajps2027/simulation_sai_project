import plotly.graph_objs as go
import plotly.offline as pyo
from django.shortcuts import render
import numpy as np
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


def xBarRchart(request): 
    if request.method == 'GET':
        # Fetch the x_bar_values and other fields
        x_bar_values = X_Bar_R_Chart.objects.all()
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

        total_count = len(filtered_readings)
        print("Total readings count:", total_count)

        # Divide readings into subgroups based on sample_size (converted to integer)
        subgroups = [filtered_readings[i:i + sample_size] for i in range(0, len(filtered_readings), sample_size)]

        # Calculate X-bar and Range (R) for each subgroup
        x_bars = [np.mean(group) for group in subgroups]
        ranges = [max(group) - min(group) for group in subgroups]

        # Calculate control limits
        x_bar, r_bar, UCLx, LCLx, UCLr, LCLr = calculate_control_limits(x_bars, ranges, sample_size)

        # Print the calculated values in the terminal
        print(f"X-bar: {x_bar}, R-bar: {r_bar}")
        print(f"UCLx: {UCLx}, LCLx: {LCLx}")
        print(f"UCLr: {UCLr}, LCLr: {LCLr}")

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

        # Layout for X-bar and R charts
        layout = go.Layout(title='X-bar and R Chart', xaxis=dict(title='Subgroup'), yaxis=dict(title='Value'))

        # Combine traces for both charts
        xbar_chart = go.Figure(data=[xbar_trace, UCLx_trace, LCLx_trace], layout=layout)
        r_chart = go.Figure(data=[r_trace, UCLr_trace, LCLr_trace], layout=layout)

        # Convert the charts to HTML
        xbar_chart_html = pyo.plot(xbar_chart, include_plotlyjs=False, output_type='div')
        r_chart_html = pyo.plot(r_chart, include_plotlyjs=False, output_type='div')

        # Pass the chart HTML to the template
        context = {
            'xbar_chart': xbar_chart_html,
            'r_chart': r_chart_html
        }

    return render(request, 'app/spc/xBarRchart.html', context)

