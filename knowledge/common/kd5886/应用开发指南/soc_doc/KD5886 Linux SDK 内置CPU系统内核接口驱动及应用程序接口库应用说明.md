# KD5886 Linux SDK 内置CPU系统内核接口驱动及应用程序接口库应用说明

KD5886 Linux SDK

内置CPU系统内核接口驱动及应用程序接口库移植开发说明

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 前言	6

1.1 概述	6

1.2 产品版本	6

1.3 读者对象	6

2 编译链接加载	7

2.1 设置环境变量	7

2.2 内核驱动编译	8

2.3 应用程序接口库编译	8

2.4 内核驱动加载和卸载	8

2.5 应用程序接口链接库加载	14

3 内核设备驱动接口	16

3.1 内核设备驱动加载卸载	16

3.2 内核设备驱动卸载	16

3.3 设备驱动注册初始化	17

3.4 设备驱动注销	18

3.5 中断管理	18

3.5.1 中断号分配	18

3.5.2 中断初始化	19

3.5.3 中断去初始化	20

3.5.4 中断使能	20

3.5.5 中断关闭	21

3.6 符设备	22

3.6.1 字符设备初始化	22

3.6.2 字符设备去初始化	22

3.7 DMA内存管理	23

3.7.1 内存管理记录表项初始化	23

3.7.2 内存管理记录表项去初始化	25

3.7.3 用户设备交互共享内存管理初始化	25

3.7.4 用户设备交互共享内存管理去初始化	26

3.7.5 共享设备交互内核支持初始化	26

3.7.6 共享设备交互内核支持去初始化	27

3.8 内核驱动设备集管理	28

3.8.1 设备集初始化	28

3.8.2 设备集去初始化	28

3.8.3 设备查找	29

3.8.4 设备添加	30

3.8.5 设备删除	31

3.8.6 设备寄存器读取	31

3.8.7 设备寄存器写入	32

4 应用程序链接库接口	34

4.1 驱动设备集管理	34

4.1.1 设备集初始化	34

4.1.2 设备集去初始化	35

4.1.3 设备查找	35

4.1.4 设备添加	36

4.1.5 设备删除	37

4.1.6 设备寄存器读取	38

4.1.7 设备寄存器写入	39

4.2 中断管理	40

4.2.1 中断号分配	40

4.2.2 中断初始化	41

4.2.3 中断去初始化	42

4.2.4 中断使能	43

4.2.5 中断关闭	43

4.2.6 中断注册	44

4.3 DMA内存管理	45

4.3.1 DMA内存管理记录表项初始化	45

4.3.2 DMA内存管理记录表项去初始化	45

4.3.3 DMA设备内存资源申请	46

4.3.4 DMA设备内存资源释放	47

4.3.5 DMA内存主机设备地址域转换	49

4.3.6 DMA内存主机设备地址域内存地址对记录添加	50

# 前言

## 概述

本文档主要是指导使用内置CPU系统进行内核接口驱动及应用程序接口库的设计、移植和开发。

## 产品版本

与本文档对应的产品版本如下：

产品名称      软件版本

KD5886 EVB    KD5886 Linux SDK 1.0

## 读者对象

本文档主要适用于以下工程师：

 技术支持工程师

 软件开发工程师

# 编译链接加载

本章介绍如何编译加载内核接口驱动和链接应用程序接口库。

## 设置环境变量

假定用户为XXXX, 内核版本位置在 /home/XXXX/osdrv/linux-，交叉编译工具链位置在/opt/ csky-ck810-linux ，DDK位置在/home/XXXX/osdrv/kdv03/kd5886-ddk/DDK，可以编辑环境变量设置脚本setvarsSoc.sh，setvarsSoc.sh参考内容如下（根据实际需要进行相应的修改设置）：

export ARCH=csky

export KERNEL_DIR=/home/XXXX/osdrv/linux-

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

export FW_EIP207_API_DIR=../Firmware/eip197/api

export HOST_COMPILER=gcc

export FW_EIP207_SRC_DIR=../Firmware

export USER_LFLAGS=

