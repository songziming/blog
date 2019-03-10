红黑树很好用，但是不好理解，本文尝试理解红黑树的工作原理，并分析Linux内核中`lib/rbtree.c`中的实现。

红黑是就是一棵二叉查找树，此外还有以下五个规则：

1. 每个节点都有颜色，非红即黑
2. 根节点一定是黑色的
3. 父子节点不能都是红色的，也就是说，红节点的子节点必然是黑色的
4. 任何一条路径的黑高度相同

在某些文献里面（例如《算法导论》），还有额外一条规则：“叶子节点（NULL）都是黑色的”。但是如果我们不把NULL当作节点，那么完全可以将这条规则删除。

红黑树的妙处就在于，只要同时满足这五个条件，我们就能确保这棵树是平衡的。

### 插入操作

向红黑树插入一个新节点，与普通的二叉查找树类似，新节点颜色设为RED。

但是由于设置了颜色之后，可能会违反红黑树的某一条规则，因此需要执行 insert_fixup 操作，用来保持红黑树的性质。

首先要分析一下，插入了一个新的红节点之后，会破坏哪些性质：如果新节点的父节点也是红色的，那么违反了相邻节点不能同为红色的性质。这是唯一可能破坏的性质。

如果新节点和父节点都是红色的，那么需要重新染色，将父节点重新染为黑色。然而，这又可能违背黑高度不同的