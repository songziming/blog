---
title: "Git工作流"
---

##### 避免提交记录产生分支

分支最常见于多人同时更新，后一个提交更新的人执行`git pull`之后，会自动产生一个分支合并操作。

为了避免这个问题，将`git pull`替换为`git fetch && git rebase`。相当于首先同步代码，之后再进行代码更新。

##### 清空项目的提交记录（commit history）

- 首先创建一个新的独立分支：`git checkout --orphan new`。
- 将当前的所有文件添加到这个分支下：` git add --all`。
- 提交代码：`git commit -m "commit message"`。
- 删除原来的master分支：`git branch -D master`，并将新分支改名为master：`git branch -m master`。
- 如果设置了远程仓库，把当前的master分支推送上去：`git push -f origin master`。

##### 使用多个远程仓库（remote repo）

Git是一个“分布式”的版本管理工具，虽然有local、remote的区别，但每一个仓库仍然是独立的，因此一个本地仓库也可以添加多个远程仓库。使用`git clone`创建本地仓库时，Git会自动关联一个远程仓库，并命名为`origin`，这个名字也是执行`fetch`、`pull`、`push`操作时的默认远程仓库。

- 查看现有的远程仓库：`git remote -v`。
- 添加一个远程仓库：`git remote add <name> <repo-url>`。
- 重命名远程仓库：`git remote rename <old-name> <new-name>`。

##### 伪造Git提交时间

在提交的时候，指定`--date`参数：

~~~ bash
git commit --date "Tue, 05 Mar 2019 17:15:58 +0800"
~~~

Git支持RFC-2822时间格式，最后的`+0800`表示东八区，也就是中国所在的时区。在Linux下可以通过`date -R`输出RFC-2822格式的当前时间。

Git记录的时间实际上有两个：author_data、committer_date。使用`--date`参数只能修改author_date。
