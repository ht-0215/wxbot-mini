# KD5886 Linux SDK U-Boot 移植应用开发说明

KD5886 Linux SDK U-Boot 移植应用开发说明

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

2 快速指南	6

2.1 代码位置	6

2.2 代码编译打包	6

2.3 镜像烧写及启动内核	6

3 开发环境搭建	7

3.1 工程代码解压	7

3.2 工具链准备	7

4 整体流程	8

4.1 总体介绍	8

4.2 第一阶段 SPL功能	8

4.2.1 SPL 配置	9

4.3 第二阶段 U-Boot 功能	9

5 源码目录结构	10

5.1 ARCH 目录	10

5.2 board 目录	10

5.3 configs 目录	11

5.4 include 目录	11

6 代码编译	12

6.1 准备配置文件	12

6.1.1 默认配置文件	12

6.2 编译 U-Boot	12

6.3 编译过程及结果	13

6.3.1 区分 SPL 与U-Boot	13

6.3.2 链接脚本	13

6.3.3 编译产物	13

7 运行调试 U-Boot	15

7.1 准备.gdbinit 文件	15

7.2 加载运行	15

7.2.1 运行 SPL	15

7.2.2 运行 U-Boot	16

8 流程解析	19

8.1 Bootrom 加载 SPL	19

8.2 U-Boot 启动 Linux	19

9 开发移植说明	22

9.1 注意事项	22

9.2 移植的一般步骤	22

9.2.1 确定启动流程	22

9.2.2 U-Boot代码框架	22

9.2.3 驱动开发	23

9.2.4 板级移植（代码添加）	23

9.2.5 制作配置文件	24

9.2.6 编译调试	24

# 前言

U-Boot，全称 Universal Boot Loader，是遵循 GPL 条款的开放源码项目。U-Boot 的作用是引导后一级的系统，例如 Linux 系统。其源码目录、编译形式与 Linux 内核很相似，事实上，不少 U-Boot 源码就是根据相应的 Linux 内核源程序进行简化而形成的，尤其是一些设备的驱动程序，这从 U-Boot 源码的注释中能体现这一点。

本文第一部分是介绍如何快速上手，去编译和使用 U-Boot；第二部分是详细介绍 U-Boot 的流程，目录结构，移植开发等技术细节。

本文档旨在为需要进行 U-Boot 开发的工程师提供快速上手的说明指南，通过本文，用户可以在开发板上进行进一步的开发，从而开发出属于自己的 U-Boot。

如没有特殊的说明，本文的所有操作目录是 U-Boot 工程的根目录。

# 快速指南

本章着重介绍如何快速的使用 U-Boot。用户可以通过阅读本章，跳过大部分技术细节，直接按步骤执行，从而最快速的将 U-Boot 使用起来。

为了达到目的，本章介绍在 buildKD5886SDK 编译环境下的 U-Boot 使用。本章的所有目录均是以buildKD5886SDK 为根目录。

## 代码位置

在./u-boot 下。

## 代码编译打包

可视化菜单配置：

make ARCH=csky CROSS_COMPILE=csky-abiv2-linux- menuconfig

编译：

make ARCH=csky CROSS_COMPILE=csky-abiv2-linux- clean

make ARCH=csky CROSS_COMPILE=csky-abiv2-linux-

打包：

./upack ./spl/u-boot-spl.bin u-boot.bin u-pack.bin

## 镜像烧写及启动内核

编译产生的镜像是u-pack.bin，位置在./u-boot 中。

具体的烧写方式请参考文档《KD5886 Linux SDK 镜像烧写指南》。

启动内核的方法请参考文档《KD5886 Linux SDK 用户指南》，具体原理在下文会有提到。

# 开发环境搭建

## 工程代码解压

tar -zxvf buildKD5886SDK.tar.gz

## 工具链准备

sudo tar -zxvf csky810CrossTool.tar.gz -C /opt/csky-ck810-linux

用户可以把它解压到自己虚拟机的特定目录（用户自行制定）。

将工具链的 bin 目录加入到环境变量$PATH中去，例如可以加入到 home目录中的.bashrc 中，方法如下：

打开.bashrc 文件。

$ sudo vi ~/.bashrc

在文件的末尾添加：

export PATH=$PATH: /opt/csky-ck810-linux/host/bin

最后执行：

