from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Image as ReportLabImage, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from indicators import soil_indicators
from fahp import fahp_weights, evaluate_soil_health
from assessment import assess_soil_health, generate_rating, generate_crop_recommendations
import matplotlib.pyplot as plt
import numpy as np
import io

def generate_pdf_report(data, file_path, indicator_values):
    report = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Create a custom style for Heading3 if it doesn't exist
    if 'Heading3' not in styles:
        styles.add(ParagraphStyle(name='Heading3', fontName='Helvetica-Bold', fontSize=12, alignment=TA_CENTER))

    # Modify the title style to use a smaller font size and center alignment
    styles["Title"].fontSize = 16
    styles["Title"].alignment = TA_CENTER

    report_elements = [Paragraph("Soil Health Report", styles["Title"]), Spacer(1, 0.2 * inch)]

    # Farmer Information
    farmer_info = [
        ['Name', data['name']],
        ['Gender', data['gender']],
        ['Age', data['age']],
        ['Address', data['address']],
        ['Mobile No.', data['mobile_no']],
        ['Area (ha)', data['area']]
    ]
    farmer_table = Table(farmer_info)
    farmer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))

    # Soil Sample Details
    sample_details = [
        ['Test ID', data['test_id']],
        ['Sample Collection Date', data['collection_date']],
        ['GPS Data', f"Latitude: {data['latitude']}, Longitude: {data['longitude']}"]
    ]
    sample_details_table = Table(sample_details)
    sample_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))

    # Create a table to hold both farmer information and sample details tables
    info_table = Table([[farmer_table, sample_details_table]])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    farmer_info_heading = Paragraph("Farmer Information", styles["Heading3"])
    sample_details_heading = Paragraph("Soil Sample Details", styles["Heading3"])

    report_elements.append(Table([[farmer_info_heading, sample_details_heading]]))
    report_elements.append(info_table)
    report_elements.append(Spacer(1, 0.2 * inch))

    # Soil Health Indicators
    table_data = [['Soil Health Indicators', 'Values', 'Normal Values']]
    for indicator in soil_indicators:
        indicator_name = indicator.name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        value = data.get(indicator_name, 'N/A')
        normal_value = indicator.optimal_range
        table_data.append([str(indicator), value, f"{normal_value[0]} - {normal_value[1]} {indicator.unit}"])
    table_data.append(['Soil Health Score', f"{data['soil_health_score']:.2f}", '0 - 1'])
    table_data.append(['Rating', generate_rating(data['soil_health_score']), ''])
    table_data.append(['Crop Recommendations', generate_crop_recommendations(data['soil_health_score']), ''])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
    ]))

    report_elements.append(Paragraph("Soil Health Indicators", styles["Heading3"]))
    report_elements.append(table)
    report_elements.append(Spacer(1, 0.2 * inch))

    # Create the radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    angles = np.linspace(0, 2 * np.pi, len(soil_indicators), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))
    indicator_values = np.concatenate((indicator_values, [indicator_values[0]]))

    ax.plot(angles, indicator_values, 'o-', linewidth=1)
    ax.fill(angles, indicator_values, alpha=0.25)

    # Modify the labels for each soil indicator

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
    ax.set_thetagrids(angles[:-1] * 180 / np.pi, labels, fontsize=8)
    ax.set_title("Soil Health Indicators", fontsize=12)
    ax.grid(True)

    # Save the radar chart as an image in memory
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=300, bbox_inches='tight')
    chart_buffer.seek(0)
    chart_img = ReportLabImage(chart_buffer, width=3 * inch, height=3 * inch)
    report_elements.append(chart_img)

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