export BUILD_CONFIGS=

export DDKDIR=/home/XXXX/osdrv/kdv03/kd5886-ddk/DDK

alias gd='cd /home/XXXX/osdrv/kdv03/kd5886-ddk/DDK'

export EARLY_USER_LFLAGS=""

export EIP28_HW_TYPE=EIP28_PKCP

export FW_EIP28_ROM=n

export EIP76_POSTPROC_TYPE=sp80090

export EIP76_PRM_ENABLED=Y

进入到工作目录：cd  ~/ osdrv/kdv03/kd5886-ddk/DDK

运行环境变量设置脚本：./ setvarsSoc.sh

## 内核驱动编译

进入到工作目录：

cd  ~/ osdrv/kdv03/kd5886-ddk/DDK/ Examples/Driver_KernelSupport/SHDevXS/build

执行：

make

编译结束将生成SOC设备管理驱动程序：umdevxs_k.ko

## 应用程序接口库编译

进入到工作目录：

cd  ~/ osdrv/kdv03/kd5886-ddk/DDK/ Examples/Driver /build

执行：

make

编译结束将生成SOC设备管理应用程序接口链接库：libdriver_eip_u.a

## 内核驱动加载和卸载

进入到NFS网络根文件系统：

cd  ~/ NFSROOT

拷贝运行脚本到网络根文件系统：

cp ~/osdrv/kd5886ddk/DDK/Examples/Driver_KernelSupport/SHDevXS/scripts/loadsoc.sh ./

cp ~/osdrv/kd5886ddk/DDK/Examples/Driver_KernelSupport/SHDevXS/scripts/unloadsoc.sh ./

cp ~/osdrv/kd5886ddk/DDK/Examples/Driver_KernelSupport/SHDevXS/build/umdevxs_k.ko ./

启动内核并成功挂载NFS系统后，登陆到root用户,执行loadsoc.sh完成内核驱动加载：

[~]# ./loadsoc.sh

同理，执行unloadsoc.sh可以完成内核驱动卸载。

脚本loadsoc.sh文本内容如下：

#!/bin/sh

#

# loadsoc.sh

#

# This script loads the Kernel Support Driver (SHDevXS) and creates

# the communication point for the application (using the proxy).

#

DIR_NAME_DRIVER=SHDevXS

KO_NAME_DRIVER=umdevxs_k.ko

CHAR_NAME_DEVICE=umdevxs_c

dmesg -c > /dev/null 2>&1

if [ $? -ne 0 ]; then

echo "Not enough rights. Try sudo."

exit;

fi

# check if already loaded (0) or not yet loaded (1)

is_loaded=$(lsmod | grep $CHAR_NAME_DEVICE > /dev/null; echo $?)

if [ $is_loaded -eq 0 ]; then

echo "Already loaded; use unloadsoc.sh first";

exit;

fi

# check if the driver binary location is provided, if not use default

