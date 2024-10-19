from django.shortcuts import render
import numpy as np
from app.models import MeasurementData, Histogram_Chart
from django.utils import timezone
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
from weasyprint import HTML, CSS
from django.http import HttpResponse
import os

def histogram(request):
    if request.method == 'POST' and request.POST.get('export_type') == 'pdf':
        # Generate the same context as before
        context = generate_histogram_context(request)
        
        # Render the HTML to a string
        html_string = render(request, 'app/spc/histogram.html', context).content.decode('utf-8')

        # Define the CSS for landscape orientation
        css = CSS(string='''
            @page {
                size: A4 landscape; /* Set the page size to A4 landscape */
                margin: 1cm; /* Adjust margins as needed */
            }
            /* Scale down the content to fit within the 1100px width */
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
        pdf_filename = f"Histogram_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"

        pdf_path = os.path.join(downloads_folder, pdf_filename)

        # Save the PDF file to the filesystem
        with open(pdf_path, 'wb') as pdf_output:
            pdf_output.write(pdf_file)

        # Optionally, return a response or notify the user
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{pdf_filename}"'
        success_message = "PDF generated successfully!"
        context['success_message'] = success_message
        return render(request, 'app/spc/histogram.html', context)

    
    elif request.method == 'GET':
        # Generate the context for rendering the histogram page
        context = generate_histogram_context(request)
        return render(request, 'app/spc/histogram.html', context)

def generate_histogram_context(request):
    # Fetch the Histogram_Chart values and other fields
    Histogram_Chart_values = Histogram_Chart.objects.all()
    part_model = Histogram_Chart.objects.values_list('part_model', flat=True).distinct().get()

    fromDateStr = Histogram_Chart.objects.values_list('formatted_from_date', flat=True).get()
    toDateStr = Histogram_Chart.objects.values_list('formatted_to_date', flat=True).get()

    parameter_name = Histogram_Chart.objects.values_list('parameter_name', flat=True).get()
    operator = Histogram_Chart.objects.values_list('operator', flat=True).get()
    machine = Histogram_Chart.objects.values_list('machine', flat=True).get()
    shift = Histogram_Chart.objects.values_list('shift', flat=True).get()

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
        'readings', 'usl', 'lsl', 'ltl', 'utl').order_by('id')

    ltl_values = [data[3] for data in filtered_data]  # List of all LTL values
    utl_values = [data[4] for data in filtered_data]  # List of all UTL values

    ltl = list(set(ltl_values))
    utl = list(set(utl_values))

    filtered_readings = list(MeasurementData.objects.filter(**filter_kwargs).values_list('readings', flat=True).order_by('id'))

    if not filtered_readings:
        return {
            'no_results': True
        }

    readings = [float(reading) for reading in filtered_readings if reading is not None]

    ltl_min = min(ltl) if ltl else None
    utl_max = max(utl) if utl else None

    bins = np.linspace(min(readings), max(readings), 30)

    plt.figure(figsize=(7, 5))
    counts, edges, patches = plt.hist(readings, bins=bins, alpha=0.7)

    for count, edge_left, edge_right, patch in zip(counts, edges[:-1], edges[1:], patches):
        if ltl_min <= edge_left and edge_right <= utl_max:
            patch.set_facecolor('green')
        else:
            patch.set_facecolor('red')

    plt.title('Histogram of Readings with Tolerance Limits')
    plt.xlabel('Readings')
    plt.ylabel('Frequency')
    plt.grid(axis='y', alpha=0.75)

    for value in ltl:
        plt.axvline(x=value, color='red', linestyle='--', linewidth=2, label=f'LTL: {value}')

    for value in utl:
        plt.axvline(x=value, color='red', linestyle='--', linewidth=2, label=f'UTL: {value}')

    plt.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    image_base64 = base64.b64encode(image_png).decode('utf-8')

    return {
        'histogram_chart': image_base64,
        'Histogram_Chart_values': Histogram_Chart_values,
    }
