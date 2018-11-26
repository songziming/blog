#! env python

import numpy as np
import csv
import iris

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def sigmoid_derivative(x):
    y = sigmoid(x)
    return y * (1.0 - y)

def sigmoid2(x):
    return 2.0 / (1.0 + np.exp(-x)) - 1.0

def sigmoid2_derivative(x):
    y = sigmoid2(x)
    return (1.0 + y) * (1.0 - y) / 2.0

def relu(x):
    return max(0.0, x)

def relu_derivative(x):
    if x > 0:
        return 1
    else:
        return 0

class BPLayer:
    # prev_dim   - 前一层的神经元数量
    # this_dim   - 这一层的神经元数量
    # activation - 这一层使用的激活函数（向量化）
    # derivative - 激活函数的导函数（向量化）
    def __init__(self, prev_dim, this_dim, activation, derivative):
        self.w = np.random.randn(prev_dim + 1, this_dim)
        self.f = activation
        self.d = derivative

    # 正向传播过程，输入前一层的输出
    def forward(self, prev_y):
        self.prev_y = np.append(np.array(prev_y), [-1]).reshape(1, -1)
        self.x      = np.dot(self.prev_y, self.w)
        self.y      = self.f(self.x)
        return self.y

    # 反向传播过程，同时更新权值，返回前一层对误差的偏导数（dE/dy）
    def backward(self, dy, eta):
        self.dy = dy.reshape(1, -1)
        self.fx = self.d(self.x)
        prev_dy = np.dot(self.dy * self.fx, self.w.T)[:, 0:-1]
        delta   = np.dot(self.prev_y.T, self.dy * self.fx)
        self.w  = self.w - delta * eta
        return prev_dy

class BPNet:
    def __init__(self, input_dim, activation, derivative):
        self.input_dim  = input_dim
        self.output_dim = input_dim
        self.layers     = []
        self.f          = np.vectorize(activation)
        self.d          = np.vectorize(derivative)
    def add_layer(self, dim):
        self.layers.append(BPLayer(self.output_dim, dim, self.f, self.d))
        self.output_dim = dim
    def calc(self, x):
        y = np.array(x).reshape(1, -1)
        for l in self.layers:
            y = l.forward(y)
        return y
    def train(self, x, t, eta = 0.5):
        y  = self.calc(x)
        dy = y - np.array(t).reshape(1, -1)
        for l in reversed(self.layers):
            dy = l.backward(dy, eta)
        return y

if __name__ == '__main__':
    net = BPNet(4, sigmoid2, sigmoid2_derivative)
    net.add_layer(4)
    net.add_layer(3)
    net.add_layer(2)
    net.add_layer(1)

    m = len(iris.iris_data)
    n = len(iris.iris_label)
    if m != n:
        print('data and label count not compliant')
        exit(0)
    data  = np.array(iris.iris_data ) * 2 - 1.0
    label = np.array(iris.iris_label) * 2 - 1.0

    for t in data[-9:]:
        print(net.calc(t))

    for round in range(0, 400):
        e = 0.0
        for i in range(0, m):
            out = net.train(data[i], label[i], 0.2)
            e += (out[0,0] - label[i]) ** 2
        if round % 5 == 0:
            print("error is %f" % e)

    for t in data[-9:]:
        print(net.calc(t))