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
    Test of the encryption method.
"""

from numpy import int32
import random as ra_random
from numpy import random as np_random

for _ in range(10):
    a = ra_random.randint(0, 1)
    b = np_random.randint(0, 2)
    print("a:", a)
    print("b:", b)
    print()


def encrypt(key, text):
    encrypted_text = ""
    for char in text:
        encrypted_text += chr(ord(key) ^ ord(char))
    return encrypted_text


def decrypt(key, encrypted_text):
    return encrypt(key, encrypted_text)


def key_array_to_key_string(key_array):
    key_string_binary = ''.join([str(x) for x in key_array])
    return ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(key_string_binary)] * 8))


text = 'hahaha'

key_array_4 = [0, 1, 1, 1, 0, 1, 0, 1, 0]
key_array_2 = [1, 0, 1, 0, 1, 1, 0, 1, 0]
key_array_1 = [0, 0, 0, 1, 1, 0, 1, 0, 1]
key_array_3 = [1, 1, 0, 0, 1, 1, 0, 0, 1]

b1 = key_array_to_key_string(key_array_1)
b2 = key_array_to_key_string(key_array_2)
b3 = key_array_to_key_string(key_array_3)
b4 = key_array_to_key_string(key_array_4)

# print("b is", b4, type(b2))


key_array_sum_1 = [key_array_1[i] ^ key_array_2[i] for i in range(len(key_array_1))]
key_array_sum_2 = [key_array_2[i] ^ key_array_3[i] for i in range(len(key_array_1))]
key_array_sum_3 = [key_array_3[i] ^ key_array_4[i] for i in range(len(key_array_1))]

b_sum_1 = key_array_to_key_string(key_array_sum_1)
b_sum_2 = key_array_to_key_string(key_array_sum_2)
b_sum_3 = key_array_to_key_string(key_array_sum_3)

c = encrypt(b1, text)
d = encrypt(b_sum_1, c)
e = encrypt(b_sum_2, d)
f = encrypt(b_sum_3, e)
g = encrypt(b4, f)

# print(g)
