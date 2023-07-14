import numpy as np

from qunetsim.components import Host
from qunetsim.components import Network
from qunetsim.objects import Qubit
from qunetsim.objects import Logger
from qunetsim.objects.logger import Logger as log

# from numpy import random
import random

Logger.DISABLED = True

wait_time = 10
qkd_key_length = 13
CRED = '\033[91m'
CEND = '\033[0m'
CGREEN = '\33[32m'
CBLUE = '\33[34m'


# Sender BB84_main Protocol
def send_bb84(sender, key, receiver):
    basis = []          # List to store all values of the basis
    # Convert key bits to qubits and send it to the receiver in a random basis
    for bit in key:
        base = random.randint(0, 1)     # choose a random basis 0 = Z basis, 1 = X basis
        basis.append(base)              # Add chosen base to basis set

        q_bit = Qubit(sender)           # create qubit

        if bit: q_bit.X()               # qubit flip operation if bit = 1
        if base: q_bit.H()              # Apply basis change if necessary

        sender.send_qubit(receiver, q_bit, await_ack=True)  # Send Qubit to Bob

    # Get measured basis of receiver
    message = sender.get_next_classical(receiver, wait_time)
    measured_basis = message.content
    measured_basis = eval(measured_basis)

    if len(basis) != len(measured_basis):
        raise KeyError("Qubits lost in transmition, basis set don't match.")

    # Compare to send basis, if same, answer with 0 and set ack True and go to next bit,
    for i in range(len(basis)):
        if basis[i] == measured_basis[i]:
            measured_basis[i] = 1
        else:
            measured_basis[i] = 0

    log.log("Sender sifted basis is ", basis)  # Only for verification

    # Send the sifted basis to the receiver for comparison
    sender.send_classical(receiver, str(measured_basis), await_ack=True)
    print(CRED + str(sender.host_id) + CEND + " sent key to " + CGREEN + str(receiver)
          + CEND + " with " + CBLUE + "%d" % len(key) + CEND + " key bits")

    # Update the sender key based on the receiver measurement and sifted basis
    key = [key[i] for i in range(len(measured_basis)) if measured_basis[i]][:qkd_key_length]
    log.log("Sender sifted key is ", str(key))     # Only for verification

    # Wait for acknowledgement from receiver
    receipt = sender.get_next_classical(receiver, wait_time)
    print(receipt.content)
    log.log("Receiver confirmation: ", receipt.content)
    return key


# Receiver BB84_main Protocol
def receive_bb84(receiver, key_size, sender):
    basis = []  # Measurement basis record
    key = []  # Raw key
    count = 0  # Count of bits received

    while count < key_size:
        base = random.randint(0, 1)  # choose a random measurement base
        basis.append(base)  # save the measurment basis
        q_bit = receiver.get_qubit(sender, wait=wait_time)  # wait for the qubit

        if base: q_bit.H()  # apply Hadamard if base is X
        bit = q_bit.measure()  # measure the qubit
        key.append(bit)  # save the full raw key
        count += 1

    # Send Alice the basis in which Bob has measured
    receiver.send_classical(sender, str(basis), await_ack=True)

    # Alice replies with the basis that is correct
    message = receiver.get_next_classical(sender, wait_time)
    sift_basis = message.content
    sift_basis = eval(sift_basis)

    key = [key[i] for i in range(len(sift_basis)) if sift_basis[i]][:qkd_key_length]

    receiver.send_classical(sender, CGREEN + str(receiver.host_id) + CEND + " received key from " + CRED + str(sender) +
                            CEND + " with " + CBLUE + "%d" % len(key) + CEND + " key bits", await_ack=True)
    return key


# Function to encrypt the message
def encrypt_msg(key, msg):
    # Make the key to a string
    key_string_binary = ''.join([str(x) for x in key])          # helper function, used to make the key to a string
    secret_key_string = ''.join(chr(int(''.join(x), 2)) for x in zip(*[iter(key_string_binary)] * 8))

    # Encrypt the message with the key string
    encrypted_msg = ""
    for char in msg:
        encrypted_msg += chr(ord(secret_key_string) ^ ord(char))

    return encrypted_msg


# Function to decrypt the message
def decrypt_msg(key, msg):
    return encrypt_msg(key, msg)


# Function to send the message
def send_msg(sender, encrypted_msg, receiver):
    print(CRED + str(sender.host_id) + CEND +" sends encrypted message to " + CGREEN + str(receiver) + CEND)
    sender.send_classical(receiver, "-1:" + encrypted_msg, await_ack=True)


# Function to receive the message
def recv_msg(receiver, sender):
    encrypted_msg = receiver.get_next_classical(sender, -1).content
    encrypted_msg = encrypted_msg.split(':')[1]
    print(CGREEN + str(receiver.host_id) + CEND + " receives encrypted message from " +
          CRED + str(sender) + CEND)
    return encrypted_msg


