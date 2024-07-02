from pdf2image import convert_from_path

images = convert_from_path('in_pdf2.pdf',500,poppler_path=r'C:\Program Files\poppler-23.08.0\Library\bin')

for i in range(len(images)):
    images[i].save('page'+str(i)+'.jpg','JPEG')
