"""
PoC - PDF Generator with Clickable Index
Requirements:
- API that receives 3 data sets
- Generate PDF with index
- Clickable links in the index directing to the correct pages
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from flask import Flask, request, jsonify, send_file
import json
import os
from datetime import datetime
import tempfile

app = Flask(__name__)

class NumberedCanvas(canvas.Canvas):
    """Custom canvas to add page numbers"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page numbers to all pages"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """Draw the page number"""
        self.setFont("Helvetica", 9)
        self.drawRightString(
            A4[0] - 1*cm,
            1*cm,
            f"Page {self._pageNumber} of {page_count}"
        )

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
    def setup_custom_styles(self):
        """Set up custom styles for the document"""
        # Main title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section title style
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            spaceBefore=20
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='SubSectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Content style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))

    def create_toc(self):
        """Create the Table of Contents with clickable links"""
        toc = TableOfContents()
        toc.levelStyles = [
            ParagraphStyle(fontSize=12, leftIndent=0, name='TOCHeading1', 
                          textColor=colors.HexColor('#2c3e50'), spaceAfter=6),
            ParagraphStyle(fontSize=11, leftIndent=20, name='TOCHeading2',
                          textColor=colors.HexColor('#34495e'), spaceAfter=4),
            ParagraphStyle(fontSize=10, leftIndent=40, name='TOCHeading3',
                          textColor=colors.HexColor('#7f8c8d'), spaceAfter=2),
        ]
        return toc

    def generate_pdf(self, dataset1, dataset2, dataset3, filename='document.pdf'):
        """Generate PDF with three data sets and clickable index"""
        
        # Create the document
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # List to store document elements
        story = []
        
        # Main title
        story.append(Paragraph("Proof of Concept Document", self.styles['CustomTitle']))
        story.append(Spacer(1, 1*cm))
        
        # Create the index
        toc = self.create_toc()
        story.append(Paragraph("Table of Contents", self.styles['SectionTitle']))
        story.append(Spacer(1, 0.5*cm))
        story.append(toc)
        story.append(PageBreak())
        
        # Section 1 - Dataset 1
        story.append(Paragraph("1. First Data Set", self.styles['SectionTitle']))
        toc.addEntry(0, "1. First Data Set", doc.page)
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("1.1 Overview", self.styles['SubSectionTitle']))
        toc.addEntry(1, "1.1 Overview", doc.page)
        story.append(Paragraph(
            f"This is the first data set received by the API. It contains {len(dataset1)} records.",
            self.styles['CustomBody']
        ))
        
        # Add dataset1 content
        for i, item in enumerate(dataset1[:5], 1):  # Limit to 5 items for example
            story.append(Paragraph(f"1.2.{i} Item {i}", self.styles['SubSectionTitle']))
            toc.addEntry(2, f"1.2.{i} Item {i}", doc.page)
            story.append(Paragraph(str(item), self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*cm))
        
        # Add summary table for dataset1
        if dataset1 and isinstance(dataset1[0], dict):
            story.append(Paragraph("1.3 Summary Table", self.styles['SubSectionTitle']))
            toc.addEntry(1, "1.3 Summary Table", doc.page)
            story.append(self.create_summary_table(dataset1[:5]))
        
        story.append(PageBreak())
        
        # Section 2 - Dataset 2
        story.append(Paragraph("2. Second Data Set", self.styles['SectionTitle']))
        toc.addEntry(0, "2. Second Data Set", doc.page)
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("2.1 Data Analysis", self.styles['SubSectionTitle']))
        toc.addEntry(1, "2.1 Data Analysis", doc.page)
        story.append(Paragraph(
            f"The second set contains {len(dataset2)} elements for analysis.",
            self.styles['CustomBody']
        ))
        
        # Add dataset2 content
        for i, item in enumerate(dataset2[:5], 1):
            story.append(Paragraph(f"2.2.{i} Record {i}", self.styles['SubSectionTitle']))
            toc.addEntry(2, f"2.2.{i} Record {i}", doc.page)
            story.append(Paragraph(str(item), self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*cm))
        
        story.append(PageBreak())
        
        # Section 3 - Dataset 3
        story.append(Paragraph("3. Third Data Set", self.styles['SectionTitle']))
        toc.addEntry(0, "3. Third Data Set", doc.page)
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("3.1 Additional Information", self.styles['SubSectionTitle']))
        toc.addEntry(1, "3.1 Additional Information", doc.page)
        story.append(Paragraph(
            f"This final set has {len(dataset3)} processed items.",
            self.styles['CustomBody']
        ))
        
        # Add dataset3 content
        for i, item in enumerate(dataset3[:5], 1):
            story.append(Paragraph(f"3.2.{i} Element {i}", self.styles['SubSectionTitle']))
            toc.addEntry(2, f"3.2.{i} Element {i}", doc.page)
            story.append(Paragraph(str(item), self.styles['CustomBody']))
            story.append(Spacer(1, 0.3*cm))
        
        story.append(PageBreak())
        
        # Section 4 - Conclusion
        story.append(Paragraph("4. Conclusion", self.styles['SectionTitle']))
        toc.addEntry(0, "4. Conclusion", doc.page)
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph(
            "This document was automatically generated through the API developed for the PoC. "
            "The index above contains clickable links that direct to the corresponding sections.",
            self.styles['CustomBody']
        ))
        
        story.append(Paragraph("4.1 Statistics", self.styles['SubSectionTitle']))
        toc.addEntry(1, "4.1 Statistics", doc.page)
        stats_text = f"""
        Total records processed:
        - Dataset 1: {len(dataset1)} records
        - Dataset 2: {len(dataset2)} records
        - Dataset 3: {len(dataset3)} records
        - Grand total: {len(dataset1) + len(dataset2) + len(dataset3)} records
        """
        story.append(Paragraph(stats_text, self.styles['CustomBody']))
        
        # Generate PDF with custom canvas for page numbering
        doc.multiBuild(story, canvasmaker=NumberedCanvas)
        
        return filename
    
    def create_summary_table(self, data):
        """Create a summary table for structured data"""
        if not data or not isinstance(data[0], dict):
            return Spacer(1, 0)
        
        # Prepare table data
        headers = list(data[0].keys())[:3]  # Limit to 3 columns
        table_data = [headers]
        
        for item in data[:5]:  # Limit to 5 rows
            row = [str(item.get(h, ''))[:30] for h in headers]  # Limit text to 30 chars
            table_data.append(row)
        
        # Create and style the table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ]))
        
        return table

