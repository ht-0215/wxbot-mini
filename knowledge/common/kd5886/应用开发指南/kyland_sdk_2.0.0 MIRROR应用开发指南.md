# kyland_sdk_2.0.0 MIRROR应用开发指南

kyland_sdk_2.0.0

MIRROR应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 MIRROR概述	4

2 芯片支持	5

3 应用简介	6

3.1 源端口镜像	6

3.2 目的端口镜像	6

3.3 Vlan镜像	6

3.4 远程镜像	7

3.5 To cpu镜像	7

3.6 Acl镜像	7

4 SDK API及应用示例	8

4.1 SDK API	8

4.1.1 MIRROR PROBE配置接口	8

4.1.2 MIRROR MONITOR PORT配置接口	12

4.1.3 MIRROR PORT配置接口	14

4.2 应用示例	15

4.2.1 源端口镜像	15

4.2.2 目的端口镜像	17

4.2.3 vlan镜像	18

4.2.4 远程镜像	19

4.2.5 to cpu镜像	21

4.2.6 acl镜像	22

# MIRROR概述

端口镜像功能是指交换机把某一个端口接收或发送的数据帧完全相同的复制给另一个端口；其中被复制的端口称为镜像源端口，复制的端口称为镜像目的端口。通常在镜像目的端口处连接一个协议分析仪（如Sniffer）或者RMON监测仪，可以监视和管理网络，并且能诊断网络故障。

# 芯片支持

支持基于VLAN/VSI/MAC表/ACL使能MIRROR

支持3组探针配置（报文最多MIRROR一份流量，不能同时MIRROR多份流量）

支持基于探针配置入口或出口MIRROR，MIRROR的目的端口

支持基于探针配置被MIRROR报文的源端口或目的端口、VLAN和MAC表是否配置MIRROR

支持基于探针配置toCPU报文的MIRROR

支持基于探针配置远程MIRROR(在MIRROR的报文前添加一个可配置的VLAN)

每组探针支持2个观察端口

# 应用简介

## 源端口镜像

对流入镜像端口的报文进行镜像。

## 目的端口镜像

对从镜像端口上流出的报文进行镜像

## Vlan镜像

镜像端口所在的vlan使能mirror，则对该vlan的报文进行镜像。例如镜像端口在vlan1和vlan2中，vlan1使能mirror，vlan2不使能mirror，vlan1的报文可以镜像到观察端口，vlan2的报文不会镜像。

## 远程镜像

当使能远程镜像时，会在镜像报文前添加一个用户可配置的vlan

## To cpu镜像

对上送cpu的报文进行镜像。

## Acl镜像

根据用户配置的策略，将符合规则的报文进行镜像

# SDK API及应用示例

## SDK API

### MIRROR PROBE配置接口

#### 功能简介

支持3个mirror探针配置，基于探针的vlan mirror/remote mirror/mc tx mirror/mirror direction配置。

#### 接口及参数描述

/**

* \brief get mirror_probe cfg

*

* \param inst [IN] 				Target instance reference

* \param mirror_porbe [IN] 		probe number

* \param mirror_probe_cfg [OUT]	probe setup structure

*

* \return Return code

**/
kyland_rc kyland_mirror_probe_get(const kyland_inst_t inst,

kyland_mirror_probe_t mirror_porbe,

kyland_mirror_probe_cfg_t *mirror_probe);

/**

* \brief set mirror_probe cfg

*

* \param inst [IN] 				Target instance reference

* \param mirror_porbe [IN] 		probe number

* \param mirror_probe_cfg [IN]		probe setup structure

*

* \return Return code

**/

kyland_rc kyland_mirror_probe_cfg(const kyland_inst_t inst,

kyland_mirror_probe_t mirror_porbe,

kyland_mirror_probe_cfg_t *mirror_probe);​
​

#### 相关数据结构

typedef enum{

KYLAND_MIRROR_TAG_NONE,

KYLAND_MIRROR_TAG_C,

KYLAND_MIRROR_TAG_S,

KYLAND_MIRROR_TAG_S_CUSTOM

}kyland_mirror_tag_t;

