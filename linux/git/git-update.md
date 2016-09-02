# 在Ubuntu上升级git

升级命令：

```sh
sudo add-apt-repository ppa:git-core/ppa
sudo apt-get update
sudo apt-get install git
```

如果提示`add-apt-repository`没有安装，则先执行：

```sh
sudo apt-get install software-properties-common
sudo apt-get install python-software-properties

# 如果是python3
sudo apt-get install python3-software-properties
```

如果安装完之后，使用`git version`看到的还是旧的版本号，则需要确认系统是否安装了多个git。使用`which git`看看是不是`/usr/bin/git`，还是`/usr/local/bin/git`, 或者其他，对应的确认其版本号，协作旧的即可，或者直接重命名。


