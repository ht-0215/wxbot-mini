# kyland_sdk_2.0.0 QOS应用开发指南

kyland_sdk_2.0.0

QOS应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 Qos概述	5

2 芯片支持	6

3 应用简介	7

3.1 流量分类	7

3.1.1 802.1p优先级	7

3.1.2 IP优先级和DSCP优先级	7

3.1.3 MPLS EXP优先级	8

3.1.4 MPLS DiffServ模型	8

3.1.5 芯片实现	9

3.2 拥塞管理	10

3.3 拥塞避免	10

3.3.1 队尾丢弃	10

3.3.2 wred	11

3.4 流量整形	12

3.5 流量监管	12

3.5.1 port policer	12

3.5.2 queue policer	13

3.5.3 acl policer	13

3.5.4 service policer	14

4 SDK API及应用示例	16

4.1 SDK API	16

4.1.1 QOS 802.1p配置相关接口	16

4.1.2 QOS DSCP配置相关接口	18

4.1.3 QOS MPLS配置相关接口	21

4.1.4 QOS PORT相关接口	26

4.1.5 PORT&PRIO POLICER相关接口	31

4.1.6 ISDX POLICER相关接口	33

4.1.7 ACL POLICER相关接口	36

4.2 应用示例	39

4.2.1 802.1p	39

4.2.2 DSCP	41

4.2.3 MPLS	43

4.2.4 拥塞管理	44

4.2.5 拥塞避免	46

4.2.6 流量整形	46

4.2.7 流量监管	47

# Qos概述

QoS（Quality of Service）即服务质量。对于网络业务，影响服务质量的因素包括传输的带宽、传送的时延、数据的丢包率等。在网络中可以通过保证传输的带宽、降低传送的时延、降低数据的丢包率以及时延抖动等措施来提高服务质量。

网络资源总是有限的，只要存在抢夺网络资源的情况，就会出现服务质量的要求。服务质量是相对网络业务而言的，在保证某类业务的服务质量的同时，可能就是在损害其它业务的服务质量。例如，在网络总带宽固定的情况下，如果某类业务占用的带宽越多，那么其他业务能使用的带宽就越少，可能会影响其他业务的使用。因此，网络管理者需要根据各种业务的特点来对网络资源进行合理的规划和分配，从而使网络资源得到高效利用。

QoS技术提供了下述功能：

流分类：采用一定的规则识别符合某类特征的报文，它是对网络业务进行区分服务的前提和基础。

流量监管：对进入或流出设备的特定流量进行监管，以保护网络资源不受损害。

流量整形：一种主动调整流的输出速率的流量控制措施，用来使流量适配下游设备可供给的网络资源，避免不必要的报文丢弃。

拥塞管理：当拥塞发生时制定一个资源的调度策略，决定报文转发的处理次序。

拥塞避免：监督网络资源的使用情况，当发现拥塞有加剧的趋势时采取主动丢弃报文的策略，通过调整队列长度来解除网络的过载。

# 芯片支持

支持每端口8个QoS优先级队列，Strict/Deficit DWRR调度

支持4个丢弃优先级/QoS队列

支持拥塞避免，每个QoS队列的多个丢弃优先级进行WRED操作

支持片上48Mb的数据报文缓存

支持服务等级QoS简单流分类，可查找L2~L4报文信息

支持复杂流分类，可匹配L2~L5报文流特征（>9元组）

支持上行或下行DSCP映射

支持基于QoS分类与丢弃优先级的DSCP重标记

支持上行或下行VLAN（PCP、DEI、VID）映射

支持基于QoS分类与丢弃优先级的PCP/DEI重标记

支持基于队列与端口的策略与整形，步长100000 bps可编程

# 应用简介

## 流量分类

### 802.1p优先级

802.1Q标签头包含了2 个字节的TPID（Tag Protocol Identifier，标签协议标识符）和2个字节的TCI（Tag Control Information，标签控制信息），Priority字段就是802.1p优先级。 在MEF业务场景中，Priority字段被定义为PCP,CFI字段被定义为DEI。

### IP优先级和DSCP优先级

IP报文头的ToS字段有8 个bit，其中前3 个bit表示的就是IP优先级，取值范围为0～ 7。RFC 2474 中，重新定义了IP报文头部的ToS域，称之为DS（Differentiated Services，差分服 务）域，其中DSCP优先级用该域的前6 位（0～5 位）表示，取值范围为0～63，后2 位（6、7 位）是保留位。

### MPLS EXP优先级

EXP 优先级位于MPLS 标签内，用于标记MPLS QoS, 长度为3 比特，取值范围为0～7。

### MPLS DiffServ模型

L-lsp/e-lsp : L-lsp基于lsp标识优先级(cos)，通过exp映射丢弃优先级(dp) E-lsp基于exp标识优先级(cos),通过car等测量丢弃优先级(dp,颜色) Uniform/pipe/short pipe: Uniform : 信任用户报文优先级(vlan/ip优先级),入口映射到mpls优先级exp，出口exp映射回报文优先级 Pipe : 不信任用户优先级，mpls优先级exp通过配置来设置，出口exp也不映射到报文优先级 Short pipe : 与Pipe处理一致，差异在于出口PE上，使用用户报文优先级做调度

Figure 47 MPLS Uniform模型

Figure 48 MPLS Pipe 模型

Figure 49 MPLS Short-Pipe 模型

### 芯片实现

入口配置：

1. 基于物理端口配置trust 802.1p/trust dscp,可配置信任外层tag 或内层tag 的802.1p

2. Mpls 基于lsp 配置uniform/pipe/short pipe 和l-lsp/e-lsp

3. 基于DSCP 全局映射表配置DSCP 是否映射到cos+dp 和映射到新的DSCP。

4. DSCP 全局一个映射表(一个domain)；802.1p 每端口有一个映射表(每端口一个domain)；MPLS 基于LSP 配置，共8 个映射表

5. 对于IP 报文，信任DSCP 的优先级高于信任802.1p

6. 对于MPLS 报文，信任EXP 的优先级高于信任802.1p

• 出口配置：

1. 基于物理端口配置remark 802.1p/dscp, 基于port+vlan/qinq 配置remark 802.1p,可配置remark 两层vlan 的802.1p

2. Mpls 基于lsp 配置uniform/pipe/short pipe 和l-lsp/e-lsp

3. 支持上行/下行REMARK DSCP（通过dscp 索引而不是内部qos）

4. 支持上行/下行基于PORT+VLAN/QINQ 设置802.1p+dei

5. 可以通过S1 实现多个domain,可以使用PAG 的一部分来代表domain,S1 代表映射表（配置比简单映射表更灵活）

## 拥塞管理

sp队列

sp队列为严格优先级队列。在调度时，SP 严格按照优先级从高到低的次序优先发送较高优先级队列中的分组，当较高优先级队列为空时，再发送较低优先级队列中的分组。

dwrr队列调度

DWRR 队列在队列之间进行轮流调度，保证每个队列都得到一定的服务时间。DWRR 可为每个队列配置一个权重，按照权重的比例分配每个队列的带宽。

