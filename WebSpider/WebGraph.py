import os
import pickle

'''
Graph construction for the uic domain.
'''


class Graph:
    graph = {}
    links_lookup = {}  # Look up for each link
    LINKS_DIRECTORY = "uic-web-graph"
    '''
    Adds a link to a lookup table, signifies the in-links to a particular node
    '''

    def add_links_to_lookup(self, node, linking_node):
        if node != linking_node:
            if node not in self.links_lookup:
                self.links_lookup[node] = set()
            self.links_lookup[node].add(linking_node)

    def get_out_degree(self, node):
        return len(self.graph[node])

    def set_node(self, node):
        if node not in self.graph:
            self.graph[node] = {}

    def set_edge(self, node1, node2):
        if node1 not in self.graph:
            self.set_node(node1)
        self.graph[node1][node2] = 1
        self.add_links_to_lookup(node2, node1)

    def get_edge(self, node1, j):
        if node1 in self.graph:
            if j in self.graph[node1]:
                return self.graph[node1][j]
        return -1

    def get_linking_nodes(self, node):
        if node in self.links_lookup:
            return self.links_lookup[node]
        else:
            return set()

    def construct_graph(self):
        files = os.listdir(self.LINKS_DIRECTORY)
        for file in files:
            with open(self.LINKS_DIRECTORY + "/" + file, "r") as f:
                raw_links = f.read()
                node = raw_links.split("::")[0]
                out_link_nodes = raw_links.split("::")[1].split(",")
                self.set_node(node)
                for out_link in out_link_nodes:
                    if "uic.edu" in out_link.strip():
                        self.set_edge(node1=node, node2=out_link)
        return self.graph

    def calculate_rank(self, a, previous_rank, alpha):

        return alpha * sum(previous_rank[b] / self.get_out_degree(b) for b in self.get_linking_nodes(a)) + \
               (1 - alpha) / len(self.graph)

    def run_page_rank(self, alpha, max_iterations):
        page_rank = {}
        last_page_rank = {}

        for node in self.graph:
            page_rank[node] = 1 / len(self.graph)
            last_page_rank[node] = 1 / len(self.graph)
        for iteration in range(0, max_iterations):
            for node in self.graph:
                page_rank[node] = self.calculate_rank(node, last_page_rank, alpha)
            early_exit = True
            for node in page_rank:
                if early_exit and last_page_rank[node] != page_rank[node]:
                    early_exit = False
                last_page_rank[node] = page_rank[node]
            if early_exit:
                return page_rank
        return page_rank

    def construct_graph_and_run_page_rank(self, alpha, max_iterations):
        self.construct_graph()
        ranked_graph = self.run_page_rank(alpha, max_iterations)
        return ranked_graph

    def persist_rank(self, ranked_graph):
        with open("uic-web-graph-output/pageRank", "w") as f:
            f.write('\n'.join('{} {}'.format(rank[0], rank[1]) for rank in ranked_graph))

    def persist_rank_binary(self, ranked_graph):
        with open('../Binaries/raw_page_ranks.pickle', 'wb') as handle:
            pickle.dump(ranked_graph, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_raw_pageranks(self):
        with open('../Binaries/raw_page_ranks.pickle', 'rb') as fp:
            return pickle.load(fp)


if __name__ == '__main__':
    uic_domain_graph = Graph()
    ranked_graph = uic_domain_graph.construct_graph_and_run_page_rank(0.15, 1000)
    print(len(ranked_graph))
    ranked_graph = sorted(ranked_graph.items(), key=lambda item: item[1], reverse=True)
    for x in ranked_graph:
        print(x)
    uic_domain_graph.persist_rank(ranked_graph)
    uic_domain_graph.persist_rank_binary(ranked_graph)
