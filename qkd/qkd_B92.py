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
    B92 protocol for quantum key distribution.
"""


# from random import random
from numpy import int32
from qunetsim.components.host import Host
from qunetsim.components.network import Network
from qunetsim.objects import Qubit
from qunetsim.objects import Logger
import random

Logger.DISABLED = True
qkd_key_length = 10
WAIT_TIME = 10
CRED = '\033[91m'
CEND = '\033[0m'
CGREEN = '\33[32m'
CBLUE = '\33[34m'

# Basis Declaration
BASIS = ['Z', 'X']  # |0>|1> = Z-Basis; |+>|-> = X-Basis


##########################################################################


def entangle(host):  # 00 + 11
    q1 = Qubit(host)
    q2 = Qubit(host)
    q1.H()
    q1.cnot(q2)
    return q1, q2


def preparation(key_size):
    alice_basis = ""
    bob_basis = ""
    for kl in range(key_size):
        alice_basis += random.choice(BASIS)
        bob_basis += random.choice(BASIS)
    return alice_basis, bob_basis


def alice_key_string(alice_bits, alice_basis, bob_basis, key_size):
    sample_size = int(key_size / 4)
    alice_key = ""
    for i in range(sample_size):
        if alice_basis[i] == bob_basis[i]:
            alice_key += str(alice_bits[i])
    # print("Alice Key: {}".format(alice_key))
    return alice_key


def bob_key_string(bob_bits, bob_basis, alice_basis, key_size):
    sample_size = int(key_size / 4)
    bob_key = ""
    for i in range(sample_size):
        if bob_basis[i] == alice_basis[i]:
            bob_key += str(bob_bits[i])
    # print("Bob Key: {}".format(bob_key))
    return bob_key


def send_qkd(host, receiver, alice_basis, key_size):
    alice_measured_bits = ""
    # For Qubit and Basis
    for basis in alice_basis:
        q1, q2 = entangle(host)
        ack_arrived = host.send_qubit(receiver, q2, await_ack=False)
        if ack_arrived:
            if basis == 'Z':
                alice_measured_bits += str(q1.measure())
            if basis == 'X':
                q1.H()
                alice_measured_bits += str(q1.measure())
    # print("Alice's measured bits: {}".format(alice_measured_bits))

    # Get message from receiver
    message = host.get_next_classical(receiver, WAIT_TIME)

    # Sending Basis to Bob
    ack_basis_alice = host.send_classical(receiver, alice_basis, await_ack=True)
    if ack_basis_alice is not None:
        print(CRED + "{}".format(host.host_id) + CEND +
              " sent basis string successfully to " +
              CGREEN + "{}.".format(receiver) + CEND +
              ".")
    # Receiving Basis from Bob
    basis_from_bob = host.get_next_classical(receiver, wait=WAIT_TIME)
    if basis_from_bob is not None:
        print(CGREEN + "{}".format(receiver) + CEND +
              " got basis string successfully from " +
              CRED + "{}".format(host.host_id) + CEND +
              ".")

    # For Key
    alice_key = alice_key_string(alice_measured_bits, alice_basis, basis_from_bob.content, key_size)
    alice_key = [int32(k) for k in alice_key][:qkd_key_length]
    print(CRED + str(host.host_id) + CEND +
          " sent key to " +
          CGREEN + str(receiver) + CEND +
          " with " +
          CBLUE + "%d" % len(alice_key) + CEND +
          " key bits")
    return alice_key

    # # For Sending Key
    # alice_brd_ack = host.send_classical(receiver, alice_key, await_ack=True)
    # if alice_brd_ack is not None:
    #     print("{}'s key successfully sent to {}".format(host.host_id, receiver))
    # bob_key = host.get_classical(receiver, wait=WAIT_TIME)
    # if bob_key is not None:
    #     print("{}'s got successfully by {}".format(receiver, host.host_id))
    #     if alice_key == bob_key[0].content:
    #         print("Same key from {}'s side".format(host.host_id))


def receive_qkd(host, receiver, bob_basis, key_size):
    bob_key = ""
    bob_measured_bits = ""
    # For Qubit and Basis
    for basis in bob_basis:
        q2 = host.get_qubit(receiver, wait=WAIT_TIME)
        if q2 is not None:
            # Measuring Alice's qubit based on Bob's basis
            if basis == 'Z':  # Z-basis
                bob_measured_bits += str(q2.measure())
            if basis == 'X':  # X-basis
                q2.H()
                bob_measured_bits += str(q2.measure())
    # print("Bob's measured bits: {}".format(bob_measured_bits))

    # Send Alice the basis in which Bob has measured
    host.send_classical(receiver, "Bob gets the message.", await_ack=True)

    # Receiving Basis from Alice
    basis_from_alice = host.get_next_classical(receiver, wait=WAIT_TIME)
    # if basis_from_alice is not None:
    #     print(CGREEN + "{}".format(receiver) + CEND +
    #           " got basis string successfully from " +
    #           CRED + "{}".format(host.host_id) + CEND +
    #           ".")
    # Sending Basis to Alice
    ack_basis_bob = host.send_classical(receiver, bob_basis, await_ack=True)
    # if ack_basis_bob is not None:
    #     print(CRED + "{}".format(host.host_id) + CEND +
    #           " sent basis string successfully to " +
    #           CGREEN + "{}.".format(receiver) + CEND +
    #           ".")

    # For sample key indices
    bob_key = bob_key_string(bob_measured_bits, bob_basis, basis_from_alice.content, key_size)
    bob_key = [int32(k) for k in bob_key][:qkd_key_length]
    print(CGREEN + str(host.host_id) + CEND +
          " received key from " +
          CRED + str(receiver) + CEND +
          " with " +
          CBLUE + "%d" % len(bob_key) + CEND +
          " key bits")
    return bob_key

    # # For Broadcast Key
    # alice_key = host.get_classical(receiver, wait=WAIT_TIME)
    # if alice_key is not None:
    #     print("{}'s key got successfully by {}".format(receiver, host.host_id))
    #     if bob_key == alice_key[0].content:
    #         print("Same key from {}'s side".format(host.host_id))
    # bob_brd_ack = host.send_classical(receiver, bob_key, await_ack=True)
    # if bob_brd_ack is not None:
    #     print("{}'s key successfully sent to {}".format(host.host_id, receiver))


# key has to be a string
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


def encry_msg(key, msg):
    secret_key_string = key_array_to_key_string(key)
    encrypted_msg_to_eve = encrypt(secret_key_string, msg)
    return encrypted_msg_to_eve


def decry_msg(key, msg):
    secret_key_string = key_array_to_key_string(key)
    decrypted_msg = decrypt(secret_key_string, msg)
    return decrypted_msg


def send_msg(sender, encrypted_msg_to_eve, receiver):
    print(CRED + str(sender.host_id) + CEND +
          " sends encrypted message to " +
          CGREEN + str(receiver) + CEND)
    sender.send_classical(receiver, "-1:" + encrypted_msg_to_eve, await_ack=True)


def recv_msg(receiver, sender):
    encrypted_msg = receiver.get_next_classical(sender, -1).content
    encrypted_msg = encrypted_msg.split(':')[1]
    print(CGREEN + str(receiver.host_id) + CEND +
          " receives encrypted message from " +
          CRED + str(sender) + CEND)
    print()
    return encrypted_msg


def eve_sniffing_quantum(sender, receiver, qubit):
    qubit.measure(non_destructive=True)


# Initialize Networks, create hosts and make connections
def connect(graph):
    # graph = {'Ani': [['sender'], ['Arya']],
    #          'Arya': [['trusted_node'], ['Ani', 'Darren']],
    #          'Darren': [['trusted_node'], ['Arya', 'Nayan']],
    #          'Nayan': [['trusted_node'], ['Darren', 'Xiufan']],
    #          'Xiufan': [['receiver'], ['Nayan']]}

    nodes = graph.keys()
    # Initialize a network
    network = Network.get_instance()
    network.delay = 0.0             # Set delay to 0
    network.start(nodes)            # Start the network with the defined hosts

    # Declare the hosts
    host_name_dic = {}
    for n in nodes:
        host_name_dic[n] = Host(n)
    # Add connections
    for n in nodes:
        for recv in graph[n][1]:
            host_name_dic[n].add_connection(recv)
    # Start
    for n in nodes:
        host_name_dic[n].start()
        network.add_host(host_name_dic[n])

    return host_name_dic, network


def QKD(graph, msg, key_size):
    nodes, edges = graph
    host_name_dic, network = connect(graph)

    sender = host_name_dic[nodes[0]]
    receiver = host_name_dic[nodes[-1]]
    trusted_nodes = nodes[1:len(nodes) - 1]

    if not trusted_nodes:
        alice_basis, bob_basis = preparation(key_size)

        # print("Sender bases: {}".format(alice_basis))
        # print("Receiver bases: {}".format(bob_basis))
        def send_func(sender):
            print(str(sender.host_id) + " encrypts the message: " + msg)
            send_key = send_qkd(sender, receiver.host_id, alice_basis, key_size)
            encrypted_msg = encry_msg(send_key, msg)
            send_msg(sender, encrypted_msg, receiver.host_id)

        def recv_func(receiver):
            recv_key = receive_qkd(receiver, sender.host_id, bob_basis, key_size)
            encrypted_msg = recv_msg(receiver, sender.host_id)
            decrypted_msg = decry_msg(recv_key, encrypted_msg)
            print(str(receiver.host_id) + " decrypts the message: " + decrypted_msg)

        # Run
        t1 = sender.run_protocol(send_func, ())
        t2 = receiver.run_protocol(recv_func, ())
        t1.join()
        t2.join()

    else:
        Alices_basis = []
        Bob_basis = []
        for i in range(len(nodes) - 1):
            alice_basis, bob_basis = preparation(key_size)
            Alices_basis.append(alice_basis)
            Bob_basis.append(bob_basis)
        # print("Sender bases: {}".format(Alices_basis))
        # print("Receiver bases: {}".format(Bob_basis))

        tn_1 = host_name_dic[trusted_nodes[0]]
        tn_n = host_name_dic[trusted_nodes[-1]]

        def send_func(sender):
            print(str(sender.host_id) + " encrypts the message: " + msg)
            send_key = send_qkd(sender, tn_1.host_id, Alices_basis[0], key_size)
            print(send_key)
            encrypted_msg = encry_msg(send_key, msg)
            send_msg(sender, encrypted_msg, tn_1.host_id)

        # Run
        Th_lst = [_ for _ in range(len(nodes))]
        Th_lst[0] = sender.run_protocol(send_func, ())

        def trus_func(trusted_node, prev_node, next_node, prev_basis, next_basis):
            # Build the QKD protocol with the previous node and obtain the private key
            prev_key = receive_qkd(trusted_node, prev_node.host_id, prev_basis, key_size)
            # Receive the encrypted message from the previous node
            msg = recv_msg(trusted_node, prev_node.host_id)
            # Build the QKD protocol with the next node and obtain the private key
            next_key = send_qkd(trusted_node, next_node.host_id, next_basis, key_size)

            print(prev_key)
            print(next_key)


            # Use the previous QKD key and the next QKD key to construct the new key by:
            # ord(K12) = ord(K2) ^ ord(K1)
            new_key = [(prev_key[j] + next_key[j]) % 2 for j in range(min([len(prev_key), len(next_key)]))]
            # Encrypt the message with the new key
            msg = encry_msg(new_key, msg)
            # Send the message to the next node
            send_msg(trusted_node, msg, next_node.host_id)

        for i in range(1, len(nodes) - 1):
            trusted_node = host_name_dic[nodes[i]]
            Th_lst[i] = trusted_node.run_protocol(trus_func, (host_name_dic[nodes[i - 1]],
                                                              host_name_dic[nodes[i + 1]],
                                                              Bob_basis[i - 1],
                                                              Alices_basis[i]))

        def recv_func(receiver):
            recv_key = receive_qkd(receiver, tn_n.host_id, Bob_basis[-1], key_size)
            print(recv_key)

            encrypted_msg = recv_msg(receiver, tn_n.host_id)
            decrypted_msg = decry_msg(recv_key, encrypted_msg)
            print(str(receiver.host_id) + " decrypts the message: " + decrypted_msg)

        Th_lst[-1] = receiver.run_protocol(recv_func, ())

        for t in Th_lst:
            t.join()

    network.stop(True)
    exit()
