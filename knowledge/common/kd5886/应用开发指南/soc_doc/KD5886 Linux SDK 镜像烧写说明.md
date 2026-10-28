# KD5886 Linux SDK 镜像烧写说明

KD5886 Linux SDK

镜像烧写说明

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 前言	4

1.1 概述	4

1.2 产品版本	4

1.3 读者对象	4

2 串口烧写 U-Boot	5

2.1 连接关系	5

2.2 工作方式	5

2.3 前期准备	5

2.4 烧写步骤	6

3 U-Boot 烧写镜像	7

3.1 连接关系	7

3.2 目标概述	7

3.3 前期准备	7

3.3.1 评估板端	7

3.3.2 服务器端	8

3.4 烧写 eMMC 的分区表	9

3.4.1 eMMC分区说明	9

3.5 烧写媒体文件分区镜像	10

3.6 烧写 Linux 内核以及 DTB 镜像	10

4 U-Boot 中部分命令介绍	11

4.1 TFTP 下载命令	11

4.2 eMMC 读写命令	11

4.2.1 读命令	11

4.2.2 写命令	11

4.2.3 擦命令	12

# 前言

## 概述

本文档主要是指导使用相关软件对目标镜像进行烧写，包括如何接线以及需要注意的问题。

## 产品版本

与本文档对应的产品版本如下：

产品名称      软件版本

KD5886 EVB    KD5886 Linux SDK 1.0

## 读者对象

本文档主要适用于以下工程师：

 技术支持工程师

 软件开发工程师

# 串口烧写 U-Boot

本章介绍如何使用 SECURECRT 串口工具烧写 U-Boot。

## 连接关系

我们通过串口连接 SECURECRT 与评估板的 bootrom，然后通过YMODEM协议实现文件的传输与烧写。

具体如图：

图 1 SECURECRT 与评估板的连接

## 工作方式

步骤 1 SECURECRT 工具通过计算机串口，实现与评估板bootrom 的连接

步骤 2 SECURECRT 工具通过Ymodem串口协议将U-BOOT 的镜像文件分批发送至发送到评估板的 SRAM中

步骤 3 bootrom将接收到的信息写入 Emmc或者SPI FLASH 。

## 前期准备

（1） 串口线连接

这里使用的是 UART0，设置baudrate:115200  bit: 8  stop: 1  no parity

（2） 调整 BOOT SELECT 管脚

BOOT SELECT管脚决定了 bootrom 的工作模式。设置为DEBUG BOOT 启动模式。

用跳线帽设置 BOOT SELECT 管脚的值，下面是对应关系。

BOOT SELECT0  BOOT SELECT1  BOOT SELECT2     功能描述

0              0            0                SPI FLASH 启动

1              0            0                1线EMMC 启动

0              1            0                4线SPI FLASH 启动

1              1            0                8线SPI FLASH 启动

X              X            1                DEBUG BOOT 启动

## 烧写步骤

步骤 1准备 U-Boot镜像u-boot.img。

发布包中有提供 u-boot.img。

用户也可以使用编译 u-boot生成的，在./u-boot目录下。

步骤 3 配置及烧写

设置baudrate:115200  bit: 8  stop: 1  no parity

#To add late

# U-Boot 烧写镜像

本章依赖于前一章节的基础，即需要 U-Boot 已经被烧写完毕。

U-Boot 需要烧写的镜像为 KD5886_evb.dtb 和 uImage，获取方式有两种。

（1） SDK 发布包中含有所有相关镜像。

（2） linux 工程的./output/images 目录下含有相关镜像。

## 连接关系

关系如图：

图 2 U-Boot 烧写关系图

## 目标概述

首先是服务器端准备相应的镜像文件， 然后将BOOT SELECT管脚设置成eMMC模式或者SPI模式， 启动U-Boot。

U-Boot 配置网卡信息，从服务器下载对应镜像到内存，最后将镜像烧写到 eMMC或者SPI FLASH。

## 前期准备

### 评估板端

要进行镜像的下载，需要先配置网卡等信息。

步骤 1 将评估板的启动

步骤 2 电脑端准备需要烧写的镜像。

步骤 3 将 BOOT SELECT管脚调整到 eMMC 模式或 SPI 模式。

步骤 4 评估板上电，启动 U-Boot。

步骤 5 配置网卡。

$ setenv ipaddr 172.16.150.100

$ setenv netmask 255.255.255.0

$ setenv gatewayip 172.16.150.254

$ setenv serverip 172.16.28.18

简单说明：

