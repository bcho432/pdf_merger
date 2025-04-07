from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def add_page_numbers_to_pdf(input_pdf_path, output_pdf_path):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for i, page in enumerate(reader.pages):
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Times-Roman", 12)
        can.drawString(30, 15, f"{i + 1}")  # set for bottom left
                                            # potentially change to bottom right
        can.save()

        packet.seek(0)
        overlay_pdf = PdfReader(packet)
        page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    with open(output_pdf_path, "wb") as f_out:
        writer.write(f_out)

def merge_pdfs(pdf1_path, pdf2_path, output_path, insert_at=None, add_page_numbers=False):
    merger = PdfMerger()
    merger.append(pdf1_path)
    
    if insert_at is not None:
        merger.merge(insert_at, pdf2_path)
    else:
        merger.append(pdf2_path)
    
    temp_merged = output_path + "_temp.pdf"
    with open(temp_merged, 'wb') as temp_file:
        merger.write(temp_file)
    merger.close()

    if add_page_numbers:
        add_page_numbers_to_pdf(temp_merged, output_path)
        os.remove(temp_merged)
    else:
        os.rename(temp_merged, output_path)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pdf1 = request.files['pdf1']
        pdf2 = request.files['pdf2']
        insert_at = request.form.get('insert_at')
        add_numbers = request.form.get('add_page_numbers') == 'on'

        insert_at = int(insert_at) if insert_at else None

        path1 = os.path.join(UPLOAD_FOLDER, pdf1.filename)
        path2 = os.path.join(UPLOAD_FOLDER, pdf2.filename)
        output_path = os.path.join(UPLOAD_FOLDER, 'merged.pdf')

        pdf1.save(path1)
        pdf2.save(path2)

        merge_pdfs(path1, path2, output_path, insert_at, add_page_numbers=add_numbers)

        return send_file(output_path, as_attachment=True)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
