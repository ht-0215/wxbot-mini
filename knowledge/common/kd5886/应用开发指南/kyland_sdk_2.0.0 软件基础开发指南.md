# kyland_sdk_2.0.0 软件基础开发指南

kyland_sdk_2.0.0

软件基础开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

# SDK 软件框架

旧版本的SDK 名称为 kyland_api-x.x.x,新版本SDK在功能上进一步完善,由单一的芯片驱动,到一套完整的软件开发工具包,为客户提供更简单、方便、快捷的开发调试, 同时用户的代码也可以在SDK框架内进行。框架如下图1所示:

图 1 SDK 软件框架

## SDK名称

kyland_sdk_A.B.C：

A：发布大版本号，一般结构性的大变化才修改。

B：发布中版本号，一般是添加大新特性修改。

C：发布小版本号，一般小的修改，如BUG，小需求等。SVN的版本号作为该版本号。

## APPL层

使用KD层提供的API实现上层应用，包括芯片初始化、CLI、一些上层协议（stp,lacp 等等）,具有如下特性：

demo功能：使用SDK实现的一些应用,方便验证/调试芯片，同时提供开发参考指导。

产品功能：可以直接当产品使用，不需要进行开发或少量开发。

初始化流程介绍：

demo_main.c

## KD层

硬件抽象层，向上屏蔽硬件信息，提供简单、易用、通用的API,提供业务级API。向下兼容各种硬件.所有物芯功能模块都能抽象成KD_xxx。

命名格式: kd_模块名_动作. 其中模块指的是vlan,port,acl等, 动作有get,set,create,destroy等.

api的返回值如果未加说明,统一返回kd_error_t 定义的错误号。

api管理的所有id 资源, 如果在create时设置为-1,由sdk自动分配id,如果是其它非0值,使用用户指定的id.

头文件：kd_api.h 为统一头文件，里面包含各模块头文件，如下：

入口初始化函数：int kd_init(void)

卸载函数：int kd_detach(void)，支持动态卸载。

函数实现有统一的模板：

参数检查模板：

Unit 检查：UNIT_CHECK(unit);

NULL 检查：KD_IF_NULL_RETURN_RET_xxx(op,ret)

函数返回检查：KD_IF_ERROR_RETURN_RET_xxx(op,ret)

模板统一定义在kd_api.h 文件中.

例如：

具体内容参考API说明文档。

## 芯片模块层

### 交换芯片驱动模块

Sdk名称为kyland_api-A.B.C。

提供交换芯片驱动级的API，能够实现交换芯片几乎所有的功能，KD层对该层API进一步通用封装。框架如下：

AIL层接口提供WX系列芯片统一的配置API，基于AIL接口，可以开发完成的业务功能。

### PHY 驱动模块

实现了PHY管理模块，并提供phy相关的api。

PHY的管理模块初始化流程：

Phy的一些通用配置在kd层port 模块中被封装，不需要单独在配置PHY，如配置kd_port_enable_set(int unit, int port, int enable)，当有外部PHY时，会自动配置PHY power down，如果没有外部PHY，配置交换芯片PORT power down。

新PHY的驱动可以方便的添加进PHY模块中，支持所有bcm phy芯片。

PHY的详细介绍参考PHY的相关文档。

## Common层

为其它层提供基础服务，是其它模块的基石。如类型定义、标准库实现、自定义库、SAL层、通用模块等，使SDK不依赖标准库（如LIBc等），能够适配所有平台。

类型：uint8、uint16、bool 等等。

标准库实现：如kd_sal_printf, kd_sal_atoi 等等。

自定义库：mac_str_to_bin, ip_str_check 等等。

SAL层：系统函数适配， kd_sal_task_create，kd_sal_time 等等。

通用模块：如syslog模块等。

# 目录结构介绍

目录结构图如下：

图  SDK软件目录结构

## Appl目录

基于SDK 应用实例。

## Common目录

公共、基础模块。

## Doc目录

SDK文档目录。

### Hal目录

硬件抽象层API实现,新版本sdk改成kd 目录。

### Kyand_api_xxx目录

交换芯片模块管理。

### Make 目录

Makefile脚本。

### Phy目录

Phy模块管理。

### System目录

存放系统相关的工具，如编译配置设置。

### Output 目录

编译目标生成文件。

### Realse 目录

版本发布目录，为output中的生成文件。

其它相关文档 doc/目录说明.docx

# SDK的编译

## 编译介绍

编译管理框架：

图  SDK编译框架

编译配置脚本指定系统参数，如os类型，芯片型号、cpu，工具链 等一些配置信息，脚本目录在system目录下。如编译KD5886 X86 linux平台：

source systems/linux/setvarsKD5886_X86_64.sh

然后再对主makefile 进行make 或make all操作。

主makefile 的主要编译命令：

Make help:

Make ,make clean:

Make all ,make cleanall:

编译配置脚本说明：

表  SDK 编译配置

| system | 脚本 | 说明 |
| --- | --- | --- |
| linux | setvarsKD5886_Csky.sh | KD5886 内置CPU 配置。 |
| linux | setvarsKD5886_X86_64.sh | KD5886 通过PCIE连接X86 CPU 配置。 |
| linux | setvarsKD6630_ARC.sh | KD6630内置CPU 配置。 |
| linux | setvarsKD6630_X86-64.sh | KD6630 通过PCIE连接X86 CPU 配置。 |
| Vxworks | 暂无 |  |
| Kernel | 暂无 |  |
|  |  |  |

