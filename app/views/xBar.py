import plotly.graph_objs as go
import plotly.io as pio
from plotly.offline import plot
from django.shortcuts import render
import numpy as np
from app.models import MeasurementData, X_Bar_Chart
from django.utils import timezone
from datetime import datetime
from django.db.models import Q
from weasyprint import HTML, CSS
from django.http import HttpResponse
import os
import io
import base64

def xBar(request):
    if request.method == 'POST' and request.POST.get('export_type') == 'pdf':
        # Generate the same context as before
        context = generate_xBar_context(request, pdf=True)

        # Render the HTML to a string
        html_string = render(request, 'app/spc/xBar.html', context).content.decode('utf-8')

        # Define the CSS for landscape orientation
        css = CSS(string='''
            @page {
                size: A4 landscape; /* Set the page size to A4 landscape */
                margin: 1cm; /* Adjust margins as needed */
            }
            body {
                transform: scale(0.9); /* Adjust scale as needed */
                transform-origin: top left; /* Set origin for scaling */
                width: 1200px; /* Width of the content */
            }
            .no-pdf {
                display: none;
            }
        ''')

        # Convert HTML to PDF
        pdf_file = HTML(string=html_string).write_pdf(stylesheets=[css])

        # Define the path to save the PDF (e.g., Downloads folder)
        downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')  # Change to your desired path
        pdf_filename = f"Xbar_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
        pdf_path = os.path.join(downloads_folder, pdf_filename)

        # Save the PDF file to the filesystem
        with open(pdf_path, 'wb') as pdf_output:
            pdf_output.write(pdf_file)

        # Return a response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
        success_message = "PDF generated successfully!"
        context['success_message'] = success_message
        return render(request, 'app/spc/xBar.html', context)

    elif request.method == 'GET':
        # Generate the context for rendering the histogram page
        context = generate_xBar_context(request, pdf=False)
        return render(request, 'app/spc/xBar.html', context)

def generate_xBar_context(request, pdf=False):
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
    
    if not filtered_data:
        context = {
            'no_results': True
        }
        return context

    filtered_readings = MeasurementData.objects.filter(**filter_kwargs).values_list('readings', flat=True).order_by('id')

    total_count = len(filtered_readings)
    readings = [float(r) for r in filtered_readings]  # Convert readings to floats

    usl = filtered_data[0][1] if filtered_data else None
    lsl = filtered_data[0][2] if filtered_data else None
    nominal = filtered_data[0][3] if filtered_data else None
    ltl = filtered_data[0][4] if filtered_data else None
    utl = filtered_data[0][5] if filtered_data else None

    if readings and usl and lsl and nominal and ltl and utl:
        x_bar = np.mean(readings)

        trace_readings = go.Scatter(
            x=list(range(len(readings))),
            y=readings,
            mode='lines+markers',
            name='Readings',
            marker=dict(color='blue')
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
            hovermode='closest',
            width=1100  # Set the chart width to 900px
        )

        fig = go.Figure(data=data, layout=layout)

        if pdf:
            # Save the chart as a PNG image for the PDF
            img_bytes = fig.to_image(format="png")
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            chart_html = f'<img src="data:image/png;base64,{img_base64}" alt="X-bar Chart">'
        else:
            # Render the chart as an interactive HTML component for normal requests
            chart_html = plot(fig, output_type='div')

        return {
            'chart': chart_html,
            'x_bar_values': x_bar_values,
            'total_count': total_count,
        }
