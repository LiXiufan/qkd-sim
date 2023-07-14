from qkd_BB84 import QKD
# from qkd_B92 import QKD

# nodes = ['Alice', 'Bob', 'Eve']
# edges = [('Alice', 'Bob'), ('Bob', 'Alice'), ('Bob', 'Eve'), ('Eve', 'Bob')]
# nodes = ['Ani', 'Arya', 'Darren', 'Nayan', 'Xiufan']
# edges = [('Ani', 'Arya'), ('Arya', 'Ani'),
#          ('Arya', 'Darren'), ('Darren', 'Arya'),
#          ('Darren', 'Nayan'), ('Nayan', 'Darren'),
#          ('Nayan', 'Xiufan'), ('Xiufan', 'Nayan')]

nodes = ['Ani', 'Darren',  'Xiufan']
edges = [('Ani','Darren'), ('Darren', 'Ani'),
         ('Darren', 'Xiufan'), ('Xiufan', 'Darren')]

graph = {'Ani': ['Arya'], 'Arya': ['Ani', 'Darren'],
              'Darren': ['Arya', 'Nayan'], 'Nayan': ['Darren', 'Xiufan'],
              'Xiufan': ['Nayan']}

# graph = [nodes, edges]
message = "Hello, is Xiufan more handsome than Patrick ???"
key_size = 180  # the size of the key in bit for BB84_main
# key_size = 180 # the size of the key in bit for B92

if __name__ == '__main__':
    QKD(graph, message, key_size)