$ source ~/.bashrc

# 整体流程

## 总体介绍

U-Boot 的整体流程如下图所示：

图  U-Boot 整体流程

（1） 评估板的启动是从 bootrom 开始的，bootrom 会根据启动方式跳线设置，选择 调试启动模式还是直接从SPI FLASH存储区或者EMMC存储区启动 U-Boot。

（2） bootrom 会从存储区域搬运 SPL（U-Boot 的第一阶段）到 SRAM 中。

（3） SPL 启动后初始化 DDR，然后从外部存储器，如SPI FLASH或者eMMC 搬运 U-Boot（第二阶段）到 DDR 高端地址。

（4） U-Boot（第二阶段）启动后，若在一定时间内无操作（一般是 3秒），则自动加载 Linux 内核并启动，若在时间内有任何操作，则进入 U-Boot 的命令行环境中，用户可以通过各种命令来使用 U-Boot 支持的功能。

## 第一阶段 SPL功能

由于 U-Boot 的功能很多，所以决定了它的体积不会小，因此它被拆分为两个阶段，第一阶段是 SPL，第二阶段是 U-Boot。

SPL，即 Secondary Program Loader。SPL 主要负责 DDR 初始化并搬移 U-Boot 第二阶段的代码到内存中运行。SPL 是由固化在芯片内部的 ROM 引导的（即 Bootrom）。

SPL 由于其大小的优势（一般在 20K 以内），可以在 SRAM 中运行，保证 U-Boot 的运行环境。

### SPL 配置

SPL 作为新版 U-Boot 的一种特性，是可选的。用户需要根据自己 SOC 的硬件配置以及业务流程来进行取舍。

要打开 SPL 这个功能，需要在配置文件中打开宏 CONFIG_SPL_FRAMEWORK，或者打开在menuconfig 中的 Boot images---->Enable SPL。

## 第二阶段 U-Boot 功能

第二阶段可以说是 U-Boot 的主体，U-Boot 在 DDR 中运行，具备强大的功能，如读写各类 FLASH，可以通过网卡下载镜像文件，并具有命令行，方便用户的操作。

U-Boot 一般占 200KB 的大小，当然实际大小会随功能的多少而改变。本次发布的 U-Boot 具备读写eMMC和SPI FLASH 的功能， 也有用 TFTP 的方式从服务器下载镜像的功能，当然还有 U-Boot最主要的功能： 启动Linux。

# 源码目录结构

U-Boot 的目录结构如下表所示：

目录名      描述

arch        各种芯片架构的相关代码、U-Boot入口代码。

board       各种单板的相关代码，主要包括存储器驱动等。

board/csky/kd5886_evb  KD5886评估板相关代码。

arch/xxx/lib  各种体系结构的相关代码，如CSKY、ARM、MIPS 的代码。

include      头文件。

include/configs 各种单板的配置文件。

common     各种功能（命令）实现文件。

drivers       网口、Flash、串口等的驱动代码。

接下来介绍相关目录的结构和作用。

## ARCH 目录

arch目录作为U-Boot中最核心的目录之一， 存放了各种芯片架构的相关代码， 下面介绍CSKY的ARCH目录。

arch 目录主要分成三部分：cpu、include、lib。

cpu 目录下存放各型号的 CPU 对应的启动文件：start.S，u-boot.lds（U-Boot 的链接脚本），目前在目录中的是 CK807 以及 CK810。

include 目录下存放各种类型的库函数的声明，也存放针对特定板子的头文件。

lib 目录下存放处理器共用的代码。

## board 目录

board目录也是 U-Boot 的核心目录之一，主要存放各种板级的相关文件，包括一些板级驱动。

csky目录下存放特定开发板的私有文件，如 kd5886_evb 中可以存放非公共的驱动。

common目录下存放着 CSKY 各个 SOC 共用的一些驱动文件， 如串口驱动， SPI FLASH 驱动， eMMC驱动等，需要说明的是，这些驱动都是在 SPL 中使用的，目的是减小代码大小。

## configs 目录

configs 目录中存放了所有板子的默认配置文件，这些配置文件指定了 ARCH 以及 SOC，主要是关于编译选项的配置。

Kd5886 的默认编译配置文件是 KD5886_defconfig

## include 目录

include 目录存放了 U-Boot 所有公共的头文件，比如 common.h 这类的通用头文件。

