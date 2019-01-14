import os
import sys
import networkx as nx
import random
import numpy as np

from utils.data_handler import DataHandler as dh
from utils import common_tools as ct
from tag_walker import utils

import pdb


def params_handler(params, info, pre_res, **kwargs):
    return {}


def tag_walker(params, info, pre_res, **kwargs):
    """ Return the filepath with the written walks \
            [from_tag, to_tag, weight] = (str, str, int)

        params: the parameters of this module
        info: the whole parameters of model
        pre_res: the results from the previous modules, for this case is HG, G
    """
    res = params_handler(params, info, pre_res)
    prefix = "hybrid_walk_nums_path(%d)_max_path_len(%d)"% \
            (params["num_paths"], params["max_path_len"])
    res["walk_file_details"] = os.path.join(info["network_folder"]["name"], "%s_details.dat"%(prefix))
    res["walk_file"] = os.path.join(info["network_folder"]["name"], "%s.dat"%(prefix))
    assert not os.path.exists(res["walk_file"]), "the walks file has existed!"

    HG = pre_res["construct_graph"]["HG"]
    G = pre_res["construct_graph"]["G"]

    tag_lst = [i for i, n in HG.nodes(data=True) if n["type"] == "tag"]
    tag_st = set(tag_lst)

    info["logger"].info("the number of pathes in tag walker is:  %d x %d = %d" \
            % (params["num_paths"], len(tag_lst), params["num_paths"]*len(tag_lst))) 

    out_mapp = dict() # mapping the tag pair to frequency
    for cnt in range(params["num_paths"]):
        random.shuffle(tag_lst)
        walks = []
        for t in tag_lst:
            # walks should be in origin id system 
            path = walker(HG, G, t, params["c"], params["max_path_len"], params["alpha"])
            if len(path) > 0:
                walks.append(path)
        info["logger"].debug("the (%d)-th time traversal the graph, \
                get the number of walks : (%d)" % (cnt, len(walks)))
        with open(res["walk_file_details"], "a") as f:
            for p in walks:
                f.write(utils.get_output_details(HG, G, p))
                tag_pair = utils.get_output(HG, p)
                out_mapp[tag_pair] = 1 if tag_pair not in out_mapp \
                        else out_mapp[tag_pair] + 1 

    with open(res["walk_file"], "w") as f:
        for k, v in out_mapp.items():
            f.write(k + "\t" + str(v) + "\n")

    info["logger"].info("the walks file path is: %s" % (res))

    return res


### TODO: weighted version with alias table
### now the walker is a version without edge weight
def walker(HG, G, start=None, c=0.5, max_path_len=4, alpha=0.0, rand=random.Random()):
    """ return walk path, that is a list of node id with start node is c
        HG records the relations between tag and entity
        G records the relations between entity
        c is is a hyper-parameter to determine the probability to entity node at the next step
        max_path_len limit the length of the walk path
        alpha is the probablity of restart
    """
    path = [start]

    # if tag break, if len == max_path_len break
    while len(path) < max_path_len:
        cur = path[-1]
        t_cur = HG.node[cur]["type"] if cur in HG else G.node[cur]["type"]

        if len(path) > 1 and t_cur == "tag":
            break

        nei_HG = HG.neighbors(cur) if cur in HG else []
        if start in nei_HG:
            nei_HG.remove(start)
        nei_G = G.neighbors(cur) if cur in G else []
        if len(path) == 1:
            if len(nei_HG) > 0:
                path.append(rand.choice(nei_HG))
                continue
            else:
                break

        # restart probability
        if rand.random() < alpha:
            path.append(path[1]) # return the first entity
            continue


        # for current node is entity
        f_nx = False
        tag_nx, en_nx, nx = None, None, None
        if len(nei_HG) > 0:
            tag_nx = rand.choice(nei_HG)
        if len(nei_G) > 0:
            en_nx = rand.choice(nei_G)

        choose_tag = True if rand.random() > pow(c, float(len(path))) else False
        if tag_nx is None or en_nx is None:
            nx = tag_nx if en_nx is None else en_nx
        else:
            if choose_tag:
                nx = tag_nx
            else:
                nx = en_nx
        
        if nx is None:
            break
        path.append(nx)

    # the path must culminate with a tag
    cur = path[-1]
    t_cur = HG.node[cur]["type"] if cur in HG else G.node[cur]["type"]

    if t_cur != "tag":
        if cur in HG:
            nei = HG.neighbors(cur)
            if start in nei:
                nei.remove(start)
            if len(nei) > 0:
                path.append(rand.choice(nei))
            else:
                path = []
        else:
            path = []

    return path
