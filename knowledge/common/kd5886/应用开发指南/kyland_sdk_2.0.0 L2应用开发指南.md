# kyland_sdk_2.0.0 L2应用开发指南

kyland_sdk_2.0.0

L2应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 术语&缩略语	5

1.1 VLAN	5

1.2 MAC	5

1.3 Flood	5

1.4 LAG（Link Aggregation Group）	5

1.5 MSTP（Multiple Spanning Tree Protocol）	5

1.6 RADIUS（Remote Authentication Dial In User Service）	5

1.7 802.1x认证	5

1.8 MAC认证	5

1.9 Portal认证	6

2 L2应用开发指南	7

2.1 概述	7

2.1.1 二层数据流转发	7

2.1.2 VLAN	7

2.1.3 MAC	7

2.1.4 聚合组	8

2.1.5 MSTP	8

2.2 API接口	9

2.2.1 创建/删除指定VLAN	9

2.2.2 获取/设置指定VLAN成员端口	10

2.2.3 添加/删除指定MAC地址	11

2.2.4 组播配置接口	14

2.2.5 聚合组配置接口	17

2.2.6 MSTP配置接口	19

2.2.7 端口安全配置接口	21

2.3 API应用	23

2.3.1 二层已知单播报文转发	23

2.3.2 二层已知组播报文转发	30

2.3.3 二层广播、未知单播、未知组播报文泛洪	43

2.3.4 通过设置聚合组实现负载分担	49

2.3.5 通过设置MSTP实现数据流丢弃	59

2.3.6 通过设置端口学习状态实现MAC认证	74

2.4 芯片实现	81

2.4.1 总体流程	81

2.4.2 二层转发流程	82

# 术语&缩略语

## VLAN

虚拟局域网（802.1q）

## MAC

媒体访问控制，特指网络设备全球唯一的48-bit标识

## Flood

泛洪，特指广播、未知单播、未知组播报文在VLAN内广播到其它成员端口的行为

## LAG（Link Aggregation Group）

链路聚合组

## MSTP（Multiple Spanning Tree Protocol）

多生成树协议（802.1s）

## RADIUS（Remote Authentication Dial In User Service）

远程用户拨号认证系统

## 802.1x认证

IEEE制定的关于用户接入网络的认证标准，全称是“基于端口的网络接入控制”，可由客户端主动发起，也可由设备端收到源MAC未知报文触发。

## MAC认证

MAC认证是一种基于端口和MAC地址对用户的网络访问权限进行控制的认证方法，最大的特点就是不需要客户端软件，也不需要输入用户名密码，设备收到源未知报文后自动触发认证。

## Portal认证

Portal认证通常也成为Web认证，是通过Web页面进行认证的，用户主动访问Portal认证网站进行认证称为“主动认证”，用户试图访问其它网址时被强制访问Portal认证网站进行认证的称为“强制认证”。

# L2应用开发指南

## 概述

### 二层数据流转发

报文的二层转发是在基于VLAN的转发域中，通过MAC地址学习、老化、添加、删除、查找来实现的。

对于已知单播报文（目的MAC为单播MAC，且存在于硬件MAC地址表中），可以通过MAC地址查找获取其出端口，进行单播转发

对于已知组播报文（目的MAC为组播MAC，且存在于硬件MAC地址表中），可以通过MAC地址查找获取相关组播表项，进行组播复制

对于广播报文、未知单播报文、未知组播报文，可以通过VLAN表获取其转发VLAN的端口成员，并泛洪（flood）到除源端口外的所有成员端口

### VLAN

VLAN（虚拟局域网）可以将一个物理LAN逻辑上划分成多个虚拟LAN，其目的就是要缩小广播域（一个广播域就是一个LAN网段，即广播数据帧可以到达的节点范围），减小广播数据帧对LAN内用户通信的影响。

VLAN表是二层核心表项，KD5886芯片VLAN表的规格为4096（0-4095），包含端口成员，flood组播组等信息

数据流的VLAN划分主要有两种：

