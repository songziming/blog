---
title: "任务切换"
---

本文只介绍Wheel中，在x86_64架构下任务切换的细节，不涉及调度。调度用来确定接下来切换到哪一个任务，与具体的架构无关，而任务切换就是在确定了要切换到的那个任务之后，真正切换上下文的过程。

### tid_prev和tid_next

我们在Wheel中，使用了两个变量`tid_prev`和`tid_next`。这两个都是percpu变量，也就是说每个CPU都有一个tid_prev、都有一个tid_next。为什么不用一个`tid_current`变量，而非要使用两个？因为调度算法选出了接下来要执行的任务，记录在tid_next里面，此时并没有立即进行切换。调度和任务切换不是同时进行的，之间可能发生抢占，可能再次发生调度，选出一个新的任务。

tid_next是percpu变量，但并不是只有当前CPU才有可能修改它的值。有可能创建了一个带有亲和性的任务，这时就要操作其他CPU的变量tid_next。更新tid_next时，不管是自己的还是其他CPU的，都应该使用cas-loop模式：

~~~ c
retry:
    task_t * next = atomic_get(percpu_ptr(ix, tid_next));
    if (cand->priority < next->priority) {
        if (!atomic_cmp_and_set(percpu_ptr(ix, tid_next), next, cand)) {
            cand->flg_next = true;
            goto retry;
        }
    }
~~~

更新tid_next时，首先要判断新的task能不能抢占tid_next，还要判断目标CPU是否允许抢占。

但是在所有抢占的条件都判断满足之后，情况有可能已经发生了变化，有可能tid_next已经变了，因此我们需要使用compare-and-set，只有条件没有改变时才能更新tid_next。

但是删除一个任务的时候，我们就要多进行一些检查。删除tid的时候，不仅要检查这个tid是否正在某个CPU上运行，还要判断这个tid是否即将在某个CPU上运行。因为在中断返回或者执行task_switch时，如果tid_next指向的那个任务已经不存在了，再去切换就有问题。

要判断一个任务是不是tid_prev或tid_next指向的，可以通过位图来记录，例如在tid->state里面，用一个bit表示是否正在某个CPU上运行，也就是是否有一个tid_prev指向自己，用另外一个bit表示是否接下来还要运行，也就是是否有一个tid_next指向自己。这两个bit不是互斥的，很多时候这两个bit都是同时置1。

也就是说，tid_next到tcb有指向关系，tcb到tid_next也有一个标志位，这两个方向应该同时满足。为了维护数据一致性，我们必须在更新tid_next的同时，也设置tcb里面的位，整个过程要保证原子性。