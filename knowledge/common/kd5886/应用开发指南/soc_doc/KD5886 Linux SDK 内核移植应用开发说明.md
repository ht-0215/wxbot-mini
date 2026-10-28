# KD5886 Linux SDK 内核移植应用开发说明

KD5886 Linux SDK

内核移植应用开发说明

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 前言	5

2 开发环境	6

2.1 嵌入式开发环境简介	6

2.2 Linux 开发环境简介	6

2.3 搭建 Linux 开发环境	7

2.3.1 安装 Linux 服务器	7

2.3.2 获取 SDK	7

3 快速指导	8

3.1 编译内核镜像文件	8

3.2 烧写镜像文件	8

3.3 运行测试程序	8

4 调试	10

5 根文件系统	14

5.1 概述	14

5.2 BusyBox 相关	15

5.3 Buildroot package相关	16

5.4 用户定制文件	16

6 应用程序开发	18

6.1 编写 hello.c应用程序	18

6.2 编译器路径设置	18

6.3 编译 linux应用程序	19

6.3.1 直接命令方式编译	19

6.3.2 编写 Makefile 编译	19

6.4 执行 linux应用程序	20

6.4.1 拷贝linux应用程序到rootfs	20

6.4.2 运行应用程序	20

术语与缩略语

| Abbreviations 缩略语 | Full spelling 英文全名 | Chinese explanation 中文解释 |
| --- | --- | --- |
| KD5886 | KD5886 | 基于 CK810 CPU 的高性能 SoC |
| SDK | Software Developer’s Kit | 软件开发工具包 |
| EVB | Evaluation Board | 评估板，用于芯片功能、性能评估的开发板 |
| JTAG | Joint Test Action Group | 联合测试工作组，C-SKY 基于 JTAG 标准，制作了CKLink调试器 |
| BusyBox | BusyBox | 一个集成了一百多个最常用 Linux命令和工具的软件 |
| rootfs | Root File System | 特指 Linux的根文件系统，包括了 Linux启动的时候所必须的一些目录结构和重要文件 |

# 前言

本文档介绍 Linux 开发环境。Linux 开发环境的搭建、Linux 内核、根文件系统以及内核和根文件系统的烧写，以及创建网络开发环境和如何启动 Linux 开发应用程序。

本文档主要提供让客户更快地了解 Linux 开发环境指导。

# 开发环境

## 嵌入式开发环境简介

由于嵌入式单板的资源有限，不能在单板上运行开发和调试工具，通常需要交叉编译调试的方式进行开发和调试，即“宿主机＋目标机（评估板）”的形式。宿主机和目标机一般采用串口连接，也可同时通过网口或者 JTAG连接，如下图所示。

图 1嵌入式开发图例

宿主机和目标机的处理器一般不相同。宿主机需要建立适合于目标机的交叉编译环境。程序在宿主机上经过“编译－连接－定位”得到可执行文件。通过一定的方法将可执行文件烧写到目标机中，然后在目标机上运行。

目标机上的 Bootloader 启动后，目标机中的操作信息通过串口或者网口输出到宿主机上显示。在宿主机上的控制台中输入命令，可以控制目标机。

## Linux 开发环境简介

在 Linux 服务器（也可以是安装 Linux 的 PC）上建立交叉编译环境，Windows 工作台通过串口和网口与单板连接，开发人员可以在 Windows 工作台中进行程序开发，或者远程登录到 Linux 服务器进行程序开发。各部分具体软件介绍如下表所示：

表 1 Linux 开发环境各部分软件描述

| 软件 | 软件 | 描述 |
| --- | --- | --- |
| Windows 工作台 | 操作系统 | Windows 2000/XP/ |
| Windows 工作台 | 应用软件 | putty、超级终端、ftp服务器等软件 |
| Linux服务器 | 操作系统 | 无特别要求，可为 Ubuntu、 RedHat、 Debian 等。 内核版本支持 及以上版本。安装时建议选择完全安装。 |
| Linux服务器 | 应用软件 | NFS、 telnetd、 samba、 VIM等。其它应用软件根据具体开发需要而定，通常系统都已默认安装，只要适当配置即可。 |
| 单板（评估板） | 引导程序 | U-boot |
| 单板（评估板） | 操作系统 | KD5886 Linux，基于 Linux 标准内核 版本一致开发，根文件系统基于BusyBox版本制作而成。 |
| 单板（评估板） | 应用软件 | 包含telnetd、gdb server等常用命令 |
| 单板（评估板） | 程序开发库 | glibc-2.17版本 |