sp+dwrr队列调度

SP队列按照严格优先级调度，DWRR队列按照权重比例分配剩余带宽。

## 拥塞避免

### 队尾丢弃

当队列的长度达到最大值后，所有新到来的报文都将被丢弃。这种丢弃策略会引发 TCP 全局同步现象：当队列同时丢弃多个TCP 连接的报文时，将造成多个TCP连接同时进入拥塞避免和慢启动状态以降低并调整流量，而后又会在某个时间同时出现流量高峰。如此反复，使网络流量忽大忽小，网络不停震荡。

### wred

为避免TCP 全局同步现象，可使用RED 或WRED。

RED 和WRED 通过随机丢弃报文避免了TCP 的全局同步现象，使得当某个TCP 连接的报文被丢弃、开始减速发送的时候，其他的TCP 连接仍然有较高的发送速度。这样，无论什么时候，总有TCP 连接在进行较快的发送，提高了线路带宽的利用率。

在 RED 类算法中，为每个队列都设定上限和下限，对队列中的报文进行如下处理：

• 当队列的长度小于下限时，不丢弃报文；

• 当队列的长度在上限和下限之间时，设备按用户配置的丢弃概率随机丢弃到来的报文。

• 当队列的长度超过上限时，丢弃所有到来的报文；

直接采用队列的长度和上限、下限比较并进行丢弃，将会对突发性的数据流造成不公正的待遇，不

利于数据流的传输。WRED 采用平均队列和设置的队列上限、下限比较来确定丢弃的概率。

队列平均长度既反映了队列的变化趋势，又对队列长度的突发变化不敏感，避免了对突发性数据流的不公正待遇。

DP-1/2/3的包：

队列平均深度小于MinTh时不丢包，队列平均深度超过MaxTh时全丢弃。

在MinTh和MaxTh之间时对应一个丢弃概率P。

## 流量整形

流量整形是一种主动调整流量输出速率的措施，其作用是限制流量与突发，使这类报文以比较均匀的速率向外发送。流量整形通常使用缓冲区和令牌桶来完成，当报文的发送速度过快时，首先在缓冲区进行缓存，在令牌桶的控制下，再均匀地发送这些被缓冲的报文。

当下游设备的接口速率小于上游设备的接口速率或发生突发流量，在下游设备接口处可能出现流量拥塞的情况，此时用户可以通过在上游设备的接口出方向配置流量整形，将上游不规整的流量进行削峰填谷，输出一条比较平整的流量，从而解决下游设备的拥塞问题。

KD5886支持基于端口和队列的流量整形。

## 流量监管

流量监管就是对流量进行控制，通过监督进入网络的流量速率，对超出部分的流量进行“惩罚”，使进入的流量被限制在一个合理的范围之内，从而保护网络资源和企业网用户的利益。

### port policer

Port policer采用单漏桶实现，每个端口有4个策略组可用于测量不同类型报文的流量。

支持特性

支持流控模式

支持pps模式。

四组漏桶可以针对不同类型的报文进行测量，可选的报文类型如下：

多播报文

广播报文

单播报文

泛洪报文

发往CPU不同队列的报文（共8个队列）

用于二层学习的报文

每组漏桶可以对上述类型报文中的一种或多种进行测量

四组漏桶之间可以采用串行模式或并行模式，串行模式即四组漏桶之中只要有一组漏桶关闭则报文不再进入其他漏桶进行统计，并行模式下报文是否被统计只与本漏桶的开关状态有关。

### queue policer

每个队列都支持policer配置，对这个队列的所有流量进行测量。

### acl policer

通过ACL来进行流的匹配，对匹配到的流进行流量监管。ACL policer采用双漏桶方案实现。支持32个policer模板，1024个实例。

支持特性：

支持色盲模式，在进行测量时不对输入报文的DP等级进行区分

色敏模式，在进行测量时根据输入报文的DP等级采用不同的漏桶进行测量。色敏模式下又分为关联模式和非关联模式。

非关联模式：

当输入报文DP等级为绿色且CIR桶不满时，报文只消耗CIR桶中的令牌并且不改变报文的DP等级；

当输入报文DP等级为绿色且CIR桶满时，报文消耗EIR桶中的令牌且报文被标记为黄色（根据配置提升DP等级）；

当输入报文DP等级为绿色且CIR桶和EIR桶都满时，报文默认被丢弃。

当输入报文为黄色时，报文只能消耗EIR桶中的令牌，如果CIR桶不满则不改变报文的DP等级，如果CIR桶满且EIR桶不满则增加报文丢弃等级，如果EIR桶满或者两个桶都满报文将默认被丢弃。

关联模式：

当输入报文为绿色报文且CIR桶不满时，会同时消耗CIR桶和EIR桶的流量，报文DP等级不会被修改。

当输入报文为绿色报文且CIR桶已满且EIR桶不满时，报文消耗EIR桶的流量且报文被标记为黄色（根据配置提升DP等级）；

当输入报文DP等级为绿色且CIR桶和EIR桶都满时，报文默认被丢弃。

当输入报文为黄色时，报文只能消耗EIR桶中的令牌，如果CIR桶不满则不改变报文的DP等级，如果CIR桶满且EIR桶不满则增加报文丢弃等级，如果EIR桶满或者两个桶都满报文将默认被丢弃。

关联模式和非关联模式在报文丢弃行为上一致，在扣桶时不一致。扣桶区别在关联模式在CIR桶不满扣桶时会同时对EIR进行扣桶，而非关联模式则是CIR和EIR分别扣桶，没有关联关系。

支持基于car动作remark qos、remark dp、remark dscp。

### service policer

对一个服务实例进行流量监管。ACL policer采用双漏桶方案实现。支持4096个实例。

支持特性：

支持色盲模式，在进行测量时不对输入报文的DP等级进行区分

色敏模式，在进行测量时根据输入报文的DP等级采用不同的漏桶进行测量。色敏模式下又分为关联模式和非关联模式。

非关联模式：

当输入报文DP等级为绿色且CIR桶不满时，报文只消耗CIR桶中的令牌并且不改变报文的DP等级；

当输入报文DP等级为绿色且CIR桶满时，报文消耗EIR桶中的令牌且报文被标记为黄色（根据配置提升DP等级）；

当输入报文DP等级为绿色且CIR桶和EIR桶都满时，报文默认被丢弃。

当输入报文为黄色时，报文只能消耗EIR桶中的令牌，如果CIR桶不满则不改变报文的DP等级，如果CIR桶满且EIR桶不满则增加报文丢弃等级，如果EIR桶满或者两个桶都满报文将默认被丢弃。

关联模式：

当输入报文为绿色报文且CIR桶不满时，会同时消耗CIR桶和EIR桶的流量，报文DP等级不会被修改。

当输入报文为绿色报文且CIR桶已满且EIR桶不满时，报文消耗EIR桶的流量且报文被标记为黄色（根据配置提升DP等级）；

当输入报文DP等级为绿色且CIR桶和EIR桶都满时，报文默认被丢弃。