表  用户常用的makefile变量表

| OUTPUT | 编译目标路径，默认是SDK中的 output目录。 |
| --- | --- |
| CSFLAGS_kyland | 目前在交换芯片目录下的makeflie中，如果外部要包含驱动头文件，需要添加到用户makeflie中。 |
| SDK | SDK路径环境变量，所有的目录信息都是参考SDK变量。 |

其它文档 doc/ sdk 编译介绍.docx

## Demo 启动介绍

当前支持：kd5886，kd6630.

Linux 系统：

加载ko：

创建设备节点：

通过cat /proc/devices 察看umdevxs 设备号。

mknod /dev/umdevxs_c c 247 0

执行demo –y （boardtype）[-mN]

表  Demo 板卡类型表

| boardtype | 名称 | 说明 |
| --- | --- | --- |
| 0 | 48xQGE_8xSFI |  |
| 1 | 36x1000baseX_4xSFI |  |
| 2 | 20x1000baseX_8xQGE |  |
| 3 | kd6630 |  |
| 4 | kd6630_12xRMII |  |
| 5 | kd5886_gpt |  |
| 6 | kd6630_test |  |

Demo 参数说明

-y/n : 初始化模式， -y：Sdk 全部初始化， -n：只初始化SDK软件。

-mN：appl 启动模式，可选，默认N=1，正常启动。 N=0：appl 部分功能不加载。

如：

# SDK 使用介绍

## Common 目录头文件路径

添加头文件路径： -I$(SDK)/common/include.

## 使用KD 层api

包含kd层的头文件，#include "kd_api.h"

添加头文件路径： -I$(SDK)/kd/include.

KD 层的API如果未加说明，返回值统一为kd_error_t 错误号。

KD 层的一些id 资源管理，统一使用kd_id_t 类型表示。如果id 为KD_ID_INVALID/-1 时，由SDK分配，如果为合法值时，使用用户指定的id。

### 使用交换芯片驱动层api

添加编译选项：CSFLAGS_kyland ，具体参考table2。

包含主要头文件，#include "kyland_api.h"，#include "kyland_state.h"

### 链接库

当前已KD5886，KD6630说明：

生成的库分动态库和静态库，根据需求使用。

表  SDK库介绍

| 库名 | 功能说明 | 是否可选 |  |
| --- | --- | --- | --- |
| libdf | 底层接口库，与kernel打交道。 | 必选 |  |
| libdriver_eip_u | 底层处理API | 必选 |  |
| libdriver_switch_u | 交换芯片驱动库 | 必选 |  |
| libsdk_common | 通用模块库 | 必选 |  |
| libsdk_phy | Phy 模块库 | 可选 |  |
| libsdk_kd | kd模块库 | 可选 |  |
| libsdk_appl | 应用层模块库 | 可选 |  |

必选的库必须要使用，可选的根据需要进行选择。如使用自己的PHY模块，可以不连接libsdk_phy.

# 基于SDK框架开发

如果没有自己的框架，可以把代码放在SDK中，如

新建一个目录usr。

copy其它目录里面的makeflie，修改相关变量。

在主makefile 中增加目标 usr。

完成添加。

# SDK端口号介绍

kd 层： unit ： 表示芯片号，port：芯片端口号。

交换芯片驱动层：交换芯片的用inst 表示实例， port_no 表示逻辑端口号，chip_port 表示芯片物理端口号，目前规定port_no 与chip_port 一一对应,即port_no=chip_port，不允许修改。在堆叠环境中使用upsid 表示芯片id, upspn 表示端口号。

Unit 与 inst 通过映射表来进行转换：int g_kd_inst[KD_UNIT_MAX]。Inst 转unit :  inst(unit) .

Port 与 port_no 一一映射，即port=port_no.

# SDK CLI 介绍

## 标准CLI

CLI 采用标准的CLI 策略，支持[ ]: 表示可选，():  单选，{}: 多选等。Demo启动后直接进入CLI模式。

SDK 的CLI 分为产品级命令行和调试级别命令行。

产品级CLI：具有产品特性，使用KD层API实现。支持配置保存恢复。

调试级CLI：芯片特性，直接使用芯片级API来实现，用来验证、调试、定位等芯片问题。

CLI命令行采用模块分类方式管理，方便了解当前支持哪些模块的命令，如

### 标准CLI的制作

命令行采用树结构管理，节点为node，命令都注册在node上。

制作步骤：

创建node ，注册node。如：

kd_cmd_node_t interface_node =

{

KD_CLI_INTERFACE_MODE,

"\rKD-CLI(interface %s)# ",

};

kd_install_node(&interface_node, NULL);

制作CLI，注册CLI。如：

KD_CLI(kd_cli_common_enter_interface_mode,

kd_cli_common_enter_interface_mode_cmd,

"interface <0-64>",

"interface",

"interface num"

)

kd_install_element(KD_CLI_COMM_MODE, &kd_cli_common_enter_interface_mode_cmd);

具体参考相关代码。

### CHIP 级命令行

还一个CHIP 级的CLI，更贴近芯片调试。会逐步被标准CLI替换。

在标准CLI下输入SDK进入.

相关模块的命令，参看相关命令行手册。

# SDK指导手册

每个模块都有相应的详细地开发指导、问题定位指导、命令行手册、缺陷手册等。

# SDK开发维护

遵循SDK开发规范。

不建议客户自己修改SDK 代码，不利于后续SDK升级。遇到问题向厂家反馈，由厂家统一修改后再进行升级。
