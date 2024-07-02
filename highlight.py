import fitz  # PyMuPDF

def highlight_text(pdf_path, output_path, text_to_highlight):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        words = page.get_text_words()
        for word in words:
            word_text = word[4]  # Convert the tuple to a string
            whole_text = text_to_highlight.split()
            
            for t in whole_text:
                if t in word_text:
                    x0, y0, x1, y1 = word[:4]  # Extract the coordinates from the tuple
                    rect = fitz.Rect(x0, y0, x1, y1)
                    highlight = page.add_highlight_annot(rect)

    # Save the modified PDF with highlighted text
    pdf_document.save(output_path)
    pdf_document.close()

if __name__ == "__main__":
    pdf_path = "in_pdf8.pdf"  # Replace with the path to your PDF file
    output_path = "output.pdf"  # Replace with the path for the output PDF
    text_to_highlight = "SAMAVAR IN-225"  # Replace with the text you want to highlight
    highlight_text(pdf_path, output_path, text_to_highlight)
    
