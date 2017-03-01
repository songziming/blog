---
title: Reinforcement Learning
---

强化学习（RL）是一种通过试错不断改进自身的学习算法。agent通过选择并执行动作与环境进行交互，

### Markov Decision Process (MDP)

马尔可夫决策过程（MDP）是一种离散时间随机控制过程。在任何时刻，系统都处在某个状态$s$之下，决策者会执行一个动作$a$，该动作会导致系统随机地转换到新的状态$s'$（两个状态可以相同），并产生一个立即回报$r(s,a,s')$。

### Agent-Environment Interface