需要特别介绍的是./include/configs/这个目录， 这个目录存放着每一块板子的代码配置文件， KD5886代码配置文件是 KD5886.h。

在编译时，U-Boot 最终使用的配置文件就是由 KD5886.h 变化而来。

# 代码编译

在准备好编译工具链和工程代码后，就可以进行 U-Boot 工程的编译了。

## 准备配置文件

这里所说的配置文件指的是编译相关的配置，包括 ARCH 与 SOC 的选择。

最后会生成.config 文件，生成此文件的方式有两种。

### 默认配置文件

使用每块板子的默认配置文件，这是最简单的方式，所有板子的默认配置文件都在./configs/下

kd5886 的配置文件是./configs/KD5886_ defconfig

只需要执行：

$ make KD5886_defconfig

这样就会在根目录下生成.config，其中包含了 ARCH 信息以及 SOC 信息。

## 编译 U-Boot

编译的方式很简单，仅需要在根目录执行：

$ make

下面来说明一下原理。

原本的 U-Boot 还需要指定 ARCH 以及工具链，但是这些在本工程中已经指定。

请查看根目录下的 Makefile，其中有这样的配置：

ARCH = csky

CROSS_COMPILE = csky-abiv2-linux-

因此，需要的操作就只剩下 make。

## 编译过程及结果

### 区分 SPL 与U-Boot

这里简单说明一下编译过程，因为一旦引入了 SPL，U-Boot 的编译过程就变得比较特别。

虽然只进行了一次编译（make），但是编译的过程却有两条线。

SPL与U-Boot共用很多文件， 比如start.S， KD5886.h， 区分这两者的标志是宏CONFIG_SPL_BUILD，

这个宏是在 Makefile 中添加到配置文件中的，这意味着 SPL 与 U-Boot 在最终使用的配置文件是不同的。

在编译完成后，根目录下有 u-boot.cfg以及在 spl 目录下 u-boot-spl.cfg，这两个配置文件的相似度很高，而区分它们的就是宏 CONFIG_SPL_BUILD。

正因为有 CONFIG_SPL_BUILD，U-Boot 和 SPL 才可能在复用配置文件的情况下又相互独立。

### 链接脚本

SPL 与 U-Boot 使用不同的链接脚本，SPL 的链接脚本需要用户指定，U-Boot 的链接脚本在用户没有

指定时，Makefile会去三个地方寻找链接脚本。

Makefile中的规则如下：

KD5886  SPL 的链接脚本指定在 KD5886.h 中：

#define CONFIG_SPL_LDSCRIPT “board/csky/kd5886_evb/KD5886/u-boot-spl.lds”

### 编译产物

SPL 的所有产物都在 spl 目录下， 包括中间文件 （.o文件） ， 目标文件是 u-boot-spl 以及 u-boot-spl.bin。

其中 u-boot-spl是 elf 文件。

U-Boot 的所有产物在根目录下，中间文件则分散在各目录中，目标文件是 u-boot 以及 u-boot.bin。

# 运行调试 U-Boot

U-Boot 的运行有两种方式，一种是将 bin 文件烧写到 FLASH 的特定位置进行冷启动，另一种是通过GDB 加载 elf 文件到评估板中运行。

前一种方式用户可以参考《Kd5886 Linux SDK 镜像烧写指南》。

由于在调试阶段，GDB 加载调试是主要的开发手段，所以下面介绍 GDB 加载的方式启动 U-Boot。

## 准备.gdbinit 文件

在工程的根目录下存在文件.gdbinit，其内容如下：

target remote 192.168.245.1:1025

set $gcr=0x00

lo

其中的 IP 地址请参考 DebugServer 连接后的结果进行修改。

## 加载运行

### 运行 SPL

SPL 在 SRAM 运行，因此不需要在运行之前进行 DDR 的初始化。

步骤 1 加载u-boot-spl 初始化程序

在控制台中执行：

$ csky-abiv2-linux-gdb -x .gdbinit ./spl/u-boot-spl

预期结果：

Loading section .text, size 0x45b2 lma 0xfffe0000

Loading section .rodata, size 0x12b7 lma 0xfffe45b4

Loading section .data, size 0x15 lma 0xfffe586c

Start address 0xfffe0180, load size 22654

Transfer rate: 14 KB/sec, 2831 bytes/write.