## 搭建 Linux 开发环境

### 安装 Linux 服务器

建议选择常用的 Linux 发行版，便于寻找各类技术资源。例如：

Ubuntu 较新的发行版，如 Ubuntu 16 LTS。（推荐）

RedHat 较新的发行版，如 RedHat Fedora Core 系列和 RedHat Enterprise Linux、RedHat

其它还有如 Debian、CentOS 等各类发行版也比较常用。

### 获取 SDK

KD5886 的 Linux SDK 发布，可从售前或售后处获得的离线压缩包。从 Release Notes 文档中获取版本号，然后从售前或者售后人员处，获取该指定版本的 tgz 压缩包形式的 SDK。将其复制到用于开发的 Linux 服务器上，然后用 tar -zxf xxx.tgz 解压缩。

# 快速指导

## 编译内核镜像文件

KD5886 Linux SDK发布时，已将评估板的各类参数配置好了，包括 U-Boot、Linux Kernel、BusyBox、rootfs 及测试应用，编译方法如下：

步骤 1 进入 SDK LINUX目录，命令如下：

$ cd  ./LINUX

步骤 2 选择评估板配置，命令如下：

$ make ARCH=csky CROSS_COMPILE=csky-abiv2-linux- menuconfig

步骤 3 编译，命令如下：

$ make ARCH=csky CROSS_COMPILE=csky-abiv2-linux- clean

$ make ARCH=csky CROSS_COMPILE=csky-abiv2-linux- uImage

步骤 4 查看编译结果，命令与可能的结果如下：

$ ls output/images

Kd5886_evb.dtb rootfs.cpio rootfs.tar spl_uboot.bin uImage

## 烧写镜像文件

目前需要烧写的主要分为两部分，第一部分是 U-Boot，第二部分是 Linux Kernel。

下文主要介绍快速烧写、启动的方法，如果需要进一步了解评估板的启动过程以及镜像的说明，请参考文档《KD5886 Linux SDK 镜像烧写指南》。

## 运行测试程序

上电，观察串口，当出现：

Welcome to Buildroot

buildroot login:

时，输入”root” + 回车，即可登录 Linux 系统的 shell 环境。

默认配置下，将会有一些测试用例，以视频播放为例：

步骤 1 挂载 EMMC分区

目的是使用事先在 EMMC中烧录的应用测试文件。

$ mount -t ext2 /dev/mmcblk1p1 /mnt

步骤 2 复制应用测试文件到内存

目的是使对应用测试文件的访问变快。

$ cp /mnt/test /tmp

步骤 3 进入工作目录

$ cd /example

步骤 4 测试文件

$ ./ test.sh /tmp/test

# 调试

Linux 内核的调试方法有几种，一种是不借助其它工具，依赖内核打印 printk(), 本文不做详细描述。

Linux 内核的调试的另外一种方法，是基于 C-SKY 的 CKLink JTAG 硬件调试器进行实时的 gdb 调试，CKLink 的两个版本如下图所示：

图 2 CKLink JTAG调试器

两款产品分别为 CKLink-Pro 和 CKLink-Lite。CKLink-Pro 支持更多的特性，具有更高的性能，更适用于 C-SKY 高端 CPU 中调试 Linux 系统。配合安装于 Linux 或者 Windows 中的 DebugServer 应用程序，可以完美地解决内核调试问题，可以使用 gdb 调试的所有特性，包括设置断点、查看修改寄存器或内存、查看 back trace 等等。

以 KD5886 EVB 为例，调试 Linux 内核时具体步骤如下：

步骤 1 做好调试前的准备：

将 CKLink与 EVB 板通过JTAG 相连。EVB 上电，CKLink USB 端口插入 PC；

