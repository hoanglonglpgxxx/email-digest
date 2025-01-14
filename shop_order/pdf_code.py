from fpdf import FPDF

pdf = FPDF(orientation="P", unit="m", format="A4")
pdf.add_page()

pdf.set_font(family="Times", size=16, style="B")
pdf.cell(w=50, h=8, txt=f'Receipt nr.1', ln=1)


pdf.set_font(family="Times", size=16, style="B")
pdf.cell(w=50, h=8, txt=f'Article: Laptop Sven', ln=1)

pdf.set_font(family="Times", size=16, style="B")
pdf.cell(w=50, h=8, txt=f'Price: 9999', ln=1)

pdf.output('receipt.pdf')