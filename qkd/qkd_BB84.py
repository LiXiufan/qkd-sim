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
    BB84 protocol for quantum key distribution between Alice and Bob.
"""

from qunetsim.objects import Qubit
from qunetsim.objects import Logger
import random
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

# Send BB84_main Protocol
def send_bb84(sender, key, receiver):
    basis = []          # List to store all values of the basis
    eves = 0 # Detection of Eavesdropper
    # Convert key bits to qubits and send it to the receiver in a random basis
    for bit in key:
        base = random.randint(0, 1)     # choose a random basis 0 = Z basis, 1 = X basis
        basis.append(base)              # Add chosen base to basis set

        q_bit = Qubit(sender)  # create qubit

        if bit: q_bit.X()  # bit flip operation if bit = 1
        if base: q_bit.H()  # Apply basis change if necessary

        sender.send_qubit(receiver, q_bit, await_ack=False)  # Send Qubit to Bob

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

    # log.log("Sender sifted basis is ", basis)  # Only for verification

    # Send the sifted basis to the receiver for comparison
    sender.send_classical(receiver, str(measured_basis), await_ack=False)
    print(CRED + str(sender.host_id) + CEND +
          " sent key to " +
          CGREEN + str(receiver) + CEND +
          " with " +
          CBLUE + "%d" % len(key) + CEND +
          " rough key bits.")

    # Update the sender key based on the receiver measurement and sifted basis
    key = [key[i] for i in range(len(measured_basis)) if measured_basis[i]][:qkd_key_length]


    # log.log("Sender sifted key is ", str(key))     # Only for verification

    # Wait for acknowledgement from receiver
    receipt = sender.get_next_classical(receiver, wait_time)
    print(receipt.content)
    # log.log("Receiver confirmation: ", receipt.content)

    # Send the key to receiver for verification and detection of Eavesdropper
    sender.send_classical(receiver, key, await_ack=False)

    # Get the error rate from the receiver
    error_rate = sender.get_next_classical(receiver, wait_time).content

    # Decide if this communication is safe or not according to the error rate
    if error_rate < ERROR_RATE:
        msg = 'Communication between ' + \
              CRED + str(sender.host_id) + CEND +\
              ' and ' + \
              CGREEN + str(receiver) + CEND +\
              ' is ' + CGREEN2 + 'SAFE' + CEND + ' with error rate: ' + CGREEN2 + str(error_rate) + " %" + CEND
        print(msg)
    else:
        msg = 'Communication between ' + \
              CRED + str(sender.host_id) + CEND +\
              ' and ' + \
              CGREEN + str(receiver) + CEND +\
              ' is ' + CRED2 + 'NOT SAFE' + CEND + ' with error rate: ' + CRED2 + str(error_rate) + " %" + CEND
        print(msg)
        print(CRED2 + "Eavesdropper Detected between " + str(sender.host_id) + " and " + str(receiver) +  " !" + CEND)
        print()
        eves += 1
    return key, eves



# Receiver BB84_main Protocol
def receive_bb84(receiver, key_size, sender):
    basis = []  # Measurement basis record
    eves = 0 # Detection of Eavesdropper
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
    receiver.send_classical(sender, str(basis), await_ack=False)

    # Alice replies with the basis that is correct
    message = receiver.get_next_classical(sender, wait_time)
    sift_basis = message.content
    sift_basis = eval(sift_basis)

    key = [key[i] for i in range(len(sift_basis)) if sift_basis[i]][:qkd_key_length]

    receiver.send_classical(sender, CGREEN + str(receiver.host_id) + CEND + " received key from " + CRED + str(sender) +
                            CEND + " with " + CBLUE + "%d" % len(key) + CEND + " key bits.", await_ack=False)

    # Receive sender's key for verification and detection of Eavesdropper
    sender_key = receiver.get_next_classical(sender, wait_time).content

    # Compare the sender and receiver's key and calculate the error rate
    # error_rate = sum([sender_key[i] ^ key[i] for i in range(len(key))]) / len(key)
    error_rate = round((sum([sender_key[i] ^ key[i] for i in range(len(key))]) / len(key)) * 100, 2)
    # Send the error rate back to sender
    receiver.send_classical(sender, error_rate, await_ack=False)

    if error_rate >= ERROR_RATE:
        eves += 1

    # Decide if this communication is safe or not according to the error rate
    # if error_rate < ERROR_RATE:
    return key, eves