启动 CSkyDebugServer这个 PC 应用程序；

点击 CSkyDebugServer上的“Control”→“RunDebugServer”，确认识别与连接成功，如下图所示：

图 3 CSkyDebugServer 连接 EVB 界面

上图中最后一行表明，CSkyDebugServer的 IP地址为 192.168.0.88，该IP将在下文中的.gdbinit中使用。

步骤 2 以下为针对 EVB 进行 DDR 初始化。

进入 ddr初始化工具目录：

$ cd ddr_init/KD5886

确保目录下.gdbinit 中的 JTAG 的地址与连接 EVB 板子的 CSkyDebugServer 所显示的 IP 地址相同。

(如果 CSkyDebugServer 显示有多个 IP，则选择其一，但必须保证在 Linux 调试环境下能 ping 通)

$ cat .gdbinit

tar jtag jtag://192.168.0.88:1025

....

加载 DDR 初始化 elf 文件，并等待加载完成：

$ csky-abiv2-linux-gdb ddr_init.elf

加载完成之后，会出现的打印输出与 gdb提示符，如下所示：

0x1fd00004 in __start ()

(cskygdb)

 按‘c’+ Enter 键开始运行，并等待初始化结束：

(cskygdb) c

Continuing.

Program received signal SIGTRAP, Trace/breakpoint trap.

0x1fd00136 in __exit_loop_start ()

(cskygdb)

按‘q' + Enter 键，再按’y’退出gdb 调试环境，返回 Linux shell 环境：

(cskygdb) q

A debugging session is active.

Inferior 1 [process <main>] will be killed.

Quit anyway? (y or n) y

$

至此，KD5886 EVB 的 DDR 初始化已经完成。

步骤 3 以下为加载、运行、调试 Linux的vmlinux（包括Linux内核与 rootfs）的方法：

正常情况下，运行需要的 gdbinit，使用 board/csky/KD5886_evb目录下的 gdbinit，需要确保.gdbinit中的JTAG Server的地址与连接 EVB 板子的JTAG Server的 IP 地址相同。

(如果 CSkyDebugServer 显示有多个 IP，则选择其一，但必须保证在 Linux 调试环境下能 ping 通)

$ cat ./board/csky/KD5886_evb/gdbinit

tar jtag jtag://192.168.0.88:1025

....

加载 vmlinux 文件，并等待加载完成

$ cd output/images

$ ../host/usr/bin/csky-abiv2-linux-gdb -x ../../board/csky/KD5886_evb/gdbinit

vmlinux

warning: A handler for the OS ABI "GNU/Linux" is not built into this configuration

of GDB. Attempting to continue with the default csky settings.

....

0x80200000 in _start ()

(cskygdb)

使用标准 gdb调试方法，增加所需的断点、watch等，然后按’c’ + Enter键运行，例如：

(cskygdb) b start_kernel

Breakpoint 1 at 0x805e23d4: file init/main.c, line 484.

(cskygdb) c

Continuing.

Breakpoint 1, start_kernel () at init/main.c:484

484 set_task_stack_end_magic(&init_task);

(cskygdb)

此时 CPU 运行到了 start_kernel()函数并停止下来，用户可以在(cskygdb) 提示符下，进行 print变量，查看 backtrace等各种gdb调试操作，更多 gdb调试方法这里不再赘述。

 按‘q' + Enter 键，再按’y’退出gdb 调试环境，返回 Linux shell 环境：

(cskygdb) q

A debugging session is active.

Inferior 1 [process <main>] will be killed.

Quit anyway? (y or n) y

$

# 根文件系统

## 概述

Linux 的目录结构的最顶层是一个被称为“/”的根目录。系统加载 Linux 内核之后，就会挂载一个设备到根目录上。存在于这个设备中的文件系统被称为根文件系统。所有的系统命令，系统配置以及其他文件系统的挂载点都位于这个根文件系统中。

根文件系统通常存放于内存和 Flash 中，或是基于网络的文件系统。根文件系统中存放了嵌入式系统使用的所有应用程序、库以及其他需要用到的服务。下图列出了根文件系统的顶层目录：

表 2 Linux 根文件系统简介

