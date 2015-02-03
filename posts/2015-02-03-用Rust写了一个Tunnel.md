用Rust写了一个Tunnel
==================

2014年的最后一个星期用Rust写了一个Tunnel，代码放在[GitHub](https://github.com/airtrack/stunnel)上。主要原因是VPN在12月开始极不稳定，其次是VPN用起来不爽，每次下东西都要关VPN，而用`ssh -D`时偶尔又会断开，最后干脆自己写一个（其实年初就想写，因为买了VPN就不想折腾了）。

编译和使用
--------

现代语言一般都自带编译工具，不用折腾`make` `cmake`等东西，Rust官方提供了[Cargo](https://crates.io/)，所以编译很简单，安装好`Cargo`，然后到源码目录下`Cargo build`就完成了。

编译完成得到两个可执行文件，分别是：`client` `server`，`server`启动在服务器上，`client`启动在本机并绑定到地址`127.0.0.1:1080`，浏览器由代理插件通过`SOCKS v5`协议连接这个地址即可。

Tunnel逻辑结构
-------------

下面是逻辑图：

	            .                      |                     .
	            .                      f                     .
	            .                      i                     .
	port1 ------|                      r                     |------ port1
	            |                      e                     |
	            |                      |                     |
	port2 ---client---------------- tunnel ----------------server--- port2
	            |                      |                     |
	            |                      w                     |
	port3 ------|                      a                     |------ port3
	            .                      l                     .
	            .                      l                     .
	            .                      |                     .

Client和Server之间通过一条TCP链接相连，客户端每收到一个TCP请求就开一个`port`处理，同时在Server上有一个`port`与之对应，这样就在Client和Server之间建立了一个会话层，这个TCP链接的数据全部都在对应的`port`里传输。

Tunnel本身跟`SOCKS v5`不相关，为了让浏览器代理能连上，Client提供了`SOCKS v5`中最简单的`NO AUTHENTICATION TCP`方法，即无用户名和密码的TCP代理。

Client和Server之间传输的数据都加了密，加密算法是Blowfish，工作模式是[Counter Mode](http://zh.wikipedia.org/wiki/%E5%9D%97%E5%AF%86%E7%A0%81%E7%9A%84%E5%B7%A5%E4%BD%9C%E6%A8%A1%E5%BC%8F#.E8.AE.A1.E6.95.B0.E5.99.A8.E6.A8.A1.E5.BC.8F.EF.BC.88CTR.EF.BC.89)，`client`和`server`启动时的参数Key即加密算法的Key。

Rust的使用感受
------------

以前虽有关注Rust，却从没用Rust写过代码，主要是还未发布1.0，语法不稳定，最近1.0快有眉目了，可以用来写写小东西了。因为有Haskell的基础，所以上手Rust对我来说没什么难度。

Rust提供了ADT(Algebraic Data Type), Pattern Matching, Traits，语法表达能力很强，同时也提供了macro，可自定扩展语法，进一步加强了语法表达能力。自动内存管理也让程序更安全，不过由此也带来一些语法表达能力的削弱，比如需要在函数返回的时候自动调用`socket.close_read`，通常可以定义一个struct，并让这个struct`impl` `trait Drop`，在结构体销毁的时候调用`socket.close_read`，又因为`socket.close_read`需要`mut`的socket引用，而`mut`的引用只能`borrow`一次，所以这个struct一旦`borrow`了socket的`mut`引用，之后再调用这个socket的`mut`函数就会报错，一个workaround的方法就是struct保存socket的一份拷贝（socket本身通过引用计数管理），虽然可行，但是总感觉有些重了，仅仅为写起来方便的一个问题引入了一次引用计数对象的拷贝。同时也会产生一个警告，由于那个struct的对象没有被使用过。

Rust编译器报错信息很详细友好，运行时依赖小，Tunnel编译出来的的`client`和`server`都可以在其它机器上直接运行。其它方面主要是API文档跟不上，最新文档上有的函数，编译器编译可能报错，函数已经不存在了（刚刚去看了看最新的文档，`std::io`变成了`std::old_io`）。库方面，虽然`Cargo`仓库里有一些第三方库，但是总体数量还不多。
