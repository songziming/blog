#! env python

import numpy as np
import csv
import iris

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))

def sigmoid_derivative(x):
    y = sigmoid(x)
    return y * (1.0 - y)

def relu(x):
    return max(0.0, x)

def relu_derivative(x):
    if x > 0:
        return 1
    else:
        return 0

class BPLayer:
    # prev_size  - 前一层的神经元数量
    # this_size  - 这一层的神经元数量
    # activation - 这一层使用的激活函数
    # derivative - 激活函数的导函数
    def __init__(self, prev_size, this_size, activation, derivative):
        self.w = np.random.rand(prev_size + 1, this_size)
        self.f = np.vectorize(activation)
        self.d = np.vectorize(derivative)

    # 正向传播过程，输入前一层的输出
    def forward(self, prev_y):
        self.prev_y = np.append(np.array(prev_y), [-1]).reshape(1, -1)
        self.x      = np.dot(self.prev_y, self.w)
        self.y      = self.f(self.x)
        return self.y

    # 反向传播过程，同时更新权值，返回前一层对误差的偏导数（dE/dy）
    def backward(self, dy, eta):
        self.dy = dy.reshape(1, -1)
        self.dx = self.d(self.x)
        prev_dy = np.dot(self.dy * self.dx, self.w.T)[:, 0:-1]
        delta   = np.dot(self.prev_y.T, self.dy * self.dx)
        self.w  = self.w - delta * eta
        return prev_dy

class BPNet:
    def __init__(self, input_size):
        self.input_size  = input_size
        self.output_size = input_size
        self.layers = []
    def add_layer(self, size):
        self.layers.append(BPLayer(
            self.output_size, size,
            # relu, relu_derivative))
            sigmoid, sigmoid_derivative))
        self.output_size = size
    def calc(self, x):
        y = np.array(x).reshape(1, -1)
        for l in self.layers:
            y = l.forward(y)
        return y
    def train(self, x, t):
        y = np.array(x).reshape(1, -1)
        t = np.array(t).reshape(1, -1)
        for l in self.layers:
            y = l.forward(y)
        dy = y - t
        for l in reversed(self.layers):
            dy = l.backward(dy, 0.8)
        return y

if __name__ == '__main__':
    net = BPNet(4)
    net.add_layer(4)
    net.add_layer(1)

    m = len(iris.iris_data)
    n = len(iris.iris_label)
    if m != n:
        print('data and label count not compliant')
        exit(0)

    test = [
        [ 0.222222222,  0.625,        0.06779661,   0.041666667 ],
        [ 0.166666667,  0.416666667,  0.06779661,   0.041666667 ],
        [ 0.111111111,  0.5,          0.050847458,  0.041666667 ],
        [ 0.75,         0.5,          0.627118644,  0.541666667 ],
        [ 0.583333333,  0.5,          0.593220339,  0.583333333 ],
        [ 0.722222222,  0.458333333,  0.661016949,  0.583333333 ],
        [ 0.444444444,  0.416666667,  0.694915254,  0.708333333 ],
        [ 0.611111111,  0.416666667,  0.711864407,  0.791666667 ],
        [ 0.527777778,  0.583333333,  0.745762712,  0.916666667 ],
    ]

    for t in test:
        print(net.calc(t))

    for round in range(0, 200):
        e = 0.0
        for i in range(0, m):
            out = net.train(iris.iris_data[i], iris.iris_label[i])
            e += (out[0,0] - iris.iris_label[i]) ** 2
        if (round % 5) == 0:
            print("error is %f" % e)

    for t in test:
        print(net.calc(t))
    for i in range(0, 10):
        out = net.train(iris.iris_data[i], iris.iris_label[i])
        print("output %f should be %f" % (out[0,0], iris.iris_label[i]))
