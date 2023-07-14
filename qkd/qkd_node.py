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
    Using BB84 protocol and XOR encryption to implement trusted node protocol for quantum key distribution
    between Alice, Bob, and Eve.
"""

from qunetsim.objects import Logger

import random
from qkd.qkd_BB84 import send_bb84, receive_bb84
from qkd.qkd_crypto import encrypt_msg, decrypt_msg, send_msg, recv_msg
Logger.DISABLED = True

wait_time = 10
qkd_key_length = 13
ERROR_RATE = 10

EAVESDROPPER_NUMBER = 1
# Eve randomly choose a number from [0, 1, ..., 9].
# If the randomly chosen number is larger than 'EAVESDROPPER_NUMBER', Eve performs X gate.

CRED = '\033[91m'
CEND = '\033[0m'
CGREEN = '\33[32m'
CBLUE = '\33[34m'
CYELLOW = '\33[33m'
CREDBG = '\33[41m'
CGREENBG = '\33[42m'
CRED2 = '\33[91m'
CGREEN2 = '\33[92m'


# Send keys between nodes
def send_node(sender, msg, secret_key, receiver):
    print(str(sender.host_id) + " encrypts the message: " + msg)
    print()
    send_key, eves = send_bb84(sender, secret_key, receiver.host_id)
    # if eves > 0:
    #     raise KeyError
    # else:
    encrypted_msg = encrypt_msg(send_key, msg)
    send_msg(sender, encrypted_msg, receiver.host_id)


# Receive keys between nodes
def recv_node(receiver, key_size, sender):
    recv_key, eves = receive_bb84(receiver, key_size, sender.host_id)
    # if eves > 0:
    #     raise KeyError
    # else:
    encrypted_msg = recv_msg(receiver, sender.host_id)
    decrypted_msg = decrypt_msg(recv_key, encrypted_msg)
    print(str(receiver.host_id) + " decrypts the message: " + decrypted_msg)


# Code for trusted node, works for any number
def trusted_node(trusted_node, prev_node, next_node, key_size, secret_key):
    # Build the QKD protocol with the previous node and obtain the private key, then receive encrypted message
    prev_key, eves = receive_bb84(trusted_node, key_size, prev_node.host_id)
    # if eves > 0:
    #     raise KeyError
    # else:
    msg = recv_msg(trusted_node, prev_node.host_id)

    # Build the QKD protocol with the next node and obtain the private key
    next_key, eves = send_bb84(trusted_node, secret_key, next_node.host_id)
    # if eves > 0:
    #     raise KeyError
    # else:
    # Use the previous QKD key and the next QKD key to construct the new key by: ord(K12) = ord(K2) ^ ord(K1)
    new_key = [(prev_key[j] + next_key[j]) % 2 for j in range(min([len(prev_key), len(next_key)]))]

    # Encrypt the message with the new key and send the message to the next node
    msg = encrypt_msg(new_key, msg)
    send_msg(trusted_node, msg, next_node.host_id)


# Spy Function for eavesdropping on BB84_main communication
# def spy_node(spy_node, sender, receiver, key_size):
#     basis = []  # Measurement basis record
#     key = []  # Raw key
#     count = 0  # Count of bits received
#
#     while count < key_size:
#         # Receive qubit from the sender
#         base = random.randint(0, 1)  # choose a random measurement base
#         basis.append(base)  # save the measurement basis
#         q_bit = spy_node.get_qubit(sender, wait=wait_time)  # wait for the qubit
#
#         if base: q_bit.H()  # apply Hadamard if base is X
#         bit = q_bit.measure()  # measure the qubit
#         key.append(bit)  # save the full raw key
#
#         # Send qubit to receiver
#         # base = random.randint(0, 1)  # choose a random basis 0 = Z basis, 1 = X basis
#         q_bit = Qubit(spy_node)  # create qubit
#
#         if bit: q_bit.X()  # qubit flip operation if bit = 1
#         if base: q_bit.H()  # Apply basis change if necessary
#
#         spy_node.send_qubit(receiver, q_bit, await_ack=False)  # Send Qubit to Bob
#         count += 1

# Spy Function using the sniffing method
# Code for Eavesdropper sniffing
def sniffing_quantum(sender, receiver, qubit):
    # Spy applies an X operation to all qubits that are routed through him.
    a = random.randint(0, 9)
    if a > EAVESDROPPER_NUMBER:
        qubit.X()

def sniffing_classical(sender, receiver, msg):
    # Bob modifies the message content of all classical messages routed through him
    msg.content = "['Darren was here :) ']" + msg.content
