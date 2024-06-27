from datetime import datetime
import pandas as pd
from django.shortcuts import render
from django.utils import timezone  # Import Django's timezone utility
from app.models import MeasurementData, parameter_settings, parameterwise_report  # Adjust import based on your project structure



from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from weasyprint import HTML,CSS
import pandas as pd
from io import BytesIO

def paraReport(request):
    if request.method == 'GET':
        parameterwise_values = parameterwise_report.objects.all()
        part_model = parameterwise_report.objects.values_list('part_model', flat=True).distinct().get()
        print("part_model:", part_model)

        fromDateStr = parameterwise_report.objects.values_list('formatted_from_date', flat=True).get()
        toDateStr = parameterwise_report.objects.values_list('formatted_to_date', flat=True).get()
        print("fromDate:", fromDateStr, "toDate:", toDateStr)

        parameter_name = parameterwise_report.objects.values_list('parameter_name', flat=True).get()
        print("parameter_name:", parameter_name)
        operator = parameterwise_report.objects.values_list('operator', flat=True).get()
        print("operator:", operator)
        machine = parameterwise_report.objects.values_list('machine', flat=True).get()
        print("machine:", machine)
        shift = parameterwise_report.objects.values_list('shift', flat=True).get()
        print("shift:", shift)
        job_no = parameterwise_report.objects.values_list('job_no', flat=True).get()
        print("job_no:", job_no)

        # Convert the string representations to naive datetime objects with the correct format
        date_format_input = '%d-%m-%Y %I:%M:%S %p'
        from_datetime_naive = datetime.strptime(fromDateStr, date_format_input)
        to_datetime_naive = datetime.strptime(toDateStr, date_format_input)

        # Convert naive datetime objects to timezone-aware datetime objects
        from_datetime = timezone.make_aware(from_datetime_naive, timezone.get_default_timezone())
        to_datetime = timezone.make_aware(to_datetime_naive, timezone.get_default_timezone())

        # Print the datetime objects to verify correct conversion
        print("from_datetime:", from_datetime, "to_datetime:", to_datetime)

        # Prepare the filter based on parameters
        filter_kwargs = {
            'date__range': (from_datetime, to_datetime),
            'part_model': part_model,
        }

        # Conditionally add filters based on values being "ALL"
        if parameter_name != "ALL":
            filter_kwargs['parameter_name'] = parameter_name

        if operator != "ALL":
            filter_kwargs['operator'] = operator

        if machine != "ALL":
            filter_kwargs['machine'] = machine

        if shift != "ALL":
            filter_kwargs['shift'] = shift

        if job_no != "ALL":
            filter_kwargs['comp_sr_no'] = job_no

        # Filter the MeasurementData records based on the constructed filter
        filtered_data = MeasurementData.objects.filter(**filter_kwargs).values()

        distinct_comp_sr_nos = MeasurementData.objects.filter(**filter_kwargs).values_list('comp_sr_no', flat=True).distinct()
        print("distinct_comp_sr_nos:",distinct_comp_sr_nos)

        total_count = distinct_comp_sr_nos.count()

        print(f"Number of distinct comp_sr_no values: {total_count}")

        # Initialize the data_dict with required headers
        data_dict = {
            'Date': [],
            'Job Number': [],
            'Shift': [],
            'Operator': []
        }

        # Query distinct values for 'parameter_name', 'usl', and 'lsl' from parameter_settings model
        parameter_data = parameter_settings.objects.filter(model_id=part_model).values('parameter_name', 'usl', 'lsl')

        # Loop through each parameter_name and add usl, lsl to dictionary
        for param in parameter_data:
            param_name = param['parameter_name']
            usl = param['usl']
            lsl = param['lsl']
            
            # Combine parameter_name, usl, lsl as key
            key = f"{param_name} <br>{usl} <br>{lsl}"
            # Initialize empty list for the key
            data_dict[key] = []

        

        

        for comp_sr_no in distinct_comp_sr_nos:
            print(f"Processing comp_sr_no: {comp_sr_no}")
            
            # Create a new dictionary for filter kwargs to avoid conflicts
            filter_params = filter_kwargs.copy()
            filter_params['comp_sr_no'] = comp_sr_no  # Add current comp_sr_no to filter params
            
            # Get distinct part_status for the current comp_sr_no
            part_status = MeasurementData.objects.filter(**filter_params).values_list('part_status', flat=True).distinct().first()
            print(f" Part Status: {part_status}")
            
            # Filter MeasurementData for the current comp_sr_no
            comp_sr_no_data = MeasurementData.objects.filter(**filter_params).values(
                'parameter_name', 'readings', 'status_cell', 'operator', 'shift', 'machine', 'date'
            )

            combined_row = {
                'Date': '',
                'Job Number': comp_sr_no,
                'Shift': '',
                'Operator': '',
               
            }

            for data in comp_sr_no_data:
                parameter_name = data['parameter_name']
                usl = parameter_settings.objects.get(parameter_name=parameter_name, model_id=part_model).usl
                lsl = parameter_settings.objects.get(parameter_name=parameter_name, model_id=part_model).lsl
                key = f"{parameter_name} <br>{usl} <br>{lsl}"
                # Format date as "21-06-2024 11:33:09 AM"
                formatted_date = data['date'].strftime('%d-%m-%Y %I:%M:%S %p')
                # Determine background color based on status_cell value
                if data['status_cell'] == 'ACCEPT':
                    # Green background for ACCEPT
                    readings_html = f'<span style="background-color: #00ff00; padding: 2px;">{data["readings"]}</span>'
                elif data['status_cell'] == 'REWORK':
                    # Yellow background for REWORK
                    readings_html = f'<span style="background-color: yellow; padding: 2px;">{data["readings"]}</span>'
                elif data['status_cell'] == 'REJECT':
                    # Red background for REJECT
                    readings_html = f'<span style="background-color: red; padding: 2px;">{data["readings"]}</span>'
                
                # Assign the HTML formatted readings to combined_row[key]
                combined_row[key] = readings_html
                combined_row['Date'] = formatted_date
                combined_row['Operator'] = data['operator']
                combined_row['Shift'] = data['shift']

            

            # Append combined_row data to data_dict lists
            for key in data_dict:
                data_dict[key].append(combined_row.get(key, ''))

        
        # Create a pandas DataFrame from the dictionary with specified column order
        df = pd.DataFrame(data_dict)

        # Assuming df is your pandas DataFrame
        df.index = df.index + 1  # Shift index by 1 to start from 1

        # Convert dataframe to HTML table with custom styling
        table_html = df.to_html(index=True, escape=False, classes='table table-striped')

        context = {
            'table_html': table_html,
            'parameterwise_values': parameterwise_values,
            
        }

       
    return render(request, 'app/reports/parameterReport.html', context)






"""
def save_as_pdf(request):
    template = get_template('app/reports/consolidateSrNo.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="consolidate_report.pdf"'

    HTML(string=html).write_pdf(response, stylesheets=[settings.STATIC_ROOT + 'app/static/css/pdf_styles.css'])

    return response

def export_to_excel(request):
    # Assuming df is your pandas DataFrame
    df = pd.DataFrame(data_dict)

    # Create a bytes buffer for the Excel file
    excel_file = BytesIO()
    xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')

    # Write the DataFrame to the Excel file
    df.to_excel(xlwriter, sheet_name='Sheet1', index=False)

    # Close the Pandas Excel writer and output the Excel file
    xlwriter.save()
    xlwriter.close()

    # Rewind the buffer and serve the response
    excel_file.seek(0)

    response = HttpResponse(excel_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="consolidate_report.xlsx"'

    return response
"""