当输入报文为黄色时，报文只能消耗EIR桶中的令牌，如果CIR桶不满则不改变报文的DP等级，如果CIR桶满且EIR桶不满则增加报文丢弃等级，如果EIR桶满或者两个桶都满报文将默认被丢弃。

关联模式和非关联模式在报文丢弃行为上一致，在扣桶时不一致。扣桶区别在关联模式在CIR桶不满扣桶时会同时对EIR进行扣桶，而非关联模式则是CIR和EIR分别扣桶，没有关联关系。

支持基于car动作remark qos、remark dp、remark dscp。

# SDK API及应用示例

## SDK API

### QOS 802.1p配置相关接口

#### 功能简介

802.1p相关特性配置，基于端口配置入口default qos、default dp、trust qos和trust dp，基于port+pcp/dei做cos/dp映射，出口封装vlan tag时可以根据端口default pcp/dei做封装、基于port+cos/dp做pcp/dei映射来进行封装、使用ES0的配置做封装、根据入口pcp/dei做封装。

#### 接口及参数描述

/**

* \brief get 802.1p cfg

*

* \param inst [IN] 	  	Target instance reference

* \param port [IN]	  	port number

* \param qos_cfg [OUT] 	802.1p setup structure

*

* \return Return code

**/
kyland_rc kyland_qos_8021p_get(const kyland_inst_t inst,

kyland_port_t port,

kyland_8021p_cfg_t *qos_cfg);

/**

* \brief set 802.1p cfg

*

* \param inst [IN] 	  	Target instance reference

* \param port [IN]	      	port number

* \param qos_cfg [IN]    	802.1p setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_8021p_cfg(const kyland_inst_t inst,

kyland_port_t port,

kyland_8021p_cfg_t *qos_cfg);

#### 相关数据结构

typedef enum{

KYLAND_TAG_REMARK_MODE_CLASSIFIED,

KYLAND_TAG_REMARK_MODE_ES0,

KYLAND_TAG_REMARK_MODE_DEFAULT,

KYLAND_TAG_REMARK_MODE_MAPPDE,

}kyland_tag_remark_mode_t;

typedef struct{

ucBool 		tag_class_ena;

/**< Ingress classification of QoS class and DP level based PCP and DEI */

kyland_cos_t 	default_cos;	/**< default port priority */

kyland_dp_level_t 	default_dp;	/**< default port dp level */

kyland_pcp_t 	default_pcp;		/**< default pcp value for ingress port */

kyland_dei_t 	default_dei;		/**< default dei value for ingress port */

kyland_cos_t 	qos_class_map[KYLAND_PCP_ARRAY_SIZE][KYLAND_DEI_ARRAY_SIZE];

/**< ingress mapping for tagged frames from pcp and dei to qos class */

kyland_dp_level_t  	dp_level_map[KYLAND_PCP_ARRAY_SIZE][KYLAND_DEI_ARRAY_SIZE];

/**< ingress mapping for tagged frames from pcp and dei to dp level */

kyland_tag_remark_mode_t	remark_mode;/**< egress tag remark mode */

kyland_pcp_t tag_		default_pcp;	/**< default pcp value for egress port */

kyland_dei_t tag_		default_dei;	/**< default dei value for egress port */

kyland_pcp_t 		pcp_map[KYLAND_PRIO_ARRAY_SIZE][2];

/**< egress mapping form qos class and (1 bit)dp level to pcp */

kyland_dei_t 		dei_map[KYLAND_PRIO_ARRAY_SIZE][2];

/**< egress mapping form qos class and (1 bit)dp level to dei */

}kyland_8021p_cfg_t;

### QOS DSCP配置相关接口

#### 功能简介

IP 报文qos配置。基于端口的dscp qos/dp使能，dscp translate使能，dscp remap使能等。基于dscp全局配置，包括基于dscp的trust  dscp、dscp映射cos/dp、

translate  dscp、出口remap dscp。

#### 接口及参数描述

/**

* \brief get dscp cfg

*

* \param inst [IN] 	  	Target instance reference

* \param dscp_cfg [OUT]  	dscp setup structure

*

* \return Return code

**/
kyland_rc kyland_qos_dscp_get(const kyland_inst_t inst,

kyland_dscp_cfg_t *dscp_cfg);

/**

* \brief set dscp cfg

*

* \param inst [IN] 	  	Target instance reference

* \param dscp_cfg [IN]	  	dscp setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_dscp_cfg(const kyland_inst_t inst,

kyland_dscp_cfg_t *dscp_cfg);​

/**

* \brief get port dscp cfg

*

* \param inst [IN] 	  	Target instance reference

* \param port [IN] 	  	port number

* \param dscp_cfg [OUT]	port dscp setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_port_dscp_get(const kyland_inst_t inst,

kyland_port_t port,

kyland_port_dscp_cfg_t *port_dscp_cfg);

/**

* \brief set port dscp cfg

*

* \param inst [IN] 	  	Target instance reference

* \param port [IN] 	  	port number

* \param dscp_cfg [IN]	  	port dscp setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_port_dscp_cfg(const kyland_inst_t inst,

kyland_port_t port,

kyland_port_dscp_cfg_t *port_dscp_cfg);

#### 相关数据结构

typedef struct{

ucBool 		dscp_trust[64];	/**< trust dscp */

kyland_prio_t 	dscp_class_map[64];	/**< mapping from dscp to qos class */

kyland_dp_level_t 	dscp_dp_map[64];	/**< mapping from dscp to dp level */

kyland_dscp_t 	dscp_qos_map[KYLAND_PRIO_ARRAY_SIZE];

/**< mapping from qos class to dscp */

ucBool 		dscp_remark[64];	/**< dscp remark enable */

kyland_dscp_t 	dscp_translate_map[64];	/**< translate dscp value */

kyland_dscp_t 	dscp_remap[64];	/**< remap one dscp to another */

}kyland_dscp_cfg_t;

typedef enum{

KYLAND_DSCP_MODE_NONE,	/**< dscp not remark */

KYLAND_DSCP_MODE_ZERO,	/**< dscp vlaue zero remark */

KYLAND_MODE_MODE_SEL,	/**< dscp value selected above(dscp_remark) are remarked */

KYLAND_DSCP_MODE_ALL,	/**< dscp remarked for all values */

}kyland_dscp_mode_t;

typedef enum

{

KYLAND_DSCP_EMODE_DISABLE,   	/**< DSCP not remarked */

KYLAND_DSCP_EMODE_REMARK,    /**< DSCP remarked with DSCP value from analyzer */

KYLAND_DSCP_EMODE_REMAP,

/**< DSCP remarked with DSCP value from analyzer remapped through global remap table  */

} kyland_dscp_emode_t;

typedef struct{

ucBool 		dscp_class_ena;		/**< dscp to qos class enable */

ucBool 		dscp_dp_ena;		/**< dscp to dp level enable */

ucBool 		dscp_translate;		/**< dscp translate enable */

ucBool 		dscp_keep_ena;		/**< dscp keep enable */

kyland_dscp_mode_t 	dscp_mode;			/**< dscp mode */

kyland_dscp_emode_t 	dscp_emode; 		/**< Egress DSCP mode */

}kyland_port_dscp_cfg_t;

