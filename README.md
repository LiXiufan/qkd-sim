# qkd-sim
This repository is for the simulation of quantum key distribution (QKD) with trusted node implementation and Eavesdropper detection. We design our modules with the QuNetSim framework: https://tqsd.github.io/QuNetSim/examples/QKD_BB84.html
The main results are below:
-  **QKD**.
  We simulated the quantum key distribution task between Alice and Bob with BB84 and B92 protocols.
-  **Trusted nodes**.
  We designed the XOR encryption method between two generated keys. K12 = K1 + K2 (mod 2). Using this encryption method, we are able to implement the trusted node protocol and realize a long-distance information transmission between Alice, Bob, and Charlie.
-  **Eavesdropper**.
  We then consider the scenario when there is an Eavesdropper listening to the quantum and classical channels --- a man in the middle. By comparing the generated keys between the sender and receiver, we are able to estimate the error rate of the keys. If the error is larger than 20%, we attribute this error to Eavesdropper and abandon the channels.
- **Network topology**.
  In realistic networks, usually, there is more than one node connecting to another one. So we are able to find an alternative path for information processing with QKD by leveraging the geometric structure of the network topology so that the Eavesdropper is avoided.
- **NQSN**.
  Eventually, we performed QKD with two trusted nodes and one Eavesdropper on the testbed infrastructure of the National Quantum-safe Networks (NQSN) in Singapore. The experiment demonstrates the feasibility and extendability of our simulation software.