_start () at arch/csky/cpu/ck807_810/start.S:37

37          mfcr    r3, psr

Loading section .text, size 0x45b2 lma 0xfffe0000

Loading section .rodata, size 0x12b7 lma 0xfffe45b4

Loading section .data, size 0x15 lma 0xfffe586c

Start address 0xfffe0180, load size 22654

Transfer rate: 14 KB/sec, 2831 bytes/write.

(cskygdb)

步骤 2 运行

(cskygdb)c

预期结果：

Program received signal SIGTRAP, Trace/breakpoint trap.

0x1fd001d6 in __exit_loop_start ()

(cskygdb)

步骤 3 退出程序

(cskygdb)q

效果如下：

Wellcome to SPL!

The U-Boot-spl start.

U-Boot version is 2016.07, internal version is 0.5

### 运行 U-Boot

如果要运行 U-Boot，请先运行 SPL DDR 初始化的程序。

具体操作：

步骤 1 加载 U-Boot

$ csky-abiv2-linux-gdb -x .gdbinit u-boot

预期结果：

Loading section .text, size 0x19a18 lma 0x17a00000

section progress: 100.0%, total progress: 75.4%

Loading section .rodata, size 0x71a0 lma 0x17a19a18

section progress: 100.0%, total progress: 96.3%

Loading section .data, size 0xfa5 lma 0x17a20bb8

section progress: 100.0%, total progress: 99.2%

Loading section .u_boot_list, size 0x468 lma 0x17a21b60

section progress: 100.0%, total progress: 100.0%

Start address 0x17a00180, load size 139205

Transfer rate: 1022 KB/sec, 3866 bytes/write.

0x17a00180 in _start ()

(cskygdb)

如果需要调试，则可以设置断点如：

(cskygdb)b board_init_r

也可以查看变量，如查看变量 xxx：

(cskygdb)p xxx

具体操作以实际为准，请用户参考 GDB 调试的标准操作。

如果需要直接运行：

(cskygdb)c

退出程序

(cskygdb)q

步骤 3 U-Boot有 3秒等待时间，3 秒内按下回车键即可进入命令行。

预期结果：

U-Boot 2016.07

DRAM: 64 MiB

MMC: KD5886 DWMMC: 0

In: serial

Out: serial

Err: serial

Net: dwmac.bfb10000

Warning: dwmac.bfb10000 (eth0) using random MAC address - be:fa:16:59:44:05

Hit any key to stop autoboot: 0

CK807 #

CK807 #

CK807 #

# 流程解析

本章主要对两个阶段进行比较深入的解释，一个是 Boortrom 加载 SPL 的过程，另一个是 U-Boot 加载Linux 的过程。

## Bootrom 加载 SPL

由于 Bootrom 没有手段获知 SPL 的准确大小，因此在 Bootrom 加载 SPL 时，Bootrom 只能从固定起始偏移地址为 0x8000位置的 FLASH或者EMMC 中拷贝 32K 的一段代码到 SRAM首地址中运行。预留FLASH和EMMC存储器的0~0x8000共32K存储空间给用户自行定义使用。

下面是流程示意图：

图  Bootrom 加载 SPL

## U-Boot 启动 Linux

U-Boot 启动 Linux 是 U-Boot 最为核心的功能，目前自动加载 Linux 运行的方式是：

图  U-Boot 加载

（1） 将 KD5886_evb.dtb 从 SPI FLASH | eMMC 的 2MB 处读取出来。

（2） 将 uImage 从 SPI FLASH | eMMC 的 4MB 处读取出来。

（3） 将 KD5886_evb.dtb 写入 DDR 中的 0x0f000000 处。

（4） 将 uImage 写入 DDR 的 0x10000000 处。

（5） 解压 uImage，并传递 DTB 文件的 DDR 地址给 Linux。

（6） 启动 Linux。

启动 Linux 使用的命令是 bootm，可以在 cmd/bootm.c中找到它对应的函数 do_bootm。最终调用

common/bootm.c中的 do_bootm_states。

在使用 bootm 命令时，用户只需要给出 uImage 在 DDR 中的地址，即 0x10000000。

最后实现 MAGIC 值传递以及 Linux 跳转的函数位于 arch/csky/lib/bootm.c 中的函数 do_bootm_linux。

实现如下：

图  U-Boot 向 Linux传递参数