untagged报文在端口缺省VLAN中转发

tagged报文在自身VLAN tag对应的VLAN中转发

### MAC

MAC地址是网络设备全球唯一的48-bit物理地址，二层交换网络就是通过保存在交换机中的MAC地址表来进行寻址的。

MAC地址表也是二层核心表项，记录了与交换机相连设备的MAC地址、接口号，以及所属VLAN ID。KD5886芯片MAC地址表的规格为65600（65536+64），其中65536个是以哈希桶方式存储的，哈希桶个数为16384，桶深为4，系统默认的哈希方式为异或方式，也可以根据需要将其改为CRC32方式。

另外64个是以CAM方式存储的，用于保存那些相关哈希桶已经存满的MAC地址

单播MAC地址通常情况下是通过硬件自动学习的，而且源未知报文不会被丢弃，也不会拷贝上CPU。出于安全方面的考虑，可以将端口设置为禁止自动学习，源未知报文丢弃，并拷贝到CPU进行安全认证（MAC认证）。此外，还可以设置端口MAC学习个数限制，这样端口硬件学习到的MAC地址数量就会被限制在设定值以内。

而组播MAC地址通常情况下是通过组播协议或者命令行静态配置的，匹配组播MAC的已知组播报文将会复制到相关组播组的成员端口。

### 聚合组

将多至8个配置相同的以太网端口聚集在一起，形成链路聚合组，可以实现增大带宽，负载分担和链路备份等功能。

KD5886芯片可配置多至32个聚合组，参与聚合组负载分担方式计算的可选因素有：

源MAC

目的MAC

IPv4的源IP和目的IP

IPv4报文的SPORT和DPORT

IPv6报文的SPORT和DPORT

IPv6报文的Flow Label

### MSTP

根据VLAN，可以划分出不同的MSTI（多生成树实例），根据协议计算结果设置各端口在各MSTI中的转发状态，可以解决二层环路导致广播风暴的问题。

KD5886芯片支持多至67个MSTI（0-66），支持三种MSTP状态：

discarding：	数据流不转发，MAC地址不学习

learning：	数据流不转发，MAC地址学习

forwarding：	数据流转发，MAC地址学习

## API接口

### 创建/删除指定VLAN

#### 功能简介

创建/删除指定VLAN（范围0-4095），所有VLAN使用前必须先创建，创建VLAN时需指定用于泛洪的组播index（范围0-8191），删除VLAN时将相关软硬件表项恢复为初始值（芯片初始化完成时的取值）。

#### API接口

kyland_rc kyland_vlan_create(const kyland_inst_t inst, /* 芯片实例指针，NULL为缺省值 */

const kyland_vid_t   vid,              /* VLAN ID：0-4095 */

const u16 flood_mc_index);             /* 泛洪组播index：0-8191 */

kyland_rc kyland_vlan_delete(const kyland_inst_t inst,  /* 芯片实例指针，NULL为缺省值 */

const kyland_vid_t   vid);              /* VLAN ID：0-4095 */

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

typedef u16 kyland_vid_t;

### 获取/设置指定VLAN成员端口

#### 功能简介

获取/设置指定VLAN的成员端口，指定VLAN须已创建，端口成员用bool型数组表示，数组长度为最大端口数64。

#### API接口

kyland_rc kyland_vlan_port_members_get(const kyland_inst_t  inst, /* 芯片实例指针，NULL为缺省值 */

const kyland_vid_t   vid,                         /* VLAN ID：0-4095 */

ucBool member[KYLAND_PORT_ARRAY_SIZE]);   /* 成员数组，size=64 */

kyland_rc kyland_vlan_port_members_set(const kyland_inst_t  inst,  /* 芯片实例指针，NULL为缺省值 */

const kyland_vid_t   vid,                           /* VLAN ID：0-4095 */

const ucBool member[KYLAND_PORT_ARRAY_SIZE]); /* 成员数组，size=64 */

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

typedef u16 kyland_vid_t;

