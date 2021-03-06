### Covariance Shift

神经网络可以通过数据学习任意函数，但是学习的结果未必与原函数相同。特别地，只有在训练数据覆盖到的范围内，神经网络才能较好地拟合原函数。

从数学角度分析，假设原函数是$f(x)$，神经网络的函数是$g(x)$，网络训练的结果就是$f(x) \approx g(x)$。然而，所有的函数都有定义域的概念，这个等式并非在$f(x)$的全体定义域之下都成立。每一次训练，输入数据$x$和教师信号$t$，都相当于让函数$g$在$x$位置更接近目标函数$f$，由于函数$g$的连续性，调整$x$位置处的取值时，可能会让相邻位置的$g$取值也发生一定的改变。最终的效果就是，$f$与$g$近似程度的分布与训练数据在定义域空间内的密度是一致的。

如果训练数据的分布和实际数据的分布密度出现了偏差，那么这个网络运行的效果就会下降，这种特点也被称为covariance shift。另一个结论就是，使用更多的数据进行训练，尽可能地让训练数据覆盖住更大的空间，是提高网络准确率的有效方法。