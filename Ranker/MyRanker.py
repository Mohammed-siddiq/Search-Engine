from Processor.Processor import load_raw_vectors, get_cosine_similarity, construct_indexed_similarity


'''
The ranker module runs the page rank algorithm over the UIC graph constructed by the Spider. 
This page rank runs only once and the ranks of each page with its score is persisted in the binary format in Binaries/ directory.
'''

def rank_urls(similarity_score):
    ordered_urls = load_raw_vectors("Binaries/raw_ordered_urls.pickle")
    page_ranks = dict(load_raw_vectors("Binaries/raw_page_ranks.pickle"))

    score_with_page_rank = {}
    for id, score in similarity_score:
        url = ordered_urls.get(id)
        urls_rank = page_ranks.get(url)
        final_score = urls_rank + score
        score_with_page_rank[url] = final_score

    ranked_urls = sorted(score_with_page_rank.items(), key=lambda item: item[1], reverse=True)
    print(ranked_urls)
    # top_ranked_urls = []
    # for id, score in similarity_score:
    #     top_ranked_urls.append((ordered_urls.get(id), score))
    # print(top_ranked_urls)
    return ranked_urls


def get_search_result(query, TOP=500):
    tfidf = load_raw_vectors("Binaries/raw_tfidf.pickle")
    tf_idf_documents = load_raw_vectors("Binaries/raw_tfidf_docs.pickle")
    # print(tfidf)

    query_vector = tfidf.transform([query])
    similar_docs = get_cosine_similarity(tf_idf_documents, query_vector)
    # print(tf_idf_documents)

    # ordered_urls = load_ordered_urls()
    # ordered_urls.get()
    similarity_docs = construct_indexed_similarity(similar_docs)
    similarity_score = sorted(similarity_docs.items(), key=lambda item: item[1], reverse=True)[:TOP]

    return rank_urls(similarity_score)