其中的 MAGIC 值为 0x20150401，是与 Linux 约定好的值，dtb_load_addr 则是 0x8f000000（打开 MMU 后的虚拟内存地址）。

到目前为止所有的中断都会被禁用，而且在 KD5886 中的 U-Boot 中，并不支持中断。

# 开发移植说明

本章主要说明，如何一步一步地配置，完成一个能跑在 KD5886 SOC 芯片上的 U-Boot。

## 注意事项

要在一块板子上移植 U-Boot，需要了解一些基本知识。

（1） 板子使用的 ARCH 是什么，使用了哪个 SOC。

（2） 板子上的硬件环境是什么样的，比如DDR 的大小和位置等。

（3） 明确 U-Boot 所能访问的 FLASH 是什么类型的，空间有多大，如何分配。

比如 KD5886 使用的是 CK810 的核，SOC 是 KD5886，board 是 KD5886_evb。

这些配置信息决定了 KD5886 的 U-Boot 在工程中选择哪些目录的代码进行编译。

## 移植的一般步骤

### 确定启动流程

流程的确定十分重要，流程决定了 U-Boot 将要使用哪些资源，需要哪些代码的支持。

Kd5886硬件资源需要 SPI FLASH，eMMC，DDR，串口，BOOT MODE 管脚等。

### U-Boot代码框架

U-Boot 作为一个开源项目，它有属于自己的公共代码流程，代码执行流程如下：

图  U-Boot 代码执行流程

其中函数 borad_init_f 与 board_init_r 是 U-Boot 的公共代码，位置在 common/board_f.c 和

common/board_r.c中。

这两个函数的主要功能是对 U-Boot 进行全方面的初始化，包括各种外设的初始化以及划分内存空间，让 U-Boot 处在一个合适的空间，分配堆栈等等工作。

U-Boot 移植的大部分工作就是去实现这两个函数调用到的函数（用户需要的）。

### 驱动开发

在前面列出的各种硬件资源，需要对应的软件驱动才可以被用户使用。

U-Boot 本身含有大量公共驱动，但如果外设的 IP 没有对应的公共驱动，则需要另外开发驱动，这里不细讲。

### 板级移植（代码添加）

板级的目录都在 board/csky/目录下，不同的板子有各自的目录，目前板级只有 kd5886_evb 目录，此目录为 kd5886 系列的总目录。

板级移植以 KD5886 为例，在 board 下 csky目录中的 kd5886_evb 目录下（board/csky/kd5886_evb）主要存放文件 kd5886_evb.c 这个文件，其中定义了板级相关配置的函数。

在 kd5886_evb.c 中，需要定义一些支持驱动初始化的函数，以满足 U-Boot 的初始化，举例来说：

函数 board_mmc_init 就是这样，它的目的是初始化 MMC，其内部实现由用户决定，KD5886 中使用的MMC 驱动是 design ware 的，因此 board_mmc_init 的内部实现就是 design ware 的 MMC 初始化。

而 board_mmc_init 的调用则是由 U-Boot 决定，用户只有打开或关闭此功能的权利，但是此函数的调用位置是固定的（在 mmc.c 中被调用，mmc.c是 MMC 驱动执行的核心逻辑）。

如果有需要，该 board/csky/kd5886_evb 下还可以放置一些驱动，不过这些驱动只应该在 SPL 阶段使用，在 U-Boot 阶段就应该使用其框架下的驱动了（U-Boot 使用的驱动一般都有其事先定义好的核心逻辑，如 MMC 驱动的 mmc.c，用户只需要去具体实现核心逻辑需要调用的函数实现，如 board_mmc_init）。

### 制作配置文件

相关的配置文件有两个，一个是用于功能配置 KD5886_defconfig，位于 configs 目录下，此文件用于生成.config 文件，其中包含的是编译配置相关的信息；另一个是板级配置的 KD5886.h，位于include/configs目录下，此文件内包含的是程序运行时的相关配置，如寄存器基址，芯片主频等。

另外用户可以通过 menuconfig 来修改.config 文件的配置。

$ make menuconfig

### 编译调试

编译调试是开发中无法跳过的阶段，其中有关编译选项的选择，Makefile的逻辑等等，另外还有可能碰到语法错误等等的编译问题。

编译完成后，成功生成 u-boot 的相关产物。