| 目录名称 | 目录用途 |
| --- | --- |
| bin | 基本命令的可执行文件 |
| dev | 设备文件 |
| etc | 系统配置文件，包括启动文件 |
| init | 系统启动程序 |
| lib | 基本库，例如 C库和内核模块 |
| lib32 | 是 lib的软链接 |
| media | 媒体文件 |
| mnt | 临时文件系统的挂载点 |
| opt | 添加的软件包 |
| proc | 内核以及进程信息的虚拟文件系统 |
| root | root用户目录 |
| run | 存放的是自系统启动以来描述系统信息的文件（取代原/var/run） |
| sbin | 用于系统管理的可执行程序 |
| sys | 系统设备和文件层次结构，向用户提供详细的内核数据信息 |
| tmp | 临时文件 |
| usr | 该目录的二级目录包含许多对用户很有用的应用程序和文档 |
| var | 存放系统日志或一些服务程序的临时文件 |

rootfs的产生在 SDK 中是由多种途径产生和组合而成，包括：

由 BusyBox 编译产生 rootfs 的基础文件；

由 Buildroot 配置的各种 package 源码包产生的库或可执行文件；

用户定制文件。下面分别介绍两部分配置和产生的方法。

由于种类繁多，本文给以上三种方法各举一些例子供用户参考。

## BusyBox 相关

以 KD5886 EVB 为例，BusyBox 的配置存放于 buildroot 目录下的board/csky/KD5886_evb/busybox.config，如果需要修改默认配置，方法如下：

步骤 1 确保已经经过首次编译，进入 BusyBox源码目录，命令如下：

$ cd output/build/busybox-/

步骤 2 打开 BusyBox配置界面，命令如下：

$ make menuconfig

界面如下图中的“BusyBox 配置界面”所示。

步骤 3 修改 BusyBox配置，退出保存。

步骤 4 经过步骤 3，新的配置文件存在于BusyBox源码目录的.config中。为了保存该新配置，最好将其复制到板级配置目录中，方法如下：

$ cp output/build/busybox-1.27.1/.config board/csky/KD5886_evb/busybox.config

警告：

如果对 BusyBox 及 Eragon EVB 没有足够了解，请勿修改默认配置，否则可能造成系统异常。

图 4 BusyBox 配置界面

## Buildroot package相关

在“Buildroot 配置”章节中，曾提到 Buildroot 配置的方法，这里再着重介绍一下如何在 rootfs中，添加所需要的 package。

Buildroot 中的 package，存放于其根目录下的 packages 目录中，但其内容仅限于名称、版本、哈希和一些patch。 只有当用户在Buildroot的menuconfig中， 增加package之后， 编译时才会被下载到buildroot中，编译并且安装到 rootfs 中去。

以 KD5886 EVB 为例，当需要增加 alsa-lib 到 rootfs中时，步骤如下：

步骤 1 进入 SDK目录，例如 buidroot目录，命令如下：

$ cd buildroot

步骤 2 打开 Buildroot配置界面，命令如下：

$ make menuconfig

然后进入 Target packages子菜单，如下图所示：

图 4-9 Buildroot package 配置界面

步骤 3 进入 Libraries -> Audio/Sound 中，选中 alsa-lib，然后在其中，选择所需的选项，保存后退出 menuconfig

步骤 4 保存之后，配置保存于 buildroot 根目录下的.config，为了保存于 KD5886 EVB 中，我们需要将该文件保存于configs/KD5886_evb_defconfig中，则需要执行如下命令：

make savedefconfig

步骤 5 重新编译整个 Buildroot，执行如下命令：

make

## 用户定制文件

无论是 BusyBox 还是 Buildroot package，都是通过 Buildroot 中相关配置得到的编译结果，而客户也有些自己的文件需要放入 rootfs 中。以 KD5886 EVB 为例，在 Buildroot 的板级配置目录中，有如下这个目录：output/build/linux-4.9.56/addons/fs-overlay，这个目录中存放着用户自己的文件，这个在最后生成rootfs时，将用来覆盖自动生成的 rootfs。

以 KD5886 EVB 为例，output/build/linux-4.9.56/addons/fs-overlay 目录结构如下：

