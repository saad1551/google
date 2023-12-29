from django.shortcuts import render
from django.http import HttpResponse

from .search import process_query

import os 
from django.conf import settings

import hashlib

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from json import load, dumps, loads, dump

nltk.download('punkt')
nltk.download('stopwords')

# Create your views here.

def calculate_word_id(word):
    word_hash = hashlib.sha256(word.encode()).hexdigest()
    return int(word_hash, 16)

def index(request):
    if request.method == "POST":
        query = request.POST.get('query')
        document_ids = process_query(query)
        return render(request, 'searchengine/index.html', {
            "docs": document_ids
        })
    return render(request, 'searchengine/index.html')


def add_content(request):
    if request.method != "POST":
        return HttpResponse("This is a portal for adding new content to this search engine and a POST request is required for this")
    
    new_content = request.FILES['json_file'].read()

    folder_name = "searchengine/static/dataset.json"

    ps = PorterStemmer()

    stop_words = set(stopwords.words('english'))

    
    with open(os.path.join(settings.BASE_DIR, folder_name), "r") as file:
        dataset = load(file)
        file.close()

        for article in new_content:
            id = 120000
             # Tokenize content and title
            content_tokens = word_tokenize(article['content'])
            title_tokens = word_tokenize(article['title'])

            # Remove stop words from content
            content_filtered = []
            for word in content_tokens:
                if word.lower() not in stop_words:
                    content_filtered.append(word)

            # Remove stop words from title
            title_filtered = []
            for word in title_tokens:
                if word.lower() not in stop_words:
                    title_filtered.append(word)

            # tokens that we don't need for query processing such as punctuations and special symbols
            unwanted_tokens = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']

            # Perform stemming on content
            content_stemmed = []
            for word in content_filtered:
                if word not in unwanted_tokens:
                    content_stemmed.append(ps.stem(word))

            # Perform stemming on title
            title_stemmed = []
            for word in title_filtered:
                if word not in unwanted_tokens:
                    title_stemmed.append(ps.stem(word))


            article["length"] = len(content_stemmed) + len(title_stemmed)

                   # Update article with processed content and title
            article['content'] = ' '.join(content_stemmed)
            article['title'] = ' '.join(title_stemmed)

            with open(os.path.join(settings.BASE_DIR, folder_name), "r") as file:
                dataset = load(file)
                file.close()

            for word in content_stemmed:
                last_three_digits = str(calculate_word_id(word))[-3:]  # Extract the last three digits
                folder_name = f"searchengine/static/barrels/{last_three_digits}.json"

                idf_increment = False
        

                word_data = dataset.get(str(calculate_word_id(word)), {})  # Retrieve word_data, empty dict if not found
                word_data[id] = [0, 0]
                if not idf_increment:
                    word_data["idf"] += 1
                    idf_increment = True


            dataset.append({
                "id": id,
                "url": article["url"],
                "title": article["title"]
            })

        with open(os.path.join(settings.BASE_DIR, folder_name), "r") as file:
            dump(dataset, file)
            file.close()

        return render(request, 'searchengine/index.html', {
            "message": "Successfully added new content"
        })