typedef enum{

KYLAND_MIRROR_PROBE_1,	/**< mirror probe 1 */

KYLAND_MIRROR_PROBE_2,	/**< mirror probe 2 */

KYLAND_MIRROR_PROBE_3,	/**< mirror probe 3 */

}kyland_mirror_probe_t;

typedef enum{

KYLAND_PROBE_VLAN_MODE_NONE,	/**< no vlan mirror */

KYLAND_PROBE_VLAN_MODE_VLAN,	/**< mirror only traffic in vlans with vlan table mirror bit set */

KYLAND_PROBE_VLAN_MODE_PROBE,	/**< mirror only traffic in the probe vid is mirror*/

KYLAND_PROBE_VLAN_MODE_VSI,	/**< mirror only traffic in the probe vsi is mirror*/

}kyland_probe_vlan_mode_t;

typedef struct{

kyland_probe_vlan_mode_t probe_vlan_mode;	/**< vlan mirror mode */

kyland_vid_t vid;			/**< vid */

}kyland_vlan_mirror_cfg_t;

typedef struct{

ucBool remote_mirror_ena;		/**< remote mirror enable */

kyland_mirror_tag_t tag;			/**< mirror tag type */

kyland_vid_t vid;			/**< mirror tag vid */

kyland_tagprio_t pcp;			/**< mirror tag pcp */

kyland_dei_t dei;			/**< mirror tag dei */

}kyland_remote_mirror_cfg_t;

typedef enum{

KYLAND_PROBE_DIRECTION_NONE,	/**< not mirror */

KYLAND_PROBE_DIRECTION_TX,	/**< probe dirction is TX */

KYLAND_PROBE_DIRECTION_RX,	/**< probe dirction is RX */

KYLAND_PROBE_DIRECTION_RX_AND_TX,/**< probe dirction is RX and TX */

}kyland_probe_direction_t;

typedef struct{

ucBool cpu_port_mirror[8];		/**< to cpu mirror enable */

kyland_vlan_mirror_cfg_t vlan_mirror;	/**< vlan mirror */

kyland_remote_mirror_cfg_t remote_mirror;	/**< remote mirror */

kyland_probe_direction_t probe_dirction;	/**< probe dirction */

}kyland_mirror_probe_cfg_t;

### MIRROR MONITOR PORT配置接口

#### 功能简介

Mirror端口配置，支持两个镜像目的端口。

#### 接口及参数描述

/**

* \brief get monitor port

*

* \param inst [IN] 		Target instance reference

* \param mirror_porbe [IN] probe number

* \param port_no [OUT] 	port number

*

* \return Return code

**/
kyland_rc  kyland_mirror_monitor_port_get(const kyland_inst_t inst,

kyland_mirror_probe_t  mirror_porbe,

kyland_monitor_port_cfg_t  *conf);

/**

* \brief set monitor port

*

* \param inst [IN] 		Target instance reference

* \param mirror_porbe [IN] probe number

* \param port_no [IN] 	port number

*

* \return Return code

**/

kyland_rc kyland_mirror_monitor_port_cfg(const kyland_inst_t inst,

kyland_mirror_probe_t mirror_porbe,

kyland_monitor_port_cfg_t *conf);

#### 相关数据结构

typedef struct{

kyland_port_t port1;	/**< monitor port 1*/

kyland_port_t port2;	/**< monitor port 2*/

}kyland_monitor_port_cfg_t;

### MIRROR PORT配置接口

#### 功能简介

mirror源端口配置。

#### 接口及参数描述

/**

* \brief get mirror port

*

* \param inst [IN] 		Target instance reference

* \param mirror_porbe [IN] probe number

* \param member [OUT] 		port member

*

* \return Return code

**/
kyland_rc kyland_mirror _port_get(const kyland_inst_t inst,

kyland_mirror_probe_t mirror_porbe,

ucBool member[KYLAND_PORT_ARRAY_SIZE]);

/**

* \brief set mirror port

*

* \param inst [IN] 		Target instance reference

* \param mirror_porbe [IN] probe number

* \param member [IN] 		port member

*

* \return Return code

**/

