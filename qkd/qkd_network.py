########################################################################################################################
# Copyright (c) Xiufan Li. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Author: Xiufan Li
# Supervisor: Patrick Rebentrost
# Institution: Centre for Quantum Technologies, National University of Singapore
# For feedback, please contact Xiufan at: shenlongtianwu8@gmail.com.
########################################################################################################################

# !/usr/bin/env python3

"""
    The building block of QKD networks within a path.
"""


import numpy as np

from qunetsim.components import Host
from qunetsim.components import Network
from qunetsim.objects import Logger

import networkx as nx
from networkx import draw_networkx
import matplotlib.pyplot as plt

from qkd.qkd_node import sniffing_quantum, sniffing_classical
from qkd.qkd_node import send_node, recv_node, trusted_node

Logger.DISABLED = True

# Initialize Networks, create hosts and make connections
def connect(graph):
    # graph = {'Ani': [['sender'], [], ['Arya', ]],
    #          'Arya': [['truster'], [], ['Ani', 'Darren', 'Nayan']],
    #          'Darren': [['truster'], [], ['Xiufan']],
    #          'Nayan': [['truster'], [], ['Arya', 'Xiufan']],
    #          'Xiufan': [['receiver'], [], ['Nayan']]}

    nodes = graph.keys()
    # Initialize a network
    network = Network.get_instance()
    network.delay = 0.0  # Set delay to 0
    network.start(nodes)  # Start the network with the defined hosts

    # Declare the hosts
    host_name_dic = {}
    for n in nodes:
        host_name_dic[n] = Host(n)
    # Add connections
    for n in nodes:
        for recv in graph[n][2]:
            host_name_dic[n].add_connection(recv)
    # Start
    for n in nodes:
        host_name_dic[n].start()
        network.add_host(host_name_dic[n])

    # Spiers start sniffing
    for n in nodes:
        if graph[n][0][0] == 'spier':
            host_name_dic[n].q_relay_sniffing = True
            host_name_dic[n].q_relay_sniffing_fn = sniffing_quantum
            # host_name_dic[n].c_relay_sniffing = True
            # host_name_dic[n].c_relay_sniffing_fn = sniffing_classical
    return host_name_dic, network


# Find all Paths and the optimal path (with smallest number of nodes) given a graph, with sender and receiver
def get_opt_path(graph):
    # graph = {'Ani': [['sender'], [], ['Arya', ]],
    #          'Arya': [['truster'], [], ['Ani', 'Darren', 'Nayan']],
    #          'Darren': [['truster'], [], ['Xiufan']],
    #          'Nayan': [['truster'], [], ['Arya', 'Xiufan']],
    #          'Xiufan': [['receiver'], [], ['Nayan']]}

    G = nx.Graph()
    G.add_nodes_from(list(graph.keys()))
    edges = []

    sender_list = []
    receiver_list = []
    trusted_nodes_list = []
    spy_nodes_list = []

    pos = {}

    for n in graph.keys():
        name = graph[n][0][0]
        recvs = graph[n][2]
        longti = graph[n][1][0]
        lati = graph[n][1][1]
        pos[n] = (longti, lati)
        if name == 'sender':
            sender = n
            sender_list.append(sender)
        elif name == 'receiver':
            receiver = n
            receiver_list.append(receiver)
        elif name == 'truster':
            trusted_nodes_list.append(n)
        elif name == 'spier':
            spy_nodes_list.append(n)
        for v in recvs:
            edges.append((n, v))
    print(edges)
    G.add_edges_from(edges)

    nodes_list = [sender_list, trusted_nodes_list, spy_nodes_list, receiver_list]
    colors = ['red', 'blue', 'gray', 'green']
    # positions = {v: pos for v in list(G.nodes)}
    # positions = spring_layout(G)
    positions = pos

    plt.figure()
    plt.title("QKE Networks Topology", fontsize=22)
    plt.xlabel("Sender (RED)     Receiver (GREEN)     Trusted Nodes (BLUE)     SPY Nodes (GRAY)", fontsize=22)
    # plt.grid()
    for j in range(4):
        for vertex in nodes_list[j]:
            options = {
                'arrows': True,
                'arrowsize': 100,
                # 'arrowstyle':'<|-|>',
                "nodelist": [vertex],
                "node_color": colors[j],
                # "node_shape": '8' if vertex in sender_list or vertex in receiver_list else 'o',
                "node_shape": 'o',
                "with_labels": True,
                'node_size': 10000,
                "width": 5,
                'linewidths': 1.5,
                'font_size': 22,
                'font_color': 'white'
            }
            draw_networkx(G, positions, **options)
            ax = plt.gca()
            ax.margins(0.20)
            plt.axis("on")
            ax.set_axisbelow(True)
    plt.show()
    PATH = list(nx.all_simple_paths(G, source=sender_list[0], target=receiver_list[0]))
    min_len = min([len(p) for p in PATH])
    OPT_PATH = [p for p in PATH if len(p) == min_len]
    return PATH, OPT_PATH


def run_path(path, graph, msg, key_size):
    # Excluded all spiers in the path.
    path_no_spiers = [n for n in path if graph[n][0][0] != 'spier']

    host_name_dic, network = connect(graph)
    # Draws out the classical_network graph
    # network.draw_classical_network()

    # Initialize a thread list
    Th_lst = [_ for _ in range(len(path_no_spiers))]
    # Eavesdropper detection using a counter

    for i in range(len(path_no_spiers)):
        n = path_no_spiers[i]
        name = graph[n][0][0]
        if name == 'sender':
            # Generate random key
            secret_key = np.random.randint(2, size=key_size)
            sender = host_name_dic[n]
            Th_lst[i] = sender.run_protocol(send_node,
                                            arguments=(msg, secret_key, host_name_dic[path_no_spiers[i + 1]]))
        elif name == 'receiver':
            receiver = host_name_dic[n]
            Th_lst[i] = receiver.run_protocol(recv_node, arguments=(key_size, host_name_dic[path_no_spiers[i - 1]]))
        elif name == 'truster':
            # Generate random key
            secret_key = np.random.randint(2, size=key_size)
            truster = host_name_dic[n]
            Th_lst[i] = truster.run_protocol(trusted_node, arguments=(host_name_dic[path_no_spiers[i - 1]],
                                                                      host_name_dic[path_no_spiers[i + 1]],
                                                                      key_size, secret_key))
        else:
            raise ValueError

    for t in Th_lst:  # join all Threads
        t.join()
    network.stop(True)
    # exit()