### QOS MPLS配置相关接口

#### 功能简介

Mpls qos配置。支持dscp remark，支持入口e-lsp模式基于domain(3)+exp(3)做cos/dp分类和l-lsp模式基于domain(3)+exp(3)映射dp level。支持出口e-lsp模式domain(3)+cos(3)和l-lsp模式domain(3)+dp(2)映射EXP做封装。

#### 接口及参数描述

/**

* \brief get exp to qos map

*

* \param inst [IN] 	  	Target instance reference

* \param domain [IN] 	  	domain(support 8 domain)

* \param mpls_map [OUT]  	exp to qos map setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_mpls_map_get(const kyland_inst_t inst,

kyland_domain_t domain,

kyland_qos_mpls_map_t *mpls_map);

/**

* \brief set exp to qos map

*

* \param inst [IN] 	  	Target instance reference

* \param domain [IN] 	  	domain(support 8 domain)

* \param mpls_map [IN]	exp to qos map setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_mpls_map_cfg(const kyland_inst_t inst,

kyland_domain_t domain,

kyland_qos_mpls_map_t *mpls_map);

/**

* \brief get cos to qos map

*

* \param inst [IN] 		Target instance reference

* \param cos [IN] 	    	prio

* \param dscp [OUT]		dscp

*

* \return Return code

**/

kyland_rc kyland_qos_mpls_dscp_map_get(const kyland_inst_t inst,

kyland_qos_mpls_dscp_map_t *map);

/**

* \brief set cos to qos map

*

* \param inst [IN] 		Target instance reference

* \param cos [IN] 	    	prio

* \param dscp [IN]	    	dscp

*

* \return Return code

**/

kyland_rc kyland_qos_mpls_dscp_map_cfg(const kyland_inst_t inst,

kyland_qos_mpls_dscp_map_t *map);

/**

* \brief get elsp qos to exp map

*

* \param inst [IN] 		Target instance reference

* \param domain [IN] 		domain(support 8 domain)

* \param qos_elsp_map [OUT]	cos to exp map setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_elsp_map_get(const kyland_inst_t inst,

kyland_domain_t domain,

kyland_qos_elsp_map_t *qos_elsp_map);

/**

* \brief set elsp qos to exp map

*

* \param inst [IN] 		Target instance reference

* \param domain [IN] 		domain(support 8 domain)

* \param qos_elsp_map [IN]	cos to exp map setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_elsp_map_cfg(const kyland_inst_t inst,

kyland_domain_t domain,

kyland_qos_elsp_map_t *qos_elsp_map);

/**

* \brief get llsp qos to exp map

*

* \param inst [IN] 		Target instance reference

* \param domain [IN] 		domain(support 8 domain)

* \param qos_llsp_map [OUT]	dp to exp map setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_llsp_map_get(const kyland_inst_t inst,

kyland_domain_t domain,

kyland_qos_llsp_map_t *qos_llsp_map);

/**

* \brief set llsp qos to exp map

*

* \param inst [IN] 		Target instance reference

* \param domain [IN] 		domain(support 8 domain)

* \param qos_llsp_map [OUT]	dp to exp map setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_llsp_map_cfg(const kyland_inst_t inst,

kyland_domain_t domain,

kyland_qos_llsp_map_t *qos_llsp_map);​

#### 相关数据结构

typedef struct{

kyland_cos_t 	cos[KYLAND_EXP_ARRAY_SIZE];/**< mapping exp to qos class */

kyland_dp_level_t 	dp[KYLAND_EXP_ARRAY_SIZE]; /**< mapping exp to dp level */

}kyland_qos_mpls_map_t;

typedef struct{

kyland_exp_t 	exp[KYLAND_PRIO_ARRAY_SIZE];/**< mapping qos class to exp */

}kyland_qos_elsp_map_t;

typedef struct{

kyland_exp_t 	exp[KYLAND_DP_ARRAY_SIZE];	/**< mapping dp level to exp */

}kyland_qos_llsp_map_t;

typedef struct{

kyland_dscp_t dscp[KYLAND_PRIO_ARRAY_SIZE]; 	/**< mapping qos class to dscp */

}kyland_qos_mpls_dscp_map_t;

### QOS PORT相关接口

#### 功能简介

Qos port配置接口。基于端口的shaper，wred配置。基于端口下8个队列的shaper，wred，sp/dwrr/sp+dwrr调度配置。支持32个shaper模板的配置，1k个wred模板配置。

#### 接口及参数描述

/**

* \brief get qos port cfg

*

* \param inst [IN] 		Target instance reference

* \param port [IN] 		port number

* \param qos_port_cfg [OUT]	qos port setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_port_get(const kyland_inst_t inst,

kyland_port_t port,

kyland_qos_port_cfg_t qos_port_cfg);

/**

* \brief set qos port cfg

*

* \param inst [IN] 		Target instance reference

* \param port [IN] 		port number

* \param qos_port_cfg [IN]	qos port setup structure

*

* \return Return code

**/

kyland_rc kyland_qos_port_cfg(const kyland_inst_t inst,

kyland_port_t port,

kyland_qos_port_cfg_t qos_port_cfg);

/**

* \brief get wred template

*

* \param inst [IN]      	Target instance reference

* \param wred_id [IN]   	wred template id(1k)

* \param wred_cfg [OUT]  	wred setup structure

*

* \return Return code

**/

kyland_rc kyland_wred_template_get(const kyland_inst_t inst,

kyland_wred_t wred_id,

kyland_wred_cfg_t *wred_cfg);

/**

* \brief set wred template

*

* \param inst [IN]      	Target instance reference

* \param wred_id [IN]   	wred template id(1k)

* \param wred_cfg [IN]  	wred setup structure

*

* \return Return code

**/

kyland_rc kyland_wred_template_add(const kyland_inst_t inst,

kyland_wred_t wred_id,

kyland_wred_cfg_t *wred_cfg);

/**

* \brief update wred template

*

* \param inst [IN]      	Target instance reference

* \param wred_id [IN]   	wred template id(1k)

* \param wred_cfg [IN]  	wred setup structure

*

* \return Return code

**/

kyland_rc kyland_wred_template_update(const kyland_inst_t inst,

kyland_wred_template_t wred_id,

kyland_wred_cfg_t *wred_cfg);

/**

* \brief del wred template

*

* \param inst [IN]      	Target instance reference

* \param wred_id [IN]   	wred template id(1k)

* \param wred_cfg [IN]  	wred setup structure

*

* \return Return code

**/

kyland_rc kyland_wred_template_del(const kyland_inst_t inst, kyland_wred_template_t wred_id);

/**

* \brief get shaper template

*

* \param inst [IN]        	Target instance reference

* \param shaper_id [IN]   	shaper template id(32)

* \param shaper_cfg [OUT] 	shaper setup structure

*

* \return Return code

**/

kyland_rc kyland_shaper_template_get(const kyland_inst_t inst,

kyland_shaper_template_t shaper_id,

kyland_shaper_cfg_t *shaper_cfg);

