import plotly.graph_objs as go
import plotly.offline as pyo
from django.shortcuts import render
import numpy as np
from app.models import MeasurementData, X_Bar_Chart
from django.utils import timezone
from datetime import datetime
from django.db.models import Q

def xBar(request):
    if request.method == 'GET':
        # Fetch the x_bar_values and other fields
        x_bar_values = X_Bar_Chart.objects.all()
        part_model = X_Bar_Chart.objects.values_list('part_model', flat=True).distinct().get()

        fromDateStr = X_Bar_Chart.objects.values_list('formatted_from_date', flat=True).get()
        toDateStr = X_Bar_Chart.objects.values_list('formatted_to_date', flat=True).get()

        parameter_name = X_Bar_Chart.objects.values_list('parameter_name', flat=True).get()
        operator = X_Bar_Chart.objects.values_list('operator', flat=True).get()
        machine = X_Bar_Chart.objects.values_list('machine', flat=True).get()
        shift = X_Bar_Chart.objects.values_list('shift', flat=True).get()

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
        filtered_data = MeasurementData.objects.filter(**filter_kwargs).values_list(
            'readings', 'usl', 'lsl', 'nominal', 'ltl', 'utl').order_by('id')

        filtered_readings = MeasurementData.objects.filter(**filter_kwargs).values_list('readings', flat=True).order_by('id')

        total_count = len(filtered_readings)
        print("total_count",total_count)

        # Extract data for plotting
        readings = [float(r) for r in filtered_readings]  # Convert readings to floats

        # Extract limits and nominal values
        usl = filtered_data[0][1] if filtered_data else None  # Upper Spec Limit
        lsl = filtered_data[0][2] if filtered_data else None  # Lower Spec Limit
        nominal = filtered_data[0][3] if filtered_data else None  # Nominal value
        ltl = filtered_data[0][4] if filtered_data else None  # Lower Tolerance Limit
        utl = filtered_data[0][5] if filtered_data else None  # Upper Tolerance Limit

        if readings and usl and lsl and nominal and ltl and utl:
            # Calculate X-bar (mean)
            x_bar = np.mean(readings)

            # Create the X-bar chart using Plotly
            trace_readings = go.Scatter(
                x=list(range(len(readings))),
                y=readings,
                mode='lines+markers',
                name='Readings',
                marker=dict(color='blue'),
                text=[f'Reading: {r}' for r in readings],  # Tooltip text for each point
                hoverinfo='text'
            )

            trace_usl = go.Scatter(
                x=list(range(len(readings))),
                y=[usl] * len(readings),
                mode='lines',
                name=f'USL ({usl})',
                line=dict(color='red', dash='dash')
            )

            trace_lsl = go.Scatter(
                x=list(range(len(readings))),
                y=[lsl] * len(readings),
                mode='lines',
                name=f'LSL ({lsl})',
                line=dict(color='red', dash='dash')
            )

            trace_nominal = go.Scatter(
                x=list(range(len(readings))),
                y=[nominal] * len(readings),
                mode='lines',
                name=f'Nominal ({nominal})',
                line=dict(color='green', dash='solid')
            )

            trace_ltl = go.Scatter(
                x=list(range(len(readings))),
                y=[ltl] * len(readings),
                mode='lines',
                name=f'LTL ({ltl})',
                line=dict(color='orange', dash='dot')
            )

            trace_utl = go.Scatter(
                x=list(range(len(readings))),
                y=[utl] * len(readings),
                mode='lines',
                name=f'UTL ({utl})',
                line=dict(color='purple', dash='dot')
            )

            trace_xbar = go.Scatter(
                x=list(range(len(readings))),
                y=[x_bar] * len(readings),
                mode='lines',
                name=f'X-bar (Mean: {x_bar:.5f})',
                line=dict(color='purple', dash='solid')
            )

            data = [trace_readings, trace_usl, trace_lsl, trace_nominal, trace_ltl, trace_utl, trace_xbar]

            layout = go.Layout(
                title='X-bar Control Chart',
                xaxis_title='Sample Number',
                yaxis_title='Measurement',
                hovermode='closest'
            )

            fig = go.Figure(data=data, layout=layout)

            # Render the chart to HTML
            chart_html = pyo.plot(fig, output_type='div')

            # Pass the chart HTML and other values to the template
            context = {
                'chart': chart_html,
                'x_bar_values': x_bar_values,
                'part_model': part_model,
                'parameter_name': parameter_name,
                'operator': operator,
                'machine': machine,
                'shift': shift,
                'total_count':total_count,
            }

            return render(request, 'app/spc/xBar.html', context)

        # Handle cases where no data is available
        else:
            context = {
                'error': 'No data available for the selected filters.',
                'x_bar_values': x_bar_values,
                'part_model': part_model,
                'parameter_name': parameter_name,
                'operator': operator,
                'machine': machine,
                'shift': shift
            }
            return render(request, 'app/spc/xBar.html', context)
