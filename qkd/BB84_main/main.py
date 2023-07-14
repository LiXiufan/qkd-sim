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
    The main execution.
"""

from qkd.qkd_protocol import QKD
# from qkd_B92 import QKD

# nodes = ['Alice', 'Bob', 'Eve']
# edges = [('Alice', 'Bob'), ('Bob', 'Alice'), ('Bob', 'Eve'), ('Eve', 'Bob')]
# nodes = ['Ani', 'Arya', 'Darren', 'Nayan', 'Xiufan']
# edges = [('Ani', 'Arya'), ('Arya', 'Ani'),
#          ('Arya', 'Darren'), ('Darren', 'Arya'),
#          ('Darren', 'Nayan'), ('Nayan', 'Darren'),
#          ('Nayan', 'Xiufan'), ('Xiufan', 'Nayan')]
# graph = [nodes, edges]
# graph = {'Ani': [['sender'], ['Arya',]],
#          'Arya': [['truster'], ['Ani', 'Darren', 'Nayan']],
#          'Darren': [['truster'], ['Xiufan']],
#          'Nayan': [['truster'], ['Arya', 'Xiufan']],
#          'Xiufan': [['receiver'], ['Nayan']]}
CQT_pos = [103.7800945, 1.2970694]
Horizon_pos = [103.8266290740217, 1.262059000000001]
NTU_pos = [103.68293320728537, 1.3484104000000001]
SMU_pos = [103.92004365998248, 1.29616795]
SUTD_pos = [103.96434326603818, 1.341603]

graph = {'Ani': [['sender'], NTU_pos, ['Arya',]],
         'Arya': [['truster'], CQT_pos, ['Ani', 'Darren', 'Nayan']],
         'Darren': [['spier'], Horizon_pos, ['Xiufan']],
         'Nayan': [['truster'], SMU_pos, ['Arya', 'Xiufan']],
         'Xiufan': [['receiver'], SUTD_pos, ['Nayan']]}

message = "Hey, are you nervous for the presentation??"
key_size = 180  # the size of the key in bit for BB84_main
# key_size = 180 # the size of the key in bit for B92

if __name__ == '__main__':
    QKD(graph, message, key_size)
