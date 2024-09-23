from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
from weasyprint import CSS, HTML
from django.template.loader import get_template

from app.models import MeasurementData, jobwise_report


def jobReport(request):
    if request.method == 'GET':
        jobwise_values = jobwise_report.objects.all()
        part_model = jobwise_report.objects.values_list('part_model', flat=True).distinct().get()
        print("part_model:", part_model)
        job_no = jobwise_report.objects.values_list('job_no', flat=True).get()
        print("job_no:", job_no)

        # Filter MeasurementData objects based on part_model and job_no
        job_number_value = MeasurementData.objects.filter(part_model=part_model, comp_sr_no=job_no).order_by('id')

        if not job_number_value:
            # Handle case where no comp_sr_no values are found
            context = {
                'no_results': True  # Flag to indicate no results found
            }
            return render(request, 'app/reports/jobReport.html', context)
        # Initialize lists to store operator and shift values
        operators = []
        shifts = []
        part_status = []

        data_dict = {
            'Date':[],
            'Parameter Name': [],
            'Limits':[],
            'Readings': [],
            
        }

        # Iterate through queryset and append parameter_name, readings, and status_cell to data_dict
        for measurement_data in job_number_value:
            print(measurement_data.__dict__)
            print("parameter_name:", measurement_data.parameter_name)
            print("readings:", measurement_data.readings)
            print("status_cell:", measurement_data.status_cell)
            operators.append(measurement_data.operator)
            shifts.append(measurement_data.shift)
            part_status.append(measurement_data.part_status)

            print(operators,shifts,part_status)

           # If you want unique values, you can convert them to sets
            unique_operators = set(operators)
            unique_shifts = set(shifts)
            unique_part_status = set(part_status)

            # Convert sets to lists and join elements into a single string
            operators_values = ' '.join(list(unique_operators))
            shifts_values = ' '.join(list(unique_shifts))
            part_status_values = ' '.join(list(unique_part_status))

            # Print the values as space-separated strings
            print(operators_values, shifts_values, part_status_values)
            print("date",measurement_data.date)

            formatted_date = measurement_data.date.strftime("%d-%m-%Y %I:%M:%S %p")
            parameter_values = f"{measurement_data.usl} / {measurement_data.lsl}"
            

            data_dict['Date'].append(formatted_date)
            data_dict['Parameter Name'].append(measurement_data.parameter_name)
            data_dict['Limits'].append(parameter_values)
            if measurement_data.status_cell == 'ACCEPT':
                readings_html = f'<span style="background-color: #00ff00; padding: 2px;">{measurement_data.readings}</span>'
            elif measurement_data.status_cell == 'REWORK':
                readings_html = f'<span style="background-color: yellow; padding: 2px;">{measurement_data.readings}</span>'
            elif measurement_data.status_cell == 'REJECT':
                readings_html = f'<span style="background-color: red; padding: 2px;">{measurement_data.readings}</span>'
            data_dict['Readings'].append(readings_html)

            

        df = pd.DataFrame(data_dict)
        df.index = df.index + 1  # Shift index by 1 to start from 1

        table_html = df.to_html(index=True, escape=False, classes='table table-striped')

        context = {
            'table_html': table_html,
            'jobwise_values':jobwise_values,
            'operators_values':operators_values,
            'shifts_values':shifts_values,
            'part_status_values':part_status_values
        }

        

        return render(request, 'app/reports/jobReport.html', context)
    
    elif request.method == 'POST':
        export_type = request.POST.get('export_type')
        data_dict = request.session.get('data_dict')
        operators_values = request.session.get('operators_values')
        shifts_values = request.session.get('shifts_values')
        part_status_values = request.session.get('part_status_values')

        if data_dict is None or operators_values is None or shifts_values is None or part_status_values is None:
            return HttpResponse("No data available for export", status=400)

        df = pd.DataFrame(data_dict)
        df.index = df.index + 1

        if export_type == 'pdf':
            template = get_template('app/reports/jobReport.html')
            context = {
                'table_html': df.to_html(index=True, escape=False, classes='table table-striped table_data'),
                'jobwise_values': jobwise_report.objects.all(),
                'operators_values': operators_values,
                'shifts_values': shifts_values,
                'part_status_values': part_status_values,
            }
            html_string = template.render(context)

            # CSS for scaling down the content to fit a single PDF page
            css = CSS(string='''
                @page {
                    size: A4; /* Landscape mode to fit more content horizontally */
                    margin: 0.5cm; /* Adjust margin as needed */
                }
                body {
                    margin: 0; /* Give body some margin to prevent overflow */
                    transform: scale(0.8); /* Scale down the entire content */
                    transform-origin: 0 0; /* Ensure the scaling starts from the top-left corner */
                }
                
                table {
                    table-layout: fixed; /* Fix the table layout */
                    font-size: 20px; /* Increase font size */
                    border-collapse: collapse; /* Collapse table borders */
                }
                table, th, td {
                    border: 1px solid black; /* Add border to table */
                }
                th, td {
                    word-wrap: break-word; /* Break long words */
                }
                .no-pdf {
                    display: none;
                }
            ''')

            pdf_filename = f"JobReport{datetime.now().strftime('%Y/%m/%d_%H/%M/%S')}.pdf"

            pdf = HTML(string=html_string).write_pdf(stylesheets=[css])
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
            return response

        else:
            return HttpResponse("Invalid export type", status=400)

    return HttpResponse("Unsupported request method", status=405)


