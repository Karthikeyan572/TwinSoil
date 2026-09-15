import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

FIXTURES_DIR = Path(__file__).resolve().parent
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

# 1. Canonical Duffy Rear Fixture (using standard ASCII hyphens for PDF compatibility)
DUFFY_REAR_DATA = {
    "sample_id": "Duffy Rear",
    "crop_code": "Home Garden / Vegetables",
    "parameters": [
        {"name": "pH", "value": 4.5, "unit": None, "reference_min": 6.0, "reference_max": 6.8, "reference_text": "6.0-6.8", "lab_status": "BELOW OPTIMUM", "computed_status": "BELOW_OPTIMUM", "source_page": 1},
        {"name": "CEC", "value": 9.5, "unit": "meq/100g", "reference_min": 10.0, "reference_max": 20.0, "reference_text": "10-20", "lab_status": "SLIGHTLY LOW", "computed_status": "BELOW_OPTIMUM", "source_page": 1},
        {"name": "Organic Matter", "value": 1.9, "unit": "%", "reference_min": 3.0, "reference_max": 5.0, "reference_text": "3-5%", "lab_status": "BELOW OPTIMUM", "computed_status": "BELOW_OPTIMUM", "source_page": 1},
        {"name": "P", "value": 2.3, "unit": "ppm", "reference_min": 4.0, "reference_max": 14.0, "reference_text": "4-14", "lab_status": "DEFICIENT", "computed_status": "BELOW_OPTIMUM", "source_page": 1},
        {"name": "K", "value": 47.0, "unit": "ppm", "reference_min": 100.0, "reference_max": 160.0, "reference_text": "100-160", "lab_status": "DEFICIENT", "computed_status": "BELOW_OPTIMUM", "source_page": 1},
        {"name": "Ca", "value": 133.0, "unit": "ppm", "reference_min": 1000.0, "reference_max": 1500.0, "reference_text": "1000-1500", "lab_status": "CRITICALLY LOW", "computed_status": "BELOW_OPTIMUM", "source_page": 1},
        {"name": "Mg", "value": 21.0, "unit": "ppm", "reference_min": 50.0, "reference_max": 120.0, "reference_text": "50-120", "lab_status": "DEFICIENT", "computed_status": "BELOW_OPTIMUM", "source_page": 1},
        {"name": "S", "value": 34.4, "unit": "ppm", "reference_min": 10.0, "reference_max": None, "reference_text": ">10", "lab_status": "OPTIMAL", "computed_status": "WITHIN_RANGE", "source_page": 1},
        {"name": "B", "value": 0.1, "unit": "ppm", "reference_min": 0.1, "reference_max": 0.5, "reference_text": "0.1-0.5", "lab_status": "LOW", "computed_status": "WITHIN_RANGE", "source_page": 1},
        {"name": "Mn", "value": 4.4, "unit": "ppm", "reference_min": 1.1, "reference_max": 6.3, "reference_text": "1.1-6.3", "lab_status": "OPTIMAL", "computed_status": "WITHIN_RANGE", "source_page": 1},
        {"name": "Zn", "value": 0.8, "unit": "ppm", "reference_min": 1.0, "reference_max": 7.6, "reference_text": "1.0-7.6", "lab_status": "SLIGHTLY LOW", "computed_status": "BELOW_OPTIMUM", "source_page": 1},
        {"name": "Cu", "value": 0.4, "unit": "ppm", "reference_min": 0.3, "reference_max": 0.6, "reference_text": "0.3-0.6", "lab_status": "OPTIMAL", "computed_status": "WITHIN_RANGE", "source_page": 1},
        {"name": "Fe", "value": 81.9, "unit": "ppm", "reference_min": 2.7, "reference_max": 9.4, "reference_text": "2.7-9.4", "lab_status": "ELEVATED", "computed_status": "ABOVE_OPTIMUM", "source_page": 1},
        {"name": "Al", "value": 94.0, "unit": "ppm", "reference_min": None, "reference_max": 75.0, "reference_text": "<75", "lab_status": "HIGH", "computed_status": "ABOVE_OPTIMUM", "source_page": 1},
        {"name": "Pb", "value": 1.3, "unit": "ppm", "reference_min": None, "reference_max": 22.0, "reference_text": "<22", "lab_status": "LOW/SAFE", "computed_status": "WITHIN_RANGE", "source_page": 1},
    ]
}