[fs-overlay]$ tree

.

├── etc

│ └── init.d

│ └── rcS

└── lib

└── firmware

└── vpu_fw_eragon.bin

当修改完 fs-overlay 里的文件之后，可以使用如下方法快速获得新的 rootfs:

步骤 1 进入 SDK目录，例如 buidroot目录，命令如下：

$ cd buildroot

步骤 2 touch一下.config，目的是为了让Makefile系统感知到已经有了变化，命令如下：

$ touch .config

步骤 3 编译，命令如下：

$ make

此时就获得了新的含 rootfs的镜像：output/images/uImage。

# 应用程序开发

本节以最简单的 hello,world 打印应用为例，说明如何使用 KD5886 Linux SDK 进行应用程序开发。

## 编写 hello.c应用程序

嵌入式环境下的应用程序编写和通常的 PC 上的没有什么不同。主要实现下面一段程序：

#include <stdio.h>

int main(void)

{

printf("hello,world\n");

return 0;

}

将上述代码保存成 hello.c。

## 编译器路径设置

由于代码是在开发板上执行，所以需要使用交叉编译的方式，将代码编译成可在开发板 CPU 上执行的格式。 Buildroot中提供了对应的编译器， 在首次编译Buildroot后， 会将工具链自动解压在output/host/usr/bin/目录中。在我们应用程序开发过程中需要把对应的编译器路径加到环境变量 PATH中。具体如下：

$ export PATH=$PATH:path_of_buildroot/output/host/usr/bin/

其中：path_of_buildroot 是 buildroot 所在目录, 根据用户实际情况而定。

## 编译 linux应用程序

### 直接命令方式编译

使用以下命令编译：

$ csky-abiv2-linux-gcc -g hello.c -o hello

### 编写 Makefile 编译

上述的编译是最简单的方式，但是如果是比较多的文件的话，通过编写 Makefile 来编译就更方便。

同样以 hello.c 文件的编译为例，编写下面的 Makefile。

CC := csky-abiv2-linux-gcc

CFLAGS := -Wall -g -O0

EXEC := hello

all: $(EXEC)

$(EXEC): $(EXEC).c

$(CC) $(CFLAGS) -o $@ $<

clean:

$(RM) $(EXEC)

将上述的 Makefile 保存在和 hello.c 同样的目录里，执行: make 就可以生成 hello。

Makefile 内容说明：

- CC : 指定默认的 gcc 编译器。

- CFLAGS: 指定编译选项，-g 与-O0是为了方便将来 gdbserver 调试。

- EXEC: 生成的可执行文件名。

- all: 默认的 Makefile 执行选项。

- clean: 清除编译生成的可执行文件。

## 执行 linux应用程序

### 拷贝linux应用程序到rootfs

为了在开发板上执行 linux 应用程序，首先需要把 Linux 应用程序拷贝到 rootfs上，主要有下面几种方式：

1. 使用 nfs挂载本地目录

nfs挂载方式是最佳的应用开发方式。在开发板上挂载了 Linux 服务器 nfs 目录之后，Linux 服务器上编译完应用程序，开发板上可以立即运行，而无需额外操作。

前提：

- 开发板上的网络已启动，且和 Linux 服务器 IP 可互相访问（例如在同一网段）。

- Linux 服务器的 nfs server 服务已启动。

在开发板的终端上执行下述命令挂载：

$ mount -t nfs 192.168.2.102:/path/to/test /mnt/nfs -o nolock,tcp

说明：192.168.2.102 为 Linux 服务器 IP，/path/to/test 目录保存 linux 应用程序，/mnt/nfs 为开发板上的挂载点。

2. 放入 fs-overlay 目录，重新生成 rootfs

将应用程序放在 fs-overlay 目录下，重新编译生成 rootfs，这样开发板启动后就会包含对应的应用程序。详细可参考本文“用户定制文件”章节。

### 运行应用程序

直接通过串口终端或是 telnet 命令连接到开发板上，就可以执行上述的 hello 命令。

$ ./hello

hello,world

结果如上所示，输出 hello,world 字符串。
