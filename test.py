from pdfrw import PdfReader

def get_pdf_page_size(file_path):
    pdf = PdfReader(file_path)
    first_page = pdf.pages[0]
    width = float(first_page.MediaBox[2]) * 4/3
    height = float(first_page.MediaBox[3]) *4/3
    return height, width

get_pdf_page_size("libs/tpdf_templates/409f05934Rtyh/form.pdf")