# Send keys between nodes
def send_node(sender, msg, secret_key, receiver):
    print(str(sender.host_id) + " encrypts the message: " + msg)
    send_key = send_bb84(sender, secret_key, receiver.host_id)
    encrypted_msg = encrypt_msg(send_key, msg)
    send_msg(sender, encrypted_msg, receiver.host_id)


# Receive keys between nodes
def recv_node(receiver, key_size, sender):
    recv_key = receive_bb84(receiver, key_size, sender.host_id)
    encrypted_msg = recv_msg(receiver, sender.host_id)
    decrypted_msg = decrypt_msg(recv_key, encrypted_msg)
    print(str(receiver.host_id) + " decrypts the message: " + decrypted_msg)


# Code for trusted node, works for any number
def trust_node(trusted_node, prev_node, next_node, key_size, secret_key):
    # Build the QKD protocol with the previous node and obtain the private key, then receive encrypted message
    prev_key = receive_bb84(trusted_node, key_size, prev_node.host_id)
    msg = recv_msg(trusted_node, prev_node.host_id)

    # Build the QKD protocol with the next node and obtain the private key
    next_key = send_bb84(trusted_node, secret_key, next_node.host_id)

    # Use the previous QKD key and the next QKD key to construct the new key by: ord(K12) = ord(K2) ^ ord(K1)
    new_key = [(prev_key[j] + next_key[j]) % 2 for j in range(min([len(prev_key), len(next_key)]))]

    # Encrypt the message with the new key and send the message to the next node
    msg = encrypt_msg(new_key, msg)
    send_msg(trusted_node, msg, next_node.host_id)


# ------------ Spy Function for eavesdropping on BB84_main communication ------------------ #
def spy_fn(spy_node, sender, receiver, key_size):
    basis = []          # Measurement basis record
    key = []            # Raw key
    count = 0           # Count of bits received

    while count < key_size:
        # Receive qubit from the sender
        base = random.randint(0, 1)                         # choose a random measurement base
        basis.append(base)                                  # save the measurement basis
        q_bit = spy_node.get_qubit(sender, wait=wait_time)  # wait for the qubit

        if base: q_bit.H()                                  # apply Hadamard if base is X
        bit = q_bit.measure()                               # measure the qubit
        key.append(bit)                                     # save the full raw key

        # Send qubit to receiver
        # base = random.randint(0, 1)  # choose a random basis 0 = Z basis, 1 = X basis
        q_bit = Qubit(spy_node)  # create qubit

        if bit: q_bit.X()  # qubit flip operation if bit = 1
        if base: q_bit.H()  # Apply basis change if necessary

        spy_node.send_qubit(receiver, q_bit, await_ack=True)  # Send Qubit to Bob
        count += 1


# Initialize Networks, create hosts and make connections
def connect(graph):
    nodes = list(graph.keys())

    # Initialize a network
    network = Network.get_instance()
    network.delay = 0.0             # Set delay to 0
    network.start(nodes)            # Start the network with the defined hosts

    # Declare the hosts
    host_name_dic = {}
    for n in nodes:
        host_name_dic[n] = Host(n)

    for c in graph:
        sender, receiver = c, graph[c]
        for i in range(len(receiver)):
            host_name_dic[sender].add_connection(receiver[i])

    for n in nodes:
        host_name_dic[n].start()
        network.add_host(host_name_dic[n])

    return host_name_dic, network


def QKD(graph, msg, key_size):
    nodes = list(graph.keys())
    host_name_dic, network = connect(graph)

    # Draws out the classical_network graph
    network.draw_classical_network()

    # Generate random key
    secret_key = np.random.randint(2, size=key_size)

    sender = host_name_dic[nodes[0]]
    receiver = host_name_dic[nodes[-1]]
    trusted_nodes = nodes[1:len(nodes) - 1]

    if not trusted_nodes:
        t1 = sender.run_protocol(send_node, arguments=(msg, secret_key, receiver))
        t2 = receiver.run_protocol(recv_node, arguments=(key_size, sender))
        t1.join()
        t2.join()

    else:
        tn_1 = host_name_dic[trusted_nodes[0]]
        tn_n = host_name_dic[trusted_nodes[-1]]
        Th_lst = [_ for _ in range(len(nodes))]           # empty list generated to keep track of all nodes

        # Run the network
        Th_lst[0] = sender.run_protocol(send_node, arguments=(msg, secret_key, tn_1))  # Sender to first node

        for i in range(1, len(nodes) - 1):                                             # Trusted nodes send/receive
            # Generate random key for each trusted node
            secret_key = np.random.randint(2, size=key_size)
            trusted_node = host_name_dic[nodes[i]]
            Th_lst[i] = trusted_node.run_protocol(trust_node, arguments=(host_name_dic[nodes[i - 1]],
                                                                         host_name_dic[nodes[i + 1]],
                                                                         key_size, secret_key))

        Th_lst[-1] = receiver.run_protocol(recv_node, arguments=(key_size, tn_n))      # Last node to Receiver

        for t in Th_lst:                                                               # join all Threads
            t.join()

    network.stop(True)
    exit()