/**

* \brief get shaper template

*

* \param inst [IN]        	Target instance reference

* \param shaper_id [IN]   	shaper template id(32)

* \param shaper_cfg [IN]  	shaper setup structure

*

* \return Return code

**/

kyland_rc kyland_shaper_template_cfg(const kyland_inst_t inst,

kyland_shaper_template_t shaper_id,

kyland_shaper_cfg_t *shaper_cfg);
​

#### 相关数据结构

typedef struct{

ucBool 		dwrr_ena;		/**< queue dwrr enable */

kyland_weight_t	weight;		/**< queue dwrr weight */

kyland_shaper_t 	shaper;		/**< queue shaper */

kyland_wred_t 	wred;		/**< queue wred */

}kyland_qos_queue_cfg_t;

typedef struct{

kyland_shaper_t 	shaper;			/**< port shaper */

kyland_wred_t 	wred;			/**< port wred */

kyland_qos_queue_cfg_t qos_queue_cfg[8];	/**< queue cfg */

}kyland_qos_port_cfg_t;

typedef struct

{

ucBool 		enable;	/**< enable/disable wred */

kyland_pct_t 	max_th;	/**< maximum threshold */

kyland_pct_t 	min_th;	/**< minimum threshold */

kyland_pct_t 	max_prob_1;/**< drop probability at max_th for drop precedence level 1 */

kyland_pct_t	max_prob_2;/**< drop probability at max_th for drop precedence level 2 */

kyland_pct_t 	max_prob_3;/**< drop probability at max_th for drop precedence level 3 */

}kyland_wred_cfg_t;

typedef struct

{

kyland_burst_level_t 	level;	/**< cbs(committed burst size).	unit:bytes */

kyland_bitrate_t	rate;	/**< cir(committed information rate).	unit:kbps */

}kyland_shaper_cfg_t;

### PORT&PRIO POLICER相关接口

#### 功能介绍

端口及每个端口下8个优先级的policer配置。每个端口4个策略组policer配置，可用于测量不同的报文类型。支持基于端口policer流控，基于端口配置帧速率模式。

#### 接口及参数描述

/**

* \brief get port policer cfg

*

* \param inst [IN] 	       	Target instance reference

* \param port_no [IN]	       	port number

* \param port_pol_cfg [OUT]   	policer setup structure

*

* \return Return code

**/
kyland_rc kyland_port_pol_get(const kyland_inst_t inst,

kyland_port_t port_no,

kyland_port_pol_cfg_t port_pol_cfg);

/**

* \brief set port policer cfg

*

* \param inst [IN] 	       	Target instance reference

* \param port_no [IN]	       	port number

* \param port_pol_cfg [IN]    	policer setup structure

*

* \return Return code

**/

kyland_rc kyland_port_pol_cfg(const kyland_inst_t inst,

kyland_port_t port_no,

kyland_port_pol_cfg_t port_pol_cfg);

#### 相关数据结构

typedef struct{

kyland_burst_level_t 	level;	/**< burst level 	unit:bytes */

kyland_bitrate_t 	rate;	/**< rate 		unit:kbps*/

}kyland_policer_cfg_t;

typedef struct{

ucBool 	frame_rate;	/**< measure rates in feames per seconds instead of bits per second */

kyland_dp_level_t 	dp_bypass_level;	/**< drop predence bypass level */

ucBool 	unicast;		/**< unicast frames are policed */

ucBool 	multicast;		/**< multicast frames are policed */

ucBool 	broadcast;		/**< broadcast frames are policed */

ucBool 	uc_no_flood;	/**< exclude flooding unicast frames(if unicast is set) */

ucBool 	mc_no_flood;	/**< exclude flooding multicast frames(if multicast is set) */

ucBool 	unknow_uc_flood;	/**< unknow uc */

ucBool 	unknow_mc_flood;	/**< unknow mc */

ucBool 	flooded;		/**< flooded frames are policed */

ucBool 	learning;		/**< learning frames are policed */

ucBool 	to_cpu;		/**< frames to the cpu are policed */

ucBool 	cpu_queue[KYLAND_PORT_POLICER_CPU_QUEUES];	/**< enable each individual cpu queue(if to cpu set) */

ucBool 	limit_noncpu_traffic;	/**< remove the front ports from the destination set for a policed frame */

ucBool 	limit_cpu_traffic;	/**< remove the cpu ports from the destination set for a policed frame */

ucBool 	flow_control;	/**< flow control is enable */

}kyland_policer_ext_cfg_t;

typedef struct{

ucBool 			enable;	/**<enable/disable policer */

kyland_policer_cfg_t 		port_pol_cfg[KYLAND_PORT_POLICERS];/**< ingress port policers */

kyland_policer_ext_cfg_t   	port_pol_ext_cfg[KYLAND_PORT_POLICERS];	/**< ingress port policers extension*/

kyland_policer_cfg_t 		queue_pol_cfg[8];	/**< ingress queue policers */

}kyland_port_pol_cfg_t;

### ISDX POLICER相关接口

#### 功能介绍

ISDX policer配置。双漏桶配置模型，支持色盲模式与色敏模式，色敏模式下可配置关联模式与非关联模式。支持基于car结果配置remark cos/dp/dscp。

#### 接口及参数描述

/**

* \brief get isdx policer cfg

*

* \param inst [IN]      	Target instance reference

* \param pol_id [IN]    	policer id

* \param pol_cfg [OUT]  	policer setup structure

*

* \return Return code

**/
kyland_rc kyland_ivport_policer_get(const kyland_inst_t inst,

kyland_pol_t pol_id,

kyland_ivport_pol_cfg_t *pol_cfg);

/**

* \brief set isdx policer cfg

*

* \param inst [IN]      	Target instance reference

* \param pol_id [IN]    	policer id

* \param pol_cfg [IN]   	policer setup structure

*

* \return Return code

**/

kyland_rc kyland_ivport_policer_cfg(const kyland_inst_t inst,

kyland_pol_t pol_id,

kyland_ivport_pol_cfg_t *pol_cfg);

#### 相关数据结构

typedef enum{

KYLAND_TIMESCALE_LVL_1,	/**< up to 10Gbps rates with 8192 kbps granularity */

KYLAND_TIMESCALE_LVL_2,	/**< up to 2Gbps rates with 1024 kbps granularity */

KYLAND_TIMESCALE_LVL_3,	/**< up to 200Mbps rates with 128 kbps granularity */

KYLAND_TIMESCALE_LVL_4,	/**< up to 32Mbps rates with 16 kbps granularity */

}kyland_timescale_t;

typedef enum{

KYLAND_CIR_INC_DP_NONE,	/**< dp is not increased */

KYLAND_CIR_INC_DP_1,	/**< dp for green traffic is increased with 1 */

KYLAND_CIR_INC_DP_2,	/**< dp for green traffic is increased with 2 */

KYLAND_CIR_INC_DP_3,	/**< dp for green traffic is increased with 3 */

}kyland_cir_inc_dp_val_t;