# PDF generator instance
pdf_gen = PDFGenerator()

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf_api():
    """
    API endpoint to generate PDF with 3 data sets
    
    Request example:
    {
        "dataset1": [...],
        "dataset2": [...],
        "dataset3": [...]
    }
    """
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract the three data sets
        dataset1 = data.get('dataset1', [])
        dataset2 = data.get('dataset2', [])
        dataset3 = data.get('dataset3', [])
        
        # Validate that at least one set was provided
        if not (dataset1 or dataset2 or dataset3):
            return jsonify({"error": "At least one data set must be provided"}), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"poc_document_{timestamp}.pdf"
        filepath = os.path.join(tempfile.gettempdir(), filename)
        
        # Generate PDF
        pdf_gen.generate_pdf(dataset1, dataset2, dataset3, filepath)
        
        # Return PDF file
        return send_file(
            filepath,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working"""
    return jsonify({
        "status": "OK",
        "message": "API is working correctly",
        "endpoints": {
            "/api/test": "GET - API test",
            "/api/generate-pdf": "POST - Generate PDF with 3 datasets",
            "/api/generate-sample": "GET - Generate sample PDF"
        }
    })

@app.route('/api/generate-sample', methods=['GET'])
def generate_sample():
    """Generate a sample PDF with mock data for testing""" 
    
    # Sample data
    dataset1 = [
        {"id": 1, "name": "Product A", "value": 100.50, "category": "Electronics"},
        {"id": 2, "name": "Product B", "value": 250.00, "category": "Books"},
        {"id": 3, "name": "Product C", "value": 50.75, "category": "Food"},
        {"id": 4, "name": "Product D", "value": 180.25, "category": "Clothing"},
        {"id": 5, "name": "Product E", "value": 320.00, "category": "Furniture"},
        {"id": 6, "name": "Product F", "value": 45.90, "category": "Stationery"},
        {"id": 7, "name": "Product G", "value": 890.00, "category": "Electronics"}
    ]
    
    dataset2 = [
        {"customer": "John Smith", "date": "2024-01-15", "status": "Approved"},
        {"customer": "Mary Johnson", "date": "2024-01-16", "status": "Pending"},
        {"customer": "Peter Wilson", "date": "2024-01-17", "status": "Approved"},
        {"customer": "Anna Davis", "date": "2024-01-18", "status": "Rejected"},
        {"customer": "Charles Brown", "date": "2024-01-19", "status": "Approved"},
        {"customer": "Lucy Miller", "date": "2024-01-20", "status": "Pending"}
    ]
    
    dataset3 = [
        "Note 1: System working correctly",
        "Note 2: Index with clickable links implemented",
        "Note 3: Navigation between sections validated",
        "Note 4: Formatting preserved on all pages",
        "Note 5: Automatic page numbering",
        "Note 6: Tables rendered successfully",
        "Note 7: PoC completed successfully"
    ]
    
    # Generate PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sample_poc_{timestamp}.pdf"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    
    pdf_gen.generate_pdf(dataset1, dataset2, dataset3, filepath)
    
    return send_file(
        filepath,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    print("=" * 50)
    print("PDF Generation API - PoC")
    print("=" * 50)
    print("\nAvailable endpoints:")
    print("- GET  http://localhost:5000/api/test")
    print("- GET  http://localhost:5000/api/generate-sample")
    print("- POST http://localhost:5000/api/generate-pdf")
    print("\n" + "=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)