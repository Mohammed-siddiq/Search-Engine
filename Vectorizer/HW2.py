
# coding: utf-8

# In[77]:


'''
Name: Mohammed Siddiq
UID:  msiddi56@uic.edu
UIN:  664750555
'''

import pandas as pd
import os
import nltk
import operator
from nltk.stem.porter import *
from nltk.corpus import stopwords 
import math



# In[2]:


stop_words = set(stopwords.words("english"))


# In[3]:


def load_documents(path,df):
    for doc in os.listdir(path):
        with open(path + "//" + doc, 'r') as content_file:    
            content = content_file.read()
#             print(content)
        df = df.append({'Content': content},ignore_index=True)
    return df


# In[4]:


def load_queries(path,qdf):
    with open(path, 'r') as file:
        for line in file:
            query = line.rstrip('\n')
#             print(query)
            qdf = qdf.append({'query': query},ignore_index=True)
    return qdf


# In[5]:


def remove_punctuation(words):
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words


# In[6]:


def remove_stopwords(words):
    new_words = []
    for word in words:
        if word not in stop_words:
            new_words.append(word)
    return new_words


# In[7]:


def stem_words(words):
    stemmer = PorterStemmer()
    stemmed_words = []
    for word in words:
        stemmed_words.append(stemmer.stem(word))
    return stemmed_words


# In[8]:


def extract_text_title_docID(text):
    
    docID = re.search(r'<DOCNO>[\s\S]*?</DOCNO>',text).group(0).replace('<DOCNO>','').replace('</DOCNO>','').strip()
    # extract title
    title_regex = re.compile(r'<TITLE>[\s\S]*?</TITLE>')
    title = title_regex.search(text).group(0)
    title = title.replace("<TITLE>","").replace("</TITLE>","").strip()
#     print("Extracted Title",title)
    text_regex = re.compile(r'<TEXT>[\s\S]*?</TEXT>')
    text = text_regex.search(text).group(0)
    text = text.replace("<TEXT>","").replace("</TEXT>","").strip()
    
#     print("Extracted Text",text)
    return text,title,docID


# In[9]:


def preprocess_get_doc_id(doc_text):
    text,title,docID = extract_text_title_docID(doc_text)
    text = text.lower()
    title = title.lower()
    text = text + title
#     print(doc_text)    
    tokens = nltk.word_tokenize(text)
#     print(tokens)
    words = remove_punctuation(tokens)
    words = stem_words(words)
    words = remove_stopwords(words)
    words.append(docID)
#     print(words)
    return words
    
    


# In[10]:


def preprocess_queries(text):
    text = text.lower()
#     print(text)    
    tokens = nltk.word_tokenize(text)
#     print(tokens)
    words = remove_punctuation(tokens)
#     print(words)
    words = stem_words(words)
    words = remove_stopwords(words)
    return words



df = pd.DataFrame()

docsPath = input("Enter the input folder\n")

print("loading docs...")
df = load_documents(docsPath, df)
print(df.head())



print("pre processing docs")
df.Content = df.Content.apply(preprocess_get_doc_id)

print("Pre-processing of docs done.....")


df['docId'] = df.Content.apply(lambda x: x[-1])
print(df.head())


# In[15]:
print("constructing tf-idf...")


def inverseDocumentFrequency(term, allDocuments):
    numDocumentsWithThisTerm = 0
    numDocumentsWithThisTerm = sum(map(lambda document: term in document,allDocuments))
#     print("number of docs with token", term , " " , numDocumentsWithThisTerm)
    if numDocumentsWithThisTerm > 0:
        return 1.0 + math.log(float(len(allDocuments)) / numDocumentsWithThisTerm)
    else:
        return 1.0


# In[16]:


all_tokens = set([word for words in df.Content for word in words])


# In[17]:


def find_idf(documents):
    idf = {}
    for token in all_tokens:
        idf[token] = inverseDocumentFrequency(token,documents)
#         number_docs_with_token = sum(map(lambda document: token in document,documents))
#         total_number_of_docs = len(documents)
#         idf[token] = math.log(total_number_of_docs/number_docs_with_token)
    return idf


# In[18]:


def find_tf(term,document):
    return document.count(term)


# In[19]:


def find_tf_idf(documents):
    idf = find_idf(documents)
    tf_idf_documents = []
    for document in documents:
        docs_tf_idf = []
        for token in idf.keys():
            tf = find_tf(token,document)