### 添加/删除指定MAC地址

#### 功能简介

根据指定的fid，mac，type，outif等参数添加指定mac地址，相关结构体是：

kyland_mac_table_entry_t

根据指定的fid，mac，type删除mac地址，相关结构体是：

kyland_vid_mac_t

#### API接口

kyland_rc kyland_mac_table_add(const kyland_inst_t inst,   /* 芯片实例指针，NULL为缺省值 */

const kyland_mac_table_entry_t  *const entry); /* mac地址entry结构体 */

kyland_rc kyland_mac_table_del(const kyland_inst_t inst,   /* 芯片实例指针，NULL为缺省值 */

const kyland_vid_mac_t  *const vid_mac);     /* mac地址key结构体 */

#### 数据结构

#### 添加mac的entry结构体

typedef struct

{

kyland_vid_mac_t vid_mac;                     /* mac地址的key */

u8 addr_type;                           /* mac地址的类型 */

/* 0: MAC_ADDR_TYPE_UPSID_PN    /* 普通端口类型 */

1: MAC_ADDR_TYPE_GCPU_UPS  /* cpu类型 */

2: MAC_ADDR_TYPE_GLAG      /* 聚合组类型 */

3: MAC_ADDR_TYPE_MC_INDEX  /* 组播类型 */

4: MAC_ADDR_TYPE_NHI         /* Next Hop类型 */  */

u8 locked;                              /* mac出端口是否固定 */

u8 aged;                                /* mac老化标志：0-3 */

u8 mirror;                              /* 报文镜像*/

u8 cpu_copy;                            /* 报文拷贝上cpu */

u8 cpu_queue;                           /* 报文拷贝上cpu进入的队列 */

u8 src_kill_fwd;                          /* 源匹配此entry的报文禁止转发 */

u8 hub_spoke;                           /* hub（1） or spoke（0） */

u16 esdx;                               /* 用于虚端口：evport id=esdx index */

union

{

u16 mc_index;                 /* mc_index，用于组播类型 */

u16 nhi;                      /* next hop index，用于nhi类型 */

kyland_gport_entry_t gport;      /* port/glag，用于普通端口或聚合组类型 */

}outIntf;                                /* 出接口共用体 */

} kyland_mac_table_entry_t;

#### gport结构体

typedef struct kyland_state_s *kyland_inst_t;

typedef struct

{

u8 upsid;  /* 芯片号，目前都为0 */

u8 upspn;  /* 端口号：0-55，或者聚合组号：0-31 */

}kyland_gport_entry_t;

#### 删除mac的key结构体

typedef struct

{

kyland_vid_t  fid;     /* 转发id：0-8192（每个vlan，vsi都需要指定fid）*/

kyland_mac_t  mac;   /* 48bit MAC地址 */

u8 type;              /* 报文转发类型 */

/* 0：基于dmac+fid

1：基于组播dip，

2：基于组播dip+sip */

} kyland_vid_mac_t;

### 组播配置接口

#### 功能简介

芯片组播复制表包括8192组播index映射表和16384组播leaf表,每项leaf包含2项叶子，表项关系如下。

#### API接口

kyland_rc kyland_mc_init(kyland_inst_t inst,kyland_mc_index_t mcIndex);

kyland_rc kyland_mc_del(kyland_inst_t inst,kyland_mc_index_t mcIndex);

/*  sdk manage the leaf index*/

kyland_rc kyland_mc_leaf_add(kyland_chipid_t chip_no,

kyland_mc_index_t mcIndex,

kyland_leaf_st *leaf);

kyland_rc kyland_mc_leaf_del(kyland_chipid_t chip_no,

kyland_mc_index_t mcIndex,

kyland_leaf_st *leaf);

#### 数据结构

typedef u16 kyland_mc_index_t;

typedef u16 kyland_leaf_index_t;

typedef struct {

u8 upsid;

u8 member[64];

} kyland_leaf_type1_t;

typedef struct {

u8 glag_id;

} kyland_leaf_type2_t;

