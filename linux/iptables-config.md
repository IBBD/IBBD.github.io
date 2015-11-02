# iptables线上服务器配置案例

## 问题 

我们有多台线上服务器，组成了一个内网，每台服务器都有内网ip和外网ip，只有一台服务器是访问的入口，现在需要配置iptables，已满足以下需求：

- 内网的操作不做限制
- 外网连接内网服务器时，只允许ssh的方式
- 在内网请求外网的服务不受限制

## 解决

```sh
# create
iptables -N IBBD

# 外网网卡的流出流量, 使用IBBD链来处理
iptables -I INPUT   1 -i eth1 -j IBBD

# 如果有docker之类的，也能使用IBBD来处理
# 如果不加这个，请求可能会被其他规则优先处理掉了
iptables -I FORWARD 1 -i eth1 -j IBBD

# 定义规则 
iptables -A IBBD -p tcp   --dport 22          -j ACCEPT 
iptables -A IBBD -p tcp   --sport 22          -j ACCEPT 
iptables -A IBBD -m state --state ESTABLISHED -j ACCEPT
iptables -A IBBD -j DROP
```

解释一下上面的代码：

1. 创建了一个名为IBBD的规则链, 这样方便后面的处理
2. 将网卡eth1的流入和转发流量都使用IBBD规则链来处理
3. 在IBBD规则链里面
  1. 允许22端口通过
  2. 允许状态为`ESTABLISHED`的请求通过, 实现本机访问外部服务不受限制。
  3. 不满足上述条件的，全部丢弃

请求的状态是比较复杂的部分，这里做个简单的说明：

以TCP请求为例，大家都知道，每个tcp是有三次握手的概念的，第一次握手时，状态是`NEW`，后面的状态就变成了`ESTABLISHED`.
从本机发出的请求，第一次握手是走OUTPUT链的，所有在INPUT链上收到的状态肯定都是`ESTABLISHED`, 这就区分了从外部请求本机的情况。

而udp, icmp也有类似的状态。

## 遇到的问题

### 区分外网流量和内网流量的问题

开始的时候考虑使用ip段来区分，例如`192.168.1.0/24`, `10.0.0.0/8`等，但是需要处理的情况很多，除了上面说的两种，还有本地回路，如果使用docker，还有docker0对应的ip 

规则复杂，没配置成功。。。

后来一想，外网的流量都是经由`eth1`进来的

### INPUT链与OUTPUT链的问题

服务器的流入流量免费，但是流出流量收费，所以开始时跑偏了题，从OUTPUT链入手。。。


## 扩展阅读

iptables 涉及的概念和内容还比较多，可以阅读下面的内容：

- [iptables指南](http://man.chinaunix.net/network/iptables-tutorial-cn-1.1.19.html)

