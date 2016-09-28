# 基于Git的分支与发布规范

- `master`: 主开发分支, 测试服务器上部署该分支. 个人可以基于master分支进行开发, 多人协作时, 也可以各自建立自己的本地开发分支.
- `release`: 发布分支, 这是受保护分支, 经过相关的测试才能合并到该分支. 联调服务器上部署该分支
- 在正式服务器上, 基于`tag`进行发布, tag是从release分支而来.
- 产品维护过程中的bug fix, 基于release分支进行. 

注: 在多分支的情况下, 提交代码时, 务必注意所在分支, 如在release分支提交需要用`git push origin release`or`git push origin release:release`, 在master提交到master通常是默认的, 可以使用简化的命令`git push`即可.


---------

Date: 2016-09-02  Author: alex cai <cyy0523xc@gmail.com>
