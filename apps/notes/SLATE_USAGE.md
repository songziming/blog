# Slate 使用方式

Slate 把文本编辑器最麻烦的操作封装起来了，我们只需要编写 model 和 view 两部分。

View 就是各种 React 组件，负责渲染文档元素。

Model 就是文档模型，一个树形的数据结构，代表了正在编辑的文档的状态。编辑的过程就是更新文档模型的过程。

## 编辑 == 更新文档模型 == Transforms

文档模型被 slate 隐藏起来，无法直接访问。我们不能像操作 JSON 一样拿到 model 并操作，只能借助 Transforms 间接操作 model。

但是，应该想象着 model 的样子，清楚我们要如何操作这个 model，这样才能寻找最合适的 Transforms 函数。

可以在操作前后 dump model JSON，比较其差异。

具体要执行哪些操作：
- Node 级别的操作，包括对 Block、Inline、Leaf 的增删改
- 对选择区的操作，改变选择的部分

