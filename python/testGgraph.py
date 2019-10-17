#!/usr/bin/python

import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt

from dyngraphplot import DynGraphPlot
import hvplot.networkx as hvnx
import matplotlib.animation
import matplotlib.animation as animation

G = nx.DiGraph()

G.add_node(1)

G.add_node(8, time=34)
G.add_edge(8, 1)

G.add_node(3)
G.add_node(5)
G.add_edge(3, 5)

G.add_node(5)
G.add_node(8)
G.add_edge(5, 8)

G.add_node(4)
G.add_node(8)
G.add_edge(4, 8)

G.add_node(6)
G.add_node(5)
G.add_edge(6, 5)

G.add_node(7)
G.add_node(6)
G.add_edge(7, 6)

G.add_node(9)
G.add_node(8)
G.add_edge(9, 8)

G.add_node(10)
G.add_node(9)
G.add_edge(10, 9)

print("Graph nodes: ",G.number_of_nodes())
print("Graph edges: ",G.number_of_edges())
#print(G.adj) works ok

def update_line(num, data, line):
    line.set_data(data[..., :num])
    return line,

fig1 = plt.figure()

data = G.adj #np.random.rand(2, 25)
l, = plt.plot([], [], 'r-')
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.xlabel('x')
plt.title('test')
line_ani = animation.FuncAnimation(fig1, update_line, 25, fargs=(data, l),
                                   interval=50, blit=True)
plt.show()



#print list(G.edges)

#G = nx.petersen_graph()
#plt.subplot(121)
#<matplotlib.axes._subplots.AxesSubplot object at ...>
#nx.draw(G, with_labels=True, font_weight='bold')
#plt.subplot(122)

#nx.draw_shell(G, with_labels=True, font_weight='bold')
#plt.show()

options = {
    'node_color': 'yellow',
    'node_size': 300,
    'width': 1,
	'with_labels':'True',
}
#plt.subplot(221)
#nx.draw_random(G, **options)
#plt.show()
#plt.subplot(222)
#nx.draw_circular(G, **options)
#plt.subplot(223)
#plt.show()

#nx.draw_spectral(G,  **options)
#plt.show()

#plt.subplot(224)

#nx.draw_shell(G, nlist=[range(5,10), range(5)], **options)

import networkx as nx
import numpy as np
import matplotlib.pylab as plt
import hvplot.networkx as hvnx
import holoviews as hv
from bokeh.models import HoverTool
hv.extension('bokeh')

# THis is working as a static graph
''''
pos = nx.spring_layout(G)
nx.draw_networkx(G, pos, node_color='lightgray')
hvnx.draw(G, pos, node_color='lightgray').opts(tools=[HoverTool(tooltips=[('index', '@index_hover')])])
#plt.show()
'''

import networkx as nx
import json
import matplotlib.pyplot as plt
%matplotlib inline

#G = nx.erdos_renyi_graph(30,4.0/30)
while not nx.is_connected(G):
    G = nx.erdos_renyi_graph(30,4.0/30)
plt.figure(figsize=(6,4));
nx.draw(G)