kyland_rc kyland_mirror _port_cfg(const kyland_inst_t inst,

kyland_mirror_probe_t mirror_porbe,

ucBool member[KYLAND_PORT_ARRAY_SIZE]);​

#### 相关数据结构

ucBool member；

## 应用示例

### 源端口镜像

Port1进入的报文镜像到port10

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_mirror_probe_t probe;

kyland_mirror_probe_cfg_t probe_conf;

probe = 0;

KYLAND_RC(kyland_mirror_probe_get(inst, probe, &conf));

probe_conf.probe_dirction = KYLAND_PROBE_DIRECTION_RX;

probe_conf.vlan_mirror.probe_vlan_mode = KYLAND_PROBE_VLAN_MODE_NONE;

KYLAND_RC(kyland_mirror_probe_cfg(inst, probe, & probe_conf));

ucBool member[KYLAND_PORT_ARRAY_SIZE] = {0};

member[1] = 1;

KYLAND_RC(kyland_mirror_port_cfg(inst, probe, member));

kyland_monitor_port_cfg_t conf;

conf.port1 = 10;

conf.port2 = KYLAND_INVALID_MONITOR_PORT;

KYLAND_RC(kyland_mirror_monitor_port_cfg(inst, probe, &conf));

### 目的端口镜像

从Port1发出的报文镜像到port10

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_mirror_probe_t probe;

kyland_mirror_probe_cfg_t probe_conf;

probe = 0;

KYLAND_RC(kyland_mirror_probe_get(inst, probe, &conf));

probe_conf.probe_dirction = KYLAND_PROBE_DIRECTION_TX;

probe_conf.vlan_mirror.probe_vlan_mode = KYLAND_PROBE_VLAN_MODE_NONE;

KYLAND_RC(kyland_mirror_probe_cfg(inst, probe, & probe_conf));

ucBool member[KYLAND_PORT_ARRAY_SIZE] = {0};

member[1] = 1;

KYLAND_RC(kyland_mirror_port_cfg(inst, probe, member));

kyland_monitor_port_cfg_t conf;

conf.port1 = 10;

conf.port2 = KYLAND_INVALID_MONITOR_PORT;

KYLAND_RC(kyland_mirror_monitor_port_cfg(inst, probe, &conf));

### vlan镜像

Port1进入的vlan1的报文镜像到port10

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_mirror_probe_t probe;

kyland_mirror_probe_cfg_t probe_conf;

probe = 0;

KYLAND_RC(kyland_mirror_probe_get(inst, probe, &conf));

probe_conf.probe_dirction = KYLAND_PROBE_DIRECTION_RX;

probe_conf.vlan_mirror.probe_vlan_mode = KYLAND_PROBE_VLAN_MODE_VLAN;

KYLAND_RC(kyland_mirror_probe_cfg(inst, probe, & probe_conf));

ucBool member[KYLAND_PORT_ARRAY_SIZE] = {0};

member[1] = 1;

KYLAND_RC(kyland_mirror_port_cfg(inst, probe, member));

kyland_monitor_port_cfg_t conf;

conf.port1 = 10;

conf.port2 = KYLAND_INVALID_MONITOR_PORT;

KYLAND_RC(kyland_mirror_monitor_port_cfg(inst, probe, &conf));

kyland_vlan_vid_conf_t vid_conf;

u32 vid = 1;

kyland_vlan_vid_conf_get(inst, vid, &vid_conf);

vid_conf.mirror = 1;

kyland_vlan_vid_conf_set(inst, vid, &vid_conf);

### 远程镜像

Port1进入的报文镜像到port10，镜像报文添加一个vid=100，prio=1，cfi=0的vlan

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_mirror_probe_t probe;

kyland_mirror_probe_cfg_t probe_conf;

probe = 0;

KYLAND_RC(kyland_mirror_probe_get(inst, probe, &conf));

probe_conf.probe_dirction = KYLAND_PROBE_DIRECTION_RX;

probe_conf.vlan_mirror.probe_vlan_mode = KYLAND_PROBE_VLAN_MODE_NONE;

probe_conf.remote_mirror.remote_mirror_ena = 1;

probe_conf.remote_mirror.tag = KYLAND_MIRROR_TAG_TYPE_C;

