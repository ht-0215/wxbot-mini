# sdk 编译介绍

sdk 编译介绍

版本 V1.1

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
| 2023.08.28 | 进行内容微调，减少歧义 | V1.1 | 梁航 |
|  |  |  |  |

目录

1 简介	4

2 设置环境变量	5

3 执行makeflie	6

4 目标生成路径修改	7

# 简介

目前只支持linux 编译环境。

编译分为3个步骤：

配置编译环境。

配置环境变量。

执行make 命令。

# 配置编译环境

如果要编译sdk包含platform，则只需要将 交叉编译工具，kernel(已编译) 解压缩放到合适目录下，并变更 设置环境变量 里的。

默认是

交叉编译工具放置在 /opt

Linux内核放置在 /opt/kernel

# 设置环境变量

环境变量的脚本在systems下面，使用setvarsCHIP_ARCH.sh 命名格式，如 setvarsKD5886_Csky.sh ，可通过下面命令设置环境变量。

source systems/linux/setvarsKD5886_Csky.sh

目前只支持linux编译环境，如setvarsKD5886_Csky.sh。

export ARCH=csky

export KERNEL_DIR=/opt/kernel/linux-4.9.56

#export KERNEL_DIR=/home/wyang/osdrv/linux-4.9.56

export CROSS_COMPILE=csky-abiv2-linux-

export CROSS_LIB_PATH=/opt/csky-ck810-linux/host/lib

export HOST_HW_PLATFORM=SOC_KD5886

export EIP197_HW_CONF=f

export EIP197_BUS_VERSION=AXI3

export EIP197_ARC4=n

export EIP197_SHA3=n

export EIP197_NOF_RINGS=4

export DDK_HOST64=n

export DDK_DEVICE64=n

export HOST_COMPILER=gcc

export USER_LFLAGS=

export BUILD_CONFIGS=

export EARLY_USER_LFLAGS=""

export EIP28_HW_TYPE=EIP28_PKCP

export FW_EIP28_ROM=n

export EIP76_POSTPROC_TYPE=sp80090

export EIP76_PRM_ENABLED=Y

export FW_EIP207_API_DIR=./Firmware

export CHIP_NAME=kd5886

export OS_TYPE=linux

export DEBUG_DDK=y

有些地方根据需要修改：如KERNEL_DIR，KERNEL目录不对，有些依赖kernel的模块编译不过。

执行：

source systems/linux/setvarsKD5886_Csky.sh  或者一条一条的执行。

# 执行makeflie

make help

***************************help**********************************************************

make all: compile all moudles ; make cleanall: clean all moudles

make [sdk]: compile sdk ; make clean: clean sdk

make platform: compile platform moudles,make platformclean: clean platform moudles

make all :傻瓜编译模式,不需要了解各个模块编译方法,编译所有模块。建议第一次编译需要执行。需要linux内核正常配置。

make platform：编译 platform 里面的一些模块。一般用在开发模式。

make 或  make sdk ，编译sdk。一般用在开发模式。

每个make 有对应的make clean.

# 目标生成路径修改

OUTPUT 环境变量指定，如果为指定，

默认在output目录下，可以同通过 OUTPUT = $(SDK)/output/$(OS_TYPE)/$(CHIP_NAME)/$(ARCH)  指定路径 .
