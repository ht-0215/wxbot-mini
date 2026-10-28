# kyland_sdk_2.0.0 PHY应用开发指南

kyland_sdk_2.0.0

PHY应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 SDK支持的PHY芯片	7

2 PHY软件设计介绍	8

2.1 1.外部PHY芯片检测接口	8

2.1.1 功能简介	8

2.1.2 接口及参数描述	8

2.1.3 相关数据结构	8

2.2 PHY芯片初始化接口	8

2.2.1 功能简介	8

2.2.2 接口及参数描述	9

2.2.3 相关数据结构	9

2.3 PHY驱动名字获取接口	9

2.3.1 功能简介	9

2.3.2 接口及参数描述	9

2.3.3 相关数据结构	10

2.4 PHY的LINK状态获取接口	10

2.4.1 功能简介	10

2.4.2 接口及参数描述	10

2.4.3 相关数据结构	10

2.5 PHY芯片的使能接口	11

2.5.1 功能简介	11

2.5.2 接口及参数描述	11

2.5.3 相关数据结构	12

2.6 PHY芯片的双工模式接口	12

2.6.1 功能简介	12

2.6.2 接口及参数描述	12

2.6.3 相关数据结构	13

2.7 PHY芯片的速率模式接口	13

2.7.1 功能简介	13

2.7.2 接口及参数描述	13

2.7.3 相关数据结构	14

2.8 PHY芯片的master模式接口	14

2.8.1 功能简介	14

2.8.2 接口及参数描述	14

2.8.3 相关数据结构	15

2.9 PHY芯片的自协商模式接口	15

2.9.1 功能简介	15

2.9.2 接口及参数描述	16

2.9.3 相关数据结构	16

2.10 PHY芯片的MDIX模式接口	17

2.10.1 功能简介	17

2.10.2 接口及参数描述	17

2.10.3 相关数据结构	18

2.11 PHY芯片名称获取接口	19

2.11.1 功能简介	19

2.11.2 接口及参数描述	19

2.11.3 相关数据结构	20

2.12 PHY地址获取接口	20

2.12.1 功能简介	20

2.12.2 接口及参数描述	20

2.12.3 相关数据结构	21

2.13 PHY Interface接口	21

2.13.1 功能简介	21

2.13.2 接口及参数描述	21

2.13.3 相关数据结构	22

2.14 PHY control接口	25

2.14.1 功能简介	25

2.14.2 接口及参数描述	25

2.14.3 相关数据结构	26

2.15 PHY 读寄存器接口	26

2.15.1 功能简介	26

2.15.2 接口及参数描述	27

2.15.3 相关数据结构	27

2.16 PHY 写寄存器接口	27

2.16.1 功能简介	27

2.16.2 接口及参数描述	27

2.16.3 相关数据结构	28

2.17 PHY dump寄存器接口	28

2.17.1 功能简介	28

2.17.2 接口及参数描述	28

2.17.3 相关数据结构	30

# SDK支持的PHY芯片

当前SDK支持的PHY芯片类型:

vtss 8512

kd3004

# PHY软件设计介绍

## 1.外部PHY芯片检测接口

### 功能简介

外部PHY芯片检测,检测外部PHY芯片是否存在.如果外部PHY芯片存在的话返回1,不存在的话返回0.

### 接口及参数描述

bool ext_phy_check(int unit, soc_port_t  port);

参数:

int unit  //芯片号

soc_port_t portnums //芯片端口号

返回值:

是否存在外部PHY.

### 相关数据结构

typedef int     soc_port_t;

## PHY芯片初始化接口

### 功能简介

初始化PHY芯片,输入初始化的最大端口号,进行逐个端口初始PHY芯片.如果该端口没有连接PHY芯片,那么就不会对该端口进行PHY芯片的初始化操作.该端口有没有连接PHY芯片是根据配置文件确定的.

### 接口及参数描述

int soc_phy_init(int unit,soc_port_t portnums)

参数:

int unit  //芯片号

soc_port_t portnums //需要初始化PHY的最大端口号

