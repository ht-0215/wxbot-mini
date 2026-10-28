# bootrom说明

BOOTROM使用说明

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 摘要	4

2 工作流图	5

3 BOOTROM文件存储运行空间	6

4 二级BOOT文件存储运行空间	7

5 BOOTROM串口使用配置	8

6 BOOTROM SPI通信配置	9

7 BOOTROM EMMC通信配置	10

# 摘要

针对SOC上ROM容量受限特性和宽泛性应用场景的一种增强SOC通用性和安全性的ROM引导方法，包括：

支持 SFDP 标准协议

SFDP标准是 JEDEC （固态技术协会）制定的串行 Flash 功能的参数表标准。该标准规定了，每个 Flash 中会存在一个参数表，该表中会存放 Flash 容量、写粒度、擦除命令、地址模式等 Flash 规格参数。软件可以通过查询读取 SFDP 表参数动态获取到串行Flash 规格参数。

支持 eMMC 标准协议

eMMC标准是 MMC协会所订立的内嵌式存储器标准规格。该标准制定了eMMc接口规范和通信协议。软件可以通过eMMC通信协议查询获取到eMMC规格参数，并通过eMMC通信协议完成对eMMC的擦除和存取操作。

支持安全启动特性

安全启动主要实现固件在线升级。

# 工作流图

# BOOTROM文件存储运行空间

BOOTROM起始地址偏移：0x0 ;

BOOTROM二进制文件最大尺寸：小于32K ;

BOOTROM: 0~32K   规划用于BOOTROM代码段;

BOOTRAM : 32K~64K 规划用于BOOTROM数据段;

# 二级BOOT文件存储运行空间

SPI flash存储起始地址偏移：0x8000 ;

EMMC存储起始地址偏移： boot1分区 0x8000  ;

二级boot二进制文件最大尺寸：小于32K ;

BOOTRAM : 0~32K   规划用于二级boot运行代码段;

BOOTRAM : 32K~64K 规划用于二级boot运行数据段;

# BOOTROM串口使用配置

Uart0 :  baudrate:115200

bit: 8

stop: 1

no parity

# BOOTROM SPI通信配置

SPI通信速率: 2M

数据位宽：8 bit

# BOOTROM EMMC通信配置

低速：400K

高速：5M

位宽：1/4/8 bit
