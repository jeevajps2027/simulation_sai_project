from django.shortcuts import render
from app.models import MeasurementData, Pie_Chart
from django.utils import timezone
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64

def pieChart(request):
    if request.method == 'GET':
        # Fetch the x_bar_values and other fields
        pie_chart_values = Pie_Chart.objects.all()
        part_model = Pie_Chart.objects.values_list('part_model', flat=True).distinct().get()

        fromDateStr = Pie_Chart.objects.values_list('formatted_from_date', flat=True).get()
        toDateStr = Pie_Chart.objects.values_list('formatted_to_date', flat=True).get()

        parameter_name = Pie_Chart.objects.values_list('parameter_name', flat=True).get()
        operator = Pie_Chart.objects.values_list('operator', flat=True).get()
        machine = Pie_Chart.objects.values_list('machine', flat=True).get()
        shift = Pie_Chart.objects.values_list('shift', flat=True).get()

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
        filtered_status = list(MeasurementData.objects.filter(**filter_kwargs).values_list('status_cell', flat=True).order_by('id'))

        status_counts = {'ACCEPT': 0, 'REJECT': 0, 'REWORK': 0}

        # Ensure both lists have the same length
        if len(filtered_readings) == len(filtered_status):
            for status in filtered_status:
                if status == 'ACCEPT':
                    status_counts['ACCEPT'] += 1
                elif status == 'REWORK':
                    status_counts['REWORK'] += 1
                elif status == 'REJECT':
                    status_counts['REJECT'] += 1

        # Filter out statuses with zero counts for the pie chart
        labels = [label for label, count in status_counts.items() if count > 0]
        sizes = [count for count in status_counts.values() if count > 0]

        # Define colors based on available statuses
        color_map = {
            'ACCEPT': '#00ff00',  # Green
            'REWORK': 'yellow',   # Yellow
            'REJECT': 'red'       # Red
        }
        colors = [color_map[label] for label in labels]

        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')  # Equal aspect ratio ensures that the pie chart is circular.

        # Save the chart to a BytesIO stream
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        # Encode the image to base64
        image_base64 = base64.b64encode(image_png).decode('utf-8')

        # Pass the base64 image data to the template
        context = {
            'pie_chart': image_base64,
            'status_counts': status_counts
        }

        return render(request, 'app/spc/pieChart.html', context)
