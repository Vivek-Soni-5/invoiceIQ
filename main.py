import torch
from transformers import pipeline
import pandas as pd
import re
import tabula
import pytesseract
from PIL import Image


# Path to Tesseract executable (change this to your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\nisha\OneDrive\Desktop\vivek\jnana_marg_development\invoice_OCR_AI\tesseract\Tesseract-OCR\tesseract.exe'


img_Path = "in2.jpg"
image = Image.open(img_Path)

# Perform OCR on the image
#total amount
ocr_text = pytesseract.image_to_string(image)
#print(ocr_text)


tqa = pipeline(task="table-question-answering",model="google/tapas-base-finetuned-wtq")

file = "in_pdf10.pdf"
tables = tabula.read_pdf(file,pages="all")
df = pd.concat(tables, ignore_index=True)
df.to_csv("all_tables.csv", index=False)

print(df['Sl.'].iloc[2])

tab = pd.read_csv("all_tables.csv",header = [0])
tab = tab.astype(str)
print(tab)

pp = pd.read_csv("all_tables.csv")
#print(pp[3]['Title'])
query = "what is total value?"
print(tqa(table=tab,query=query)["answer"])