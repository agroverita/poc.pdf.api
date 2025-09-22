from flask import Flask, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

app = Flask(__name__)

# Sample data
data = [
    {"title": "Introduction", "content": "This is the introduction."},
    {"title": "Chapter 1", "content": "This is the content of chapter 1."},
    {"title": "Chapter 2", "content": "This is the content of chapter 2."},
]

def create_pdf(filename):
    pdf_path = os.path.join("pdfs", filename)
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Create clickable index
    c.drawString(1 * inch, height - 1 * inch, "Clickable Index")
    for idx, item in enumerate(data):
        c.drawString(1 * inch, height - (1 * inch + (0.5 * idx * inch)), f"{idx + 1}. {item['title']}")
        c.linkAbsolute(f"{idx + 1}. {item['title']}", pdf_path, (1 * inch, height - (1 * inch + (0.5 * idx * inch)), 2 * inch, height - (1 * inch + (0.5 * (idx + 1) * inch))))

    c.showPage()

    # Add content for each section
    for item in data:
        c.drawString(1 * inch, height - 1 * inch, item['title'])
        c.drawString(1 * inch, height - 1.5 * inch, item['content'])
        c.showPage()

    c.save()

@app.route('/generate_pdf')
def generate_pdf():
    filename = "report.pdf"
    create_pdf(filename)
    return send_file(os.path.join("pdfs", filename), as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists("pdfs"):
        os.makedirs("pdfs")
    app.run(debug=True)