typedef struct {

u8 upsid;	//upsid.bit4 = 1时，upspn表示glagid

u8 upspn;

u16 esdx;

u16 evmid;

} kyland_leaf_type34_t;

typedef struct {

u8 upsid;	//upsid = 0xff表示glag

u8 upspn;

u16 token;

u16 lrn_nhi;

} kyland_leaf_type56_t;

typedef struct {

u8 isValid[2];

u8 hub_spk[2];

u8 type[2];	// when type1, only type[0] is valid(isValid[0]=1,isValid[1]=0);

union

{

kyland_leaf_type1_t  bitmap[2];

kyland_leaf_type2_t  lag[2];

kyland_leaf_type34_t l3mc[2];

kyland_leaf_type56_t pw[2];

}outInfo;

} kyland_leaf_st;

### 聚合组配置接口

#### 功能简介

聚合组配置的内容包括：

1、获取/设置聚合组负载分担模式

2、获取/设置聚合组成员端口

获取/设置聚合组负载分担模式，可以参与流量负载分担哈希计算的参数有6个：

smac（报文源MAC）

dmac（报文目的MAC）

ipv4_sip_dip（IPv4报文的源IP和目的IP）

ipv4_sport_dport（IPv4报文的源端口和目的端口）

ipv6_sport_dport（IPv6报文的源端口和目的端口）

ipv6_flow_label（IPv6报文的Flow Lable字段）

可选择其中一个或者多个进行哈希计算，实现流量的负载分担

获取/设置聚合组成员端口，聚合组最大个数为32，每个聚合组最多端口成员个数为8，端口是否为聚合组成员用bool型数组表示，数组长度为最大端口数64

#### API接口

kyland_rc kyland_glag_get_mode(kyland_inst_t inst, /* 芯片实例指针，NULL为缺省值 */

kyland_glag_mode_t *mode)          /* 负载分担模式结构指针 */

kyland_rc kyland_glag_set_mode(kyland_inst_t inst, /* 芯片实例指针，NULL为缺省值 */

kyland_glag_mode_t *mode)          /* 负载分担模式结构指针 */

/* get glag member list */

kyland_rc kyland_glag_get_member(kyland_inst_t inst, /* 芯片实例指针，NULL为缺省值 */

kyland_glag_no_t       glag, /* 聚合组号 */

kyland_glag_member_t  *entry) /* 聚合组结构体指针 */

/* set glag member list */

kyland_rc kyland_glag_set_member(kyland_inst_t inst, /* 芯片实例指针，NULL为缺省值 */

kyland_glag_no_t      glag, /* 聚合组号 */

kyland_glag_member_t *entry) /* 聚合组结构体指针 */

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

typedef struct kyland_state_s *kyland_inst_t;

typedef u32 kyland_glag_no_t;

/*brief Aggregation traffic distribution mode */

typedef struct

{

ucBool smac_enable;                    /* source mac address */

ucBool dmac_enable;                    /* destination mac address */

ucBool ipv4_sip_dip_enable;          /* ipv4 source & destination ip address */

ucBool ipv4_sport_dport_enable;   /* ipv4 source & destination tcp/udp port */

ucBool ipv6_sport_dport_enable;   /* ipv6 source & destination tcp/udp port */

ucBool ipv6_flow_label_enable;      /* ipv6 flow label */

} kyland_glag_mode_t;

typedef struct

{

u32 num;                          /* 聚合组成员端口数：0-8 */

u32 upsid[KYLAND_GLAG_PORTS];  /* 聚合组成员芯片号，size=8 */

u32 upspn[KYLAND_GLAG_PORTS]; /* 聚合组成员端口号，size=8 */

} kyland_glag_member_t;

### MSTP配置接口

#### 功能简介

MSTP配置的内容包括：

1、获取/设置指定VLAN的MSTI

2、获取/设置指定端口指定MSTI的MSTP状态

MSTI（MSTP实例）：0-66

MSTP状态有三种：

0---discarding		不学mac，不转发

