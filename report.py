from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # Import TA_LEFT
from indicators import soil_indicators
from fahp import fahp_weights, evaluate_soil_health
from assessment import assess_soil_health, generate_rating, generate_crop_recommendations
import matplotlib.pyplot as plt
import numpy as np
import io
import sqlite3
import openpyxl
from tkinter import filedialog
from datetime import datetime


def generate_pdf_report(data, file_path, indicator_values):
    report = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    # Define custom color palette
    primary_color = colors.HexColor('#2E8B57')  # Green
    secondary_color = colors.HexColor('#000000')  # Black
    tertiary_color = colors.HexColor('#808080')  # Grey
    accent_color = colors.HexColor('#FFFFFF')  # White

    # Define custom font styles
    if 'MainTitle' not in styles:
        styles.add(ParagraphStyle(name='MainTitle', fontName='Helvetica-Bold', fontSize=16, textColor=colors.black,
                                  spaceAfter=6, alignment=TA_CENTER))
    if 'TableTitle' not in styles:
        styles.add(ParagraphStyle(name='TableTitle', fontName='Helvetica-Bold', fontSize=8, textColor=secondary_color,
                                  spaceAfter=4, alignment=TA_CENTER))
    if 'BodyText' not in styles:
        styles.add(ParagraphStyle(name='BodyText', fontName='Helvetica', fontSize=8, textColor=secondary_color,
                                  spaceAfter=4))

    # Create the report elements
    report_elements = []

    # Add the main title with image
    main_image = Image('main.png', width=0.5 * inch, height=0.5 * inch)
    main_title = Paragraph('Soil Health Diagnostic System Report', styles['MainTitle'])
    main_title_with_image = Table([[main_image, Spacer(0.05 * inch, 0), main_title]], colWidths=[0.2 * inch, 0.05 * inch, None], hAlign='LEFT')
    main_title_with_image.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, 0), 0),  # Remove left padding for the image
        ('RIGHTPADDING', (-1, 0), (-1, 0), 0),  # Remove right padding for the title
        ('PADDING', (0, 0), (-1, 0), 0.05 * inch),  # Reduce padding between cells
    ]))
    report_elements.append(main_title_with_image)
    report_elements.append(Spacer(0.2, 0.2 * inch))

    # Add farmer information and sample details tables
    farmer_info_data = [
        ['Name', data['name']],
        ['Gender', data['gender']],
        ['Age', data['age']],
        ['Address', data['address']],
        ['Mobile No.', data['mobile_no']],
        ['Area (ha)', data['area']]
    ]
    farmer_info_table = Table(farmer_info_data, colWidths=[1.5 * inch, 2.0 * inch])
    farmer_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4682B4')),  # Steelblue
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#FFFFFF')),  # White
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E6F2FF')),  # Light Blue
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),  # Black
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))

    sample_details_data = [
        ['Test ID', data['test_id']],
        ['Sample Date', data['collection_date']],
        ['GPS Data', f"Lat: {data['latitude']}° N, Long: {data['longitude']}° E"]
    ]
    sample_details_table = Table(sample_details_data, colWidths=[1.0 * inch, 2.3 * inch])
    sample_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4682B4')),  # Steelblue
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#FFFFFF')),  # White
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E6F2FF')),  # Light Blue
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),  # Black
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))

    farmer_info_title = Paragraph("Farmer Information",
                                  ParagraphStyle(name='TableTitle', fontSize=10, alignment=TA_CENTER, fontWeight='bold'))
    sample_details_title = Paragraph("Sample Details",
                                     ParagraphStyle(name='TableTitle', fontSize=10, alignment=TA_CENTER,
                                                    fontWeight='bold'))

    info_table = Table([[farmer_info_title, sample_details_title],
                        [farmer_info_table, sample_details_table]],
                       colWidths=[3.5 * inch, 3.5 * inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Left padding for the first column
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),  # Right padding for the last column
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    report_elements.append(info_table)
    report_elements.append(Spacer(1, 0.2 * inch))

    # Add soil health indicators table
    soil_health_data = [
        ['Indicators', 'Value', 'Normal Range'],
        ['Soil pH', data['soil_ph'], '6.0 - 7.5'],
        ['Nitrogen (N)(mg/kg)', data['nitrogen'], '50 - 250 mg/kg'],
        ['Phosphorus (P)(mg/kg)', data['phosphorus'], '20 - 100 mg/kg'],
        ['Potassium (K)(mg/kg)', data['potassium'], '50 - 200 mg/kg'],
        ['EC(dS/m)', data['electrical_conductivity'], '0 - 2 dS/m'],
        ['Temperature (°C)', data['temperature'], '10 - 30 °C'],
        ['Moisture (%)', data['moisture'], '20 - 80 %'],
        ['Humidity (%)', data['humidity'], '30 - 70 %']
    ]
    # Create the radar chart
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={'projection': 'polar'})
    angles = np.linspace(0, 2 * np.pi, len(soil_indicators), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))
    indicator_values = np.concatenate((indicator_values, [indicator_values[0]]))

    ax.plot(angles, indicator_values, 'o-', linewidth=1)
    ax.fill(angles, indicator_values, alpha=0.25)

    labels = [
        'pH',
        'N\n(mg/kg)',
        'P\n(mg/kg)',
        'K\n(mg/kg)',
        'EC\n(dS/m)',
        'Temp\n(°C)',
        'Moist\n(%)',
        'Humid\n(%)'
    ]
    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels, fontsize=6)
    ax.set_title("Soil Health Indicators", fontsize=10)
    ax.grid(True)

    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
    chart_buffer.seek(0)
    chart_img = Image(chart_buffer, width=3 * inch, height=3 * inch)

    # Get the height of the chart_img
    chart_height = chart_img.drawHeight

    # Create the soil_health_table
    soil_health_table = Table(soil_health_data, colWidths=[1.5 * inch, 0.7 * inch, 1.3 * inch],
                              rowHeights=[chart_height / len(soil_health_data)] * len(soil_health_data))
    soil_health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), accent_color),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0FFF0')),
        ('TEXTCOLOR', (0, 1), (-1, -1), secondary_color),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))

    # Create a parent table to hold the soil_health_table and chart image side by side
    soil_health_parent_table = Table([[soil_health_table, Spacer(0.2 * inch, 0), [Spacer(0.5 * inch, 0), chart_img]]],
                                     colWidths=[3.4 * inch, 0.2 * inch, 3 * inch])
    soil_health_parent_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically center the content
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Left padding for the first column
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),  # Right padding for the last column
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    soil_health_title = Paragraph("Soil Test Information",
                                  ParagraphStyle(name='TableTitle', fontSize=10, alignment=TA_CENTER,
                                                 fontWeight='bold'))

    indicators_table = Table([[soil_health_title, ''],
                              [soil_health_parent_table]],
                             colWidths=[3.5 * inch, 3.5 * inch])
    indicators_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align tops of cells
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Horizontally center the title
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Left padding for the first column
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),  # Right padding for the last column
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    report_elements.append(indicators_table)
    report_elements.append(Spacer(1, 0.2 * inch))

    # Add 'Overall Result' table
    value_ranges_text = "Very Poor, Poor,\nBelow Average, Average,\nAbove Average, Good,\nExcellent"
    overall_result_data = [
        ['Result', 'Value', 'Range'],
        ['Soil Health Score', f"{data['soil_health_score']:.2f}", '0 - 1'],
        ['Rating', data['rating'], value_ranges_text],
        ['Crop Recommendations', data['crop_recommendations'], '']
    ]
    overall_result_table = Table(overall_result_data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch])
    overall_result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), accent_color),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F0FFF0')),
        ('TEXTCOLOR', (0, 1), (-1, -1), secondary_color),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))

    overall_result_title = Paragraph("Overall Result",
                                     ParagraphStyle(name='TableTitle', fontSize=10, alignment=TA_CENTER,
                                                    fontWeight='bold'))
    overall_result_table_with_title = Table([[overall_result_title],
                                             [overall_result_table]],
                                            colWidths=[4.5 * inch])
    overall_result_table_with_title.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align tops of cells
        ('LEFTPADDING', (0, 0), (0, -1), 0),  # Left padding for the first column
        ('RIGHTPADDING', (-1, 0), (-1, -1), 0),  # Right padding for the last column
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    report_elements.append(overall_result_table_with_title)
    report_elements.append(Spacer(1, 0.2 * inch))

    # Add the generated report time and date
    report_date = datetime.now().strftime('%d-%m-%Y(%A) %I:%M:%S%p')
    report_elements.append(Paragraph(f"Report Generated On: {report_date}", ParagraphStyle(name='ReportDate', alignment=TA_CENTER, fontSize=8, textColor=tertiary_color)))

    # Add developer information
    report_elements.append(Spacer(1, 0.2 * inch))

    credentials_text = "Designed & Developed by: LALDINPUIA, Research Scholar"
    report_elements.append(Paragraph(credentials_text,
                                     ParagraphStyle(name='CredentialsText', fontName='Helvetica', fontSize=6,
                                                    textColor=secondary_color, alignment=TA_CENTER)))

    department_text = "Department of Mathematics and Computer Science, Mizoram University"
    report_elements.append(Paragraph(department_text,
                                     ParagraphStyle(name='DepartmentText', fontName='Helvetica', fontSize=6,
                                                    textColor=secondary_color, alignment=TA_CENTER, fontWeight='bold')))

    email_link_style = ParagraphStyle(name='EmailLink', fontName='Helvetica', fontSize=8,
                                      textColor=colors.HexColor('#2E8B57'), alignment=TA_CENTER)
    report_elements.append(Paragraph("Email: mzu22000486@mzu.edu.in", email_link_style))

    # Build the report
    report.build(report_elements)

def export_to_excel(test_id):
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")], initialfile=f"{test_id}_test.xlsx")
    if file_path:
        conn = sqlite3.connect('soil_health.db')
        c = conn.cursor()
        c.execute("SELECT * FROM soil_tests WHERE test_id = ?", (test_id,))
        data = c.fetchall()
        conn.close()

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['ID', 'Test ID', 'Sample Collection Date', 'Latitude', 'Longitude', 'Name', 'Area (ha)', 'Gender',
                      'Age', 'Address', 'Mobile No.', 'Soil pH', 'Nitrogen', 'Phosphorus', 'Potassium',
                      'Electrical Conductivity', 'Temperature', 'Moisture', 'Humidity', 'Soil Health Score',
                      'Crop Recommendations'])
        for row in data:
            sheet.append(row)
        workbook.save(file_path)
    return file_path