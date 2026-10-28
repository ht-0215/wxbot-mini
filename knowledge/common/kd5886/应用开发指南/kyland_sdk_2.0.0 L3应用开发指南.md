# kyland_sdk_2.0.0 L3应用开发指南

kyland_sdk_2.0.0

L3应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 术语&缩略语	4

1.1 FRR（Fast ReRoute）	4

1.2 ECMP（Equal-Cost Multi-Path Routing）	4

2 L3应用开发指南	5

2.1 概述	5

2.1.1 三层数据流转发	5

2.1.2 链路保护	5

2.1.3 负载均衡	5

2.2 API接口	6

2.2.1 三层全局配置	6

2.2.2 添加/删除一个三层接口	8

2.2.3 设置NHI	13

2.2.4 添加/删除路由	14

2.2.5 NHI保护组配置接口	16

2.2.6 ECMP配置接口	19

2.3 API应用	20

2.3.1 IPv4单播	20

2.3.2 IPv4组播	37

2.3.3 IPv6单播	54

2.3.4 IPv6组播	73

2.3.5 FRR	91

2.3.6 ECMP	124

2.4 芯片实现	178

2.4.1 总体流程	178

2.4.2 三层单播转发流程	179

2.4.3 三层组播转发流程	180

# 术语&缩略语

## FRR（Fast ReRoute）

快速重路由，简单地说就是对单播路由的下一跳（对应NHI）进行1:1保护，当主NHI所在链路发生故障时，会触发链路切换事件，将转发到主NHI的流量切换到备NHI。FRR是提高业务可用性的重要途径。

## ECMP（Equal-Cost Multi-Path Routing）

等价多路径路由，就是说存在到同一IP的多条路由转发路径（对应多个NHI）时，可以设置ECMP group，实现三层报文的在多路径上进行负载分担。ECMP对于提高业务的网络带宽具有重要意义。

# L3应用开发指南

## 概述

### 三层数据流转发

报文的三层转发是在不同VLAN广播域间，通过路由转发表（FIB）的设置、查找来实现的

IPv4单播报文匹配目的IP（32bit）+Mask（32bit），下一跳（NEXT HOP）为相邻路由器/交换机/主机的IP（32bit），报文源MAC，目的MAC，VLAN TAG，TTL字段会根据实际情况进行更新

IPv4组播报文匹配目的DIP（32bit）或者DIP（32bit）+SIP（32bit），组播报文会复制到各个成员，报文源MAC，VLAN TAG，TTL字段会根据实际情况进行更新

IPv6单播报文匹配目的DIP6（128bit）+prefix（0-128）下一跳为相邻路由器/交换机/主机的IP6（128bit），报文源MAC，目的MAC，VLAN TAG，TTL字段会根据实际情况进行更新

IPv6组播报文匹配目的DIP6（128bit）或者DIP6（128bit）+SIP6（128bit），组播报文会复制到各个成员，报文源MAC，VLAN TAG，TTL字段会根据实际情况进行更新

### 链路保护

对IPv4或者IPv6单播路由的下一跳，可以进行1:1的保护（即IP FRR），主备两条备份链路的设置，可以大大提高承载业务的可靠性

### 负载均衡

每个ECMP GROUP可配置多达8个下一跳，用ECMP GROUP代替IPv4或者IPv6中的下一跳，可以实现IP报文在多条等价路径上的负载均衡

## API接口

### 三层全局配置

#### 功能简介

三层全局配置的内容包括获取和设置rleg全局参数，包括全局mode和base MAC，通常情况下，全局mode为single，所有三层接口（rleg）共用一个三层MAC（base MAC）。

#### API接口

kyland_rc kyland_l3_rleg_common_get(const kyland_inst_t inst,

const kyland_l3_rleg_common_conf_t * const rleg_comm_conf)

kyland_rc kyland_l3_rleg_common_set(const kyland_inst_t inst,

const kyland_l3_rleg_common_conf_t * const rleg_comm_conf);

#### 数据结构

/** \brief MAC addressing mode for routing legs */

typedef enum

{

/** The addressing mode has still not been configured */

KYLAND_ROUTING_RLEG_MAC_MODE_INVALID = 0,

/** One common MAC address is used for all legs */

KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE = 1,

/** The following two patterns are not usually used */

KYLAND_ROUTING_RLEG_MAC_MODE_VID = 2,

KYLAND_ROUTING_RLEG_MAC_MODE_VMID = 3,

KYLAND_ROUTING_RLEG_MAC_MODE_MAX,

} kyland_l3_rleg_common_mode_t;

/** \brief MAC Address */

typedef struct

{

u8 addr[6];   /**< Network byte order */

} kyland_mac_t;

/** \brief Common configurations for all routing legs */

typedef struct

{

/** Common rleg-mode for all routing legs. */

kyland_l3_rleg_common_mode_t rleg_mode;

/** Base mac address used to derive addresses for all routing legs. */

kyland_mac_t                 base_address;

} kyland_l3_rleg_common_conf_t;

### 添加/删除一个三层接口

#### 功能简介

1. kyland_l3_rleg_get

获取当前配置了多少个Rleg，具体的内容一并获取。

说明：

只能直接看出哪些vlan 配置了Rleg， 具体的RlegID需要通过vlanTable获取。即RlegID由SDK内部管理，没对外体现。

2. kyland_l3_rleg_get_specific

指定vlan获取Rleg信息。

3. kyland_l3_rleg_add

给vlan设置rleg，可设置的字段即包括PFS_MPLS_L3的VMID_TBL_0/1/2也包括PES的EVMID_TBL_0/1/2。

在l3_state结构体的rleg_conf结构体数组中存储配置值，rleg_conf数组的索引就是RlegID。RlegID要配置在PFS_MPLS_L3::VLAN_TBL_0[0:7]中, 同时bit28的VLAN_RLEG_ENA要置1。

说明：

API入参支持单独设置vrid0_enable和vrid1_enable，但硬件只有一个vrid_enable字段，只有一个vridenable时，寄存器VMID_TBL_1和VMID_TBL_2设置相同的vrid。

4. kyland_l3_rleg_update

更新特定vlan的Rleg配置。 如果指定的vlan没有使能过Rleg，那么函数返回。

说明：此时不需要重新配置vlanTable0。

4. kyland_l3_rleg_del

删除指定vlan对应的三层接口

#### API接口

kyland_rc kyland_l3_rleg_get(const kyland_inst_t     inst,

u32                  *cnt,

kyland_l3_rleg_conf_t   buf[KYLAND_RLEG_CNT]);

kyland_rc kyland_l3_rleg_get_specific(const kyland_inst_t     inst,

kyland_vid_t            vid,

kyland_l3_rleg_id_t     *rleg_id,

kyland_l3_rleg_conf_t  *conf);

kyland_rc kyland_l3_rleg_add(const kyland_inst_t          inst,

const kyland_l3_rleg_conf_t *const conf);

kyland_rc kyland_l3_rleg_del(const kyland_inst_t inst,

const kyland_vid_t  vlan)

kyland_rc kyland_l3_rleg_update(const kyland_inst_t          inst,

const kyland_l3_rleg_conf_t *const conf);

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

typedef struct

{

/** Enable IPv4 routing */

ucBool ipv4_unicast_enable;

ucBool ipv4_multicast_enable;

/** Enable IPv6 routing */

ucBool ipv6_unicast_enable;

ucBool ipv6_multicast_enable;

/** Enable mpls routing */

ucBool mpls_uc_enable;

ucBool mpls_mc_enable;

/** Enable IPv4/IPv6 icmp redirect If enabled then frames with IVMD==EVMID are redirected to CPU.*/

ucBool ipv4_icmp_redirect_enable;

ucBool ipv6_icmp_redirect_enable;

/** Vlan for which the router leg is instantiated */

kyland_vid_t          vlan;

/** Enable/disable VRRP for a given router leg.

*

* The hardware has support for enabling 0-2 VRID's for a given router leg.

* This is activated by configured vrid0_enable and vrid1_enable. The actual

* VRID the route is assigned to is configured in vrid0/vrid1.

* After vrrp enabled, the hardware will consider all

* destination mac addresses matching 00-00-5E-00-XX-{VRID} as VRRP address.

*/

ucBool                vrid0_enable;

/** The VRID value assigned to this router leg. */

kyland_l3_vrid_t      vrid0;

/** Enable/disable vrid1 for this router leg. */

ucBool                vrid1_enable;

/** The VRID value assigned to this router leg. */

kyland_l3_vrid_t      vrid1;

/** L3vpn id*/

u8 vrfid;

u8 reserved1;

/**Egress define*/

/**IPv4/IPv6 multicast TTL limit*/

u8 ipv4mc_limit_ttl;

u8 ipv6mc_limit_ttl;

/**IPv4/IPv6 MTU*/

u16 ipv4_mtu;

u16 ipv6_mtu;

u8 reserved2[2];

} kyland_l3_rleg_conf_t;