1---learning		学习mac，不转发

2---forwarding		学习mac，且转发

#### API接口

kyland_rc kyland_mstp_vlan_msti_get(const kyland_inst_t  inst, /* 芯片实例指针，NULL为缺省值 */

const kyland_vid_t   vid,                      /* VLAN ID：0-4095 */

kyland_msti_t        *const msti);              /* MSTP实例号指针 */

kyland_rc kyland_mstp_vlan_msti_set(const kyland_inst_t  inst, /* 芯片实例指针，NULL为缺省值 */

const kyland_vid_t   vid,                      /* VLAN ID：0-4095 */

const kyland_msti_t  msti);                     /* MSTP实例号 ：0-66*/

kyland_rc kyland_mstp_port_msti_state_get(const kyland_inst_t inst, /* 芯片实例指针，NULL为缺省值 */

const kyland_port_no_t  port_no,                  /* 端口号：0-55 */

const kyland_msti_t     msti,                     /* MSTP实例号 */

kyland_stp_state_t      *const state);              /* MSTP状态指针 */

kyland_rc kyland_mstp_port_msti_state_set(const kyland_inst_t inst, /* 芯片实例指针，NULL为缺省值 */

const kyland_port_no_t    port_no,                /* 端口号：0-55 */

const kyland_msti_t       msti,                   /* MSTP实例号 */

const kyland_stp_state_t  state);                    /* MSTP状态 */

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

typedef u16 kyland_vid_t;

typedef u32 kyland_msti_t;

typedef u32 kyland_port_no_t;

typedef enum

{

KYLAND_STP_STATE_DISCARDING,  /**< STP state discarding (admin/operational down) */

KYLAND_STP_STATE_LEARNING,    /**< STP state learning */

KYLAND_STP_STATE_FORWARDING   /**< STP state forwarding */

} kyland_stp_state_t;

### 端口安全配置接口

#### 功能简介

端口安全的内容包括：

1、端口mac学习个数限制

端口mac学习个数达到限定值情况下，源未知报文是否拷贝上CPU

3、设置端口学习状态

是否硬件自动学习

源未知和源端口迁移报文是否拷贝上CPU

源未知报文是否丢弃

#### API接口

kyland_rc kyland_mac_port_learn_limit_max_num_set (

const kyland_inst_t inst,                       /* 芯片实例指针，NULL为缺省值 */

const kyland_port_no_t  port_no,               /* 端口号：0-55 */

const u32   num)                            /* 端口mac学习最大个数限制值 */

kyland_rc kyland_mac_port_learn_limit_exceed_action_set (

const kyland_inst_t inst,                       /*芯片实例指针，NULL为缺省值*/

const ucBool copy_to_cpu)                    /* 是否拷贝源mac超限报文上cpu */

kyland_rc kyland_learn_port_mode_set(const kyland_inst_t inst, /* 芯片实例指针，NULL为缺省值 */

const kyland_port_no_t     port_no,            /* 端口号：0-55 */

const kyland_learn_mode_t  *const mode)        /* 端口学习模式 */

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

typedef u32 kyland_port_no_t;

typedef struct

{

ucBool automatic; /* 是否硬件自动学习 */

ucBool cpu;      /*源未知和源端口迁移报文是否拷贝上CPU */

ucBool discard;   /*源未知报文是否丢弃*/

} kyland_learn_mode_t;

## API应用

### 二层已知单播报文转发

#### 测试环境

（图中黑色实线表示物理连接，图中红色虚线表示单播报文转发路径）

SW1，SW2是两个以KD5886交换芯片为核心的交换机

PC1-PC5是5个网络终端设备

具体连接关系如下表所示：

| 设备名 | 端口 | 对端设备名 |
| --- | --- | --- |
| SW1 | 0 | SW2 |
| SW1 | 1 | PC1 |
| SW1 | 2 | PC2 |
| SW2 | 0 | SW1 |
| SW2 | 3 | PC3 |
| SW2 | 4 | PC4 |
| SW2 | 5 | PC5 |

