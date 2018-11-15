#! env python

import numpy as np
import csv

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def dsigmoid(x):
    y = sigmoid(x)
    return y * (1.0 - y)

class Layer:
    def __init__(self, prev_size, size, f, fd):
        self.w  = np.random.rand(prev_size + 1, size)
        self.f  = np.vectorize(f)
        self.fd = np.vectorize(fd)
    def forward(self, prev_y):
        self.prev_y = np.append(prev_y, [[-1]], axis=1) # needed when updating
        self.x = np.dot(self.prev_y, self.w)
        self.y = self.f(self.x)
        return self.y
    def backward(self, dy):
        self.dy = dy
        self.fx = self.fd(self.x)
        return np.dot(dy * self.fx, self.w.T)[:, 0:-1]  # prev_dy
    def update(self, eta):
        delta = np.dot(self.prev_y.T, self.dy * self.fx)
        # print(" --> %s" % delta)
        self.w = self.w - delta * eta

class Network:
    def __init__(self, input_size):
        self.input_size  = input_size
        self.output_size = input_size
        self.layers = []
    def add_layer(self, size):
        self.layers.append(Layer(self.output_size, size, sigmoid, dsigmoid))
        # self.layers.append(Layer(self.output_size, size, relu, drelu))
        self.output_size = size
    def calc(self, x):
        y = x.reshape((1, x.size))  # input layer
        for l in self.layers:
            y = l.forward(y)
        return y
    def train(self, x, t):
        y = x.reshape((1, x.size))      # input layer's output
        for l in self.layers:
            y = l.forward(y)
        dy = y - t.reshape((1, t.size)) # output layer's error
        for l in reversed(self.layers):
            dy = l.backward(dy)
            l.update(0.8)

if __name__ == '__main__':
    data = []
    with open('wheat.csv') as f:
        reader = csv.reader(f, delimiter=',')
        line_count = 0
        for row in reader:
            data.append(np.array(row).astype(np.float))

    net = Network(3)
    net.add_layer(4)
    net.add_layer(1)

    print(net.calc( np.array([[ 0.1, 0.1, 0.1 ]]) ))
    print(net.calc( np.array([[ 0.9, 0.9, 0.9 ]]) ))
    
    for x in range(0, 30):
        for i in range(0, 10):
            net.train( np.array([[ 0.1, 0.1, 0.0 ]]), np.array([[ 0 ]]) )
            net.train( np.array([[ 0.1, 0.1, 0.2 ]]), np.array([[ 0 ]]) )
            net.train( np.array([[ 0.1, 0.0, 0.1 ]]), np.array([[ 0 ]]) )
            net.train( np.array([[ 0.1, 0.2, 0.1 ]]), np.array([[ 0 ]]) )
            net.train( np.array([[ 0.0, 0.1, 0.1 ]]), np.array([[ 0 ]]) )
            net.train( np.array([[ 0.2, 0.1, 0.1 ]]), np.array([[ 0 ]]) )
        for i in range(0, 10):
            net.train( np.array([[ 0.9, 0.9, 0.8 ]]), np.array([[ 1 ]]) )
            net.train( np.array([[ 0.9, 0.9, 1.0 ]]), np.array([[ 1 ]]) )
            net.train( np.array([[ 0.9, 0.8, 0.9 ]]), np.array([[ 1 ]]) )
            net.train( np.array([[ 0.9, 1.0, 0.9 ]]), np.array([[ 1 ]]) )
            net.train( np.array([[ 0.8, 0.9, 0.9 ]]), np.array([[ 1 ]]) )
            net.train( np.array([[ 1.0, 0.9, 0.9 ]]), np.array([[ 1 ]]) )

    print(net.calc( np.array([[ 0.1, 0.1, 0.1 ]]) ))
    print(net.calc( np.array([[ 0.9, 0.9, 0.9 ]]) ))