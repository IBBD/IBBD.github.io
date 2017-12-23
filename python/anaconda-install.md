# Anaconda安装（ubuntu16.04）

## 安装Anaconda3

- Anaconda的官方下载网址在 https://www.continuum.io/downloads/
- 国内的镜像：https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/

Step01: 安装命令：

```sh
bash Anaconda3-5.0.1-Linux-x86_64.sh -b -p $HOME/anaconda/envs/py3
```

Step02: 配置.bashrc, 在文件`~/.bashrc`的最后加上：

```sh
export PATH="/home/alex/anaconda/envs/py3/bin:$PATH"
```

注：如果使用zsh，记得配置文件`.zshrc`

Step03: 判断是否成功

```sh
# 打开新终端
conda info -envs

conda list

python --version
# Python 3.6.3 :: Anaconda custom (64-bit)
```

Step04: 激活环境

```sh
source activate py3
```

注：如果需要删除anaconda的话，直接删掉anaconda的文件夹就行。

