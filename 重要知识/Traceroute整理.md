#　Traceroute命令解析
---

## Traceroute

#### 基本含义
traceroute是追踪路径的命令；traceroute命令用来显示数据包到达目标主机**所经过的路径，并显示到达每个节点的时间**；

通过traceroute我们可以知道信息从你的计算机到互联网另一端的主机是走的**什么路径**


#### 协议
ICMP协议

#### 原理
假设A点traceroute节点E,过程如下：

首先，在节点A发出一个TTL是1的ip包到达目的地；

当路径上第一个路由B收到这个包时，它将TTL减1；此时TTL变为0，所以路由B会把此包丢掉，并回送A一个超时消息；该消息也是一个ip包，里面包括发ip包的源地址A、ip包的所有内容和路由B的ip地址；节点A收到这个消息后，便知道路由B位于这个路径上；

接着，traceroute再送出另一个TTL为2的包，发现第二个路由C......依次下去，traceroute每次将送出包的TL加1来发现一个路由，重复这个动作直到某个包到达目的地E。

此时，该主机不会回复超时消息，因为E已经是目的地了。

Traceroute如何知道到达了目的地呢？

traceroue在送出ip包到达目的地E时，将选择一个一般都不会使用的端口号；当ip包到达目的地E后，该节点会回送给A一个“端口不可达”消息，当A收到这个消息，便知道目的地已经到达了。

使用traceroute之前，一般先使用ping确定是否联通。


#### 作用
当出现网络故障时，可以查看是那条路径发生了拥塞，有利于快速排查故障；


#### 注意
在windows中，traceroute命令写作tracert

---
以上内容参考自：《一本书读懂TCP/IP》 8.3节内容；


2017.09.30