### 设置NHI

#### 功能简介

1. kyland_l3_nhi_set

当nhi 索引由上层软件自己管理时，可以使用此接口下发nhi信息到硬件。

2. kyland_l3_nhi_get

当nhi 索引由上层软件自己管理时，可以使用此接口查询特定索引对应的nhi信息，信息来自硬件。

#### API接口

kyland_rc kyland_l3_nhi_set(const kyland_inst_t       inst,

const u32 index,

const kyland_l3_next_hop_conf_t * const next_hop_conf);

kyland_rc kyland_l3_nhi_get(const kyland_inst_t       inst,

const u32 index,

kyland_l3_next_hop_conf_t * const next_hop_conf);

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

typedef struct {

kyland_l3_next_hop_type_t fwd_cmd;

union

{

kyland_mac_t      mac;                           //FWD_CMD_ARP

//kyland_l3_next_hop_tunnel_t tunnel_info;  //FWD_CMD_TNL

u8      cpu_queue_id;                     //FWD_CMD_TOCPU

u16     mc_index;                         //FWD_CMD_MC

}fwd_info;

//below are not always needed

kyland_vid_t   out_vlan;

kyland_fwd_port_t out_port;

u8  secur_match_mac_ena;

u8  secur_match_vmid_ena;

//u16             evport;

} kyland_l3_next_hop_conf_t;

### 添加/删除路由

#### 功能简介

1. kyland_l3_route_entry_add

此接口负责下发lpm tcam的key和action配置, lpm tcam资源由SDK内部管理，其它索引由上层管理。

2. kyland_l3_route_entry_del

此接口负责下发lpm tcam的key和action删除, lpm tcam资源由SDK内部管理，其它索引由上层管理。

3. kyland_l3_route_entry_find

此接口负责查找指定路由表项是否存在。

#### API接口

kyland_rc kyland_l3_route_entry_add(const kyland_inst_t inst,

kyland_l3_route_entry_t * const entry);

kyland_rc kyland_l3_route_entry_del(const kyland_inst_t inst,

kyland_l3_route_entry_t * const entry);

kyland_rc kyland_l3_route_entry_find(const kyland_inst_t inst,

kyland_l3_route_entry_t *const entry);

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

typedef struct

{

/** Type of route */

kyland_l3_route_entry_type_t type;

union {

/** IPv4 unicast route */

kyland_l3_ipv4_uc_t ipv4_uc;

/** IPv4 muticast route */

kyland_l3_ipv4_mc_t ipv4_mc;

/** IPv6 unicast route */

kyland_l3_ipv6_uc_t ipv6_uc;

/** IPv6 muticast route */

kyland_l3_ipv6_mc_t ipv6_mc;

} route; /**< Route */

} kyland_l3_route_entry_t;

### NHI保护组配置接口

#### 功能简介

NHI保护组配置的内容包括：

获取/设置NHI保护组信息

获取/设置保护组状态

#### API接口

kyland_rc kyland_l3_prot_nhi_get(const kyland_inst_t inst,

const u32 index,

kyland_l3_prot_nhi_conf_t *const prot_nhi_conf)

kyland_rc kyland_l3_prot_nhi_set (const kyland_inst_t inst,

const u32 index,

const kyland_l3_prot_nhi_conf_t *const prot_nhi_conf);

kyland_rc kyland_l3_prot_group_get(const kyland_inst_t inst,

const u32 index,

kyland_l3_prot_group_conf_t *const prot_group_conf)

kyland_rc kyland_l3_prot_group_set(const kyland_inst_t inst,

const u32 index,

const kyland_l3_prot_group_conf_t *const prot_group_conf);

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

/** \brief primary path type*/

typedef enum

{

KYLAND_L3_PRIM_PATH_TYPE_TUNNEL,

KYLAND_L3_PRIM_PATH_TYPE_PW,

} kyland_l3_prim_path_type_t;

/** \brief primary path status*/

typedef enum

{

KYLAND_L3_PRIM_PATH_STATUS_DOWN,

KYLAND_L3_PRIM_PATH_STATUS_UP,

} kyland_l3_prim_path_status_t;

typedef struct{

u32 prot_group_index;

u32 backup_nh_index;

} kyland_l3_prot_nhi_conf_t;

typedef struct{

kyland_l3_prim_path_type_t type;

kyland_l3_prim_path_status_t status;

} kyland_l3_prot_group_conf_t;

### ECMP配置接口

#### 功能简介

ECMP配置的内容为获取/设置ECMP组信息，包括成员数和成员列表

#### API接口

kyland_rc kyland_l3_ecmp_get(const kyland_inst_t inst,

const u32 group_index,

u32 * const member_cnt,

kyland_l3_ecmp_member_conf_t * const member_conf)

kyland_rc kyland_l3_ecmp_set(const kyland_inst_t inst,

const u32 group_index,

const u32 member_cnt,

const kyland_l3_ecmp_member_conf_t * const member_conf)

#### 数据结构

typedef struct kyland_state_s *kyland_inst_t;

typedef struct{

u32 prot_group_index;

u32 primary_nh_index;

u32 backup_nh_index;

} kyland_l3_ecmp_member_conf_t;

## API应用

### IPv4单播

#### 测试环境

SW1，SW2，SW3是三个以KD5886交换芯片为核心的交换机

PC1-PC5是5个网络终端设备

具体连接关系如下表所示：

| 设备名 | 端口 | 对端设备名 |
| --- | --- | --- |
| SW1 | 1 | PC1 |
| SW1 | 2 | PC2 |
| SW1 | 0 | SW3 |
| SW2 | 3 | PC3 |
| SW2 | 4 | PC4 |
| SW2 | 5 | PC5 |
| SW2 | 0 | SW3 |
| SW3 | 1 | SW1 |
| SW3 | 2 | SW2 |

报文VLAN TAG状况如下表所示：

| 本端设备 | 对端设备 | TAG状况 |
| --- | --- | --- |
| PC1 | SW1 | untagged（pvid=123） |
| PC2 | SW1 | untagged（pvid=123） |
| SW1 | SW3 | c-tagged vid=123 |
| PC3 | SW2 | untagged（pvid=456） |
| PC4 | SW2 | untagged（pvid=456） |
| PC5 | SW2 | untagged（pvid=456） |
| SW2 | SW3 | c-tagged vid=456 |

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

将端口1,2的PVID设置为456

端口0的PVID仍然保持默认值1（上行报文将以vid=123的c-tagged报文发送到SW3）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 1,&vp_conf);

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