#             print("TF - ", token, " : ", tf )
            docs_tf_idf.append(tf*idf[token])
        tf_idf_documents.append(docs_tf_idf)
    return tf_idf_documents


def find_cosine_similarity(v1,v2):
    dot_product = sum(p*q for p,q in zip(v1, v2))
    magnitude = math.sqrt(sum([val**2 for val in v1])) * math.sqrt(sum([val**2 for val in v2]))
    if not magnitude:
        return 0
    return dot_product/magnitude


# In[22]:


docs_tf_idf = find_tf_idf(df.Content)


# In[23]:

print("Tfidf Construction done ....")
queries_df = pd.DataFrame()
query_path = input("Enter the query file path\n")
queries_df = load_queries(query_path,queries_df)
queries_df.head()


# In[24]:

print("pre processing queries...")
queries_df['q'] = queries_df['query'].apply(preprocess_queries)


# In[25]:

print("pre porcessed queries ..")
print(queries_df.head())


print("queries tfidf construction...")
queries_tf_idf = find_tf_idf(queries_df.q)

print("computing cosine similarity between query and documents")


def find_relevant_docs(query,docs):
    cos_similarity = []
    for doc in docs:
        cos_similarity.append(find_cosine_similarity(doc,query))
    similar_docs = {df.iloc[k]['docId']: v for k, v in enumerate(cos_similarity)}
    ranked_docs = sorted(similar_docs.items(), key=operator.itemgetter(1),reverse=True)
    return ranked_docs


# In[48]:


def rank_docs(queries,docs,rank):
    query_ranked_list = []
    q = 1
    for query in queries:
        ranked_list = []
        ra = find_relevant_docs(query,docs)
        for r in range(rank):
            ranked_list.append((q,int(ra[r][0])))
        q=q+1
        query_ranked_list.append(ranked_list)
    return query_ranked_list


# In[62]:


print("Ranking docs based on cosine similarity")

ranked_docs = rank_docs(queries_tf_idf, docs_tf_idf, 500)

# In[64]:

print("Best 500 ranked documents for each query :\n (query document) ...")


def write_ranked_list(output_path,ranked_list):
    with open(output_path, 'w') as file:
        for r in ranked_list:
            for q, d in r:
                line = str(q) + " " + str(d) + "\n"
                # print(line)
                file.write(line)


# In[65]:


write_ranked_list("output.txt", ranked_docs)

print("output written to file : output.txt")

# In[66]:


output_ranked_list = []
for r in ranked_docs:
    query_rank = []
    for q, d in r:
        query_rank.append(d)
    output_ranked_list.append(query_rank)


def read_relevance_text(path):
    rel_dict = {'1':[],'2':[],'3':[],'4':[],'5':[],'6':[],'7':[],'8':[],'9':[],'10':[]}
    with open(path, 'r') as file:
        for line in file:
            rel = line.rstrip('\n')
            q = rel.split(" ")[0]
            doc = rel.split(" ")[1]
            up_l = rel_dict[q] 
            up_l.append(int(doc))
            rel_dict[q] = up_l
    return rel_dict


relevance_path = input("Enter the relevance file's path\n")
relevant_doc_list = read_relevance_text(relevance_path)
# print(relevant_doc_list)

# Precision = No. of relevant documents retrieved / No. of total documents retrieved
# Recall = No. of relevant documents retrieved / No. of total relevant documents


def get_number_of_relevant_docs (relevant_docs,retrieved_docs,n):
    number = 0
    # print(retrieved_docs)
    # print(relevant_docs[:n])
    for i in range(n):
        if retrieved_docs[i] in relevant_docs:
            number += 1
    # print(number)
    return number


def calculate_precision():
    docs_offset = [10,50,100,500]

    query = 1
    for i in docs_offset:
        precision = 0.0
        recall = 0.0
        for q in range(10): # for each query
            relevant_documents = relevant_doc_list[str(q+1)]
            my_ranked_documents = output_ranked_list[q]
            no_of_rel_docs = get_number_of_relevant_docs(relevant_documents,my_ranked_documents, i)
            # print("number of relevant docs retrieved for query ", q , " ", no_of_rel_docs)
            recall = recall + (no_of_rel_docs / len(relevant_documents))
            precision = precision + no_of_rel_docs /i
        print("Average precision for top ", i , " docs : ", precision/10)
        print("Average recall for top ", i , " docs : ", recall / 10)
        query += 1


calculate_precision()