ipaddr是评估板的 ip地址

serverip是服务器端的ip地址

这里设置的地址仅供参考，实际值取决于用户的网络环境。

步骤 6 保存 ENV

$ saveenv

说明：

保存 ENV 是为了下次启动时不用再次设置。

### 服务器端

建立 TFTP服务器，可以使用发布包中提供的软件 tftpd64.exe

如图：

图 3 tftpd64 使用

需要用户在红色按钮处给出镜像文件所在文件夹的路径。

## 烧写 eMMC 的分区表

在进行下列操作时请确保前期准备已经完成。

步骤 1 开发板上电，启动 U-Boot。

步骤 2 下载分区表镜像到内存。

$ tftpboot 0x80000000 eMMC_MBR.bin

步骤 3 将内存的分区表镜像烧到 eMMC 中。

$ mmc write 0x0 0x0 0x1

-结束-

### eMMC分区说明

eMMC 的分区大小的默认设置如下图：

图 4 eMMC 分区说明

1) 前 64M 的裸分区中存放分区表信息、DTB 文件以及内核镜像，如下图

图 5 前 64M 裸分区说明

这 64M 的空间不进行格式化以及分区处理，作为裸分区存放上述内容，用户无法在文件系统中访问这个空间。

其中 eMMC 的 1 sector = 512B。

2) 128M 的媒体分区用来存放在外设操作时可能用到的音视频文件，另外还有图片文件。

3) 剩余的所有空间都留给用户自由使用，用户可以把这个空间作为一个分区使用，也可以分成多个分区使用。

4) 除了烧写 MBR 表的方式之外，还可以手动对 eMMC 进行分区。

## 烧写媒体文件分区镜像

媒体文件分区镜像是以 ext2 格式打包的文件镜像，其中包含了本公司提供的各种媒体文件，主要用于验证 SDK 发布包中提供的各类驱动。

媒体文件分区镜像可以在 SDK 发布包中获取。

在进行下列操作时，请确保 eMMC 分区表镜像已经正常烧写，或者正常手动分区。

步骤 1 开发板上电，启动 U-Boot。

步骤 2 下载镜像文件到内存。

$ tftpboot 0x80000000 media-partition.ext2

步骤 3 查看 eMMC 的分区信息

$ mmc part

预期结果：

Part     Start Sector     Num Sectors     UUID         Type

1         131008        262208        00000000-01   83

2         393216         15237120     00000000-02   83

步骤 4 烧写入 eMMC

$ mmc write 0x0 0x1ffc0 0x40001

## 烧写 Linux 内核以及 DTB 镜像

DTB 镜像是 DTS 配置文件生成的，主要作用是配置 Linux 各种驱动设备，比如 Timer、UART 等等，此镜像可以在 linux 的./output/images 目录中获取。

在进行下列操作时，请确保前期准备已经完成。

步骤 1 开发板上电，启动 U-Boot。

步骤 2 下载并烧写 DTB 镜像。

$ run update_dtb

步骤 3 下载并烧写 linux内核。

$ run update_linux

# U-Boot 中部分命令介绍

## TFTP 下载命令

U-Boot 中，TFTP 方式下载文件使用的命令是 tftpboot

具体方法

tftpboot [loadAddress] [[hostIPaddr:] bootfilename]

boot image via network using TFTP protocol

举例：

$ tftpboot 0x800000000 media-partition.ext2

其中 0x80000000 是开了 MMU 之后的内存 0地址。

media-partiton.ext2 是文件名称。

这里隐去了 hostIPaddr，是因为已经设置了 serverip 的 ENV 值。

## eMMC 读写命令

需要注意 eMMC 的所有命令，其中的参数都需要是 16 进制数。

### 读命令

mmc read addr blk# cnt

举例：

KD5886 # mmc read 0x0 0x1ffc0 0x40001

其中 0x0 是内存 0 地址，不能使用 MMU 开启后的地址，只能使用原始的物理地址。

0x1ffc0是起始的 sector 值。

0x400001 是 sector 的数量，即文件的大小。

### 写命令

mmc write addr blk# cnt

举例：

KD5886 # mmc write 0x0 0x1ffc0 0x40001

所有参数的解释与读命令相同，两者仅为相反的操作。

### 擦命令

一般来说，在 eMMC 烧写文件之前，是不需要擦除原有的数据的。

mmc erase blk# cnt

举例：

KD5886 # mmc erase 0x0 0x1

其中 0x0 是起始的 sector。

0x1 是需要擦除的 sector 的数量。
