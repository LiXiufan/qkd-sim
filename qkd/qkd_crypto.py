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
    Cryptographic module of QKD. The messages are encrypted by Python's pointer 'ord' and 'chr' functions.
"""

from qunetsim.objects import Logger
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
def send_msg(sender, encrypted_msg_to_eve, receiver):
    print(CRED + str(sender.host_id) + CEND +
          " sends encrypted message to " +
          CGREEN + str(receiver) + CEND)
    sender.send_classical(receiver, "-1:" + encrypted_msg_to_eve, await_ack=False)

# Function to receive the message
def recv_msg(receiver, sender):
    encrypted_msg = receiver.get_next_classical(sender, -1).content
    encrypted_msg = encrypted_msg.split(':')[1]
    print(CGREEN + str(receiver.host_id) + CEND +
          " receives encrypted message from " +
          CRED + str(sender) + CEND)
    print()
    return encrypted_msg