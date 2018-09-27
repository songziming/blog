---
title: "无锁数据结构"
---

> 发现一位俄罗斯大神的博客[1024cores](http://www.1024cores.net)，里面关于无锁算法这个话题有详细的介绍。

无锁并不是完全不需要进行同步，而是用底层的原子性操作替换粗粒度的锁。在CPU级别，原子性操作也要锁住总线，但是这种级别的锁已经可以认为几乎没有性能损失了。

### lockless queue

这里的队列只有两种操作，push和pop，因此可能的竞争一共有三种情况：push与push竞争、pop与pop竞争、push与pop竞争。

网上的某些实现只能保证 single-producer, single-consumer，也就是只能保证push与pop竞争时的正确性。

数据结构可以直接使用双链表，但是针对队列这个特化的链表，我们可以去掉prev指针，每个元素只保留next字段，队列头节点同时记录head和tail：

~~~ c
typedef struct qnode {
    struct qnode * next;
} qnode_t;

typedef struct queue {
    struct qnode * head;
    struct qnode * tail;
} queue_t;
~~~

向队列添加元素的逻辑：

~~~ c
void queue_push(dllist_t * q, dlnode_t * node) {
    node->next = NULL;
    dlnode_t * tail = atomic_set(&q->tail, node);
    node->prev = tail;
    if (NULL == tail) {
        q->head = node;
    } else {
        tail->next = node;
    }
}
~~~

如果有多个push操作同时执行，因为我们使用atomic_set来修改tail指针，同时获取tail指针的原值，因此我们能够保证，tail始终指向添加这个元素之前的链表尾，但是我们不能保证这个tail元素的prev指针指向正确的值。但这并不重要，因为我们要做的不是将tail和前一个元素连接起来，而是把tail和node连接起来。

从队列取出一个元素的逻辑：

~~~ c
dlnode_t * queue_pop(dllist_t * q) {
retry:
    dlnode_t * head = q->head;
    if (NULL == head) { return NULL; }

    dlnode_t * next = head->next;
    if (!atomic_cas(&q->head, head, next)) { goto retry; }

    if (NULL == next) {
        q->tail = NULL;
    } else {
        next->prev = NULL;
    }

    return head;
}
~~~

取出元素的过程，操作的关键变量就是head，我们要将其替换成链表中的第二个元素。只不过，与push不同的是，push的新元素是我们给定的，但pop过程要给head赋的新值是要根据head确定的。在我们取出了head，得到head->next，到设置head新值之间，有可能发生抢占，导致链表头指针改变，破坏一致性，因此我们在修改头指针的时候，一定要使用compare-and-set，如果发现一致性被破坏，那就必须重复一遍，再次计算head->next的值。
在实际执行时，重试的概率其实是比较低的，但概率再低我们也要进行检查。由于重试的概率较低，因此这个代码并不会对性能造成太多影响。

下面分析push和pop相竞争的情况。前面的两种竞争，争抢的都是同一个变量，但是现在，争抢的是两个变量。争抢的对象不同，看似不会有竞争，然而有一些特殊情况。如果对一个空队列执行push，我们就会操作head指针；如果对一个单元素的队列执行pop，我们就会操作tail指针。

push过程，如果发现tail==NULL，才会修改head，有没有可能在`tail==NULL`和`head=node`之间，其他代码改变了head的值？应该是不可能的。
pop过程，我们在成功地取出一个元素之后（也就是这个时候head指针已经指向下一个元素了，只不过那个元素的prev还没有修改），如果发现`next==NULL`，那么才会修改tail。有没有一种可能，使得`next==NULL`和`tail=NULL`之间修改了tail的指针，应该是有可能的。

pop让一个单元素队列变为空队列，同时push让这个空队列变为非空队列。pop取出头节点后，已经判断了head->next==NULL，此时的状态，是head指针为空，tail仍然指向原来那个唯一的元素。如果这个时候执行了push，那么push函数会认为这个链表非空，因此不会修改head，反而会去修改那个已经被取出来的head。