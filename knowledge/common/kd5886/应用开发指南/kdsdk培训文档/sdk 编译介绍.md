# sdk 编译介绍

1：简介：

目前只支持linux 编译环境。

编译分为2个步骤：

配置环境变量。编译环境脚本放在 systems目录下，如

source systems/linux/setvarsKD5886_Csky.sh

执行make 命令。

make all  ,make xxx

2：设置环境变量。

环境变量的脚本在systems下面，使用setvarsCHIP_ARCH.sh 命名格式，目前只支持linux编译环境，如setvarsKD5886_Csky.sh。

export ARCH=x86

export KERNEL_DIR=/usr/src/linux-headers-4.8.0-36-generic

#export KERNEL_DIR=/usr/src/linux-headers-4.15.0-29-generic

export KERNEL_DIR=/usr/src/linux-headers-4.10.0-28-generic

export HOST_HW_PLATFORM=SOC_KD6630_PCI

export DDK_HOST64=y

export DDK_DEVICE64=n

export HOST_COMPILER=gcc

export USER_LFLAGS=

export CROSS_COMPILE=

export CROSS_LIB_PATH=

export EARLY_USER_LFLAGS=""

export BUILD_CONFIGS=

export WARNING_FLAGS=""

export CHIP_NAME=kd6630

export DEBUG_DDK=y

export OS_TYPE=linux

有些地方根据需要修改：如KERNEL_DIR，KERNEL目录不对，有些依赖kernel的模块编译不过。

执行：

source systems/linux/setvarsKD5886_Csky.sh  或者一条一条的执行。

3：执行makeflie

make help

***************************help**********************************************************

make all: compile all moudles ; make cleanall: clean all moudles

make [sdk]: compile sdk ; make clean: clean sdk

make platform: compile platform moudles,make platformclean: clean platform moudles

make all :傻瓜编译模式,不需要了解各个模块编译方法,编译所有模块。建议第一次编译需要执行。

make platform：编译 platform 里面的一些模块。一般用在开发模式。

make 或  make sdk ，编译sdk。一般用在开发模式。

每个make 有对应的make clean.

4: 目标生成路径修改 ：

OUTPUT 环境变量指定，如果为指定，

默认在output目录下，可以同通过 OUTPUT = $(SDK)/output/$(OS_TYPE)/$(CHIP_NAME)/$(ARCH)  指定路径 .