返回值:

返回操作成功或失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY驱动名字获取接口

### 功能简介

获取当前端口PHY驱动的名称.输入需要查询的端口号,函数返回当前端口的PHY驱动名称指针.

### 接口及参数描述

char * soc_phyctrl_drv_name(int unit,soc_port_t port);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

返回值:

返回当前端口PHY驱动名称的指针.

### 相关数据结构

typedef int     soc_port_t;

## PHY的LINK状态获取接口

### 功能简介

获取当前端口PHY的LINK状态.

### 接口及参数描述

int  soc_phyctrl_link_get(int unit, soc_port_t port, int *link);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int *link	//获取到的link状态.

返回值:

操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY芯片的使能接口

### 功能简介

使用set函数使能或者去使能当前端口的PHY芯片功能.

使用get函数获取当前端口的PHY芯片使能状态.

### 接口及参数描述

int  soc_phyctrl_enable_set(int unit, soc_port_t port, int enable);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int enable  //控制PHY使能或者去使能

返回值:

操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

int  soc_phyctrl_enable_get(int unit, soc_port_t port, int *enable);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int *enable  //读取到的当前端口PHY芯片的使能状态

返回值:

操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY芯片的双工模式接口

### 功能简介

使用set函数配置当前端口PHY芯片的双工模式.

使用get函数获取当前端口的双工模式.

### 接口及参数描述

int  soc_phyctrl_duplex_set(int unit, soc_port_t port, int duplex);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int duplex  //控制PHY芯片的双工模式.

返回值:

操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

int  soc_phyctrl_enable_get(int unit, soc_port_t port, int *enable);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int *enable  //读取到的当前端口PHY芯片的使能状态

返回值:

操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY芯片的速率模式接口

### 功能简介

使用set函数配置当前端口PHY芯片的速率模式.

使用get函数获取当前端口的速率模式.

### 接口及参数描述

int  soc_phyctrl_speed_set(int unit, soc_port_t port, int speed);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int speed //控制PHY芯片的速率

返回值:

操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

int  soc_phyctrl_ speed _get(int unit, soc_port_t port, int * speed);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int * speed   //读取到的当前端口PHY芯片的速率

返回值:

操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY芯片的master模式接口

### 功能简介

使用set函数配置当前端口PHY芯片的master模式.

使用get函数获取当前端口的master模式.

### 接口及参数描述

int  soc_phyctrl_master_set(int unit, soc_port_t port, int master);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int master //控制PHY芯片的master模式

返回值:

操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

int  soc_phyctrl_ master _get(int unit, soc_port_t port, int * master);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int * master //读取到的当前端口PHY芯片的master模式

返回值:

操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY芯片的自协商模式接口

### 功能简介

使用set函数配置当前端口PHY芯片的自协商模式.

使用get函数获取当前端口的自协商模式.

### 接口及参数描述

int  soc_phyctrl_auto_negotiate_set(int unit, soc_port_t port, int an);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int an //控制PHY芯片的自协商模式

返回值:

操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

int  soc_phyctrl_ negotiate _get(int unit, soc_port_t port, int * an);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int * an //读取到的当前端口PHY芯片的自协商模式

返回值:

操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY芯片的MDIX模式接口

### 功能简介

使用set函数配置当前端口PHY芯片的MDIX模式.

使用get函数获取当前端口的MDIX模式.

### 接口及参数描述

int  soc_phyctrl_mdix_set(int unit, soc_port_t port, soc_port_mdix_t mdix);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

soc_port_mdix_t mdix  //MDIX模式

返回值:

操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

int soc_phyctrl_mdix_get(int unit, soc_port_t port, soc_port_mdix_t *mdix);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

soc_port_mdix_t *mdix  //读取到的MDIX模式

返回值:

操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

int  soc_phyctrl_mdix_status_get(int  unit, soc_port_t  port, soc_port_mdix_status_t *status);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

soc_port_mdix_status_t *status  //获取到的当前PHY芯片MDIX状态

