import os
import sys
import json
import argparse
import numpy as np
import networkx as nx
import random
from operator import itemgetter

from utils.env import *
from utils.data_handler import DataHandler as dh
from utils import common_tools as ct

def init(args, params, whole_params):
    """
        1. Inject params configuration of model into info
        2. set logger
        3. set random seed
        4. set symlink for the newly results and log
    """
    info = {}
    for k, v in params.items():
        info[k] = v
    info['time'] = ct.get_time_str()
    info['whole_params'] = whole_params
    info["conf_name"] = args.conf
    info["res_home"] = os.path.join(os.path.join(RES_PATH, args.conf), info["time"])
    info["data_path"] = DATA_PATH
    info["home_path"] = ROOT_PATH
    info["network_folder"] = os.path.join(DATA_PATH, params["network_folder"]["name"])

    log_path = os.path.join(LOG_PATH, info["time"] + ".log")
    info["logger"] = ct.get_logger(log_path)

    ct.symlink(log_path, os.path.join(LOG_PATH, "new_log"))
    ct.symlink(info["res_home"], os.path.join(RES_PATH, "new_res"))

    random.seed(info["random_seed"])
    np.random.seed(info["np_seed"])
    return info

def main():
    parser = argparse.ArgumentParser(formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument("--conf", type = str, default = "template")
    args = parser.parse_args()
    params = dh.load_json(os.path.join(CONF_PATH, args.conf + ".json"))
    info = init(args, params["static_info"], params)
    info["logger"].info("init finished!")

    res = {}
    for module in params["run_modules"]:
        info["logger"].info("run module: %s" % (module["func"]))
        mdl_name = module["func"]
        mdl_params = module["params"]
        mdl = __import__(mld_name + "." + mld_params["func"], fromlist=[mdl_name])
        res[mdl_name] = getattr(mdl, mdl_name)(mdl_params, info = info, pre_res = res, mdl_name = mdl_name)
        # print (res) 

if __name__ == "__main__":
    main()
