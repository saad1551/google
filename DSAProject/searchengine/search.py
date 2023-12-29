from collections import defaultdict
import nltk
from json import load
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
# from lexicon import calculate_word_id
from math import log
import hashlib
import os
import time
from django.conf import settings


nltk.download('punkt')
nltk.download('stopwords')

def calculate_word_id(word):
    word_hash = hashlib.sha256(word.encode()).hexdigest()
    return int(word_hash, 16)


def process_query(query):
    start = time.time()

    ps = PorterStemmer()

    stop_words = set(stopwords.words('english'))

    query_tokenized = word_tokenize(query)

    # remove stop words
    query_filtered = []
    for word in query_tokenized:
        if word.lower() not in stop_words:
            query_filtered.append(word.lower())

    # Stemming
    query_stemmed = []
    # for word in query_tokenized:
    for word in query_filtered:
        query_stemmed.append(ps.stem(word))

    word_ids = []

    for word in query_filtered:
        word_ids.append(calculate_word_id(word))


    # Initialize a defaultdict to store the TF-IDF values for each document

    result = defaultdict(float)


    # Extract last three digits and search for corresponding JSON file
    for word_id in word_ids:
        last_three_digits = str(word_id)[-3:]  # Extract the last three digits
        folder_name = f"searchengine/static/barrels/{last_three_digits}.json"

        
        with open(os.path.join(settings.BASE_DIR, folder_name), "r") as file:
            data = load(file)
            file.close()
            word_data = data.get(str(word_id), {})  # Retrieve word_data, empty dict if not found
            
            # Calculate IDF
            idf = word_data.get("idf", [0, 1])  # Default idf values
            idf_value = idf[0] / idf[1] if idf[1] != 0 else 0  # Calculate IDF
            if idf_value > 0:
                idf_value = log(idf_value, 10)
            # Calculate TF-IDF for each document in word_data
            for doc_id, values in word_data.items():
                if doc_id != "idf":
                    tf = values[2]  # Assuming tf is the third value in the list [weightage, hitlist, tf]
                    
                    # Calculate TF-IDF
                    tf_idf = tf * idf_value  # Multiply tf with the idf value

                    
                    if doc_id in result:
                        result[doc_id] += tf_idf
                    else:
                        result[doc_id] = tf_idf
                        
        # else:
        #     print(f"No JSON file found for word ID {last_three_digits}")

    # Convert the defaultdict to a regular dictionary
    result = dict(result)

    document_ids = sorted(result.keys(), key = lambda x: result[x])

    # return document_ids

    documents = []

    with open(os.path.join(settings.BASE_DIR, f"searchengine/static/dataset.json"), "r") as file:
        dataset = load(file)
        file.close()

        for document_id in document_ids:
            documents.append({
                "url": dataset[int(document_id) - 1]["url"],
                "title": dataset[int(document_id) - 1]["title"]
            })

    end = time.time()

    # # with open("dataset.json", "r") as dataset:
    # #     data = load(dataset)

    # # for document_id in document_ids:
    # #     print(document_id + ": " + str(result[document_id]))


    # # # print(document_ids)
    # # print((end - start) * 1000)

    return documents

#adding this comment because git is not letting me push just the py files

# adding this comment for the same reason as above