返回值:

操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

------------------------------------------------------------------------------------------------------------------------------------------ typedef enum _shr_port_mdix_e {

_SHR_PORT_MDIX_AUTO,

_SHR_PORT_MDIX_FORCE_AUTO,

_SHR_PORT_MDIX_NORMAL,

_SHR_PORT_MDIX_XOVER,

_SHR_PORT_MDIX_COUNT    /* last, please */

} _shr_port_mdix_t;

typedef _shr_port_mdix_t soc_port_mdix_t;

------------------------------------------------------------------------------------------------------------------------------------------ typedef enum _shr_port_mdix_status_e {

_SHR_PORT_MDIX_STATUS_NORMAL,

_SHR_PORT_MDIX_STATUS_XOVER,

_SHR_PORT_MDIX_STATUS_COUNT       /* last, please */

} _shr_port_mdix_status_t;

typedef _shr_port_mdix_status_t soc_port_mdix_status_t;

## PHY芯片名称获取接口

### 功能简介

获取当前端口上的PHY芯片的名称.

### 接口及参数描述

char * soc_phyctrl_name_get(int  unit, soc_port_t  port);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

返回值:

当前端口上PHY芯片名称的指针.

### 相关数据结构

typedef int     soc_port_t;

## PHY地址获取接口

### 功能简介

获取当前端口对应的PHY地址.当前端口对应的PHY地址是配置文件进行配置的,PHY驱动中只有获取接口,没有配置接口.如需配置,请使用配置文件进行配置.

### 接口及参数描述

int  soc_phyctrl_addr_get(int  unit, soc_port_t  port,int  *bus_id,int  *phy_addr);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

int  *bus_id  //获取到的bus id

int  *phy_addr  //获取到的phy addr

返回值:

当前操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY Interface接口

### 功能简介

使用set接口,配置当前端口对应的PHY芯片的Interface类型.

使用get接口,获取当前端口对应的PHY芯片的Interface类型.

使用show接口,显示当前端口对应的PHY芯片的Interface类型.

### 接口及参数描述

int  soc_phyctrl_interface_set(int unit, soc_port_t port, soc_port_if_t pif);

参数:

int unit  //芯片号

soc_port_t  port  //芯片端口号

soc_port_if_t pif  //配置当前端口的PHY Interface

返回值:

当前操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

int  soc_phyctrl_interface_get(int unit, soc_port_t port, soc_port_if_t *pif);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

soc_port_if_t *pif  //获取到的PHY Interface

返回值:

当前操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

char *  soc_phyctrl_interface_show(soc_port_if_t pif);

参数:

soc_port_if_t  pif  //PHY Interface

返回值:

Interface 名称的指针.

### 相关数据结构

typedef int     soc_port_t;

------------------------------------------------------------------------------------------------------------------------------------------

typedef enum _shr_port_if_e {

_SHR_PORT_IF_NOCXN, /* No physical connection */

_SHR_PORT_IF_NULL,  /* Pass-through connection without PHY */

_SHR_PORT_IF_MII,

_SHR_PORT_IF_GMII,

_SHR_PORT_IF_SGMII,

_SHR_PORT_IF_TBI,

_SHR_PORT_IF_XGMII,

_SHR_PORT_IF_RGMII,

_SHR_PORT_IF_RvMII,

_SHR_PORT_IF_SFI,

_SHR_PORT_IF_XFI,

_SHR_PORT_IF_KR,

_SHR_PORT_IF_KR4,

_SHR_PORT_IF_CR,

_SHR_PORT_IF_CR4,

_SHR_PORT_IF_XLAUI,

_SHR_PORT_IF_SR,

_SHR_PORT_IF_RXAUI,

_SHR_PORT_IF_XAUI,

_SHR_PORT_IF_SPAUI,

_SHR_PORT_IF_QSGMII,

_SHR_PORT_IF_ILKN,

_SHR_PORT_IF_RCY,

_SHR_PORT_IF_FAT_PIPE,

_SHR_PORT_IF_CGMII,

_SHR_PORT_IF_CAUI,

_SHR_PORT_IF_LR,

_SHR_PORT_IF_LR4,

_SHR_PORT_IF_SR4,

_SHR_PORT_IF_KX,

_SHR_PORT_IF_ZR,

_SHR_PORT_IF_SR10,

_SHR_PORT_IF_OTL,

_SHR_PORT_IF_CPU,

_SHR_PORT_IF_OLP,

_SHR_PORT_IF_OAMP,

_SHR_PORT_IF_ERP,

_SHR_PORT_IF_COUNT /* last, please */

} _shr_port_if_t;

