import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
import pickle

class City:

    def __init__(self, g, rho=2): #default rho is 2

        self.rho = rho

        self.g = g
        for _, data in self.g.nodes(data=True):
            data['amt'] = False
            data['inh'] = set()
            data['dow_thr'] = 0
            data['upk'] = None
            data['cmt'] = None
            data['pop_hist'] = []
            data['cmt_hist'] = []

        self.diam = nx.diameter(self.g, weight='length')
        self.dist = dict(nx.all_pairs_dijkstra_path_length(self.g, weight='length'))
        self.dist = pd.DataFrame.from_dict(self.dist).sort_index() / self.diam
        self.dist = self.dist.to_numpy()

        self.amts = None
        self.amts_dist = None

        self.agts = None
        self.agt_dows = None

    def set_amts(self, amts):
        self.amts = amts
        for u in self.amts:
            data = self.g.nodes[u]
            data['amt'] = True
            data['inh'] = None
            data['dow_thr'] = None
            data['upk'] = None
            data['cmt'] = None
            data['pop_hist'] = None
            data['cmt_hist'] = None
        self.amts_dist = np.array([min(self.dist[u][v] for v in self.amts) for u in self.g.nodes()])

    def set_agts(self, agts):
        self.agts = agts
        self.agt_dows = np.array([a.dow for a in self.agts])

    def update(self):
        for u, data in self.g.nodes(data=True):
            if data['amt']:
                continue
            pop = len(data['inh'])
            cmt = np.average(self.agt_dows, weights=[(1 - self.dist[u][a.u]) ** 2 for a in self.agts])
            if pop > 0:
                if pop < self.rho:
                    data['dow_thr'] = 0
                else:
                    data['dow_thr'] = sorted([a.dow for a in self.g.nodes[u]['inh']])[-self.rho]
                data['upk'] = True
            else:
                data['dow_thr'] = 0
                data['upk'] = False
            data['cmt'] = cmt

            data['pop_hist'].append(pop)
            data['cmt_hist'].append(cmt)

    def plot(self, cmap='YlOrRd', figkey=None):

        for u, data in self.g.nodes(data=True):
            if not data['amt']:
                data['dow'] = np.average(self.agt_dows, weights=[a.avg_probabilities[u] for a in self.agts])
                data['dow'] = (data['dow'] - min(city.agt_dows)) / (max(city.agt_dows) - min(city.agt_dows))
                data['pop'] = np.sum([a.avg_probabilities[u] for a in self.agts])
            else:
                data['dow'] = np.nan
                data['pop'] = np.nan

        no_agts = len(self.agts)
        node_size = [no_agts / 10 * data['pop'] if not data['amt'] else no_agts / 2.5 for _, data in self.g.nodes(data=True)]
        node_color = ox.plot.get_node_colors_by_attr(self.g, 'dow', start=0, stop=1, na_color='b', cmap=cmap)
        fig, ax = plt.subplots(figsize=(9, 6))
        cb = fig.colorbar(
            plt.cm.ScalarMappable(cmap=plt.colormaps[cmap]), ax=ax, location='bottom', shrink=0.5, pad=0.05
        )
        cb.set_label('Expected Endowment', fontsize=14)
        ox.plot_graph(self.g, ax=ax, bgcolor='w', node_color=node_color, node_size=node_size)
        plt.show()
        if figkey is not None:
            plt.savefig('./figures/{0}.pdf'.format(figkey), bbox_inches='tight', format='pdf')