typedef enum{

KYLAND_AWARE_DP_0,	/**< dp=0 is green and dp>0 is yellow */

KYLAND_AWARE_DP_1,	/**< dp<=1 is green and dp>1 is yellow */

KYLAND_AWARE_DP_2,	/**< dp<=2 is green and dp>2 is yellow */

KYLAND_COLOR_BLINDNESS_MODE,	/**< green */

}kyland_dp_aware_lvl_t;

typedef struct{

ucBool 	action_ena;		/**< car action enable */

ucBool 	drop_ena;		/**< drop/pass */

ucBool 	updata_dscp_ena;	/**< enable/disable updata dscp */

u32 	dscp_val;		/**< dscp value */

ucBool 	updata_qos_ena;	/**< enable/disable updata qos */

u32 	qos_val;		/**< qos value */

ucBool 	updata_dp_ena;	/**< enable/disable updata dp */

u32 	dp_val;		/**< dp value */

}kyland_transmit_action_t;

typedef struct{

ucBool 		enable;	/**< enable/disable policer */

kyland_timescale_t 	timescale;	/**< configuration of the leaky bucket scale to enable from

16kbps up to 10Gbps rates*/

u32	cir;	/**< cir */

u32	cbs;	/**< cbs */

u32 	pir;	/**< pir */

u32 	pbs;	/**< pbs */

//u32 	gap_val;	/**< gap value */

kyland_cir_inc_dp_val_t 	inc_dp_val;	/**< DP for green traffic is increased with n when CIR is exceeded */

kyland_dp_aware_lvl_t 		dp_aware_lvl;/**< color sensitivity and color blindness */

ucBool 			coupling_ena;/**< enable/disable coupling */

kyland_transmit_action_t 	yellow_action;/**< yellow frame action */

kyland_transmit_action_t	green_action;/**< green frame action */

kyland_transmit_action_t 	red_action;	/**< red frame action */

}kyland_ivport_pol_cfg_t;

### ACL POLICER相关接口

#### 功能介绍

ACL policer配置。双漏桶配置模型，支持色盲模式与色敏模式，色敏模式下可配置关联模式与非关联模式。支持基于car结果配置remark cos/dp/dscp。支持32个policer模板配置，1024个规则实例配置。

#### 接口及参数描述

/**

* \brief get acl policer template

*

* \param inst [IN]               	Target instance reference

* \param pol_template_id [IN]    	policer template id

* \param pol_template_cfg [OUT]  policer template setup structure

*

* \return Return code

**/
kyland_rc kyland_acl_pol_template_get(const kyland_inst_t inst,

kyland_pol_template_t pol_template_id,

kyland_acl_pol_template_cfg_t *pol_template_cfg);

/**

* \brief set acl policer template

*

* \param inst [IN] 		Target instance reference

* \param pol_template_id [IN]	policer template id

* \param pol_template_cfg [OUT]  policer template setup structure

*

* \return Return code

**/

kyland_rc kyland_acl_pol_template_cfg(const kyland_inst_t inst,

kyland_pol_template_t pol_template_id,

kyland_acl_pol_template_cfg_t *pol_template_cfg);​

/**

* \brief get acl policer cfg

*

* \param inst [IN] 	  	Target instance reference

* \param pol_id [IN]	  	policer id

* \param pol_cfg [OUT]   	policer setup structure

*

* \return Return code

**/

kyland_rc kyland_acl_policer_get(const kyland_inst_t inst,

kyland_pol_t pol_id,

kyland_acl_pol_cfg_t *pol_cfg);

/**

* \brief set acl policer cfg

*

* \param inst [IN] 	  	Target instance reference

* \param pol_id [IN]	  	policer id

* \param pol_cfg [IN]    	policer setup structure

*

* \return Return code

**/

kyland_rc kyland_acl_policer_cfg(const kyland_inst_t inst,

kyland_pol_t pol_id,

kyland_acl_pol_cfg_t *pol_cfg);

#### 相关数据结构

typedef struct{

ucBool 		enable;	/**< enable/disable policer */

kyland_timescale_t 	timescale;	/**< configuration of the leaky bucket scale to enable from 16kbps up to 10Gbps rates*/

u32 	cir;	/**< cir */

u32	cbs;	/**< cbs */

u32 	pir;	/**< pir */

u32 	pbs;	/**< pbs */

u32 	gap_val;	/**< gap value */

kyland_cir_inc_dp_val_t 	inc_dp_val;	/**< dp for green traffic is increased with n */

kyland_dp_aware_lvl_t 		dp_aware_lvl;/**< color sensitivity and color blindness */

ucBool 			coupling_ena;/**< enable/disable coupling */

}kyland_acl_pol_template_cfg_t;

typedef struct{

u32 			pol_template_id;	/**< policer template id */

kyland_transmit_action_t	yellow_action;	/**< yellow frame action */

kyland_transmit_action_t	green_action;	/**< green frame action */

kyland_transmit_action_t	red_action;		/**< red frame action */

}kyland_acl_pol_cfg_t;

## 应用示例

### 802.1p

API使用说明：

kyland_qos_8021p_cfg用于配置802.1p的qos分类和remark。

入口qos分类：

端口默认分类

default cos/default dp为端口默认分类，当其他分类使能为0时，所有报文都会根据这个结果进行入队。

基于vlan tag分类

配置tag_class_ena=1后会根据qos_class_map和dp_level_map的配置来映射cos和dp。

出口remark：

出口通过remark_mode的配置决定pcp/dei的封装方式。

remark_mode= KYLAND_TAG_REMARK_MODE_CLASSIFIED时

根据上行remark的pcp/dei值封装

remark_mode=KYLAND_TAG_REMARK_MODE_ES0时

根据ES0的配置封装

remark_mode=KYLAND_TAG_REMARK_MODE_DEFAULT时

根据default pcp/default dei的配置封装

remark_mode=KYLAND_TAG_REMARK_MODE_MAPPED时

根据pcp_map/dei_map的配置做封装

示例：

入口配置tag_class_ena=1，根据tag pcp/dei查qos_class_map和dp_level_map决定qos分类结果。出口remark_mode= KYLAND_TAG_REMARK_MODE_MAPPED，通过cos/dp查pcp_map和dei_map做封装。

kyland_rc kd5886_8021p_qos_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_port_t port;

u32 pcp, dei, cos, de;

kyland_8021p_cfg_t conf;

port = 1;

conf.tag_class_ena = 1;

conf.default_cos = 0;

conf.default_dp = 0;

for(pcp = 0; pcp > 8; pcp++){

for(dei = 0; dei < 2; dei++){

conf.dp_level_map[pcp][dei] = dei;

conf.qos_class_map[pcp][dei] = pcp;

}

}

conf.remark_mode = KYLAND_TAG_REMARK_MODE_MAPPED;

conf.tag_default_pcp = 0;

conf.tag_default_dei = 0;

for(cos = 0; cos < 8; cos++){

for(de = 0; de < 2; de++){

conf.pcp_map[cos][de] = cos;

conf.dei_map[cos][de] = de;

}

}

KYLAND_RC(kyland_qos_8021p_cfg(inst, port, &conf));

return rc;

}

### DSCP

API使用说明：