#### SW1配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[0] = TRUE;

member[1] = TRUE;

member[2] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 1,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW2配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[0] = TRUE;

member[3] = TRUE;

member[4] = TRUE;

member[5] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

PC1和PC5对打已知单播报文

PC1=>SW1的报文：

dmac=00-55-55-55-55-55，smac=00-11-11-11-11-11，dip=1.1.1.5，sip=1.1.1.1

PC5=>SW2的报文：

dmac=00-11-11-11-11-11，smac=00-55-55-55-55-55，dip=1.1.1.1，sip=5.5.5.5

只有PC1和PC5可以收到对端发送的报文，PC2、PC3、PC4不能收到相关报文

### 二层已知组播报文转发

#### 测试环境

（图中黑色实线表示物理连接，图中红色虚线表示组播报文转发路径）

SW1，SW2是两个以KD5886交换芯片为核心的交换机

PC1-PC5是5个网络终端设备

具体连接关系如下表所示：

| 设备名 | 端口 | 对端设备名 |
| --- | --- | --- |
| SW1 | 0 | SW2 |
| SW1 | 1 | PC1 |
| SW1 | 2 | PC2 |
| SW2 | 0 | SW1 |
| SW2 | 3 | PC3 |
| SW2 | 4 | PC4 |
| SW2 | 5 | PC5 |

#### SW1配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加成员

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[0] = TRUE;

member[1] = TRUE;

member[2] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 1,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建组播组

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create mc group */

rc = kyland_mc_init(inst, 1234);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_init failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 组播组添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_leaf_st leaf;

/* mc group add l2 port member */

KYLAND_OS_MEMSET(&leaf, 0, sizeof(leaf));

leaf.valid = 1;

leaf.type = leaf_type_l2_port;

leaf.outInfo.l2port = 2;