ARCHETYPES = {
    "duffy_rear": DUFFY_REAR_DATA,
    "balanced_soil": {
        "sample_id": "Balanced Field 1",
        "crop_code": "Corn / Maize",
        "parameters": [
            {"name": "pH", "value": 6.5, "unit": None, "reference_min": 6.0, "reference_max": 7.0, "reference_text": "6.0-7.0", "lab_status": "OPTIMAL", "computed_status": "WITHIN_RANGE", "source_page": 1},
            {"name": "Organic Matter", "value": 3.8, "unit": "%", "reference_min": 3.0, "reference_max": 5.0, "reference_text": "3-5%", "lab_status": "OPTIMAL", "computed_status": "WITHIN_RANGE", "source_page": 1},
            {"name": "N", "value": 45.0, "unit": "ppm", "reference_min": 30.0, "reference_max": 60.0, "reference_text": "30-60", "lab_status": "OPTIMAL", "computed_status": "WITHIN_RANGE", "source_page": 1},
            {"name": "P", "value": 25.0, "unit": "ppm", "reference_min": 20.0, "reference_max": 40.0, "reference_text": "20-40", "lab_status": "OPTIMAL", "computed_status": "WITHIN_RANGE", "source_page": 1},
            {"name": "K", "value": 140.0, "unit": "ppm", "reference_min": 120.0, "reference_max": 180.0, "reference_text": "120-180", "lab_status": "OPTIMAL", "computed_status": "WITHIN_RANGE", "source_page": 1},
        ]
    },
    "strongly_acidic": {
        "sample_id": "Acidic Pine Plot",
        "crop_code": "Blueberries",
        "parameters": [
            {"name": "pH", "value": 4.2, "unit": None, "reference_min": 6.0, "reference_max": 6.8, "reference_text": "6.0-6.8", "lab_status": "VERY LOW", "computed_status": "BELOW_OPTIMUM", "source_page": 1},
            {"name": "Al", "value": 115.0, "unit": "ppm", "reference_min": None, "reference_max": 75.0, "reference_text": "<75", "lab_status": "TOXIC / HIGH", "computed_status": "ABOVE_OPTIMUM", "source_page": 1},
            {"name": "Ca", "value": 250.0, "unit": "ppm", "reference_min": 800.0, "reference_max": 1500.0, "reference_text": "800-1500", "lab_status": "DEFICIENT", "computed_status": "BELOW_OPTIMUM", "source_page": 1}
        ]
    },
    "alkaline": {
        "sample_id": "West Basin Calcareous",
        "crop_code": "Wheat",
        "parameters": [
            {"name": "pH", "value": 8.2, "unit": None, "reference_min": 6.2, "reference_max": 7.2, "reference_text": "6.2-7.2", "lab_status": "VERY HIGH", "computed_status": "ABOVE_OPTIMUM", "source_page": 1},
            {"name": "Fe", "value": 2.1, "unit": "ppm", "reference_min": 4.0, "reference_max": 12.0, "reference_text": "4.0-12.0", "lab_status": "DEFICIENT", "computed_status": "BELOW_OPTIMUM", "source_page": 1}
        ]
    }
}

def render_pdf_report(data: dict, output_pdf_path: Path):
    doc = SimpleDocTemplate(str(output_pdf_path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    notice_style = ParagraphStyle('Notice', parent=styles['Normal'], fontSize=11, textColor=colors.red, fontName='Helvetica-Bold', alignment=1)
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=18, leading=22, textColor=colors.HexColor('#1b4332'))
    subtitle_style = ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#2d6a4f'))
    
    elements = []
    
    # Non-negotiable visible notice
    elements.append(Paragraph("*** SYNTHETIC TEST REPORT - not from a real laboratory ***", notice_style))
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("SOIL TEST REPORT & AGRONOMIC PROFILE", title_style))
    elements.append(Paragraph(f"<b>Sample ID:</b> {data['sample_id']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Crop:</b> {data.get('crop_code', 'N/A')}", subtitle_style))
    elements.append(Spacer(1, 16))
    
    # Table data
    table_data = [["Parameter", "Value", "Lab Range", "Status"]]
    for p in data["parameters"]:
        val_str = f"{p['value']} {p['unit']}" if p.get('unit') else f"{p['value']}"
        table_data.append([
            p["name"],
            val_str,
            p.get("reference_text") or "—",
            p.get("lab_status") or "—"
        ])
        
    t = Table(table_data, colWidths=[130, 110, 130, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d6a4f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d8f3dc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    
    elements.append(t)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("<b>Laboratory Notes:</b> Routine agricultural soil assay. Values validated according to standard regional soil testing methodologies.", styles['Normal']))
    
    doc.build(elements)

def generate_all_fixtures():
    for name, data in ARCHETYPES.items():
        pdf_path = FIXTURES_DIR / f"{name}.pdf"
        json_path = FIXTURES_DIR / f"{name}.json"
        
        render_pdf_report(data, pdf_path)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            
    print(f"Generated {len(ARCHETYPES)} synthetic test fixtures successfully in {FIXTURES_DIR}")

if __name__ == "__main__":
    generate_all_fixtures()