kyland_qos_port_dscp_cfg配置端口的dscp分类使能、translate_ena、keep_ena、remark_mode。

kyland_qos_ dscp_cfg基于每个dscp进行配置映射的qos、dp、remark_dscp等。

入口基于dscp分类

dscp_class_ena=1&dscp_dp_ena=1时

如果dscp_translate=0、trust_dscp=1直接通过frame_dscp查dscp_class_map和dscp_dp_map

如果dscp_translate=1、trust_dscp=1则通过查dscp_translate_map得到新的dscp，然后根据新的dscp查dscp_class_map/dscp_dp_map

如果trust_dscp=0，则查端口default_qos和default_dp

dscp_class_ena=0&dscp_dp_ena=0时查端口default_qos和default_dp。

出口remark dscp

dscp_emode=KYLAND_DSCP_EMODE_DISABLE时，出口不做remark，使用原始报文dscp封装

dscp_emode=KYLAND_DSCP_EMODE_REMARK时，使用上行remark dscp封装

dscp_emode=KYLAND_DSCP_EMODE_REMAP时，查找dscp_remap映射表，使用映射的dscp封装

示例：

入端口为48，目的端口为49，打入dscp=10的ipv4报文。基于dscp分类，qos=1，dp=0，出口remark dscp=20。

配置48端口dscp_class_ena= enable、使用dscp10映射内部优先级qos=1、dp=0；配置49端口dscp_emode= KYLAND_DSCP_EMODE_REMAP，配置dscp_remap[10]=20，出口使用dscp20封装。

kyland_rc kd5886_qos_dscp_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_port_t port;

kyland_port_dscp_cfg_t conf1,conf2;

kyland_dscp_cfg_t dscp_conf;

kyland_dscp_t dscp, translate_dscp, rew_dscp, remap_dscp;

u32 cos1, cos2, dp1, dp2;

ucBool enable = 1, disable = 0;

port = 48;

conf1.dscp_class_ena = enable;

conf1.dscp_dp_ena = enable;

KYLAND_RC(kyland_qos_port_dscp_cfg(inst, port, &conf1));

port = 49;

conf2.dscp_emode = KYLAND_DSCP_EMODE_REMAP;

KYLAND_RC(kyland_qos_port_dscp_cfg(inst, port, &conf2));

dscp = 10;

cos1 = 1;

dp1 = 0;

dscp_conf.dscp_trust[dscp] = enable;

dscp_conf.dscp_class_map[dscp] = cos1;

dscp_conf.dscp_dp_map[dscp] = dp1;

dscp_conf.dscp_remap[dscp] = 20;

KYLAND_RC(kyland_qos_dscp_cfg(inst, &dscp_conf));

return rc;

}

### MPLS

API使用说明：

kyland_qos_mpls_map_cfg来配置EXP到qos/dp的映射，支持8个domain，选择哪个domain做映射需要在ILM中配置。

kyland_qos_elsp_map_cfg配置的是qos到EXP的映射，kyland_qos_llsp_map_cfg配置dp到EXP的映射，同样都支持8个domain。

如果是MPLS->IP类型可以通过kyland_qos_mpls_dscp_map_cfg来配置qos->dscp的映射做出口dscp封装。

示例：

MPLS->MPLS，入口为48端口，exp为1，出口为49端口，exp为2

入口查domain1的映射表得到cos/dp，出口用cos查映射表获取exp

kyland_rc kd5886_qos_mpls_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

u32 exp, cos, dp;

kyland_domain_t domain;

kyland_qos_mpls_map_t map;

kyland_qos_elsp_map_t elsp_map;

domain = KYLAND_MPLS_QOS_DOMAIN_1;

exp = 1;

cos = 5;

dp = 0;

map.cos[exp] = cos;

map.dp[exp] = dp;

KYLAND_RC(kyland_qos_mpls_map_cfg(inst, domain, &map));

exp = 2;

map.exp[cos] = exp;

KYLAND_RC(kyland_qos_elsp_map_cfg(inst, domain, &map));

return rc;

}

### 拥塞管理

API使用说明：

通过kyland_qos_port_cfg配置拥塞管理

qos_port_cfg-> qos_queue_cfg[qu].dwrr_ena=1为dwrr队列，

qos_port_cfg-> qos_queue_cfg[qu].dwrr_ena=0为sp队列

qos_port_cfg-> qos_queue_cfg[qu].weight为权重

示例：

队列sp+dwrr调度，队列6和7sp调度，其他权重1:1:2:2:3:3

kyland_rc kd5886_sp_dwrr_queue_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

u32 qu;

kyland_port_t port;

kyland_qos_port_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_qos_port_cfg_t));

port = 1;

KYLAND_RC(kyland_qos_port_get(inst, port, &conf));

conf.qos_queue_cfg[0].dwrr_ena = 1;

conf.qos_queue_cfg[0].weight = 1;

conf.qos_queue_cfg[1].dwrr_ena = 1;

conf.qos_queue_cfg[1].weight = 1;

conf.qos_queue_cfg[2].dwrr_ena = 1;

conf.qos_queue_cfg[2].weight = 2;

conf.qos_queue_cfg[3].dwrr_ena = 1;

conf.qos_queue_cfg[3].weight = 2;

conf.qos_queue_cfg[4].dwrr_ena = 1;

conf.qos_queue_cfg[4].weight = 3;

conf.qos_queue_cfg[5].dwrr_ena = 1;

conf.qos_queue_cfg[5].weight = 3;

conf.qos_queue_cfg[6].dwrr_ena = 0;

conf.qos_queue_cfg[6].weight = 1;

conf.qos_queue_cfg[7].dwrr_ena = 0;

conf.qos_queue_cfg[7].weight = 1;

KYLAND_RC(kyland_qos_port_cfg(inst, port, &conf));

}

### 拥塞避免

### 流量整形

API使用说明：

通过kyland_shaper_template_cfg配置shaper模板，支持32个shaper模板。

Kyland_qos_port_cfg配置端口和队列选择shaper模板

示例：

shaper模板配置，cir=100Mbps，cbs=10240Bytes

kyland_rc kd5886_shaper_template_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_shaper_template_t shaper_id;

kyland_shaper_cfg_t conf;

shaper_id = 10;

conf.level = 10240;

conf.rate = 100000;

KYLAND_RC(kyland_shaper_template_cfg(inst, shaper_id, &conf));

return rc;

}

端口shaper，端口1配置shaper100Mbps

kyland_rc kd5886_port_shaper_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_port_t port;

kyland_qos_port_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_qos_port_cfg_t));

port = 1;

KYLAND_RC(kyland_qos_port_get(inst, port, &conf));

conf.shaper.shaper_ena = 1;

conf.shaper.shaper_id = 10;

KYLAND_RC(kyland_qos_port_cfg(inst, port, &conf));

}

### 流量监管

#### Port policer

API使用说明：

通过kyland_port_pol_cfg来配置端口policer。

port_pol_cfg[KYLAND_PORT_POLICERS]配置4个策略组的burst_level和rate，单位分别为bytes和kbps。

