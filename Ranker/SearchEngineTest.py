import os
from Ranker.MyRanker import get_search_result

'''
Testing search engine
'''
if __name__ == '__main__':
    query = "uic latest news today"
    print(os.listdir("."))
    urls = get_search_result(query)
    print(query)
    [print(url) for url in urls]
