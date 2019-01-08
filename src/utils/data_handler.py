import os
import sys
import networkx as nx
import json
import numpy as np
from datetime import datetime

class DataHandler(object):
    @staticmethod
    def load_edge(file_path):
        """ 
            Read edge file {int, int [, weight]}
            Return edge list with weight [int, int, float]
        """
        lst = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) < 2:
                    continue
                items = line.split()
                if len(items) == 2:
                    items.append(1) # the weight of edge
                items[0] = int(items[0]) # from node
                items[1] = int(items[1]) # to node
                items[2] = float(items[2]) # edge weight
                lst.append(items)
        return lst

if __name__ == "__main__":
    file_path = "./t.dat"
    lst = DataHandler.load_edge(file_path)
    print (len(lst))
    print ("%d\t%d\t%f" % (lst[0][0], lst[0][1], lst[0][2]))