if [ $# -eq 1 ]; then

build=$1/$KO_NAME_DRIVER

else

build=./$KO_NAME_DRIVER

fi

if [ ! -f "$build" ]; then

echo "Fatal: cannot find driver";

exit;

fi

# load the driver

insmod $build

# grab the major number for the character device

major_nr=`awk "\\$2==\"$CHAR_NAME_DEVICE\" {print \\$1}" /proc/devices`

#echo "Major nr: $major_nr";

# make the communication pointer

mknod /dev/$CHAR_NAME_DEVICE c ${major_nr} 0

# make accessible to application

chmod 666 /dev/$CHAR_NAME_DEVICE

# print and clear start-up messages

dmesg -c

# end of file loadsoc.sh

脚本unloadsoc.sh文本内容如下：

#!/bin/sh

#

# unloadsoc.sh

#

# This script unloads the Kernel Support Driver and deletes the communication

# point for the application (using the proxy).

#

NAME_DRIVER=umdevxs_k

CHAR_NAME_DEVICE=umdevxs_c

# print and clear messages

dmesg -c 2>/dev/null

# check that we run with root rights

# (this assumes dmesg -c is root-only)

if [ $? -ne 0 ]; then

echo "Not enough rights. Try sudo."

exit;

fi

# remove the communication point

rm -f /dev/$CHAR_NAME_DEVICE

# unload the driver

rmmod $NAME_DRIVER

# print and clear the shutdown-messages

dmesg -c

# end of script unloadsoc.sh

## 应用程序接口链接库加载

编译SDK的应用程序需要链接应用程序接口链接库libdriver_eip_u.a，

通过编辑makefile实现链接应用程序接口链接库libdriver_eip_u.a。

编译应用程序pie_tx参考示例：

LIB_PATH:=${CROSS_LIB_PATH}

LIB_DF_NAME:=driver_eip_u

PATH_DF_LIB=../../../Examples/Driver/build

OBJS_TX = \

pie_tx.o \

strfunc.o

DEMO_CFLAGS += \

-W -Wall -Wextra -Wstrict-prototypes -Wmissing-prototypes \

-Wmissing-declarations -Wold-style-definition -Wpointer-arith -Wcast-align \

-Wnested-externs -Wcast-qual -Wundef -Wwrite-strings

pie_tx: $(OBJS_TX)

$(COMPILER) $(DEMO_CFLAGS) -o pie_tx $(OBJS_TX) \

-L$(LIB_PATH) -L$(PATH_DF_LIB) -l$(LIB_DF_NAME) -lpthread -lc $(USER_LFLAGS)

# 内核设备驱动接口

umdevxs_k.ko是SOC设备全模块使用的内核设备驱动，需要加载到内核系统中运行，实现SOC设备全模块的SOC接口模式下内核设备驱动注册、初始化、读写访问空间管理、中断路由分发管理、DMA内存CACHE一致性管理，创建用户程序访问SOC的内核设备 umdevxs_c，应用程序通过该设备直接访问SOC全模块设备。

## 内核设备驱动加载卸载

/*----------------------------------------------------------------------------

* UMDevXS_module_init

* Returns <0 on error.

* Returns =0 on success.

*/

static int UMDevXS_module_init(void)

该接口为加载内核设备驱动的主体功能函数，实现对所有需要完成的初始化接口的调用，用户添加的初始化接口需要在此函数中显示调用。

驱动加载系统调用：

module_init(UMDevXS_module_init);

## 内核设备驱动卸载

/*----------------------------------------------------------------------------

* UMDevXS_module_exit

*/

static void

UMDevXS_module_exit(void)

该接口为卸载内核设备驱动的主体功能函数，实现对所有需要完成的去初始化接口的调用，用户添加的去初始化接口需要在此函数中显示调用。

驱动卸载系统调用：

module_exit(UMDevXS_module_exit);

## 设备驱动注册初始化

/*----------------------------------------------------------------------------

* UMDevXS_OFDev_Init

*

* Returns <0 on error.

* Returns >=0 on success. The number is the interrupt number associated

* with this OF device.

*/

Int UMDevXS_OFDev_Init(void)

该接口为内核设备驱动初始化的主体功能函数，实现内核设备探测、初始化、内核设备树资源读取和驱动读写访问设备空间管理，完成驱动对内核设备树中搜索到的对应设备的注册，该初始化接口需要在UMDevXS_module_init函数中显示调用。

## 设备驱动注销

/*----------------------------------------------------------------------------

* UMDevXS_OFDev_Init

*

* Returns <0 on error.

* Returns >=0 on success. The number is the interrupt number associated

* with this OF device.

*/

int

UMDevXS_OFDev_Init(void)

该接口为内核设备驱动注销的主体功能函数，完成设备驱动的系统注销，该初始化接口需要在UMDevXS_module_exit函数中显示调用。

## 中断管理

### 中断号分配

本内核设备驱动只管理SWITCH CORE和EIP设备占有的14个中断号，CPU系统中断由内核单独管理，具体分配如下：

#define NUMBER_PIE_DMA_IRQ                             0

#define NUMBER_EIP150_TRNG_IRQ                         1

#define NUMBER_EIP150_AIC_OUT_IRQ                      2

#define NUMBER_EIP150_S1_ERR_IRQ                       3

#define NUMBER_EIP150_PKA_INT0_IRQ                     4

#define NUMBER_EIP150_PKA_INT1_IRQ                     5

#define NUMBER_EIP150_PKA_INT2_IRQ                     6

#define NUMBER_EIP197_CMS_OUT_IRQ                     7

#define NUMBER_EIP197_CMS_RING0_IRQ                    8

#define NUMBER_EIP197_CMS_RING1_IRQ                    9

#define NUMBER_SWITCH_GLB_MAC_IRQ                    10

#define NUMBER_SWITCH_GLB_PCS_IRQ                     11

#define NUMBER_SWITCH_GLB_INTERGRITY_IRQ               12

#define NUMBER_SWITCH_GLB_OTHERS_IRQ                  13

#define NUMBER_SWITCH_PMU_PD_IRQ                     14

### 中断初始化

/*----------------------------------------------------------------------------

*  UMDevXS_Interrupt_Init

*  nIRQ：Interrupt number （0~14）

*  Returns : none

*/

Void UMDevXS_Interrupt_Init(const int nIRQ)

该接口主要实现中断向量资源管理和信号量初始化，完成设备向量和中断服务程序的系统注册，该初始化接口需要在UMDevXS_module_init函数中显示调用。

### 中断去初始化

/*----------------------------------------------------------------------------

*  UMDevXS_Interrupt_UnInit

*  nIRQ：Interrupt number （0~14）

*  Returns : none

*/

Void UMDevXS_Interrupt_UnInit( const int nIRQ)

该接口主要实现中断向量资源管理去初始化，完成设备向量和中断服务程序的系统释放，该初始化接口需要在UMDevXS_module_exit函数中显示调用。

### 中断使能

/*----------------------------------------------------------------------------

*  UMDevXS_Interrupt_Unmask

*  nIRQ：Interrupt number （0~14）

*  Returns : none

*/

Void UMDevXS_Interrupt_Unmask ( const int nIRQ)

该接口主要实现打开设备中断功能，系统可以接收来自于设备的中断请求。

### 中断关闭

/*----------------------------------------------------------------------------

*  UMDevXS_Interrupt_Mask

*  nIRQ：Interrupt number （0~14）

*  Returns : none

*/

Void UMDevXS_Interrupt_Mask ( const int nIRQ)

该接口主要实现关闭设备中断功能，系统不接收来自于设备的中断请求。

## 符设备

### 字符设备初始化

/*----------------------------------------------------------------------------

* UMDevXS_ChrDev_Init

* Returns <0 on error.

* Returns =0 on success.

*/

Int UMDevXS_ChrDev_Init(void)

该接口主要实现字符设备的系统注册和创建，该初始化接口需要在UMDevXS_module_init函数中显示调用。

### 字符设备去初始化

/*----------------------------------------------------------------------------

* UMDevXS_ChrDev_UnInit

* Returns <0 on error.

* Returns =0 on success.

*/

Int UMDevXS_ChrDev_UnInit (void)

该接口主要实现字符设备的系统注销和删除，该初始化接口需要在UMDevXS_module_exit函数中显示调用。

## DMA内存管理

### 内存管理记录表项初始化

/*----------------------------------------------------------------------------

* BufAdmin_Init

*

* This function must be used to initialize the buffer record administration.

* It must be called before any of the other BufAdmin_* functions may

* be called. It may be called anew only after BufAdmin_UnInit has

* been called.

*

* MaxHandles (input)

*     Maximum number of handles that must be possible to administrate. The

*     implementation will allocate enough memory to fulfill this requirement.

*     Set to 0 to force the implementation to use the memory provided via

*     AdminMemory_p and AdminMemorySize.

*

* AdminMemory_p (input)

*     This parameter is used only when MaxHandles is 0.

*     Pointer to the block of memory this implementation may use for the

*     records.

*

* AdminMemorySize (input)

*     This parameter is used only when MaxHandles is 0.

*     Size of the memory block pointed to by AdminMemory_p.

*     The implementation will calculate the maximum number of handles it can

*     administrate.

*

* Return Value

*     true   Initialization successfully, rest of the API may now be used.

*     false  Initialization failed.

*/

bool

BufAdmin_Init(

const unsigned int MaxHandles,

void * AdminMemory_p,

const unsigned int AdminMemorySize)

该接口主要实现内存管理记录表项资源申请和初始化，该初始化接口需要在UMDevXS_module_init函数中显示调用。

### 内存管理记录表项去初始化

/*----------------------------------------------------------------------------

* BufAdmin_UnInit

* Return : N/A

*/

Void BufAdmin_UnInit(void)

该接口主要实现内存管理记录表项资源申请释放，该接口需要在UMDevXS_module_exit函数中显示调用。

### 用户设备交互共享内存管理初始化

/*----------------------------------------------------------------------------

* UMDevXS_SMBuf_Init

* Return Value

*     true   Initialization successfully.

*     false  Initialization failed.

*/

Int UMDevXS_SMBuf_Init(void)

该接口主要实现设备DMA内存最大可寻址位数，该初始化接口需要在UMDevXS_module_init函数中显示调用。

### 用户设备交互共享内存管理去初始化

/*----------------------------------------------------------------------------

* UMDevXS_SMBuf_UnInit

* Return Value

*     true   Initialization successfully.

*     false  Initialization failed.

*/

Int UMDevXS_SMBuf_UnInit (void)

该接口主要清除设备DMA内存最大可寻址位数，该初始化接口需要在UMDevXS_module_exit函数中显示调用。

### 共享设备交互内核支持初始化

/*----------------------------------------------------------------------------

* SHDevXS_Init

* Return Value

*     0   Initialization successfully.

*     -1  Initialization failed.

*/

Int SHDevXS_Init (void)

该接口主要实现共享设备交互的内核设备树初始化和DMA内存池初始化，该初始化接口需要在UMDevXS_module_init函数中显示调用。

### 共享设备交互内核支持去初始化

/*----------------------------------------------------------------------------

* SHDevXS_UnInit

* Return Value

*     0   Initialization successfully.

*     -1  Initialization failed.

*/

Int SHDevXS_UnInit (void)

该接口主要实现共享设备交互的内核设备树删除和DMA内存池释放，该初始化接口需要在UMDevXS_module_exit函数中显示调用。

## 内核驱动设备集管理

### 设备集初始化

/*-----------------------------------------------------------------------------

* Device_Initialize

*  CustomInitData_p (input)

*  Custom initialization data for interrupt number

*  Return Value

*     0   Initialization successfully.

*     -1  Initialization failed.

*/

Int Device_Initialize( void * CustomInitData_p)

该接口实现设备集搜索、创建、管理、设备地址、中断和内存资源申请的初始化配置。

### 设备集去初始化

/*-----------------------------------------------------------------------------

* Device_UnInitialize

*  return N/A

*/

Void Device_UnInitialize(void)

该接口实现设备集注销、删除、释放申请到的内存资源。

### 设备查找

/*-----------------------------------------------------------------------------

* Device_Find

*/

/*-----------------------------------------------------------------------------

* Device_Find

*

* These functions support finding a device given its name.

* A handle is returned that is needed in the device_rw API

* to read or write the device

*

*  DeviceName_p (input)

*  Device name

*  Return Value

*    Device handle on successfully.

*    Null on failed.

*/

Device_Handle_t  Device_Find( const char * DeviceName_p)

该接口实现通过设备名称查找到设备并返回设备句柄。

### 设备添加

/*----------------------------------------------------------------------------

* Device_Add

*  Index (input)

*  Device index

*  Props_p (input)

*  Device properties

*  Return Value

*     0   Initialization successfully.

*     -1  Initialization failed.

*/

Int Device_Add( const unsigned int Index,

const Device_Properties_t * const Props_p)

该节口实现添加设备到设备集管理中。

### 设备删除

/*----------------------------------------------------------------------------

* Device_Remove

*  Index (input)

*  Device index

*  Return Value

*     0   Initialization successfully.

*     -1  Initialization failed.

*/

int

Device_Remove( const unsigned int Index)

该节口实现删除设备集管理的制定索引。

### 设备寄存器读取

/*----------------------------------------------------------------------------

* Device_Read32

*

* Device (input)

*     Handle for the device instance as returned by Device_Find.

*

* ByteOffset (input)

*     The byte offset within the device for the resource to read.

*

* Return Value

*     The value read.

*

* When the Device or Offset parameters are invalid, the implementation will

* return an unspecified value.

*/

uint32_t

Device_Read32(

const Device_Handle_t Device,

const unsigned int ByteOffset);

该接口实现读取指定设备偏移地址为ByteOffset的32位寄存器的值。

### 设备寄存器写入

/*----------------------------------------------------------------------------

* Device_Write32

*

*

* Device (input)

*     Handle for the device instance as returned by Device_Find.

*

* ByteOffset (input)

*     The byte offset within the device for the resource to write.

*

* Value (input)

*     The 32bit value to write.

*

* Return Value

*     None

*

* The write can only be successful when the Device and ByteOffset parameters

* are valid.

*/

该接口实现读取指定设备偏移地址为ByteOffset的32位寄存器的值。

# 应用程序链接库接口

应用程序接口链接库libdriver_eip_u.a 实现用户态下应用程序对内核SOC设备的设备管理器初始化、设备搜索、设备添加、设备删除、设备读写访问、设备管理器去初始化功能集，中断分发、注册、使能和屏蔽管理功能集，DMA内存CACHE一致性管理功能集。

## 驱动设备集管理

### 设备集初始化

/*-----------------------------------------------------------------------------

* Device_Initialize

*  CustomInitData_p (input)

*  Custom initialization data for interrupt number

*  Return Value

*     0   Initialization successfully.

*     -1  Initialization failed.

*/

Int Device_Initialize( void * CustomInitData_p)

该接口实现设备集搜索、创建、管理、设备地址、中断和内存资源申请的初始化配置。

### 设备集去初始化

/*-----------------------------------------------------------------------------

* Device_UnInitialize

*  return N/A

*/

Void Device_UnInitialize(void)

该接口实现设备集注销、删除、释放申请到的内存资源。

### 设备查找

/*-----------------------------------------------------------------------------

* Device_Find

*/

/*-----------------------------------------------------------------------------

* Device_Find

*

* These functions support finding a device given its name.

* A handle is returned that is needed in the device_rw API

* to read or write the device

*

*  DeviceName_p (input)

*  Device name

*  Return Value

*    Device handle on successfully.

*    Null on failed.

*/

Device_Handle_t  Device_Find( const char * DeviceName_p)

该接口实现通过设备名称查找到设备并返回设备句柄。

### 设备添加

/*----------------------------------------------------------------------------

* Device_Add

*  Index (input)

*  Device index

*  Props_p (input)

*  Device properties

*  Return Value

*     0   Initialization successfully.

*     -1  Initialization failed.

*/

Int Device_Add( const unsigned int Index,

const Device_Properties_t * const Props_p)

该节口实现添加设备到设备集管理中。

### 设备删除

/*----------------------------------------------------------------------------

* Device_Remove

*  Index (input)

*  Device index

*  Return Value

*     0   Initialization successfully.

*     -1  Initialization failed.

*/

int

Device_Remove( const unsigned int Index)

该节口实现删除设备集管理的制定索引。

### 设备寄存器读取

/*----------------------------------------------------------------------------

* Device_Read32

*

* Device (input)

*     Handle for the device instance as returned by Device_Find.

*

* ByteOffset (input)

*     The byte offset within the device for the resource to read.

*

* Return Value

*     The value read.

*

* When the Device or Offset parameters are invalid, the implementation will

* return an unspecified value.

*/

uint32_t

Device_Read32(

const Device_Handle_t Device,

const unsigned int ByteOffset);

该接口实现读取指定设备偏移地址为ByteOffset的32位寄存器的值。

### 设备寄存器写入

/*----------------------------------------------------------------------------

* Device_Write32

*

*

* Device (input)

*     Handle for the device instance as returned by Device_Find.

*

* ByteOffset (input)

*     The byte offset within the device for the resource to write.

*

* Value (input)

*     The 32bit value to write.

*

* Return Value

*     None

*

* The write can only be successful when the Device and ByteOffset parameters

* are valid.

*/

该接口实现读取指定设备偏移地址为ByteOffset的32位寄存器的值。

## 中断管理

### 中断号分配

本内核设备驱动只管理SWITCH CORE和EIP设备占有的14个中断号，CPU系统中断由内核单独管理，具体分配如下：

#define ADAPTER_PIE_DMA_IRQ                             0

#define ADAPTER_EIP150_TRNG_IRQ                         1

#define ADAPTER_EIP150_AIC_OUT_IRQ                      2

#define ADAPTER_EIP150_S1_ERR_IRQ                       3

#define ADAPTER_EIP150_PKA_INT0_IRQ                     4

#define ADAPTER_EIP150_PKA_INT1_IRQ                     5

#define ADAPTER_EIP150_PKA_INT2_IRQ                     6

#define ADAPTER_EIP197_CMS_OUT_IRQ                      7

#define ADAPTER_EIP197_CMS_RING0_IRQ                    8

#define ADAPTER_EIP197_CMS_RING1_IRQ                    9

#define ADAPTER_SWITCH_GLB_MAC_IRQ                      10

#define ADAPTER_SWITCH_GLB_PCS_IRQ                      11

#define ADAPTER_SWITCH_GLB_INTERGRITY_IRQ               12

#define ADAPTER_SWITCH_GLB_OTHERS_IRQ                   13

#define ADAPTER_SWITCH_PMU_PD_IRQ                       14

### 中断初始化

/*----------------------------------------------------------------------------

* Adapter_Interrupts_Init

*  nIRQ：Interrupt number （0~14）

*

* Return Value

*     true   Initialization successfully, rest of the API may now be used.

*     false  Initialization failed.

*/

bool

Adapter_Interrupts_Init(

const int nIRQ)

该接口主要实现中断向量资源管理和信号量创建初始化，中断分发接收线程创建。

### 中断去初始化

/*----------------------------------------------------------------------------

*  Adapter_Interrupts_UnInit

*  nIRQ：Interrupt number （0~14）

*  Returns : none

*/

void

Adapter_Interrupts_UnInit(const int nIRQ)

该接口主要实现中断服务程序注销，中断分发接收线程终结和资源回收。

### 中断使能

/*----------------------------------------------------------------------------

* Adapter_Interrupt_Enable

*

*  nIRQ：Interrupt number （0~14）

*  Flags：reserved

*  Returns : N/A

*/

void

Adapter_Interrupt_Enable(

const int nIRQ,

const unsigned int Flags)

该接口主要实现打开设备中断功能，应用程序可以接收来自于设备的中断请求。

### 中断关闭

/*----------------------------------------------------------------------------

* Adapter_Interrupt_ Disable

*

*  nIRQ：Interrupt number （0~14）

*  Flags：reserved

*  Returns : N/A

*/

void

Adapter_Interrupt_Disable(

const int nIRQ,

const unsigned int Flags)

该接口主要实现关闭设备中断功能，应用程序不接收来自于设备的中断请求。

### 中断注册

/*----------------------------------------------------------------------------

* Adapter_Interrupt_SetHandler

*

*  nIRQ：Interrupt number （0~14）

*  HandlerFunction：Interrupt service routine

*  Returns : N/A

*/

void

Adapter_Interrupt_SetHandler(

const int nIRQ,

Adapter_InterruptHandler_t HandlerFunction)

该接口主要实现注册中断服务程序到中断号。

## DMA内存管理

### DMA内存管理记录表项初始化

/*----------------------------------------------------------------------------

* DMAResource_Init

*/

bool

DMAResource_Init(void)

该接口主要实现内存管理记录表项资源申请和初始化。

### DMA内存管理记录表项去初始化

/*----------------------------------------------------------------------------

* DMAResource_UnInit

*

*/

void

DMAResource_UnInit(void)

该接口主要实现内存管理记录表项资源申请释放。

### DMA设备内存资源申请

/*----------------------------------------------------------------------------

* DMAResource_Alloc

*

* Allocate a buffer of requested size that can be used for device DMA.

* DMAResource_Create is used to create a record and handle to administer

* the buffer.

*

* RequestedProperties

*     Requested properties of the buffer that will be allocated, including

*     the size, start address alignment, etc. See DMAResource_Properties_t.

*

* AddrPair_p (output)

*     Pointer to the memory location where the address and domain of the

*     buffer will be written by this function when allocation is successful.

*     This buffer address can then be used in the caller's memory domain.

*

* Handle_p (output)

*     Pointer to the memory location when the handle will be returned.

*

* Return Values

*     0    Success

*     <0   Error code (implementation specific)

*/

int

DMAResource_Alloc(

const DMAResource_Properties_t RequestedProperties,

DMAResource_AddrPair_t * const AddrPair_p,

DMAResource_Handle_t * const Handle_p);

该接口主要实现为DMA设备申请内存资源。

### DMA设备内存资源释放

/*----------------------------------------------------------------------------

* DMAResource_Release

*

* This function must be used as a counter-operation for DMAResource_Alloc,

* DMAResource_CheckAndRegister and DMAResource_Attach. Allocated buffers are

* freed, attached buffers are detached and registered buffers are simply

* forgotten.

* The caller must ensure the buffers are not in use anymore when this

* function is called.

* The related record and handle are also destroyed using DMAResource_Destroy,

* so the handle and record cannot be used anymore when this function returns.

*

* Handle (input)

*     The handle to the DMA Resource record that was returned by

*     DMAResource_Alloc, DMAResource_CheckAndRegister or DMAResource_Attach.

*

* Return Values

*     0    Success

*     <0   Error code (implementation specific)

*/

int

DMAResource_Release(

const DMAResource_Handle_t Handle);

该接口主要实现为DMA设备释放申请到的内存资源。

### DMA内存主机设备地址域转换

/*----------------------------------------------------------------------------

* DMAResource_Translate

*

* Attempts to provide an address for a DMA Resource that can be used in the

* requested address domain. Typically used to get the address that can be

* used by a device to perform DMA.

*

* Handle (input)

*     The handle to the DMA Resource record that was returned by

*     DMAResource_Alloc, DMAResource_CheckAndRegister or DMAResource_Attach.

*

* DestDomain (input)

*     The requested domain to translate the address to.

*     Please check the implementation notes for supported domains.

*

* PairOut_p (output)

*     Pointer to the memory location when the converted address plus domain

*     will be written.

*

* Return Values

*     0    Success

*     <0   Error code (implementation dependent)

*/

int

DMAResource_Translate(

const DMAResource_Handle_t Handle,

const DMAResource_AddrDomain_t DestDomain,

DMAResource_AddrPair_t * const PairOut_p);

该接口主要实现DMA内存地址主机地址域和设备地址域之间相互转换。

### DMA内存主机设备地址域内存地址对记录添加

/*----------------------------------------------------------------------------

* DMAResource_AddPair

*

* This function can be used to register another address pair known to the

* caller for a DMA Resource.

* The information will be stored in the DMA Resource Record and can be used

* by DMAResource_Translate.

* Typically used when an external DMA-safe buffer allocator returns two

* addresses (for example virtual and physical).

* Note: How many address pairs are supported is implementation specific.

*

* Handle (input)

*     The handle to the DMA Resource record that was returned by

*     DMAResource_CheckAndRegister or DMAResource_Attach.

*

* Pair (input)

*     Address pair (address + domain) to be associated with the DMA Resource.

*

* Return Values

*     0    Success

*     <0   Error code (implementation dependent)

*/

int

DMAResource_AddPair(

const DMAResource_Handle_t Handle,

const DMAResource_AddrPair_t Pair);

该接口主要实现DMA内存主机地址域和设备地址域组成的内存地址对添加到DMA资源管理记录表中，。
