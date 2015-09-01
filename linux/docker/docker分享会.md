# 20150901 Docker主题分享

## Docker解决什么问题

Docker可以解决虚拟机能够解决的问题，同时也能够解决虚拟机由于资源要求过高而无法解决的问题。Docker能处理的事情包括：

- 隔离应用依赖
- 创建应用镜像并进行复制
- 创建容易分发的即启即用的应用
- 允许实例简单、快速地扩展
- 测试应用并随后销毁它们

Docker背后的想法是创建软件程序可移植的轻量容器，让其可以在任何安装了Docker的机器上运行，而不用关心底层操作系统，就像野心勃勃的造船者们成功创建了集装箱而不需要考虑装在哪种船舶上一样。

## 基本概念

### 整体架构

见：https://www.processon.com/view/link/55dc515de4b0f425ec5a48a6

### 镜像

Docker的镜像类似虚拟机的快照，但更轻量，非常非常轻量。

### 容器

从镜像中创建容器，这等同于从快照中创建虚拟机，不过更轻量。应用是由容器运行的。

### Dockerfile

可以说是创建容器的原材料，通过编译之后就能生成镜像。

- nginx：https://github.com/IBBD/dockerfile-nginx/blob/master/Dockerfile
- php：https://github.com/IBBD/dockerfile-php-fpm/blob/master/Dockerfile

### docker-compose

一个开发环境或者生成环境，可能需要多个镜像，而且他们之间可能存在各种link关系，使用docker-compose能更好的对他们进行管理，减少可能的人为错误。

- php开发环境：https://github.com/IBBD/docker-compose/blob/master/php-dev/docker-compose.yml

## 内部如何使用

以下是基于ubuntu14.04系统（12.04上安装docker可能会有问题）：

- 安装docker环境：https://github.com/IBBD/docker-compose/blob/master/install-docker.sh
- git clone相关dockerfile：https://github.com/IBBD/docker-compose/blob/master/git-clone-all-dockerfiles.sh
- 配置好相关目录（待完善）
- 在各个目录下运行：`./build.sh`