port_pol_ext_cfg[KYLAND_PORT_POLICERS]配置4个策略组的规则。

示例：

配置48端口使能policer，rate为1Gbps，burst_level为20480bytes。策略组1为未知单播，策略组2为未知组播，策略组3为未广播，策略组4为to cpu。

kyland_rc kd5886_port_pol_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

int i;

kyland_port_t port = 48;

kyland_port_pol_cfg_t pol;

KYLAND_OS_MEMSET(&pol,0,sizeof(kyland_port_pol_cfg_t));

for(i = 0; i < 8; i++){

pol.port_pol_ext_cfg[0].cpu_queue[i] = 1;

pol.port_pol_ext_cfg[1].cpu_queue[i] = 1;

pol.port_pol_ext_cfg[2].cpu_queue[i] = 1;

pol.port_pol_ext_cfg[3].cpu_queue[i] = 1;

}

pol.port_pol_cfg[0].level = 20480;

pol.port_pol_cfg[0].rate = 1000000;

pol.port_pol_ext_cfg[0].frame_rate = 0;

pol.port_pol_ext_cfg[0].flow_control = 0;

pol.port_pol_ext_cfg[0].unknow_uc_flood = 1;

pol.port_pol_ext_cfg[0].to_cpu = 1;

pol.port_pol_ext_cfg[0].limit_noncpu_traffic = 1;

pol.port_pol_cfg[1].level = 20480;

pol.port_pol_cfg[1].rate = 1000000;

pol.port_pol_ext_cfg[1].frame_rate = 0;

pol.port_pol_ext_cfg[1].flow_control = 0;

pol.port_pol_ext_cfg[1].unknow_mc_flood = 1;

pol.port_pol_ext_cfg[1].to_cpu = 1;

pol.port_pol_ext_cfg[1].limit_noncpu_traffic = 1;

pol.port_pol_cfg[2].level = 20480;

pol.port_pol_cfg[2].rate = 1000000;

pol.port_pol_ext_cfg[2].frame_rate = 0;

pol.port_pol_ext_cfg[2].flow_control = 0;

pol.port_pol_ext_cfg[2].broadcast = 1;

pol.port_pol_ext_cfg[2].to_cpu = 1;

pol.port_pol_ext_cfg[2].limit_noncpu_traffic = 1;

pol.port_pol_cfg[3].level = 20480;

pol.port_pol_cfg[3].rate = 1000000;

pol.port_pol_ext_cfg[3].frame_rate = 0;

pol.port_pol_ext_cfg[3].flow_control = 0;

pol.port_pol_ext_cfg[3].to_cpu = 1;

pol.port_pol_ext_cfg[3].limit_noncpu_traffic = 1;

for(i = 0; i < 8; i++){

pol.queue_pol_cfg[i].level = 20480;

pol.queue_pol_cfg[i].rate = KYLAND_BITRATE_DISABLED;

}

pol.enable = 1;

KYLAND_RC(kyland_port_pol_cfg(inst, port, &pol));

return rc;

}

#### Queue policer

API使用说明：

通过kyland_port_pol_cfg来配置队列policer。

port_pol_cfg.queue_pol_cfg[queue].level单位为byte

port_pol_cfg.queue_pol_cfg[queue].rate单位为kbps，

rate=KYLAND_BITRATE_DISABLED时表示关闭policer

示例：

配置8个队列rate=100Mbps

kyland_rc kd5886_queue_pol_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

int i;

kyland_port_t port = 48;

kyland_port_pol_cfg_t pol;

KYLAND_OS_MEMSET(&pol,0,sizeof(kyland_port_pol_cfg_t));

pol.port_pol_cfg[0].level = 20480;

pol.port_pol_cfg[0].rate = KYLAND_BITRATE_DISABLED;

pol.port_pol_cfg[1].level = 20480;

pol.port_pol_cfg[1].rate = KYLAND_BITRATE_DISABLED;

pol.port_pol_cfg[2].level = 20480;

pol.port_pol_cfg[2].rate = KYLAND_BITRATE_DISABLED;

pol.port_pol_cfg[3].level = 20480;

pol.port_pol_cfg[3].rate = KYLAND_BITRATE_DISABLED;

for(i = 0; i < 8; i++){

pol.queue_pol_cfg[i].level = 20480;

pol.queue_pol_cfg[i].rate = 100000;

}

pol.enable = 1;

KYLAND_RC(kyland_port_pol_cfg(inst, port, &pol));

return rc;

#### ACL policer

API使用说明：

通过kyland_acl_pol_template_cfg配置policer模板，支持32个policer模板。

kyland_acl_policer_cfg配置car动作和选择模板。

Rate单位：kbps

Burst size单位：bytes

示例：

Index = 1, template id = 1, Cir = 1Gbps，cbs = 10240bytes，pir = 1Gbps，pbs = 10240bytes，使能色盲模式，红色报文丢弃。

kyland_rc kd5886_acl_policer_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_pol_template_t template_id;

kyland_acl_pol_template_cfg_t template_conf;

kyland_pol_t pol_id;

kyland_acl_pol_cfg_t conf;

KYLAND_OS_MEMSET(&template_conf,0,sizeof(kyland_acl_pol_template_cfg_t));

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_pol_cfg_t));

template_id = 1;

template_conf.timescale = KYLAND_TIMESCALE_LVL_2;

template_conf.cir = 1000000;

template_conf.cbs = 10240;

template_conf.pir = 1000000;

template_conf.pbs = 10240;

template_conf.coupling_ena = 0;

template_conf.inc_dp_val = KYLAND_CIR_INC_DP_1;

template_conf.dp_aware_lvl = KYLAND_COLOR_BLINDNESS_MODE;

KYLAND_RC(kyland_acl_pol_template_cfg(inst, template_id, &template_conf));

pol_id = 1;

conf.pol_template_id = template_id;

conf.green_action.action_ena = 1;

conf.yellow_action.action_ena = 1;

conf.red_action.action_ena = 1;

conf.red_action.drop_ena = 1;

KYLAND_RC(kyland_acl_policer_cfg(inst, pol_id, &conf));

}

#### Service policer

index = 1, Cir = 1Gbps，cbs = 10240bytes，pir = 1Gbps，pbs = 10240bytes，使能色盲模式，红色报文丢弃。

kyland_rc kd5886_isdx_policer_demo()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_pol_t pol_id;

kyland_ivport_pol_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_ivport_pol_cfg_t));

pol_id = 1;

conf.coupling_ena = 0;

conf.timescale = KYLAND_TIMESCALE_LVL_2;

conf.dp_aware_lvl = KYLAND_COLOR_BLINDNESS_MODE;

conf.inc_dp_val = KYLAND_CIR_INC_DP_1;

conf.cir = 1000000;

conf.cbs = 10240;

conf.pir = 1000000;

conf.pbs = 10240;

conf.green_action.action_ena = 1;

conf.yellow_action.action_ena = 1;

conf.red_action.action_ena = 1;

conf.red_action.drop_ena = 1;

KYLAND_RC(kyland_ivport_policer_cfg(inst, pol_id, &conf));

return rc;

}
