from datetime import datetime
import re
import pandas as pd
from django.shortcuts import render
from django.utils import timezone  # Import Django's timezone utility
from app.models import MeasurementData,CustomerDetails, parameter_settings, parameterwise_report  # Adjust import based on your project structure
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from django.http import JsonResponse


from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from weasyprint import HTML,CSS
import pandas as pd
from io import BytesIO



# Function to remove HTML tags
def strip_html_tags(text):
    # Check if text is a string, then remove HTML tags
    if isinstance(text, str):
        return re.sub(r'<.*?>', '', text)
    return text

# Function to replace <br> with \n for multi-line headers
def replace_br_with_newline(text):
    if isinstance(text, str):
        return text.replace('<br>', '\n')
    return text

def paraReport(request):
    if request.method == 'GET':
        parameterwise_values = parameterwise_report.objects.all()
        part_model = parameterwise_report.objects.values_list('part_model', flat=True).distinct().get()
        print("part_model:", part_model)

        email_1 = CustomerDetails.objects.values_list('primary_email',flat=True).get()
        print('your primary mail id from server to front end now :',email_1)

        email_2 = CustomerDetails.objects.values_list('secondary_email',flat=True).get()
        print('your primary mail id from server to front end now :',email_2)

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

        distinct_comp_sr_nos = filtered_data.exclude(comp_sr_no__isnull=True).exclude(comp_sr_no__exact='').values_list('comp_sr_no', flat=True).distinct().order_by('date')
        print("distinct_comp_sr_nos:",distinct_comp_sr_nos)
        if not distinct_comp_sr_nos:
            # Handle case where no comp_sr_no values are found
            context = {
                'no_results': True  # Flag to indicate no results found
            }
            return render(request, 'app/reports/parameterReport.html', context)


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
        parameter_data = parameter_settings.objects.filter(model_id=part_model).values('parameter_name', 'usl', 'lsl').order_by('id')

        # Loop through each parameter_name and add usl, lsl to dictionary
        for param in parameter_data:
            param_name = param['parameter_name']
            usl = param['usl']
            lsl = param['lsl']
            
            # Combine parameter_name, usl, lsl as key
            key = f"{param_name} <br>{usl} <br>{lsl}"
            # Initialize empty list for the key
            data_dict[key] = []


        # Now add 20 empty lists after all parameters
        for i in range(1, 21):
            data_dict[str(i)] = []    

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
            'email_1': email_1,
            'email_2': email_2
        }

        request.session['data_dict'] = data_dict  # Save data_dict to the session for POST request

        return render(request, 'app/reports/parameterReport.html', context)
    
    elif request.method == 'POST':
        export_type = request.POST.get('export_type')
        recipient_email = request.POST.get('recipient_email')
        data_dict = request.session.get('data_dict')  # Retrieve data_dict from session
        if data_dict is None:
            return HttpResponse("No data available for export", status=400)

        df = pd.DataFrame(data_dict)
        df.index = df.index + 1


        if export_type == 'pdf' or export_type == 'send_mail':
            template = get_template('app/reports/parameterReport.html')
            context = {
                'table_html': df.to_html(index=True, escape=False, classes='table table-striped table_data'),
                'parameterwise_values': parameterwise_report.objects.all(),
            }
            html_string = template.render(context)

            # CSS for scaling down the content to fit a single PDF page
            css = CSS(string='''
                @page {
                    size: A4 landscape; /* Landscape mode to fit more content horizontally */
                    margin: 0.5cm; /* Adjust margin as needed */
                }
                body {
                    margin: 0; /* Give body some margin to prevent overflow */
                    transform: scale(0.2); /* Scale down the entire content */
                    transform-origin: 0 0; /* Ensure the scaling starts from the top-left corner */
                }
                .table_data {
                    width: 5000px; /* Increase the table width */
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


            pdf = HTML(string=html_string).write_pdf(stylesheets=[css])

            # Get the Downloads folder path
            downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
            pdf_filename = f"parameterReport_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
            pdf_file_path = os.path.join(downloads_folder, pdf_filename)

            # Save the PDF file in the Downloads folder
            with open(pdf_file_path, 'wb') as pdf_file:
                pdf_file.write(pdf)

            # Return the PDF file for download
            if export_type == 'pdf':
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{pdf_filename}"'
                  # Pass success message to the context to show on the front end
                success_message = "PDF generated successfully!"
                context['success_message'] = success_message
                return render(request, 'app/reports/parameterReport.html', context)

            elif export_type == 'send_mail':
                # Send the PDF as an email attachment
                send_mail_with_pdf(pdf, recipient_email)
                success_message = "PDF generated and email sent successfully!"
                return render(request, 'app/reports/parameterReport.html', {'success_message': success_message, **context})
        
        elif request.method == 'POST' and export_type == 'excel':
            template = get_template('app/reports/parameterReport.html')
            context = {
                'table_html': df.to_html(index=True, escape=False, classes='table table-striped table_data'),
                'parameterwise_values': parameterwise_report.objects.all(),
            }
            # Remove HTML tags from the DataFrame before exporting
            df = df.applymap(strip_html_tags)

            # Replace <br> with newline in column headers to make them multi-line in Excel
            df.columns = [replace_br_with_newline(col) for col in df.columns]

            # Create a new DataFrame for parameterwise_values
            parameterwise_values = parameterwise_report.objects.all()
            parameterwise_data = []

            for data in parameterwise_values:
                parameterwise_data.append({
                    'PARTMODEL': data.part_model,
                    'PARAMETER NAME': data.parameter_name,
                    'OPERATOR': data.operator,
                    'FROM DATE': data.formatted_from_date,
                    'TO DATE': data.formatted_to_date,
                    'MACHINE': data.machine,
                    'VENDOR CODE': data.vendor_code,
                    'JOB NO': data.job_no,
                    'SHIFT': data.shift,
                    'CURRENT DATE': data.current_date_time,
                })

            parameterwise_df = pd.DataFrame(parameterwise_data)

            # Create an Excel writer object using BytesIO as a file-like object
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                # Write parameterwise_df to the Excel sheet first
                parameterwise_df.to_excel(writer, sheet_name='ParameterReport', index=False, startrow=0)

                # Write the original DataFrame to the same sheet below the parameterwise data
                df.to_excel(writer, sheet_name='ParameterReport', index=True, startrow=len(parameterwise_df) + 2)

                # Get access to the workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['ParameterReport']

                # Format for multi-line header
                header_format = workbook.add_format({
                    'text_wrap': True,  # Enable text wrap
                    'valign': 'top',    # Align to top
                    'align': 'center',  # Center align the text
                    'bold': True        # Make the headers bold
                })

                # Apply formatting to the headers of the parameterwise data
                for col_num, value in enumerate(parameterwise_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)

                # Apply formatting to the headers of the main DataFrame (startrow=len(parameterwise_df)+2)
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(len(parameterwise_df) + 2, col_num + 1, value, header_format)

            # Get the Downloads folder path
            downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
            excel_filename = f"parameterReport_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
            excel_file_path = os.path.join(downloads_folder, excel_filename)

            # Save the Excel file in the Downloads folder
            with open(excel_file_path, 'wb') as excel_file:
                excel_file.write(excel_buffer.getvalue())

            # Return the Excel file for download
            response = HttpResponse(excel_buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{excel_filename}"'
            
            success_message = "Excel file generated successfully!"
            
            # Render success message in the frontend
            return render(request, 'app/reports/parameterReport.html', {'success_message': success_message ,**context})

        return HttpResponse("Unsupported request method", status=405)



def send_mail_with_pdf(pdf_content, recipient_email):
    sender_email = "itzprem1203@gmail.com"
    sender_password = "dxnb lcho buxy yang"
    subject = "Consolidate Report PDF"
    body = "Please find the attached PDF report."

    # Setup email parameters
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    # Attach the PDF file
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(pdf_content)
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', f'attachment; filename="parameterReport_report.pdf"')
    msg.attach(attachment)

    # Send the email using SMTP
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")





