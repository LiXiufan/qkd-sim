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
    QKD protocol with trusted node implementation and Eavesdropper detection.
"""


from qunetsim.objects import Logger
Logger.DISABLED = True

from qkd.qkd_network import get_opt_path, run_path
def QKD(graph, msg, key_size):

    # Get all paths and the optimal path from sender to receiver
    PATH, OPT_PATH = get_opt_path(graph)

    # Run protocol with a path
    # EAVES_DETECTOR = 0
    path = OPT_PATH[0]

    run_path(path, graph, msg, key_size)

    OPT_PATH = [i for i in OPT_PATH if i != path]
    PATH = [i for i in PATH if i != path]
    if OPT_PATH:
        path = OPT_PATH[0]
        run_path(path, graph, msg, key_size)
    else:
        if PATH:
            path = PATH[0]
            run_path(path, graph, msg, key_size)




