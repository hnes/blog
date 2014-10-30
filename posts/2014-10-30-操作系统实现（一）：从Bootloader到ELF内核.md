操作系统实现（一）：从Bootloader到ELF内核
====================================

Bootloader
----------

我们知道计算机启动是从BIOS开始，再由BIOS决定从哪个设备启动以及启动顺序，比如先从DVD启动再从硬盘启动等。计算机启动后，BIOS根据配置找到启动设备，并读取这个设备的第0个扇区，把这个扇区的内容加载到`0x7c00`,之后让CPU从`0x7c00`开始执行，这时BIOS已经交出了计算机的控制权，由被加载的扇区程序接管计算机。

这第一个扇区的程序就叫Boot，它一般做一些准备工作，把操作系统内核加载进内存，并把控制权交给内核。由于Boot只能有一个扇区大小，即512字节，它所能做的工作很有限，因此它有可能不直接加载内核，而是加载一个叫Loader的程序，再由Loader加载内核。因为Loader不是BIOS直接加载的，所以它可以突破512字节的程序大小限制（在实模式下理论上可以达到1M）。如果Boot没有加载Loader而直接加载内核，我们可以把它叫做Bootloader。

Bootloader加载内核就要读取文件，在实模式下可以用BIOS的`INT 13h`中断。内核文件放在哪里，怎么查找读取，这里牵涉到文件系统，Bootloader要从硬盘（软盘）的文件系统中查找内核文件，因此Bootloader需要解析文件系统的能力。GRUB是一个专业的Bootloader，它对这些提供了很好的支持。

对于一个Toy操作系统来说，可以简单处理，把内核文件放到Bootloader之后，即从软盘的第1个扇区开始，这样我们可以不需要支持文件系统，直接读取扇区数据加载到内存即可。

实模式到保护模式
-------------

我们知道Intel x86系列CPU有实模式和保护模式，实模式从8086开始就有，保护模式从80386开始引入。为了兼容，Intel x86系列CPU都支持实模式。现代操作系统都是运行在保护模式下（Intel x86系列CPU）。计算机启动时，默认的工作模式是实模式，为了让内核能运行在保护模式下，Bootloader需要从实模式切换到保护模式，切换步骤如下：

1. 准备好GDT(Global Descriptor Table)
2. 关中断
3. 加载GDT到GDTR寄存器
4. 开启A20，让CPU寻址大于1M
5. 开启CPU的保护模式，即把cr0寄存器第一个bit置1
6. 跳转到保护模式代码

GDT是Intel CPU保护模式运行的核心数据结构，所有保护模式操作的数据都从GDT表开始查找，[这里](http://wiki.osdev.org/GDT_Tutorial)有GDT的详细介绍。

GDT中的每一个表项由8字节表示，如下图：

![GDT Descriptor](http://wiki.osdev.org/images/f/f3/GDT_Entry.png "GDT Descriptor")

其中Access Byte和Flags如下图：

![GDT bits](http://wiki.osdev.org/images/1/1b/Gdt_bits.png "GDT bits")

[这里](http://wiki.osdev.org/Global_Descriptor_Table)是详细说明。

GDTR是一个6字节的寄存器，有4字节表示GDT表的基地址，2字节表示GDT表的大小，即最大65536（实际值是65535，16位最大值是65535），每个表项8字节，那么GDT表最多可以有8192项。

实模式的寻址总线是20bits，为了让寻址超过1M，需要开启A20，可以通过以下指令开启：

	in al, 0x92
	or al, 2
	out 0x92, al

把上述步骤完成之后，我们就进入保护模式了。在保护模式下我们要使用GDT通过GDT Selector完成，它是GDT表项相对于起始地址的偏移，因此它的值一般是`0x0` `0x8` `0x10` `0x18`等。

ELF文件
------

Bootloader程序是原始可执行文件，如果程序由汇编写成，汇编编译器编译生成的文件就是原始可执行文件，也可以使用C语言编写，编译成可执行文件之后通过objcopy转换成原始可执行文件，[这篇文章](http://crimsonglow.ca/~kjiwa/x86-dos-boot-sector-in-c.html)介绍了用C语言写Bootloader。

那么内核文件是什么格式的呢？跟Bootloader一样的当然可以。内核一般使用C语言编写，每次编译链接完成之后调用objcopy是可以的。我们也可以支持通用的可执行文件格式，ELF(Executable and Linkable Format)即是一种通用的格式，它的[维基百科](http://en.wikipedia.org/wiki/Executable_and_Linkable_Format)。

ELF文件有两种视图（View），链接视图和执行视图，如下图：

![ELF Views](/images/elf_views.jpg "ELF Views")

链接视图通过Section Header Table描述，执行视图通过Program Header Table描述。Section Header Table描述了所有Section的信息，包括所在的文件偏移和大小等；Program Header Table描述了所有Segment的信息，即Text Segment, Data Segment和BSS Segment，每个Segment中包含了一个或多个Section。

对于加载可执行文件，我们只需关注执行视图，即解析ELF文件，遍历Program Header Table中的每一项，把每个Program Header描述的Segment加载到对应的虚拟地址即可，然后从ELF header中取出Entry的地址，跳转过去就开始执行了。对于ELF格式的内核文件来说，这个工作就需要由Bootloader完成。Bootloader支持ELF内核文件加载之后，用C语言编写的内核编译完成之后就不需要objcopy了。

为什么写操作系统
-------------

首先是兴趣，在现在这个时代，写操作系统几乎没有实用价值，只能是一个Toy，在写一个Toy OS时，可以学习掌握很多知识，并把这些知识贯穿实用起来。操作系统是一个复杂的系统，牵涉到的东西很多，我相信写操作系统可以帮助理解现代操作系统及其它底层知识。我目前才刚开始写，代码放在[Github](https://github.com/airtrack/airix)上。