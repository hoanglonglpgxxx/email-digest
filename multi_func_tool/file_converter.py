from pdf2docx import Converter

def convert_to_docx(pdf_file):
    docx_file = pdf_file.replace('.pdf', '.docx')
    cv = Converter(pdf_file)
    cv.convert(docx_file)
    cv.close()
