import json
from bs4 import BeautifulSoup
from transformers import pipeline
import pytesseract
import mysql.connector
from flask import Flask, jsonify, request
import fitz 
from PIL import Image
import requests
from frontend import *
from pdf2image import convert_from_path
import pandas as pd
import tabula
from duckpy import Client
from elasticsearch import Elasticsearch
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
'''
#configuring database
db_config = {
    'host': 'localhost',      # Usually 'localhost' if the database is on the same server
    'user': 'root',
    'password': '',
    'database': 'course_enhancer',
}

conn = mysql.connector.connect(**db_config)
'''

# Path to Tesseract executable (change this to your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\nisha\OneDrive\Desktop\vivek\jnana_marg_development\invoice_OCR_AI\tesseract\Tesseract-OCR\tesseract.exe'


#getting google search results link
def get_google_search_links(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        result_divs = soup.find_all('div', class_='tF2Cxc')  # Adjust the class based on the current structure

        links = []
        for result_div in result_divs:
            link_tag = result_div.find('a')
            if link_tag:
                href_value = link_tag.get('href')
                clean_url = href_value.split('&')[0]
                links.append(clean_url)

        return links
    else:
        print(f"Failed to fetch {url}. Status code: {response.status_code}")
        return []

#function to highlight text in pdf
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
    
     
#extracting key value pair from invoices using pdf path   
def extract_info_from_invoice(pdf_path):
    url_parts = pdf_path.split('/')
    lasts_part = url_parts[-1]
    last_parts = lasts_part.split('.pdf')
    if last_parts:
        last_part = last_parts[0]+".pdf"
    else:
        last_part = lasts_part
    image_name = last_part.split('.pdf')    
    images = []   
    images = convert_from_path(pdf_path,500,poppler_path=r'C:\Program Files\poppler-23.08.0\Library\bin')
    for i in range(len(images)):
        img_path = "images/image_"+ str(image_name[0]) +'.jpg'
        images[i].save(img_path,'JPEG')
        img_Path = img_path

        models_checkpoints = {
            "LayoutMv1":"impira/layoutlm-document-qa",
            "LayoutMv1 for Invoices":"impira/layoutlm-invoices",
            "Donut":"naver-clova-ix/donut-base-finetuned-docvqa",
        }
        pipe = pipeline("document-question-answering",model = models_checkpoints["LayoutMv1 for Invoices"])
        
        #generating description
        company = pipe(image=img_Path,question="It belongs to which website Amazon or Flipkart or Apple or what?")[0]["answer"]
        
        #generating description through dataFrame
        file = pdf_path
        tables = tabula.read_pdf(file,pages="all")
        if len(tables) != 0:
            df = pd.concat(tables, ignore_index=True)
            print(df)
            if 'Description' in df.columns:
                desc = df['Description'].iloc[0] +"\n"
                desc += df['Description'].iloc[1]
            elif 'Sl.' in df.columns:
                desc = df['Sl.'].iloc[2]
                #desc += df['Sl.'].iloc[3]
            elif 'Title' in df.columns:
                desc = df['Title'].iloc[2]
                #desc += df["Title"].iloc[3]
            else:
                #generating description through pipeline
                desc = pipe(image=img_Path,question="what is the Full Title or Full Description of the product?")[0]["answer"]
        else:
            desc = pipe(image=img_Path,question="what is the Full Title or Full Description of the product?")[0]["answer"]
        print(company)
        print(desc) 
        #getting Links to purchase
        # results = Client().search(desc)
        # if results:
        #     link = results[0].url
        # else:
        #     link = "No link Found"
        
        links = get_google_search_links(desc)
        link = ""
        for li in links[:1]:
            link = link + li
          
        #getting yt videos related to this 
        # YouTube Data API key.
        #my key AIzaSyCAdrtgNARFEl0oDZoKCfC7lKmBv409t6w
        #my 2nd key AIzaSyB5fvApLJKnnNgFdz5Vxae_vTHY-j97Wnc
        API_KEY = 'AIzaSyB5fvApLJKnnNgFdz5Vxae_vTHY-j97Wnc'
        search_query = request.args.get('q', str(desc))
        max_results = request.args.get('maxResults', 1)
        
        # Define the API endpoint URL.
        api_url = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults={max_results}&q={search_query}&key={API_KEY}"
        # Send a GET request to the YouTube API.
        response = requests.get(api_url)

        # Check if the request was successful.
        if response.status_code == 200:
            data = response.json()
            # Check if 'items' key exists in the response data
            if 'items' in data:
                #video_ids = [item['id']['videoId'] for item in data['items'] if 'id' in item and 'videoId' in item['id']]
                titles_and_video_ids = [(item['snippet']['title'], item['id']['videoId'], item['snippet']['thumbnails']['high']['url']) for item in data['items'] if 'id' in item and 'videoId' in item['id']]
                # Create a list of dictionaries for each title and videoID pair
                titles_and_video_id = [{"title": title, "videoID": video_id, "thumbnail": thumbails} for title, video_id,thumbails in titles_and_video_ids]  
                videos = titles_and_video_id       
            else:
                videos = "No videos available."
        else:
            videos = "unable to find videos."
            
        
        name = pipe(image=img_Path,question="To whom this invoice refers?")[0]["answer"]
        address = pipe(image=img_Path,question="what is the address?")[0]["answer"]
        #phone = pipe(image=img_Path,question="what is the phone number?")[0]["answer"]
        pan = pipe(image=img_Path,question="what is the PAN number?")[0]["answer"]
        total = pipe(image=img_Path,question="what is the total amount?")[0]["answer"]
        invoice_number = pipe(image=img_Path,question="what is the invoice number?")[0]["answer"]
        invoice_date = pipe(image=img_Path,question="what is the invoice date?")[0]["answer"]
        
        whole_text_highlight = name+" "+address+" "+pan+" "+total+" "+invoice_number+" "+invoice_date+" "+desc 
        output_path = "highlighted_pdf_database/highlight_" + last_part
        highlight_text(pdf_path, output_path, whole_text_highlight)
        
        response = {
            "product_description":desc,    
            "link_to_buyAgain":link,
            "name":name,
            "address":address,
            "PAN":pan,
            "total":total,
            "invoice_number":invoice_number,
            "invoice_date":invoice_date,
            "product_review_video":videos
        }
        return response
    
@app.route("/query_from_invoice" , methods = ['POST', 'OPTIONS'])
def query_from_invoice():
    if request.method == 'OPTIONS':
        return '', 200  # Handle CORS preflight
    
    try:
        data = request.get_json()
        pdf_path = data.get('pdf_path', '')
        query = data.get('query', '')
        url_parts = pdf_path.split('/')
        lasts_part = url_parts[-1]
        last_parts = lasts_part.split('.pdf')
        if last_parts:
            last_part = last_parts[0]+".pdf"
        else:
            last_part = lasts_part
        image_name = last_part.split('.pdf')    
        images = []   
        images = convert_from_path(pdf_path,500,poppler_path=r'C:\Program Files\poppler-23.08.0\Library\bin')
        for i in range(len(images)):
            img_path = "images/image_"+ str(image_name[0]) +'.jpg'
            images[i].save(img_path,'JPEG')
            img_Path = img_path

            models_checkpoints = {
                "LayoutMv1":"impira/layoutlm-document-qa",
                "LayoutMv1 for Invoices":"impira/layoutlm-invoices",
                "Donut":"naver-clova-ix/donut-base-finetuned-docvqa",
            }
            pipe = pipeline("document-question-answering",model = models_checkpoints["LayoutMv1 for Invoices"])
            
            ans = pipe(image=img_Path,question=query)[0]["answer"]
            
        return jsonify({'query': ans})
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Failed to process request'}), 500
    
    

#function to extract images from one pdf
@app.route("/extract_one_pdf" , methods = ['POST'])
def extract_images_from_pdf():
    
    data = request.get_json()
    url = data['url']
    images = []
    
    '''
    response = requests.get(url)
    my_raw_data = response.content

    with open("my_pdf.pdf", 'wb') as my_data:
        my_data.write(my_raw_data)
    open_pdf_file = open("my_pdf.pdf", 'rb')
    '''
    #pdf_path = open_pdf_file
    pdf_path = url
    
    res = extract_info_from_invoice(pdf_path)
    json_data = json.dumps(res)
    return jsonify(res)

@app.route("/extract_many_pdf" , methods = ['POST'])
def extract_images_from_many_pdf():
    if request.method == 'POST':
        total_list_data = []
        data = request.get_json()
        num_url = data['num_url']
        urls = data['urls']
        list_of_url = urls.split(',')
        for i in list_of_url:
            # url = data['url'+str(i)]
            url = i
            images = []
            
            '''
            response = requests.get(url)
            my_raw_data = response.content

            with open("my_pdf.pdf", 'wb') as my_data:
                my_data.write(my_raw_data)
            open_pdf_file = open("my_pdf.pdf", 'rb')
            '''
            #pdf_path = open_pdf_file
            pdf_path = url
            
            #JSON res
            res = extract_info_from_invoice(pdf_path)
            total_list_data.append(res)
        total_json_data = json.dumps(total_list_data)
        return total_json_data
    return jsonify("Not post method")
        
#performing elastic search
@app.route('/elastic_search', methods = ['POST'])
def elastic_search():
    if request.method == 'POST':
        es = Elasticsearch([{'scheme':'http','host': 'localhost', 'port': 9200}])
        data = request.get_json()
        token_id = data['token_id']
        invoice_data = data['invoice_data']
        query = data['query']
        index_name = token_id
        es.indices.create(index=index_name, ignore=400)
        
        data = []
        for item in invoice_data:
            invoice_number = item['invoice_number']
            invoice_date = item['invoice_date']
            pan_number = item['pan_number']
            name = item['name']
            address = item['address']
            product_description = item['product_description']
            total_value = item['total_value']
            purchase_links = item['purchase_links']
            related_video_id = item['related_video_id']
            related_video_title = item['related_video_title']
            related_video_thumbnail = item['related_video_thumbnail']
            res = {
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "pan_number": pan_number,
                "name": name,
                "address": address,
                "product_description": product_description,
                "total_value": total_value,
                "purchase_links": purchase_links,
                "related_video_id": related_video_id,
                "related_video_title": related_video_title,
                "related_video_thumbnail": related_video_thumbnail
            }
            data.append(res)
            
        for document in data:
            es.index(index=index_name, document=document, id=document['invoice_number'])
        es.indices.refresh(index=index_name)
        queries = {
            "query": {
                "simple_query_string": {
                "query": query
                }
            },
            "request_cache": False
        }
        response = []
        results = es.search(index=index_name, body=queries)
        for hit in results['hits']['hits']:
            invoice = hit['_source']
            response.append(invoice)
        print(response)
        return jsonify(response)
        


if __name__ == "__main__":
    app.run(debug = True)
        