typedef _shr_port_if_t soc_port_if_t;

## PHY control接口

### 功能简介

使用set接口,配置当前端口对应的PHY芯片的控制项.

使用get接口,获取当前端口对应的PHY芯片的控制项.

### 接口及参数描述

int  soc_phyctrl_control_set(int unit, soc_port_t port, soc_phy_control_t phy_ctrl, uint32 value);

参数:

int unit  //芯片号

soc_port_t  port  //芯片端口号

soc_phy_control_t phy_ctrl //控制类型

uint32 value  //配置的参数

返回值:

当前操作成功或者失败.

------------------------------------------------------------------------------------------------------------------------------------------

int  soc_phyctrl_control_get(int unit, soc_port_t port, soc_phy_control_t phy_ctrl, uint32 *value);

参数:

int unit  //芯片号

soc_port_t port  //芯片端口号

soc_phy_control_t phy_ctrl  //控制类型

uint32 *value  //获取到的值

返回值:

当前操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

------------------------------------------------------------------------------------------------------------------------------------------ /* PHY specific control settings */

typedef enum soc_phy_control_e {

SOC_PHY_CONTROL_WAN           ,

SOC_PHY_CONTROL_INTERFACE_SYS,

SOC_PHY_CONTROL_COUNT           /* always last */

} soc_phy_control_t;

## PHY 读寄存器接口

### 功能简介

读取PHY芯片寄存器的值.

### 接口及参数描述

int  soc_phyctrl_reg_read(int unit, soc_port_t port, uint32 flag, uint32 addr, uint32 *data);

参数:

int unit  //芯片号

soc_port_t  port  //芯片端口号

uint32 flag  //PHY寄存器页选择

uint32 addr  //PHY寄存器地址

uint32 *data  //读取到的PHY寄存器值

返回值:

当前操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY 写寄存器接口

### 功能简介

配置PHY芯片寄存器的值.

### 接口及参数描述

int  soc_phyctrl_reg_write(int unit, soc_port_t port, uint32 flag, uint32 addr, uint32 data);

参数:

int unit  //芯片号

soc_port_t  port  //芯片端口号

uint32 flag  //PHY寄存器页选择

uint32 addr  //PHY寄存器地址

uint32 data  //写入PHY寄存器的值

返回值:

当前操作成功或者失败.

### 相关数据结构

typedef int     soc_port_t;

## PHY dump寄存器接口

### 功能简介

Dump PHY芯片寄存器的值.

三种dump方式:

指定端口,指定起始地址和长度dump

指定起始地址和长度dump全端口

Dump全端口所有寄存器

### 接口及参数描述

void  soc_phyctrl_reg_dump(int unit,soc_port_t port,int addr,int len);

参数:

int unit  //芯片号

soc_port_t  port  //芯片端口号

int addr  //起始PHY地址

int len  //从起始地址往后dump的数量

返回值:

空

------------------------------------------------------------------------------------------------------------------------------------------ void  soc_phyctrl_reg_dump_allport(int unit,int addr,int len);

参数:

int unit  //芯片号

int addr  //起始PHY地址

int len  //从起始地址往后dump的数量

返回值:

空

------------------------------------------------------------------------------------------------------------------------------------------ void  soc_phyctrl_reg_dump_all(int unit);

参数:

int unit  //芯片号

返回值:

空

### 相关数据结构

typedef int     soc_port_t;