rc = kyland_mc_leaf_add(inst, 1234, &leaf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_leaf_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

leaf.outInfo.l2port = 0;

rc = kyland_mc_leaf_add(inst, 1234, &leaf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_leaf_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加组播MAC

kyland_mac_table_entry_t entry;

memset(&entry, 0, sizeof(entry));

entry.vid_mac.type = 0;/*dmac+fid*/

entry.vid_mac.fid = 123;

entry.vid_mac.mac.addr[0] = 0x01;

entry.vid_mac.mac.addr[1] = 0x00;

entry.vid_mac.mac.addr[2] = 0x5e;

entry.vid_mac.mac.addr[3] = 0x00;

entry.vid_mac.mac.addr[4] = 0x12;

entry.vid_mac.mac.addr[5] = 0x34;

entry.addr_type = MAC_ADDR_TYPE_MC_INDEX;/*3*/

entry.locked = 1;

entry.outIntf.mc_index = 1234;

if(kyland_mac_table_add(req->api_inst, &entry) == KYLAND_RC_OK){

printf("ADD MAC OK!\n");

cli_mac_print(&entry,1);

}

#### SW2配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加成员

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[0] = TRUE;

member[3] = TRUE;

member[4] = TRUE;

member[5] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建组播组

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create mc group */

rc = kyland_mc_init(inst, 1234);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_init failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 组播组添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_leaf_st leaf;

/* mc group add l2 port member */

KYLAND_OS_MEMSET(&leaf, 0, sizeof(leaf));

leaf.valid = 1;

leaf.type = leaf_type_l2_port;

leaf.outInfo.l2port = 4;

rc = kyland_mc_leaf_add(inst, 1234, &leaf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_leaf_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

leaf.outInfo.l2port = 0;

rc = kyland_mc_leaf_add(inst, 1234, &leaf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_leaf_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加组播MAC

kyland_mac_table_entry_t entry;

memset(&entry, 0, sizeof(entry));

entry.vid_mac.type = 0;/*dmac+fid*/

entry.vid_mac.fid = 123;

entry.vid_mac.mac.addr[0] = 0x01;

entry.vid_mac.mac.addr[1] = 0x00;

entry.vid_mac.mac.addr[2] = 0x5e;

entry.vid_mac.mac.addr[3] = 0x00;

entry.vid_mac.mac.addr[4] = 0x12;

entry.vid_mac.mac.addr[5] = 0x34;

entry.addr_type = MAC_ADDR_TYPE_MC_INDEX;/*3*/

entry.locked = 1;

entry.outIntf.mc_index = 1234;

if(kyland_mac_table_add(req->api_inst, &entry) == KYLAND_RC_OK){

printf("ADD MAC OK!\n");

cli_mac_print(&entry,1);

}

#### 流量测试

PC5向端口5发送二层组播报文，mac=01-00-5e-00-12-34，c-tagged vid=123，端口2和端口4可以收到二层组播复制报文，端口1和端口3不能收到相关组播报文

### 二层广播、未知单播、未知组播报文泛洪

#### 测试环境

（图中黑色实线表示物理连接，图中红色虚线表示报文泛洪路径）

#### SW1配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[0] = TRUE;

member[1] = TRUE;

member[2] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 1,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW2配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[0] = TRUE;

member[3] = TRUE;

member[4] = TRUE;

member[5] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

PC5向SW2分别发送广播、未知单播、未知组播报文，报文可以flood到PC1-PC4。

### 通过设置聚合组实现负载分担

#### 测试环境

#### SW1配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[1] = TRUE;

member[2] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 1,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 聚合组添加端口

kyland_inst_t inst = NULL;

kyland_glag_member_t entry;

KYLAND_OS_MEMSET(&entry,0,sizeof(entry));

kyland_rc rc = KYLAND_RC_OK;

entry.num=4;

entry.upsid[0]=0;

entry.upspn[0]=7;

entry.upsid[1]=0;

entry.upspn[1]=8;

entry.upsid[2]=0;

entry.upspn[2]=9;

entry.upsid[3]=0;

entry.upspn[3]=10;

rc=kyland_glag_set_member(inst, 12, &entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_glag_set_member failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 聚合组加入VLAN

glag 12加入vlan 123（glag成员加入vlan，glag加入vlan flood组播组）

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

rc=kyland_glag_add_to_vlan(inst, 12, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_glag_add_to_vlan failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW2配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[3] = TRUE;

member[4] = TRUE;

member[5] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 聚合组添加端口

kyland_inst_t inst = NULL;

kyland_glag_member_t entry;

KYLAND_OS_MEMSET(&entry,0,sizeof(entry));

kyland_rc rc = KYLAND_RC_OK;

entry.num=4;

entry.upsid[0]=0;

entry.upspn[0]=7;

entry.upsid[1]=0;

entry.upspn[1]=8;

entry.upsid[2]=0;

entry.upspn[2]=9;

entry.upsid[3]=0;

entry.upspn[3]=10;

rc=kyland_glag_set_member(inst, 12, &entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_glag_set_member failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 聚合组加入VLAN

glag 12加入vlan 123（glag成员加入vlan，glag加入vlan flood组播组）

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

rc=kyland_glag_add_to_vlan(inst, 12, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_glag_add_to_vlan failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

通过端口报文统计信息，确认以下报文流量在聚合组的4个成员端口上进行了负载分担：

PC1和PC5对打的源MAC变化的二层已知单播报文

PC5发送的 UDP DPORT/SPORT变化的二层已知组播报文

PC5发送的源MAC变化的广播、未知单播、未知组播报文

### 通过设置MSTP实现数据流丢弃

#### 测试环境

#### SW1配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 456, 456);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[1] = TRUE;

member[7] = TRUE;

member[8] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[2] = TRUE;

member[7] = TRUE;

member[8] = TRUE;

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 1,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置VLAN所属MSTI

设置vlan123的msti=10，vlan456的msti=20

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* set mstp vlan msti */

rc = kyland_mstp_vlan_msti_set(inst, 123, 10);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_vlan_msti_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_vlan_msti_set(inst, 456, 20);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_vlan_msti_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口指定MSTI的MSTP状态

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

rc = kyland_mstp_port_msti_state_set(inst, 1, 10, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 2, 20, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 7, 10, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 7, 20, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 8, 10, KYLAND_STP_STATE_DISCARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 8, 20, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW2配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 456, 456);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[3] = TRUE;

member[4] = TRUE;

member[7] = TRUE;

member[8] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[5] = TRUE;

member[7] = TRUE;

member[8] = TRUE;

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置VLAN所属MSTI

设置vlan123的msti=10，vlan456的msti=20

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* set mstp vlan msti */

rc = kyland_mstp_vlan_msti_set(inst, 123, 10);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_vlan_msti_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_vlan_msti_set(inst, 456, 20);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_vlan_msti_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口指定MSTI的MSTP状态

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

rc = kyland_mstp_port_msti_state_set(inst, 3, 10, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 4, 10, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 5, 20, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 7, 10, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 7, 20, KYLAND_STP_STATE_DISCARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 8, 10, KYLAND_STP_STATE_DISCARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_mstp_port_msti_state_set(inst, 8, 20, KYLAND_STP_STATE_FORWARDING);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mstp_port_msti_state_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

通过端口报文统计信息可以确认：

VLAN123报文都通过SW1/SW2的端口7进行跨设备转发

VLAN456报文都通过SW1/SW2的端口8进行跨设备转发

### 通过设置端口学习状态实现MAC认证

#### 测试环境

SW1是以KD5886交换芯片为核心的交换机

PC1-PC3是3个网络终端设备

具体连接关系如下表所示：

| 设备名 | 端口 | 对端设备名 |
| --- | --- | --- |
| SW1 | 0 | RADIUS Server（用于认证的服务器） |
| SW1 | 1 | PC1 |
| SW1 | 2 | PC2 |
| SW1 | 3 | PC3 |

#### SW配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 123, 123);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 456, 456);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### VLAN添加端口

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

ucBool         member[KYLAND_PORT_ARRAY_SIZE];

/* set vlan member */

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[1] = TRUE;

member[2] = TRUE;

member[3] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

member[0] = TRUE;

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 1,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口学习状态

kyland_learn_mode_t     mode;

mode.automatic = 0;

mode.cpu = 1;

mode.discard = 1;

rc = kyland_learn_port_mode_set(inst, 1, &mode);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_learn_port_mode_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_learn_port_mode_set(inst, 2, &mode);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_learn_port_mode_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_learn_port_mode_set(inst, 3, &mode);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_learn_port_mode_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 安全认证

PC1，PC2，PC3连接的端口1，端口2，端口3都被设置成为了源MAC不自动学习，丢弃，拷贝上CPU（相当于将报文重定向到CPU），这就意味着用户想要上网，必须先通过安全认证。

通过安全认证前，报文源MAC为未知，报文会被重定向到CPU上进行安全认证，CPU收到认证报文后，会连接到认证服务器RADIUS Server，对报文源MAC进行认证（源MAC认证是最简易的认证方式，交换机不需要和上网设备有任何报文交互，当然也可以采用其它更复杂的认证方式，如802.1x认证和Portal认证）。

如果安全认证成功，此MAC会被设为普通的MAC，报文则变为已知报文，不再重定向上CPU，可以进行三层转发，二层单播转发，或者在VLAN内泛洪

如果安全认证失败，此MAC会被设为源丢弃的MAC，报文也会变为已知报文，被彻底丢弃。

## 芯片实现

### 总体流程

报文转发总体流程如上图所示，转发类型分为以下几类：

二层转发（L2 Forwarding）

三层单播转发（IP Unicast）

三层组播转发（IP Multicast）

MPLS转发（MPLS）

协议报文重定向到CPU（Redirect to CPU）

### 二层转发流程

L2 Forwarding的流程如上图所示，关键的处理有：

源MAC查询，学习

目的MAC查询，转发

目的地址为NHI，进行FRR处理
