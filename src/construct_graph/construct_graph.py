import os
import sys
import networkx as nx

#sys.path.insert(0, "..") # for test
from utils.data_handler import DataHandler as dh
from utils import common_tools as ct


def params_handler(params, info, pre_res, **kwargs):
    params["network_folder"] = info["network_folder"]
    return {}


def construct_graph(params, info, pre_res, **kwargs):
    """
        params: the parameters of the current module
        info: the whole parameters of model
        pre_res: the results from previous modules

        Return: 
            HG: hybrid graph, which illustrate the affiliation relation between tag and entities, node attribute {"type", "oid"=old id}
            G: graph, which illustrate the association relation with entities, node attribute {"oid"}
    """
    res = params_handler(params, info, pre_res) # return {}
    en_id, tag_id, edge_lst, mix_edge_lst = load_graph(params["network_folder"])
    o2n_mp = get_hybrid_idmap(en_id, tag_id)
    info["logger"].info("The number of entities and tags are %d and %d, respectively" % (len(en_id), len(tag_id)))

    HG = init_graph("Hybrid Graph", params["directed"])
    for e, t, w in mix_edge_lst:
        ne = o2n_mp["entity"][e]
        nt = o2n_mp["tag"][t]
        HG.add_node(ne, {"type": "entity", "oid": e})
        HG.add_node(nt, {"type": "tag", "oid": t})
        HG.add_edge(ne, nt, weight=w)

    G = init_graph("Entity Graph", params["directed"])
    for f, t, w in edge_lst:
        nf = o2n_mp["entity"][f]
        nt = o2n_mp["entity"][t]
        G.add_node(nf, {"oid": f})
        G.add_node(nt, {"oid": t})
        G.add_edge(nf, nt, weight=w)

    return HG, G


def load_graph(params):
    """
        params: data file path

        Return:
            en_id: the entity id from 0-(n-1)
            tag_id: the tag id from 0-(n-1)
            edge_lst: entity relations
            mix_edge_lst: entity and tag relations
    """
    en_id = list(dh.load_name(os.path.join(params["name"], params["entity"])).keys())
    tag_id = list(dh.load_name(os.path.join(params["name"], params["tag"])).keys())
    edge_lst = dh.load_edge(os.path.join(params["name"], params["edge"]))
    mix_edge_lst = dh.load_edge(os.path.join(params["name"], params["mix_edge"]))

    return en_id, tag_id, edge_lst, mix_edge_lst


def get_hybrid_idmap(en_id, tag_id):
    """
        build hybrid network node id map with tag and entity

        en_id: entity id list
        tag_id: tag id list

        Return:
            o2n_mp: map from old id to new id for entity and tag respectively
                o2n_mp["tag"] = {}
                o2n_mp["entity"] = {}
    """
    o2n_mp = dict()
    o2n_mp["entity"] = dict()
    o2n_mp["tag"] = dict()
    for i, it in enumerate(en_id):
        o2n_mp["entity"][it] = i
    for i, it in enumerate(tag_id, start=len(en_id)):
        o2n_mp["tag"][it] = i

    return o2n_mp

def init_graph(name=None, directed=False):
    if directed:
        return nx.DiGraph(name=name)
    else:
        return nx.Graph(name=name)


if __name__ == "__main__":
    en_id = [0, 1, 2, 3, 4]
    tag_id = [0, 1, 2]
    n2o_mp, o2n_mp = get_hybrid_idmap(en_id, tag_id)