rc = kyland_vlan_port_conf_get(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

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

rc = kyland_vlan_create(inst, 456, 456)

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

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

将端口3,4,5的PVID设置为456

端口0的PVID仍然保持默认值1（上行报文将以vid=456的c-tagged报文发送到SW3）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_get(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_get(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW3配置

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

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层全局配置

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x11;

rleg_common_cfg.base_address.addr[2] = 0x22;

rleg_common_cfg.base_address.addr[3] = 0x33;

rleg_common_cfg.base_address.addr[4] = 0x44;

rleg_common_cfg.base_address.addr[5] = 0x55;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 123;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 456;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建ARP类型NHI

u8 RT_NHI_A_MAC[6] =               {0x00, 0x11, 0x11, 0x11, 0x11, 0x23};

u8 RT_NHI_B_MAC[6] =               {0x00, 0x44, 0x44, 0x44, 0x44, 0x56};

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_next_hop_conf_t next_hop_conf;

kyland_l3_route_entry_t route_entry;

/* add nhi with arp type */

/* nhi a with outport A */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

KYLAND_OS_MEMCPY(next_hop_conf.fwd_info.mac.addr, RT_NHI_A_MAC, 6);

next_hop_conf.out_vlan = 123;

next_hop_conf.out_port.fwd_port.out_port.port_num = 1;

rc = kyland_l3_nhi_set(inst, 111, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi b with outport B */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

KYLAND_OS_MEMCPY(next_hop_conf.fwd_info.mac.addr, RT_NHI_B_MAC, 6);

next_hop_conf.out_vlan = 456;

next_hop_conf.out_port.fwd_port.out_port.port_num = 2;

rc = kyland_l3_nhi_set(inst, 222, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加IPv4单播路由

kyland_inst_t inst = NULL;

kyland_l3_route_entry_t route_entry;

/* add route A */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x01020304;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 111;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* add route B */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x05060708;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 222;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

SW3上，设置vlanif 123的IP地址为1.2.3.1

SW3上，设置vlanif 456的IP地址为5.6.7.1

PC1上，设置IP地址为1.2.3.4，缺省网关为1.2.3.1

PC5上，设置IP地址为5.6.7.8，缺省网关为5.6.7.1

在PC1（1.2.3.4）上ping PC5（5.6.7.8），可以ping通

在PC5（5.6.7.8）上ping PC1（1.2.3.4），也可以ping通

PC1向SW1发送IP报文SIP=1.2.3.4，DIP=5.6.7.8，SMAC=00-11-11-11-11-23，DMAC=e0-11-22-33-44-55，可以到达PC5，SMAC替换为e0-11-22-33-44-55，DMAC替换为00-44-44-44-44-56，ttl数值减1

PC5向SW2发送IP报文SIP=5.6.7.8，DIP=1.2.3.4，SMAC=00-44-44-44-44-56，DMAC=e0-11-22-33-44-55，可以到达PC1，SMAC替换为e0-11-22-33-44-55，DMAC替换为00-11-11-11-11-23，ttl数值减1

### IPv4组播

#### 测试环境

SW1，SW2，SW3是三个以KD5886交换芯片为核心的交换机

PC1-PC5是5个网络终端设备

具体连接关系如下表所示：

| 设备名 | 端口 | 对端设备名 |
| --- | --- | --- |
| SW1 | 1 | PC1 |
| SW1 | 2 | PC2 |
| SW1 | 0 | SW3 |
| SW2 | 3 | PC3 |
| SW2 | 4 | PC4 |
| SW2 | 5 | PC5 |
| SW2 | 0 | SW3 |
| SW3 | 0 | 组播服务器 （Multicast Server） |
| SW3 | 1 | SW1 |
| SW3 | 2 | SW2 |
| SW3 | 3 | 测试仪（Test Device） |

报文VLAN TAG状况如下表所示：

| 本端设备 | 对端设备 | TAG状况 |
| --- | --- | --- |
| PC1 | SW1 | untagged（pvid=123） |
| PC2 | SW1 | untagged（pvid=123） |
| SW1 | SW3 | c-tagged vid=123 |
| PC3 | SW2 | untagged（pvid=456） |
| PC4 | SW2 | untagged（pvid=456） |
| PC5 | SW2 | untagged（pvid=456） |
| SW2 | SW3 | c-tagged vid=456 |
| Multicast Server | SW3 | untagged（pvid=123） |
| Test Device | SW3 | any（pvid=1） |

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

将端口1,2的PVID设置为456

端口0的PVID仍然保持默认值1（上行报文将以vid=123的c-tagged报文发送到SW3）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 1,&vp_conf);

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

rc = kyland_vlan_port_conf_get(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

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

rc = kyland_vlan_create(inst, 456, 456)

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

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

将端口3,4,5的PVID设置为456

端口0的PVID仍然保持默认值1（上行报文将以vid=456的c-tagged报文发送到SW3）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_get(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_get(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW3配置

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

member[0] = TRUE;

member[1] = TRUE;

member[2] = TRUE;

member[3] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

将端口0的PVID设置为123

端口1,2,3的PVID仍然保持默认值1（下行报文和到测试仪的报文都带tag）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层全局配置

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x11;

rleg_common_cfg.base_address.addr[2] = 0x22;

rleg_common_cfg.base_address.addr[3] = 0x33;

rleg_common_cfg.base_address.addr[4] = 0x44;

rleg_common_cfg.base_address.addr[5] = 0x55;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 123;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 456;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建组播组，并加入L3成员

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_leaf_st leaf;

/* create mc group */

rc = kyland_mc_init(inst, 1234);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_init failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* mc group add l3 ac member */

KYLAND_OS_MEMSET(&leaf, 0, sizeof(leaf));

leaf.valid = 1;

leaf.type = leaf_type_l3_ac;

leaf.outInfo.l3ac.vport.port= 1;

leaf.outInfo.l3ac.vid = 123;

rc = kyland_mc_leaf_add(inst, group, &leaf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_leaf_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

leaf.outInfo.l3ac.vport.port= 2;

leaf.outInfo.l3ac.vid = 456;

rc = kyland_mc_leaf_add(inst, group, &leaf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_leaf_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建IPv4组播路由

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_route_entry_t route_entry;

/* add IPv4 mc route  */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_MC;

route_entry.route.ipv4_mc.key.mc_ip_addr = 0xe1000001;

route_entry.route.ipv4_mc.key.s_ip_addr = 0x06060606;

route_entry.route.ipv4_mc.action.mc_index = 1234;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

组播服务器向SW3的端口0发送三层组播报文DMAC=01-00-5e-00-00-01，SMAC=00-66-66-66-66-66，DIP=225.0.0.1，SIP=6.6.6.6，c-tagged vid=123

PC1和PC5都可以收到组播复制报文，其中：

PC1收到的报文没有进行三层替换，SMAC没有变化，ttl数值没有减1

PC2收到的报文进行了三层替换，SMAC替换为e0-11-22-33-44-55，ttl数值减1

测试仪端口没有收到相关组播报文。

删除IPv4组播路由，报文会在vlan 123中泛洪，PC1，PC2，测试仪端口都可以收到

### IPv6单播

#### 测试环境

SW1，SW2，SW3是三个以KD5886交换芯片为核心的交换机

PC1-PC5是5个网络终端设备

具体连接关系如下表所示：

| 设备名 | 端口 | 对端设备名 |
| --- | --- | --- |
| SW1 | 1 | PC1 |
| SW1 | 2 | PC2 |
| SW1 | 0 | SW3 |
| SW2 | 3 | PC3 |
| SW2 | 4 | PC4 |
| SW2 | 5 | PC5 |
| SW2 | 0 | SW3 |
| SW3 | 1 | SW1 |
| SW3 | 2 | SW2 |

报文VLAN TAG状况如下表所示：

| 本端设备 | 对端设备 | TAG状况 |
| --- | --- | --- |
| PC1 | SW1 | untagged（pvid=123） |
| PC2 | SW1 | untagged（pvid=123） |
| SW1 | SW3 | c-tagged vid=123 |
| PC3 | SW2 | untagged（pvid=456） |
| PC4 | SW2 | untagged（pvid=456） |
| PC5 | SW2 | untagged（pvid=456） |
| SW2 | SW3 | c-tagged vid=456 |

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

将端口1,2的PVID设置为123

端口0的PVID仍然保持默认值1（上行报文将以vid=123的c-tagged报文发送到SW3）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 1,&vp_conf);

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

rc = kyland_vlan_port_conf_get(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

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

rc = kyland_vlan_create(inst, 456, 456)

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

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

将端口3,4,5的PVID设置为456

端口0的PVID仍然保持默认值1（上行报文将以vid=456的c-tagged报文发送到SW3）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_get(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_get(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW3配置

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

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层全局配置

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x11;

rleg_common_cfg.base_address.addr[2] = 0x22;

rleg_common_cfg.base_address.addr[3] = 0x33;

rleg_common_cfg.base_address.addr[4] = 0x44;

rleg_common_cfg.base_address.addr[5] = 0x55;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 123;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 456;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建ARP类型NHI

u8 RT_NHI_A_MAC[6] =               {0x00, 0x11, 0x11, 0x11, 0x11, 0x23};

u8 RT_NHI_B_MAC[6] =               {0x00, 0x44, 0x44, 0x44, 0x44, 0x56};

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_next_hop_conf_t next_hop_conf;

kyland_l3_route_entry_t route_entry;

/* add nhi with arp type */

/* nhi a with outport A */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

KYLAND_OS_MEMCPY(next_hop_conf.fwd_info.mac.addr, RT_NHI_A_MAC, 6);

next_hop_conf.out_vlan = 123;

next_hop_conf.out_port.fwd_port.out_port.port_num = 1;

rc = kyland_l3_nhi_set(inst, 111, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi b with outport B */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

KYLAND_OS_MEMCPY(next_hop_conf.fwd_info.mac.addr, RT_NHI_B_MAC, 6);

next_hop_conf.out_vlan = 456;

next_hop_conf.out_port.fwd_port.out_port.port_num = 2;

rc = kyland_l3_nhi_set(inst, 222, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加IPv6单播路由

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV6_UC;

route_entry.route.ipv6_uc.key.network.address.addr[0] = 0x20;

route_entry.route.ipv6_uc.key.network.address.addr[1] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[2] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[3] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[4] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[5] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[6] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[7] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[8] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[9] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[10] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[11] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[12] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[13] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[14] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[15] = 0x01;

route_entry.route.ipv6_uc.key.network.prefix_size = 128;

route_entry.route.ipv6_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv6_uc.action.next_hop.nhi.nhi_index = 111;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV6_UC;

route_entry.route.ipv6_uc.key.network.address.addr[0] = 0x20;

route_entry.route.ipv6_uc.key.network.address.addr[1] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[2] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[3] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[4] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[5] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[6] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[7] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[8] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[9] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[10] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[11] = 0x02;

route_entry.route.ipv6_uc.key.network.address.addr[12] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[13] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[14] = 0x00;

route_entry.route.ipv6_uc.key.network.address.addr[15] = 0x03;

route_entry.route.ipv6_uc.key.network.prefix_size = 128;

route_entry.route.ipv6_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv6_uc.action.next_hop.nhi.nhi_index = 222;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

SW3上，设置vlanif 123的IP地址为2000::123

SW3上，设置vlanif 456的IP地址为2000::2:456

PC1上，设置IP6地址为2000::1，缺省网关为2000::123

PC5上，设置IP6地址为2000::2:3，缺省网关为2000::2:456

在PC1（2000::1）上ping PC5（2000::2:3），可以ping通

在PC5（2000::2:3）上ping PC1（2000::1），也可以ping通

PC1向SW1发送IP报文SIP=2000::1，DIP=2000::2:3，SMAC=00-11-11-11-11-23，DMAC=e0-11-22-33-44-55，可以到达PC2，SMAC替换为e0-11-22-33-44-55，DMAC替换为00-44-44-44-44-56，ttl数值减1

PC5向SW2发送IP报文SIP=2000::2:3，DIP=2000::1，SMAC=00-44-44-44-44-56，DMAC=e0-11-22-33-44-55，可以到达PC1，SMAC替换为e0-11-22-33-44-55，DMAC替换为00-11-11-11-11-23，ttl数值减1

### IPv6组播

#### 测试环境

SW1，SW2，SW3是三个以KD5886交换芯片为核心的交换机

PC1-PC5是5个网络终端设备

具体连接关系如下表所示：

| 设备名 | 端口 | 对端设备名 |
| --- | --- | --- |
| SW1 | 1 | PC1 |
| SW1 | 2 | PC2 |
| SW1 | 0 | SW3 |
| SW2 | 3 | PC3 |
| SW2 | 4 | PC4 |
| SW2 | 5 | PC5 |
| SW2 | 0 | SW3 |
| SW3 | 0 | 组播服务器 （Multicast Server） |
| SW3 | 1 | SW1 |
| SW3 | 2 | SW2 |
| SW3 | 3 | 测试仪（Test Device） |

报文VLAN TAG状况如下表所示：

| 本端设备 | 对端设备 | TAG状况 |
| --- | --- | --- |
| PC1 | SW1 | untagged（pvid=123） |
| PC2 | SW1 | untagged（pvid=123） |
| SW1 | SW3 | c-tagged vid=123 |
| PC3 | SW2 | untagged（pvid=456） |
| PC4 | SW2 | untagged（pvid=456） |
| PC5 | SW2 | untagged（pvid=456） |
| SW2 | SW3 | c-tagged vid=456 |
| Multicast Server | SW3 | untagged（pvid=123） |
| Test Device | SW3 | any（pvid=1） |

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

将端口1,2的PVID设置为456

端口0的PVID仍然保持默认值1（上行报文将以vid=123的c-tagged报文发送到SW3）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 1,&vp_conf);

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

rc = kyland_vlan_port_conf_get(NULL, 2,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

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

rc = kyland_vlan_create(inst, 456, 456)

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

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

将端口3,4,5的PVID设置为456

端口0的PVID仍然保持默认值1（上行报文将以vid=456的c-tagged报文发送到SW3）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 3,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_get(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 4,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_conf_get(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 456;

vp_conf.untagged_vid = 456;

rc = kyland_vlan_port_conf_set(NULL, 5,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW3配置

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

member[0] = TRUE;

member[1] = TRUE;

member[2] = TRUE;

member[3] = TRUE;

rc = kyland_vlan_port_members_set(inst, 123, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_port_members_set(inst, 456, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置端口PVID

将端口0的PVID设置为123

端口1,2,3的PVID仍然保持默认值1（下行报文和到测试仪的报文都带tag）

kyland_vlan_port_conf_t vp_conf;

rc = kyland_vlan_port_conf_get(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_get failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

vp_conf.pvid = 123;

vp_conf.untagged_vid = 123;

rc = kyland_vlan_port_conf_set(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层全局配置

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x11;

rleg_common_cfg.base_address.addr[2] = 0x22;

rleg_common_cfg.base_address.addr[3] = 0x33;

rleg_common_cfg.base_address.addr[4] = 0x44;

rleg_common_cfg.base_address.addr[5] = 0x55;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 123;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 456;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建组播组，并加入L3成员

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_leaf_st leaf;

/* create mc group */

rc = kyland_mc_init(inst, 1234);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_init failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* mc group add l3 ac member */

KYLAND_OS_MEMSET(&leaf, 0, sizeof(leaf));

leaf.valid = 1;

leaf.type = leaf_type_l3_ac;

leaf.outInfo.l3ac.vport.port= 1;

leaf.outInfo.l3ac.vid = 123;

rc = kyland_mc_leaf_add(inst, group, &leaf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_leaf_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

leaf.outInfo.l3ac.vport.port= 2;

leaf.outInfo.l3ac.vid = 456;

rc = kyland_mc_leaf_add(inst, group, &leaf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_mc_leaf_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建IPv6组播路由

/* add IPv6 mc route  */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV6_MC;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[0] = 0xff;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[1] = 0x0e;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[2] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[3] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[4] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[5] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[6] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[7] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[8] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[9] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[10] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[11] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[12] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[13] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[14] = 0x00;

route_entry.route.ipv6_mc.key.mc_ip_addr.addr[15] = 0x01;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[0] = 0x20;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[1] = 0x01;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[2] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[2] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[3] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[4] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[5] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[6] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[7] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[8] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[9] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[10] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[11] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[12] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[13] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[14] = 0x00;

route_entry.route.ipv6_mc.key.s_ip_addr.addr[15] = 0x01;

route_entry.route.ipv6_mc.action.mc_index = 1234;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

测试仪端口B模拟组播源，向SW3的端口3发送三层组播报文DMAC=01-00-5e-00-00-01，SMAC=00-66-66-66-66-66，DIP=FF0E::01，SIP=2001::1，c-tagged vid=123

PC1和PC2都可以收到组播复制报文，其中：

PC1收到的报文没有进行三层替换，SMAC没有变化，ttl数值没有减1

PC2收到的报文进行了三层替换，SMAC替换为e0-11-22-33-44-55，ttl数值减1

### FRR

#### 测试环境

端口连接关系表

| 设备端口 | 对端设备端口 | 报文TAG情况 |
| --- | --- | --- |
| PC1网口 | SW1 Port0 | untagged(pvid=111) |
| PC2网口 | SW2Port0 | untagged(pvid=222) |
| SW1 Port1 | SW3 Port0 | c-tagged vid=333 |
| SW1 Port2 | SW4 Port0 | c-tagged vid=444 |
| SW2 Port1 | SW3 Port1 | c-tagged vid=333 |
| SW2 Port2 | SW4 Port0 | c-tagged vid=444 |

VLANIF IP表

| VLANIF | 设备名称 | IP地址 |
| --- | --- | --- |
| 111 | SW1 | 1.1.1.1 |
| 222 | SW2 | 2.2.2.2 |
| 333 | SW1 | 3.3.3.1 |
| 333 | SW2 | 3.3.3.2 |
| 444 | SW1 | 4.4.4.1 |
| 444 | SW2 | 4.4.4.2 |

#### SW1配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 111, 111);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 333, 333);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 444, 444);

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

rc = kyland_vlan_port_members_set(inst, 111, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[1] = TRUE;

rc = kyland_vlan_port_members_set(inst, 333, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[2] = TRUE;

rc = kyland_vlan_port_members_set(inst, 444, member);

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

vp_conf.pvid = 111;

vp_conf.untagged_vid = 111;

rc = kyland_vlan_port_conf_set(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层mac地址

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

kyland_l3_next_hop_conf_t next_hop_conf;

kyland_l3_route_entry_t route_entry;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x11;

rleg_common_cfg.base_address.addr[2] = 0x11;

rleg_common_cfg.base_address.addr[3] = 0x11;

rleg_common_cfg.base_address.addr[4] = 0x11;

rleg_common_cfg.base_address.addr[5] = 0x11;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口VLANIF

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 111;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 333;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 444;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建ARP类型NHI

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_next_hop_conf_t next_hop_conf;

/* add nhi with arp type */

/* nhi 111 with outport 0 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0x00;

next_hop_conf.fwd_info.mac.addr[1] =0x11;

next_hop_conf.fwd_info.mac.addr[2] =0x11;

next_hop_conf.fwd_info.mac.addr[3] =0x11;

next_hop_conf.fwd_info.mac.addr[4] =0x11;

next_hop_conf.fwd_info.mac.addr[5] =0x11;

next_hop_conf.out_vlan = 111;

next_hop_conf.out_port.fwd_port.out_port.port_num = 0;

rc = kyland_l3_nhi_set(inst, 111, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 333 with outport 1 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x22;

next_hop_conf.fwd_info.mac.addr[2] =0x22;

next_hop_conf.fwd_info.mac.addr[3] =0x22;

next_hop_conf.fwd_info.mac.addr[4] =0x22;

next_hop_conf.fwd_info.mac.addr[5] =0x22;

next_hop_conf.out_vlan = 333;

next_hop_conf.out_port.fwd_port.out_port.port_num = 1;

rc = kyland_l3_nhi_set(inst, 333, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 444 backup with outport 2 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x22;

next_hop_conf.fwd_info.mac.addr[2] =0x22;

next_hop_conf.fwd_info.mac.addr[3] =0x22;

next_hop_conf.fwd_info.mac.addr[4] =0x22;

next_hop_conf.fwd_info.mac.addr[5] =0x22;

next_hop_conf.out_vlan = 444;

next_hop_conf.out_port.fwd_port.out_port.port_num = 2;

rc = kyland_l3_nhi_set(inst, 444, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置NHI保护组

kyland_l3_prot_group_conf_t prot_group_conf;

kyland_l3_prot_nhi_conf_t prot_nhi_conf;

kyland_rc rc = KYLAND_RC_OK;

/* set protect group backup nhi */

prot_nhi_conf.prot_group_index = 12;

prot_nhi_conf.backup_nh_index = 444;

rc = kyland_l3_prot_nhi_set(inst, 333, &prot_nhi_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_prot_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* set protect group status */

prot_group_conf.type =   KYLAND_L3_PRIM_PATH_TYPE_TUNNEL;

prot_group_conf.status = KYLAND_L3_PRIM_PATH_STATUS_UP;

rc = kyland_l3_prot_group_set(inst, 12, &prot_group_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_prot_group_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加IPv4单播路由

kyland_l3_route_entry_t route_entry;

kyland_rc rc = KYLAND_RC_OK;

/* add route A */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x01010100;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 111;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* add route B */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x02020200;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 333;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 切换NHI保护组状态（模拟）

kyland_inst_t inst = NULL;

kyland_l3_prot_group_conf_t prot_group_conf;

kyland_rc rc = KYLAND_RC_OK;

rc = kyland_l3_prot_group_get(inst, 12, &prot_group_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_prot_group_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* set protect group status: frr swtich to backup path or switch back */

if(KYLAND_L3_PRIM_PATH_STATUS_UP==prot_group_conf.status){

prot_group_conf.status = KYLAND_L3_PRIM_PATH_STATUS_DOWN;

}

else{

prot_group_conf.status = KYLAND_L3_PRIM_PATH_STATUS_UP;

}

rc = kyland_l3_prot_group_set(inst, 12, &prot_group_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_prot_group_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW2配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 222, 222);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 333, 333);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 444, 444);

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

rc = kyland_vlan_port_members_set(inst, 222, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[1] = TRUE;

rc = kyland_vlan_port_members_set(inst, 333, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[2] = TRUE;

rc = kyland_vlan_port_members_set(inst, 444, member);

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

vp_conf.pvid = 222;

vp_conf.untagged_vid = 222;

rc = kyland_vlan_port_conf_set(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层mac地址

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

kyland_l3_next_hop_conf_t next_hop_conf;

kyland_l3_route_entry_t route_entry;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x22;

rleg_common_cfg.base_address.addr[2] = 0x22;

rleg_common_cfg.base_address.addr[3] = 0x22;

rleg_common_cfg.base_address.addr[4] = 0x22;

rleg_common_cfg.base_address.addr[5] = 0x22;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口VLANIF

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 222;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 333;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 444;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建ARP类型NHI

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_next_hop_conf_t next_hop_conf;

/* add nhi with arp type */

/* nhi 222 with outport 0 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0x00;

next_hop_conf.fwd_info.mac.addr[1] =0x22;

next_hop_conf.fwd_info.mac.addr[2] =0x22;

next_hop_conf.fwd_info.mac.addr[3] =0x22;

next_hop_conf.fwd_info.mac.addr[4] =0x22;

next_hop_conf.fwd_info.mac.addr[5] =0x22;

next_hop_conf.out_vlan = 222;

next_hop_conf.out_port.fwd_port.out_port.port_num = 0;

rc = kyland_l3_nhi_set(inst, 222, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 333 with outport 1 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x11;

next_hop_conf.fwd_info.mac.addr[2] =0x11;

next_hop_conf.fwd_info.mac.addr[3] =0x11;

next_hop_conf.fwd_info.mac.addr[4] =0x11;

next_hop_conf.fwd_info.mac.addr[5] =0x11;

next_hop_conf.out_vlan = 333;

next_hop_conf.out_port.fwd_port.out_port.port_num = 1;

rc = kyland_l3_nhi_set(inst, 333, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 444 backup with outport 2 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x11;

next_hop_conf.fwd_info.mac.addr[2] =0x11;

next_hop_conf.fwd_info.mac.addr[3] =0x11;

next_hop_conf.fwd_info.mac.addr[4] =0x11;

next_hop_conf.fwd_info.mac.addr[5] =0x11;

next_hop_conf.out_vlan = 444;

next_hop_conf.out_port.fwd_port.out_port.port_num = 2;

rc = kyland_l3_nhi_set(inst, 444, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置NHI保护组

kyland_l3_prot_group_conf_t prot_group_conf;

kyland_l3_prot_nhi_conf_t prot_nhi_conf;

kyland_rc rc = KYLAND_RC_OK;

/* set protect group backup nhi */

prot_nhi_conf.prot_group_index = 12;

prot_nhi_conf.backup_nh_index = 444;

rc = kyland_l3_prot_nhi_set(inst, 333, &prot_nhi_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_prot_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* set protect group status */

prot_group_conf.type =   KYLAND_L3_PRIM_PATH_TYPE_TUNNEL;

prot_group_conf.status = KYLAND_L3_PRIM_PATH_STATUS_UP;

rc = kyland_l3_prot_group_set(inst, 12, &prot_group_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_prot_group_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加IPv4单播路由

kyland_l3_route_entry_t route_entry;

kyland_rc rc = KYLAND_RC_OK;

/* add route A */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x02020200;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 222;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* add route B */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x01010100;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 333;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 切换NHI保护组状态（模拟）

kyland_inst_t inst = NULL;

kyland_l3_prot_group_conf_t prot_group_conf;

kyland_rc rc = KYLAND_RC_OK;

rc = kyland_l3_prot_group_get(inst, 12, &prot_group_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_prot_group_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* set protect group status: frr swtich to backup path or switch back */

if(KYLAND_L3_PRIM_PATH_STATUS_UP==prot_group_conf.status){

prot_group_conf.status = KYLAND_L3_PRIM_PATH_STATUS_DOWN;

}

else{

prot_group_conf.status = KYLAND_L3_PRIM_PATH_STATUS_UP;

}

rc = kyland_l3_prot_group_set(inst, RT_FRR_PROTECT_GROUP, &prot_group_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_prot_group_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW3配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 333, 333);

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

rc = kyland_vlan_port_members_set(inst, 333, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW4配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 444, 444);

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

rc = kyland_vlan_port_members_set(inst, 444, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

SW1上：

设置vlanif111的IP地址为1.1.1.1

设置vlanif333的IP地址为3.3.3.1

设置vlanif444的IP地址为4.4.4.1

SW2上：

设置vlanif222的IP地址为2.2.2.2

设置vlanif333的IP地址为3.3.3.2

设置vlanif444的IP地址为4.4.4.2

SW3和SW4上

纯二层转发，不需配置IP

PC1上：

设置IP地址为1.1.1.111，缺省网关为1.1.1.1（SW1）

PC2上：

设置IP地址为2.2.2.222，缺省网关为2.2.2.2（SW2）

在PC1（1.1.1.111）上ping PC2（2.2.2.222），可以ping通

在PC2（2.2.2.222）上ping PC1（1.1.1.111），也可以ping通

PC1向SW1发送IP报文SIP=1.1.1.111，DIP=2.2.2.222，SMAC=00-11-11-11-11-11，DMAC=e0-11-11-11-11-11，可以到达PC2，SMAC替换为e0-22-22-22-22-22，DMAC替换为00-22-22-22-22-22，ttl数值减1

PC2向SW2发送IP报文SIP=2.2.2.222，DIP=1.1.1.111，SMAC=00-22-22-22-22-22，DMAC=e0-22-22-22-22-22，可以到达PC1，SMAC替换为e0-11-11-11-11-11，DMAC替换为00-11-11-11-11-23，ttl数值减1

没有切换NHI保护组状态的情况下，报文转发路径为PC1<=>SW1<=>SW3<=>SW2<=>PC2，通过查看SW1，SW2端口报文统计可以得到确认

如SW发生故障，SW1和SW2将触发保护机制，切换NHI保护组的状态，报文转发路径将变为PC1<=>SW1<=>SW4=>SW2<=>PC2，同样可以通过查看SW1，SW2端口报文统计可以得到确认

### ECMP

#### 测试环境

端口连接关系表

| 设备端口 | 对端设备端口 | 报文TAG情况 |
| --- | --- | --- |
| PC1网口 | SW1 Port0 | untagged(pvid=111) |
| PC2网口 | SW2 Port0 | untagged(pvid=222) |
| SW1 Port3 | SW3 Port1 | c-tagged vid=331 |
| SW1 Port4 | SW4 Port1 | c-tagged vid=441 |
| SW1 Port5 | SW5 Port1 | c-tagged vid=551 |
| SW2 Port3 | SW3 Port2 | c-tagged vid=332 |
| SW2 Port4 | SW4 Port2 | c-tagged vid=442 |
| SW2 Port5 | SW5 Port2 | c-tagged vid=552 |

VLANIF IP表

| VLANIF | 设备名称 | IP地址 |
| --- | --- | --- |
| 111 | SW1 | 1.1.1.1 |
| 222 | SW2 | 2.2.2.2 |
| 331 | SW1 | 3.3.1.1 |
| 331 | SW3 | 3.3.1.3 |
| 332 | SW2 | 3.3.2.2 |
| 332 | SW3 | 3.3.2.3 |
| 441 | SW1 | 4.4.1.1 |
| 441 | SW3 | 4.4.1.3 |
| 442 | SW2 | 4.4.2.2 |
| 442 | SW3 | 4.4.2.3 |
| 551 | SW1 | 5.5.1.1 |
| 551 | SW3 | 5.5.1.3 |
| 552 | SW2 | 5.5.2.2 |
| 552 | SW3 | 5.5.2.3 |

#### SW1配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 111, 111);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 331, 331);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 441, 441);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 551, 551);

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

rc = kyland_vlan_port_members_set(inst, 111, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[3] = TRUE;

rc = kyland_vlan_port_members_set(inst, 331, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[4] = TRUE;

rc = kyland_vlan_port_members_set(inst, 441, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

member[5] = TRUE;

rc = kyland_vlan_port_members_set(inst, 551, member);

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

vp_conf.pvid = 111;

vp_conf.untagged_vid = 111;

rc = kyland_vlan_port_conf_set(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层MAC地址

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x11;

rleg_common_cfg.base_address.addr[2] = 0x11;

rleg_common_cfg.base_address.addr[3] = 0x11;

rleg_common_cfg.base_address.addr[4] = 0x11;

rleg_common_cfg.base_address.addr[5] = 0x11;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口VLANIF

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 111;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 331;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 441;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 551;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建ARP类型NHI

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_next_hop_conf_t next_hop_conf;

/* add nhi with arp type */

/* nhi 111 with outport 0 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0x00;

next_hop_conf.fwd_info.mac.addr[1] =0x11;

next_hop_conf.fwd_info.mac.addr[2] =0x11;

next_hop_conf.fwd_info.mac.addr[3] =0x11;

next_hop_conf.fwd_info.mac.addr[4] =0x11;

next_hop_conf.fwd_info.mac.addr[5] =0x11;

next_hop_conf.out_vlan = 111;

next_hop_conf.out_port.fwd_port.out_port.port_num = 0;

rc = kyland_l3_nhi_set(inst, 111, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 331 with outport 3 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x33;

next_hop_conf.fwd_info.mac.addr[2] =0x33;

next_hop_conf.fwd_info.mac.addr[3] =0x33;

next_hop_conf.fwd_info.mac.addr[4] =0x33;

next_hop_conf.fwd_info.mac.addr[5] =0x33;

next_hop_conf.out_vlan = 331;

next_hop_conf.out_port.fwd_port.out_port.port_num = 3;

rc = kyland_l3_nhi_set(inst, 331, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 441 backup with outport 4 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x44;

next_hop_conf.fwd_info.mac.addr[2] =0x44;

next_hop_conf.fwd_info.mac.addr[3] =0x44;

next_hop_conf.fwd_info.mac.addr[4] =0x44;

next_hop_conf.fwd_info.mac.addr[5] =0x44;

next_hop_conf.out_vlan = 441;

next_hop_conf.out_port.fwd_port.out_port.port_num = 5;

rc = kyland_l3_nhi_set(inst, 441, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 551 backup with outport 5 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x55;

next_hop_conf.fwd_info.mac.addr[2] =0x55;

next_hop_conf.fwd_info.mac.addr[3] =0x55;

next_hop_conf.fwd_info.mac.addr[4] =0x55;

next_hop_conf.fwd_info.mac.addr[5] =0x55;

next_hop_conf.out_vlan = 551;

next_hop_conf.out_port.fwd_port.out_port.port_num = 5;

rc = kyland_l3_nhi_set(inst, 551, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置ECMP

ecmp group 12，count=3，member=331,441,551

kyland_l3_ecmp_member_conf_t member_conf[KYLAND_ECMP_GROUP_MEMBER_NUM_MAX];

member_conf[0].primary_nh_index = 331;

member_conf[1].primary_nh_index = 441;

member_conf[2].primary_nh_index = 551;

rc = kyland_l3_ecmp_set(0, 12, 3, member_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_ecmp_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加IPv4单播路由

kyland_l3_route_entry_t route_entry;

kyland_rc rc = KYLAND_RC_OK;

/* add route A */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x01010100;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 111;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* add route B */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x02020200;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.ecmp=1;

route_entry.route.ipv4_uc.action.next_hop.ecmp_group_index = 12;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW2配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 222, 222);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 332, 332);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 442, 442);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_create failed!!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rc = kyland_vlan_create(inst, 552, 552);

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

rc = kyland_vlan_port_members_set(inst, 222, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[3] = TRUE;

rc = kyland_vlan_port_members_set(inst, 332, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

KYLAND_OS_MEMSET(member, 0, sizeof(member));

member[4] = TRUE;

rc = kyland_vlan_port_members_set(inst, 442, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

member[5] = TRUE;

rc = kyland_vlan_port_members_set(inst, 552, member);

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

vp_conf.pvid = 222;

vp_conf.untagged_vid = 222;

rc = kyland_vlan_port_conf_set(NULL, 0,&vp_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_conf_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层MAC地址

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x22;

rleg_common_cfg.base_address.addr[2] = 0x22;

rleg_common_cfg.base_address.addr[3] = 0x22;

rleg_common_cfg.base_address.addr[4] = 0x22;

rleg_common_cfg.base_address.addr[5] = 0x22;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口VLANIF

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 222;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 332;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 442;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 552;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建ARP类型NHI

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_next_hop_conf_t next_hop_conf;

/* add nhi with arp type */

/* nhi 222 with outport 0 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0x00;

next_hop_conf.fwd_info.mac.addr[1] =0x22;

next_hop_conf.fwd_info.mac.addr[2] =0x22;

next_hop_conf.fwd_info.mac.addr[3] =0x22;

next_hop_conf.fwd_info.mac.addr[4] =0x22;

next_hop_conf.fwd_info.mac.addr[5] =0x22;

next_hop_conf.out_vlan = 222;

next_hop_conf.out_port.fwd_port.out_port.port_num = 0;

rc = kyland_l3_nhi_set(inst, 222, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 332 with outport 3 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x33;

next_hop_conf.fwd_info.mac.addr[2] =0x33;

next_hop_conf.fwd_info.mac.addr[3] =0x33;

next_hop_conf.fwd_info.mac.addr[4] =0x33;

next_hop_conf.fwd_info.mac.addr[5] =0x33;

next_hop_conf.out_vlan = 332;

next_hop_conf.out_port.fwd_port.out_port.port_num = 3;

rc = kyland_l3_nhi_set(inst, 332, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 442 backup with outport 4 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x44;

next_hop_conf.fwd_info.mac.addr[2] =0x44;

next_hop_conf.fwd_info.mac.addr[3] =0x44;

next_hop_conf.fwd_info.mac.addr[4] =0x44;

next_hop_conf.fwd_info.mac.addr[5] =0x44;

next_hop_conf.out_vlan = 442;

next_hop_conf.out_port.fwd_port.out_port.port_num = 4;

rc = kyland_l3_nhi_set(inst, 442, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 552 backup with outport 5 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x55;

next_hop_conf.fwd_info.mac.addr[2] =0x55;

next_hop_conf.fwd_info.mac.addr[3] =0x55;

next_hop_conf.fwd_info.mac.addr[4] =0x55;

next_hop_conf.fwd_info.mac.addr[5] =0x55;

next_hop_conf.out_vlan = 552;

next_hop_conf.out_port.fwd_port.out_port.port_num = 5;

rc = kyland_l3_nhi_set(inst, 552, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置ECMP

ecmp group 12，count=3，member=332,442,552

kyland_l3_ecmp_member_conf_t member_conf[KYLAND_ECMP_GROUP_MEMBER_NUM_MAX];

member_conf[0].primary_nh_index = 332;

member_conf[1].primary_nh_index = 442;

member_conf[2].primary_nh_index = 552;

rc = kyland_l3_ecmp_set(0, 12, 3, member_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_ecmp_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加IPv4单播路由

kyland_l3_route_entry_t route_entry;

kyland_rc rc = KYLAND_RC_OK;

/* add route A */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x02020200;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 222;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* add route B */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x01010100;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.ecmp=1;

route_entry.route.ipv4_uc.action.next_hop.ecmp_group_index = 12;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW3配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 333, 333);

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

rc = kyland_vlan_port_members_set(inst, 333, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层MAC地址

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x33;

rleg_common_cfg.base_address.addr[2] = 0x33;

rleg_common_cfg.base_address.addr[3] = 0x33;

rleg_common_cfg.base_address.addr[4] = 0x33;

rleg_common_cfg.base_address.addr[5] = 0x33;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口VLANIF

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 331;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 332;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建ARP类型NHI

NHI 111：vlan=331，mac=e0-11-11-11-11-11，port=1

NHI 222：vlan=332，mac= e0-22-22-22-22-22，port=2

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_next_hop_conf_t next_hop_conf;

/* add nhi with arp type */

/* nhi 111 with outport 1 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x11;

next_hop_conf.fwd_info.mac.addr[2] =0x11;

next_hop_conf.fwd_info.mac.addr[3] =0x11;

next_hop_conf.fwd_info.mac.addr[4] =0x11;

next_hop_conf.fwd_info.mac.addr[5] =0x11;

next_hop_conf.out_vlan = 331;

next_hop_conf.out_port.fwd_port.out_port.port_num = 1;

rc = kyland_l3_nhi_set(inst, 111, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 222 with outport 2 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x22;

next_hop_conf.fwd_info.mac.addr[2] =0x22;

next_hop_conf.fwd_info.mac.addr[3] =0x22;

next_hop_conf.fwd_info.mac.addr[4] =0x22;

next_hop_conf.fwd_info.mac.addr[5] =0x22;

next_hop_conf.out_vlan = 332;

next_hop_conf.out_port.fwd_port.out_port.port_num = 2;

rc = kyland_l3_nhi_set(inst, 222, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加IPv4单播路由

kyland_l3_route_entry_t route_entry;

kyland_rc rc = KYLAND_RC_OK;

/* add route A */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x01010100;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 111;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* add route B */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x02020200;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 222;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW4配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 444, 444);

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

rc = kyland_vlan_port_members_set(inst, 444, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层MAC地址

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x44;

rleg_common_cfg.base_address.addr[2] = 0x44;

rleg_common_cfg.base_address.addr[3] = 0x44;

rleg_common_cfg.base_address.addr[4] = 0x44;

rleg_common_cfg.base_address.addr[5] = 0x44;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口VLANIF

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 441;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 442;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建ARP类型NHI

NHI 111：vlan=441，mac=e0-11-11-11-11-11，port=1

NHI 222：vlan=442，mac= e0-22-22-22-22-22，port=2

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_next_hop_conf_t next_hop_conf;

/* add nhi with arp type */

/* nhi 111 with outport 1 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x11;

next_hop_conf.fwd_info.mac.addr[2] =0x11;

next_hop_conf.fwd_info.mac.addr[3] =0x11;

next_hop_conf.fwd_info.mac.addr[4] =0x11;

next_hop_conf.fwd_info.mac.addr[5] =0x11;

next_hop_conf.out_vlan = 441;

next_hop_conf.out_port.fwd_port.out_port.port_num = 1;

rc = kyland_l3_nhi_set(inst, 111, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 222 with outport 2 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x22;

next_hop_conf.fwd_info.mac.addr[2] =0x22;

next_hop_conf.fwd_info.mac.addr[3] =0x22;

next_hop_conf.fwd_info.mac.addr[4] =0x22;

next_hop_conf.fwd_info.mac.addr[5] =0x22;

next_hop_conf.out_vlan = 442;

next_hop_conf.out_port.fwd_port.out_port.port_num = 2;

rc = kyland_l3_nhi_set(inst, 222, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加IPv4单播路由

kyland_l3_route_entry_t route_entry;

kyland_rc rc = KYLAND_RC_OK;

/* add route A */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x01010100;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 111;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* add route B */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x02020200;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 222;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### SW5配置

#### 创建VLAN

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

/* create vlan */

rc = kyland_vlan_create(inst, 555, 555);

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

rc = kyland_vlan_port_members_set(inst, 555, member);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_vlan_port_members_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 设置三层MAC地址

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_rleg_common_conf_t rleg_common_cfg;

/* set global mac */

rleg_common_cfg.rleg_mode = KYLAND_ROUTING_RLEG_MAC_MODE_SINGLE;

rleg_common_cfg.base_address.addr[0] = 0xe0;

rleg_common_cfg.base_address.addr[1] = 0x55;

rleg_common_cfg.base_address.addr[2] = 0x55;

rleg_common_cfg.base_address.addr[3] = 0x55;

rleg_common_cfg.base_address.addr[4] = 0x55;

rleg_common_cfg.base_address.addr[5] = 0x55;

rc = kyland_l3_rleg_common_set(inst, &rleg_common_cfg);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_common_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建三层接口VLANIF

kyland_l3_rleg_conf_t rleg_conf;

/* add vlanif */

KYLAND_OS_MEMSET(&rleg_conf, 0, sizeof(rleg_conf));

rleg_conf.ipv4_unicast_enable = TRUE;

rleg_conf.ipv4_multicast_enable = TRUE;

rleg_conf.ipv6_unicast_enable = TRUE;

rleg_conf.ipv6_multicast_enable = TRUE;

rleg_conf.mpls_uc_enable= TRUE;

rleg_conf.mpls_mc_enable = TRUE;

rleg_conf.ipv4_mtu = 1500;

rleg_conf.ipv6_mtu = 1500;

rleg_conf.ipv4mc_limit_ttl = 10;

rleg_conf.ipv6mc_limit_ttl = 10;

rleg_conf.vlan = 551;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

rleg_conf.vlan = 552;

rc = kyland_l3_rleg_add(inst, &rleg_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_rleg_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 创建ARP类型NHI

NHI 111：vlan=551，mac=e0-11-11-11-11-11，port=1

NHI 222：vlan=552，mac= e0-22-22-22-22-22，port=2

kyland_inst_t inst = NULL;

kyland_rc rc = KYLAND_RC_OK;

kyland_l3_next_hop_conf_t next_hop_conf;

/* add nhi with arp type */

/* nhi 111 with outport 1 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x11;

next_hop_conf.fwd_info.mac.addr[2] =0x11;

next_hop_conf.fwd_info.mac.addr[3] =0x11;

next_hop_conf.fwd_info.mac.addr[4] =0x11;

next_hop_conf.fwd_info.mac.addr[5] =0x11;

next_hop_conf.out_vlan = 551;

next_hop_conf.out_port.fwd_port.out_port.port_num = 1;

rc = kyland_l3_nhi_set(inst, 111, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* nhi 222 with outport 2 */

KYLAND_OS_MEMSET(&next_hop_conf, 0, sizeof(next_hop_conf));

next_hop_conf.fwd_cmd = KYLAND_L3_NH_FWD_CMD_ARP;

next_hop_conf.fwd_info.mac.addr[0] =0xe0;

next_hop_conf.fwd_info.mac.addr[1] =0x22;

next_hop_conf.fwd_info.mac.addr[2] =0x22;

next_hop_conf.fwd_info.mac.addr[3] =0x22;

next_hop_conf.fwd_info.mac.addr[4] =0x22;

next_hop_conf.fwd_info.mac.addr[5] =0x22;

next_hop_conf.out_vlan = 552;

next_hop_conf.out_port.fwd_port.out_port.port_num = 2;

rc = kyland_l3_nhi_set(inst, 222, &next_hop_conf);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_nhi_set failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 添加IPv4单播路由

kyland_l3_route_entry_t route_entry;

kyland_rc rc = KYLAND_RC_OK;

/* add route A */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x01010100;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 111;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

/* add route B */

KYLAND_OS_MEMSET(&route_entry, 0, sizeof(route_entry));

route_entry.type = KYLAND_L3_ROUTE_ENTRY_TYPE_IPV4_UC;

route_entry.route.ipv4_uc.key.network.address = 0x02020200;

route_entry.route.ipv4_uc.key.network.prefix_size = 24;

route_entry.route.ipv4_uc.key.lookup_type = KYLAND_ROUTE_LOOKUP_TYPE_BOTH;

route_entry.route.ipv4_uc.action.next_hop.nhi.nhi_index = 222;

rc = kyland_l3_route_entry_add(inst, &route_entry);

if(KYLAND_RC_OK != rc){

KYLAND_E("\r\n call kyland_l3_route_entry_add failed !!! rc=%d \r\n ",rc);

return KYLAND_RC_ERROR;

}

#### 流量测试

PC1上：

设置IP地址为1.1.1.111，缺省网关为1.1.1.1（SW1）

PC2上：

设置IP地址为2.2.2.222，缺省网关为2.2.2.2（SW2）

SW1上：

设置VLANIF 111的IP地址为1.1.1.1

设置VLANIF 331的IP地址为3.3.1.1

设置VLANIF 441的IP地址为4.4.1.1

设置VLANIF 551的IP地址为5.5.1.1

SW2上：

设置VLANIF 222的IP地址为2.2.2.2

设置VLANIF 332的IP地址为3.3.2.2

设置VLANIF 442的IP地址为4.4.2.2

设置VLANIF 552的IP地址为5.5.2.2

SW3上：

设置VLANIF 331的IP地址为3.3.1.3

设置VLANIF 332的IP地址为3.3.2.3

SW4上：

设置VLANIF 441的IP地址为4.4.1.3

设置VLANIF 442的IP地址为4.4.2.3

SW5上：

设置VLANIF 551的IP地址为5.5.1.3

设置VLANIF 552的IP地址为5.5.2.3

在PC1（1.1.1.111）上ping PC2（2.2.2.222），可以ping通

在PC2（2.2.2.222）上ping PC1（1.1.1.111），也可以ping通

PC1向SW1发送IPv4已知单播报文：SIP=1.1.1.111，DIP=2.2.2.222，SMAC=00-11-11-11-11-11，DMAC=e0-11-11-11-11-11，DPORT=2222，SPORT=1111，可以到达PC2，SMAC替换为e0-22-22-22-22-22，DMAC替换为00-22-22-22-22-22，ttl数值减1

PC2向SW2发送IPv4已知单播报文：SIP=2.2.2.222，DIP=1.1.1.111，SMAC=00-22-22-22-22-22，DMAC=e0-22-22-22-22-22，DPORT=1111，SPORT=2222，可以到达PC1，SMAC替换为e0-11-11-11-11-11，DMAC替换为00-11-11-11-11-23，ttl数值减1

此时报文转发路径通过SW1，SW2，SW3三者之一

PC1：

将报文SPORT改为1111-1122循环12个，报文则在三条路径上负载分担

将报文DPORT改为2222-2233循环12个，报文也在三条路径上负载分担

PC2：

将报文SPORT改为2222-2233循环12个，报文则在三条路径上负载分担

将报文DPORT改为1111-1122循环12个，报文也在三条路径上负载分担

## 芯片实现

### 总体流程

报文转发总体流程如上图所示，转发类型分为以下几类：

二层转发（L2 Forwarding）

三层单播转发（IP Unicast）

三层组播转发（IP Multicast）

MPLS转发（MPLS）

协议报文重定向到CPU（Redirect to CPU）

### 三层单播转发流程

IP Unicast转发处理流程如上图所示

### 三层组播转发流程

IP Multicast转发处理流程如上图所示
