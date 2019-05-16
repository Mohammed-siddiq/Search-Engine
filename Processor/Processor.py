import os
import pandas as pd

from nltk.stem.porter import *
from nltk.corpus import stopwords
import math
import re
import string
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


'''
Loads the crawled and scraped documents by the spider, 
preprocesses these documents and 
generates the TF-IDF representation of these documents.

'''
DOCUMENT_DIRECTORY = "../WebSpider/uic-docs-text"
ps = PorterStemmer()
stop_words = set(stopwords.words("english"))


def construct_indexed_similarity(similarity):
    score_with_index = {}
    for score, index in zip(similarity, range(0, len(similarity))):
        score_with_index[index] = score[0]
    return score_with_index


def load_documents(path):
    df = pd.DataFrame()
    documents = os.listdir(path)
    for doc in documents:
        #         print("reading doc " , doc)
        try:
            with open(path + "/" + doc, 'r', encoding='ascii', errors='ignore') as content_file:
                content = content_file.read()
                url = re.search('URL : .+?\n', content).group(0)
                doc_id = doc.replace(".txt", "")
            #            print(content)
            df = df.append({'doc_id': doc_id, 'content': content.replace(url, "").strip(),
                            'page_url': url.split(':', 1)[1].strip()},
                           ignore_index=True)
        except Exception as e:
            print(e)
            input()
            continue
    return df


def remove_punctions(word):
    for c in word:
        if c in string.punctuation:
            word = word.replace(c, '')
    return word.strip().lower()


def preprocess_document(document):
    words = document.split()
    preprocessed_doc = []
    for word in words:
        word = remove_punctions(word)
        if word not in stop_words:
            word = ps.stem(word)
            if word not in stop_words and len(word) > 1:
                preprocessed_doc.append(word)
    return ' '.join(preprocessed_doc)


def find_tf(term, document):
    return document.count(term)


def verify_tf_idf(documents):
    tfidf = TfidfVectorizer()
    tf_idf_documents = tfidf.fit_transform(documents)
    return tfidf, tf_idf_documents


def inverse_document_frequency(term, all_documents):
    num_documents_with_this_term = sum(map(lambda document: term in document, all_documents))
    if num_documents_with_this_term > 0:
        return 1.0 + math.log(float(len(all_documents)) / num_documents_with_this_term)
    else:
        return 1.0


def find_idf(documents, all_tokens):
    idf = {}
    for token in all_tokens:
        idf[token] = inverse_document_frequency(token, documents)
    return idf


def find_tf_idf(documents, ids):
    #     tokens = [word for words in documents.Content for word in words]
    idf = find_idf(documents)
    tf_idf_documents = {}
    for document, doc_id in zip(documents, ids):
        docs_tf_idf = {}
        for token in idf.keys():
            tf = find_tf(token, document)
            #             print("TF - ", token, " : ", tf )
            docs_tf_idf.append(tf * idf[token])
        tf_idf_documents.append(docs_tf_idf)
    return tf_idf_documents


def vectorize_documents():
    df = load_documents(DOCUMENT_DIRECTORY)
    df['content'] = df['content'].apply(preprocess_document)
    tfidf, tfidf_documents = verify_tf_idf(df.content)
    return df.page_url, tfidf, tfidf_documents


def persist_raw(FilePath, vectors):
    with open(FilePath, 'wb') as fp:
        pickle.dump(vectors, fp, protocol=pickle.HIGHEST_PROTOCOL)


def load_raw_vectors(Filepath):
    with open(Filepath, 'rb') as fp:
        return pickle.load(fp)


# def persist_ordered_url(urls):
#     with open('Processor/ordered_url.pickle', 'wb') as fp:
#         pickle.dump(urls, fp, protocol=pickle.HIGHEST_PROTOCOL)


def load_ordered_urls():
    with open('Processor/ordered_url.pickle', 'rb') as fp:
        return pickle.load(fp)


def get_cosine_similarity(vector1, vector2):
    return cosine_similarity(vector1, vector2)


def get_top_similar_documents(query, TOP=500):
    tfidf = load_raw_vectors("../Binaries/raw_tfidf.pickle")
    tf_idf_documents = load_raw_vectors(
        "../Binaries/raw_tfidf_docs.pickle")
    print(tfidf)

    query_vector = tfidf.transform([query])
    similar_docs = cosine_similarity(tf_idf_documents, query_vector)
    print(tf_idf_documents)

    # ordered_urls = load_ordered_urls()
    # ordered_urls.get()
    similarity_docs = construct_indexed_similarity(similar_docs)
    # ordered_urls = load_raw_vectors("../Binaries/raw_ordered_urls")
    return sorted(similarity_docs.items(), key=lambda item: item[1], reverse=True)[:TOP]


if __name__ == '__main__':
    # ordered_urls, tfidf, tfidf_documents = vectorize_documents()
    # persist_raw("../Binaries/raw_tfidf.pickle",tfidf)
    # persist_raw("../Binaries/raw_tfidf_docs.pickle",tfidf_documents)
    # print(ordered_urls)
    # persist_raw("../Binaries/raw_ordered_urls.pickle",ordered_urls)
    print(os.listdir("."))
    print(load_raw_vectors("../Binaries/raw_ordered_urls.pickle"))
    print(load_raw_vectors("../Binaries/raw_tfidf_docs.pickle"))
    print(load_raw_vectors("../Binaries/raw_tfidf.pickle"))