probe_conf.remote_mirror.vid = 100;

probe_conf.remote_mirror.pcp = 1;

probe_conf.remote_mirror.dei = 0;

KYLAND_RC(kyland_mirror_probe_cfg(inst, probe, & probe_conf));

ucBool member[KYLAND_PORT_ARRAY_SIZE] = {0};

member[1] = 1;

KYLAND_RC(kyland_mirror_port_cfg(inst, probe, member));

kyland_monitor_port_cfg_t conf;

conf.port1 = 10;

conf.port2 = KYLAND_INVALID_MONITOR_PORT;

KYLAND_RC(kyland_mirror_monitor_port_cfg(inst, probe, &conf));

### to cpu镜像

送cpu4号队列的报文镜像到port10。

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_mirror_probe_t probe;

kyland_mirror_probe_cfg_t probe_conf;

probe = 0;

KYLAND_RC(kyland_mirror_probe_get(inst, probe, &conf));

probe_conf.probe_dirction = KYLAND_PROBE_DIRECTION_TX;

probe_conf.vlan_mirror.probe_vlan_mode = KYLAND_PROBE_VLAN_MODE_NONE;

conf.cpu_port_mirror[4] = 1;

KYLAND_RC(kyland_mirror_probe_cfg(inst, probe, & probe_conf));

ucBool member[KYLAND_PORT_ARRAY_SIZE] = {0};

member[1] = 1;

KYLAND_RC(kyland_mirror_port_cfg(inst, probe, member));

kyland_monitor_port_cfg_t conf;

conf.port1 = 10;

conf.port2 = KYLAND_INVALID_MONITOR_PORT;

KYLAND_RC(kyland_mirror_monitor_port_cfg(inst, probe, &conf));

### acl镜像

添加ACL，index=100，key为sip=1.1.1.1、dip=20.20.20.20、proto=6、sport=123、dport=456，action为重定向mirror。匹配这条规则的报文镜像到port10。

kyland_rc kd5886_ip_tcp_entry_acl_add()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = param[0];

conf.acl_key.type = KYLAND_ACL_TYPE_IPV4;

conf.acl_key.first = KYLAND_ACE_BIT_1;

conf.acl_key.dmac_bc = KYLAND_ACE_BIT_ANY;

conf.acl_key.dmac_mc = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.cfi = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.tagged = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.usr_prio.mask = 0;

conf.acl_key.vlan.vid.mask = 0;

conf.acl_key.frame.ipv4.sip.value = 0x01010101;

conf.acl_key.frame.ipv4.sip.mask = 0xffffffff;

conf.acl_key.frame.ipv4.dip.value = 0x14141414;

conf.acl_key.frame.ipv4.dip.mask = 0xffffffff;

conf.acl_key.frame.ipv4.sport.low = 123;

conf.acl_key.frame.ipv4.sport.high = 123;

conf.acl_key.frame.ipv4.sport.in_range = 0;

conf.acl_key.frame.ipv4.dport.low = 456;

conf.acl_key.frame.ipv4.dport.high = 456;

conf.acl_key.frame.ipv4.dport.in_range = 0;

conf.acl_key.frame.ipv4.proto.value = 6;

conf.acl_key.frame.ipv4.proto.mask = 0xff;

conf.acl_action.forward = 1;

conf.acl_action.rt = 1;

conf.acl_action.mirror_id = 1;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_mirror_probe_t probe;

kyland_mirror_probe_cfg_t probe_conf;

probe = 0;

KYLAND_RC(kyland_mirror_probe_get(inst, probe, &conf));

probe_conf.probe_dirction = KYLAND_PROBE_DIRECTION_RX;

probe_conf.vlan_mirror.probe_vlan_mode = KYLAND_PROBE_VLAN_MODE_NONE;

KYLAND_RC(kyland_mirror_probe_cfg(inst, probe, & probe_conf));

kyland_monitor_port_cfg_t conf;

conf.port1 = 10;

conf.port2 = KYLAND_INVALID_MONITOR_PORT;

KYLAND_RC(kyland_mirror_monitor_port_cfg(inst, probe, &conf));
