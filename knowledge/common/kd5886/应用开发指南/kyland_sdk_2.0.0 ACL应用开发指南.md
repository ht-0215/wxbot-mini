# kyland_sdk_2.0.0 ACL应用开发指南

kyland_sdk_2.0.0

ACL应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 ACL概述	4

2 芯片支持	5

2.1 支持规格和特性	5

2.2 ACL KEY	5

2.2.1 KEY 类型	5

2.2.2 组KEY 条件	6

2.2.3 组KEY 优先级与流程	7

2.3 ACL ACTION	10

3 SDK API及应用示例	13

3.1 SDK API	13

3.1.1 ACL配置接口	13

3.1.2 ACL组KEY使能配置	20

3.1.3 端口默认ACL配置	23

3.1.4 统计	26

3.2 应用示例	29

3.2.1 ETYPE_ENTRY	29

3.2.2 LLC_ENTRY	31

3.2.3 SNAP_ENTRY	34

3.2.4 ARP_ENTRY	38

3.2.5 IP_OTHER_ENTRY	40

3.2.6 IP_TCP_ENTRY	42

3.2.7 IP_UDP_ENTRY	45

3.2.8 IP_MAC_ENTRY	47

3.2.9 IP6_STD_ENTRY	51

3.2.10 MPLS_ENTRY	56

3.2.11 基于端口使能ACL	58

# ACL概述

访问控制列表ACL（Access Control List）是由一系列规则组成的集合，ACL通过这些规则对数据包进行分类，从而设备可以对不同类报文进行不同的处理。

ACL负责管理用户配置的所有规则，并提供报文匹配规则的算法。

# 芯片支持

## 支持规格和特性

支持基于TCAM的安全控制ACL复杂流分类

支持2K ACL表项

支持1K个共享的双漏桶ACL Policer，可按比特/秒进行测量

支持8个共享范围检查器，可基于TCP/UDP端口号进行范围匹配检查

支持18种TCAM匹配模板，包括ETH/LLC/SNAP/ARP/IPv4/IPv6/IPv6STD/TCPUDP/IPMAC/MPLS模板，与8种可自定义的模板类型

ACL查表命中动作包括允许/拒绝、Police、计数、CPU复制和镜像

支持IP分片检查、UDP/TCP端口范围检查、ARP检查

可支持通过ACL Policer与首次命中检测功能阻止CPU DOS攻击

支持40bits的ACL表项命中计数器

## ACL KEY

### KEY 类型

支持MAC_ETYPE类型ACL，KEY模板为SMAC+DMAC+EtherType+VID，基于端口使能该ACL类型。

支持MAC_LLC类型ACL，KEY模板为SMAC+DMAC+DSAP+SSAP+CTRL，基于端口使能该ACL类型。

支持MAC_SNAP类型ACL，KEY模板为SMAC+DMAC+ORG_CODE+TYPE，基于端口使能该ACL类型。

支持ARP类型ACL，KEY模板为SMAC+IPv4 SIP+IPv4 DIP+ARP/RARP，基于端口使能该ACL类型。

支持IP_OTHER类型ACL，KEY模板为包括IPV4和IPV6两种情况，两种情况共用的KEY关健域包括PROTOCOL+DSCP+TTL+VRF，IPv4的KEY关健域还包括IPv4 SIP+IPv4 DIP+IPv4 Payload（其中IPv4 Payload在IPSEC的情况下包含SPI）；IPv6的KEY关健域还包括IPv6 SIP低64bit+IPv6 Payload，基于端口使能该ACL类型。

支持IP_TCP_UDP类型ACL，KEY模板包括IPV4和IPV6两种情况，两种情况共用的KEY关健域包括SPORT+DPORT+PROTOCOL+DSCP+TTL+VRF ，IPv4的KEY关健域还包括IPv4 SIP+IPv4 DIP；IPv6的KEY关健域还包括IPv6 SIP低64bit，基于端口使能该ACL类型。

支持IP_MAC类型的ACL，KEY模板为SMAC+DMAC+SPORT+DPORT+PROTOCOL+DSCP+TTL+VRF+IP(IPv4 SIP+IPv4 DIP或IPv6 SIP低64bit)，该KEY占据两条表项的长度。使用HALF WORD方式组织S2的TCAM。如果报文是TCP/UDP报文，则该KEY的IP部分与IP_TCP_UDP的KEY一致。否则与IP_OTHER的KEY一致。

支持IPv6_STD类型ACL，KEY模板为IPv6 SIP+DIP+VRF+ SPORT+DPORT+ PROTOCOL+TTL+ DSCP，该KEY占据两条表项的长度，基于端口使能该ACL类型。

支持MPLS类型的ACL，KEY模板为PAG +LABEL0+LABEL1(如果存在）+LABEL2(如果存在），基于端口使能该ACL类型。如果标签不存在则填1。

支持CUSTOM类型ACL，KEY由ACL_S1:VLAN_PAG_ACTION:CUSTOM_POS定义的4*32Bits，基于ACL_S1 Action使能该ACL类型。

### 组KEY 条件

由于MAC_ETYPE类型是默认使能的，所以不需要在ACL PORT表里体现。又因为此类型优先级最低，所以只有在没有配置其他类型的使能的情况下才会默认去组MAC_ETYPE类型的KEY进行查找。这里如果某个端口两次查找都没有使能其他类型，则会组MAC_ETYPE类型的KEY去查找两次，但这不会造成浪费。因为按照程序流水，一个报文来了之后固定是要查两次的，只不过可能某次查找KEY的vld为0，不会查中。两次的KEY是否一样都不影响查两次的流程。此外，即使用MAC_ETYPE类型的KEY去查找两次，也很大可能查找结果不同。因为所有TCAM表项都有一个first域，标志着该表项是允许第一次查找命中还是第二次查找命中。因此即使一样的报文组一样类型的KEY去查，两次组成的KEY的first域的值却不同，因此命中的表项也不同。因此也不算浪费

以MPLS开头的表项提供给使用者更多的灵活性。即如果该端口终结到二层的MPLS报文查IP_OTHER类型而普通报文查IP_MAC类型。则可以使能MPLS_SEC_TYPE_IP_OTHER_ENA以及SEC_TYPE_IP_MAC_ENA。可以让MPLS和普通报文分别组不同KEY。

SEC_TYPE_IP6_TCPUDP_OTHER_ENA的作用是使能IPV6报文组IP_TCP_UDP和IP_OTHER的KEY。当SEC_TYPE_IP6_TCPUDP_OTHER_ENA使能时，如果L4_TYPE是TCP或UDP，则组IP_TCP_UDP的KEY，如果L4_TYPE不是TCP或UDP，则组IP_OTHER的KEY。所以对于想组TCP_UDP的KEY的报文，如果是IPV4报文，则使能SEC_TYPE_IP_TCPUDP_ENA，而如果是IPV6报文，则使能SEC_TYPE_IP6_TCPUDP_OTHER_ENA。同理想组IP_OTHER的KEY也是如此。

除了PORT表中的使能信号，组KEY的条件还受报文类型等影响。

### 组KEY 优先级与流程

支持每报文多种KEY联合查找，按2.1节(1)~(10)的KEY的顺序编号，匹配优先级递增。在同一次查找中，符合组多种KEY条件的报文最终只会用优先级最高的KEY去查找。

支持二次查表，每一种KEY都可以使能第一次查找或（和）第二次查找。PORT表查出来的KEY使能信号都是2bit的，用来表示是使能第一次查还是第二次查。

cell有效时长为2个时钟周期，即SOC的一个时钟周期。那么当SOC为1时进行第一次查表，SOC为0时进行第二次查表。

两次查表的任一个action的域符合动作条件都会触发相应动作，都不符合条件则相应的输出req边带信号透传或保持复位值，即不做动作。例如IRQ_TRIGGER域，任一次查得的IRQ_TRIGGER为1则使能ACL中断。两次查得的IRQ_TRIGGER都为0则透传req_acl_irq_ena信号。如果两次查表都符合动作条件且结果有冲突，则选择第一次查表的action。例如DLB_OFFSET 域，如果两次查得的DLB_OFFSET 都大于0，则选择第一次查得的DLB_OFFSET赋值给req_acl_dlb_offset_o。

KEY优先级排序及查表流程见下图 ：

图 1 KEY优先级与S2查表流程

当二层头的type/length域小于16'h0600的就是LLC帧。可以组LLC的KEY或SNAP的KEY。如果该帧的{DSAP，SSAP，Ctrl} == 24'hAAAA03，则确定为LLC帧中的特殊类型——SNAP帧。此时要组SNAP的KEY，否则组LLC的KEY。

MPLS报文组KEY流程

处理流程如下图所示：

图 2 MPLS报文组KEY流程图

由图2可知， MPLS有四种组KEY的情况，其中提到的组MAC类型的KEY只有一种，即MAC_ETYPE类型。不包含LLC和SNAP类型（因为这两种类型应用很少，用在MPLS场景就更少）。各种情况关键域解析方法如下：

MPLS组KEY：

此时组MPLS类型的KEY。首先要获知MPLS标签的起始位置，解析报文判断有几层VLAN，“剥除”所有VLAN TAG以及type域；然后检查每个MPLS LABEL的栈底标志，小于等于三层标签的情况下，有几层就用几层LABEL组KEY，不满三层的填全0。大于三层的标签不支持，也不会用来组KEY。然后查找S2获取相应的aciton，并根据action处理报文。

MPLS报文的req_mpls_fwd_cmd_i的值为SWAP且MPLS_ENA无效：

此时默认组MAC_ETYPE的KEY。因为是MPLS报文，又不使能MPLS组KEY，所以只能利用MPLS外层的二层头组MAC_ETYPE的KEY。此种应用出现在软件没有配置MPLS类型的KEY的表项但却收到了一些SWAP的MPLS报文的情况。

MPLS报文的req_mpls_fwd_cmd_i的值取Term to VPWS或Term to VPLS，即终结到二层：

此时可以组IP类型KEY，也可以组MAC类型的KEY。查ACL_PORT表并根据优先级选择组哪种KEY。如果租MAC类型的KEY，首先根据1）的方法剥除外层的二层头，并根据req_mpls_pop_cnt_i剥除所有MPLS LABEL，剩余的就是一个二层帧，然后正常解析该二层帧的二层头，获取MAC/VLAN等关健域组成MAC类型的KEY即可。MPLS的四种情况中，唯有终结到二层的MPLS报文组的MAC_ETYPE使用的是MPLS标签内层的二层头，其余的都用MPLS标签外层的二层头；如果组IP类型KEY，则还需继续剥除内层的二层头，解析三层头，解析出IP相关关键域组成IP类型的KEY。

此时可以组的KEY包括MAC_ETYPE、IP_MAC、IP6_STD、IP_TCP_UDP、IP_OTHER。

req_mpls_fwd_cmd_i的值取Term to L3VPN/Term to IP，即终结到三层：

此时组IP类型KEY。首先按照3）的方法剥除外层二层头和MPLS标签，剩余的就是一个三层报文，然后解析三层头的关键域组成IP类型的KEY。

由于终结到三层的MPLS报文的二层头意义不大，因此多数情况是使用该报文的三层内容来组IP类的KEY。包括IP6_STD、IP_TCP_UDP、IP_OTHER三种。但为了在不使能任何KEY的情况下仍然能够组KEY，所以也会使用该报文的二层头组默认KEY（也就是MAC_ETYPE类型KEY）。

## ACL ACTION

| Offset | Bit | Name | Field | Description |
| --- | --- | --- | --- | --- |
| 0x0 | [0:0] | A | HIT_ME_ONCE | 该bit为高，则第一个命中该条目的报文会被复制到CPU队列（由CPU_QU_NUM指定），然后该位会被清除，并且后续报文不会再被复制到CPU队列 |
| 0x0 | [1:1] | A | CPU_COPY_ENA | 报文复制CPU队列使能 |
| 0x0 | [4:2] | A | CPU_QU_NUM | 在报文被复制到CPU时，用于指定CPU队列 |
| 0x0 | [5:5] | A | IRQ_TRIGGER | 中断触发位 |
| 0x0 | [6:6] | A | FW_ENA | 报文转发使能位，0丢弃报文，1则使能报文的转发（具体是否转发还要看其他条件）；该字段在两次匹配中只要有一次结果为0，则报文就会被丢弃。 |
| 0x0 | [7:7] | A | LRN_ENA | 报文学习使能，0为disable，1为enable |
| 0x0 | [8:8] | A | RT_ENA | 报文路由使能，0为disable，1为enable |
| 0x0 | [9:9] | A | POLICE_ENA | POLICE使能标志 |
| 0x0 | [14:10] | A | POLICE_IDX | POLICE索引号 |
| 0x0 | [17:15] | A | DLB_OFFSET | DLB policer的偏移值 |
| 0x0 | [19:18] | A | MIRROR_PROBE | 用于配置镜像探针号，0表示不镜像；1/2/3分别对应三个镜像探针。当一个报文命中多个镜像探针时（在不同流程中），最终只采用探针号最大的那个镜像探针 |
| 0x0 | [20:20] | A | FORCE_L2FWD | 强制L2转发，为1时设置req_l2_fwd_o=1,req_l3_fwd_o=0; 不可与FORCE_L3FWD同时为1 |
| 0x0 | [21:21] | A | FORCE_L3FWD | 强制L3转发，为1时设置req_l2_fwd_o=0,req_l3_fwd_o=1; 不可与FORCE_L2FWD同时为1 |
| 0x0 | [22:22] | A | LOOPBACK_SEL | 报文环回转发使能（报文被转发至接收端口）。在进行环回转发时，报文不会被修改。0，不使能；1，使能。 |
| 0x0 | [23:23] | A | OAM_RX_TIMESTAMP_ENA | 转发至CPU报文接收时间戳打入使能。0，不打时间戳；1，打入时间戳。 |
| 0x0 | [25:24] | A | OAM_TX_TIMESTAMP_SEL | 用于选择报文发出时报文ID以及时间戳的存储寄存器： 0：不存储 1：存储至latch register0 2：存储至latch register1 3：存储至latch register2 |
| 0x4 | [0:0] | B | SECOND_LOOKUP_DIS | 如果两次命中，且第一次动作表中此项值为1，则使用第一次的ACTION表；否则两次命中的ACTION都起作用 |
| 0x4 | [3:1] | B | REDIR | 重定向方向选择 0：no redirection 1：nhi 2：gport(upsid+upcn) 3：isdx |
| 0x4 | [16:4] | B | NHI_IPSEC_SA_ID | 当REDIR = 1时，NHI_IPSEC_SA_ID为NHI值，此时将此域的值同时赋给req_nhi_o，而不是用req_nhi_i的值 当REDIR = 2时，NHI_IPSEC_SA_ID为upsid+upcn的值，并从req_acl_dst_port_o给到L2； 当REDIR = 3时，NHI_IPSEC_SA_ID为isdx的值，此时将此域的值同时赋给req_isdx_o，而不是用req_isdx_i的值 |
| 0x8 | [1:0] | C | REMARK_TYPE | 重写类型： 0：no remark 1：remark dscp 2：remark 802.1p（pcp）+dei |
| 0x8 | [4:2] | C | REMARK_FIELD1 | 当REMARK_TYPE = 1时，REMARK_FIELD1为dscp高3bit； 当REMARK_TYPE = 2时，REMARK_FIELD1为802.1p的值； |
| 0x8 | [7:5] | C | REMARK_FIELD2 | 当REMARK_TYPE = 1时，REMARK_FIELD2为dscp低3bit； 当REMARK_TYPE = 2时，REMARK_FIELD2的最低位为dei； |
| 0x8 | [8:8] | C | REMARK_QOS | 0：no remark 1：set qos+dp |
| 0x8 | [11:9] | C | CL_QOS | Cos值 |
| 0x8 | [13:12] | C | CL_DP | Dp值 |
| 0x8 | [23:14] | C | CARID | CAR ID的索引值 |
| 0xC | [31:0] | D | HIT_CNT_LOW | 命中计数低32bit |
| 0xF | [7:0] | E | HIT_CNT_HIGH | 命中计数高8bit |

# SDK API及应用示例

## SDK API

### ACL配置接口

#### 功能简介

包括acl规则添加、删除、查询和搬移API接口。支持2k ACL表项，16种TCAM匹配模板，由上层软件管理芯片ACL表项资源。

#### API接口

/**

* \brief get acl cfg

*

* \param inst [IN] 	  		Target instance reference

* \param acl_id [IN] 	  		acl id

* \param acl_cfg [OUT]		acl setup structure

*

* \return Return code

**/

kyland_rc  kyland_acl_get(const kyland_inst_t  inst,

kyland_acl_t  acl_id,

kyland_acl_cfg_t * acl_cfg);

/**

* \brief set acl cfg

*

* \param inst [IN] 	  		Target instance reference

* \param acl_id [IN] 	  		acl id

* \param acl_cfg [IN]			acl setup structure

*

* \return Return code

**/

kyland_rc  kyland_acl_add(const kyland_inst_t  inst,

kyland_acl_t  acl_id,

kyland_acl_cfg_t * acl_cfg);

/**

* \brief del acl cfg

*

* \param inst [IN] 	  		Target instance reference

* \param acl_id [IN] 	  		acl id

*

* \return Return code

**/

kyland_rc  kyland_acl_del(const kyland_inst_t  inst,

kyland_acl_t  acl_id);

/**

* \brief acl move

*

* \param inst [IN] 	  		Target instance reference

* \param acl_id [IN] 	  		acl id

* \param move_cfg [IN]		move cfg setup structure

*

* \return Return code

**/

kyland_rc  kyland_acl_move(const kyland_inst_t  inst,

kyland_acl_t  acl_id,

kyland_acl_move_cfg_t * move_cfg);

#### 数据结构

typedef struct{

kyland_acl_key_t 		acl_key;	/**< KEY */

kyland_acl_action_cfg_t 	acl_action;	/**< ACTION */

}kyland_acl_cfg_t;

typedef struct{

kyland_ace_u8_t	port;	 /**< Port number or KYLAND_PORT_NO_ANY */

kyland_ace_u8_t	policy;	 /**< PAG, Policy number */

kyland_acl_type_t	type;	 /**< ACE frame type */

kyland_ace_bit_t	first;	 /**< first,second or both lookup*/

kyland_ace_bit_t	dmac_mc;	 /**< Multicast DMAC */

kyland_ace_bit_t	dmac_bc;   /**< Broadcast DMAC */

kyland_ace_bit_t	mpls_avail;  /**< Mpls Avail */

kyland_ace_bit_t 	l2_fwd;	 /**< L2_FWD */

kyland_ace_vlan_t	vlan;       /**< VLAN Tag */

kyland_ace_bit_t	tocpu;	 /**< TO CPU */

kyland_ace_bit_t	l3_fwd;	 /**< L3_FWD */

kyland_ace_bit_t	l3_rt;	 /**< L3_RT */

kyland_ace_u8_t     	vlan_gid;  	/**< vlan gid */

kyland_ace_u16_t     	acl_gid;  	/**< acl gid */

ucBool 		ip_mac;	/**< IP_MAC */

kyland_ace_u48_t 	ip_dmac;  	/**< DMAC */

kyland_ace_u48_t 	ip_smac;  	/**< SMAC */

union

{

kyland_acl_frame_etype_t etype;  /**< KYLAND_ACE_TYPE_ETYPE */

kyland_acl_frame_llc_t   llc;    /**< KYLAND_ACE_TYPE_LLC */

kyland_acl_frame_snap_t  snap;   /**< KYLAND_ACE_TYPE_SNAP */

kyland_acl_frame_arp_t   arp;    /**< KYLAND_ACE_TYPE_ARP */

kyland_acl_frame_ipv4_t  ipv4;   /**< KYLAND_ACE_TYPE_IPV4 */

kyland_acl_frame_ipv6_t  ipv6;   /**< KYLAND_ACE_TYPE_IPV6 */

kyland_acl_frame_ipv6_std_t ipv6_std;/**< KYLAND_ACE_TYPE_IPV6_STD */

kyland_acl_frame_mpls_t  mpls;	 /**< KYLAND_ACE_TYPE_MPLS */

kyland_acl_frame_custom_t  custom0;   /**< KYLAND_ACE_TYPE_CUSTOM0 */

kyland_acl_frame_custom_t  custom1;   /**< KYLAND_ACE_TYPE_CUSTOM1 */

kyland_acl_frame_custom_t  custom2;   /**< KYLAND_ACE_TYPE_CUSTOM2 */

kyland_acl_frame_custom_t  custom3;   /**< KYLAND_ACE_TYPE_CUSTOM3 */

kyland_acl_frame_custom_t  custom4;   /**< KYLAND_ACE_TYPE_CUSTOM4 */

kyland_acl_frame_custom_t  custom5;   /**< KYLAND_ACE_TYPE_CUSTOM5 */

kyland_acl_frame_custom_t  custom6;   /**< KYLAND_ACE_TYPE_CUSTOM6 */

kyland_acl_frame_custom_t  custom7;   /**< KYLAND_ACE_TYPE_CUSTOM7 */

} frame; /**< Frame type specific data */

}kyland_acl_key_t;

typedef struct{

ucBool 	cpu;	/**< copy to cpu */

ucBool 	cpu_once;	/**< first hit copy to cpu */

kyland_packet_rx_queue_t 	cpu_queue;	/**< cpu queue */

ucBool 	police;	/**< police ena */

kyland_acl_policer_no_t 	policer_no;	/**< police id */

u16 	car_id;	/**< car id(= acl_police_template_id) */

ucBool 	rx_timestamp_ena;	/**< rx timestamp ena */

kyalnd_tx_timestamp_sel 	tx_timestamp; /**< tx timestamp sel */

ucBool 	forward;	/**< forward ena*/

ucBool 	loopback;	/**< forward ena*/

ucBool 	force_l2;	/**< force_l2 ena*/

ucBool 	force_l3;	/**< force_l3 ena*/

ucBool 	rt;	/**< rt ena*/

ucBool 	learn;	/**< learn ena*/

ucBool 	second_search_disable;	/**< second_search_disable*/

kyland_acl_redirect_cmd_t 	redir_cmd;	/**< redir_cmd*/

u16 	redir_id;	/**< redir_id*/

kyland_acl_remark_type_t 	remark_type; /**< remark type*/

u8 	remark_dscp;	/**< remark dscp val*/

u8 	remark_pcp;		/**< remark pcp val*/

u8 	remark_dei;		/**< remark dei val*/

ucBool 	remark_qos;		/**< remark qos ena*/

u8 	qos_cos;		/**< remark qos val*/

u8 	qos_dp;		/**< remark dp val*/

u8 	mirror_id;		/**< mirror probe*/

ucBool 	irq_trigger;		/**< irq_trigger*/

}kyland_acl_action_cfg_t;

### ACL组KEY使能配置

#### 功能简介

基于端口配置组什么类型的KEY。

#### API接口

/**

* \brief acl port get

*

* \param inst [IN] 	  	Target instance reference

* \param port [IN] 	  	port

* \param conf [OUT]		port cfg setup structure

*

* \return Return code

**/

kyland_rc  kyland_acl_port_get(const kyland_inst_t  inst,

kyland_port_t  port,

kyland_acl_port_cfg_t  *conf);

/**

* \brief acl port set

*

* \param inst [IN] 	  	Target instance reference

* \param port [IN] 	  	port

* \param conf [IN]		port cfg setup structure

*

* \return Return code

**/

kyland_rc  kyland_acl_port_cfg(const kyland_inst_t  inst,

kyland_port_t  port,

kyland_acl_port_cfg_t  *conf);

#### 数据结构

typedef struct{

kyland_acl_lookup_t 	sec_ena;		/**<  sec_ena*/

kyland_acl_lookup_t 	mac_llc_ena;	/**<  mac_llc_ena*/

kyland_acl_lookup_t 	mac_snap_ena;	/**<  mac_snap_ena*/

kyland_acl_lookup_t 	arp_ena;		/**<  arp_ena*/

kyland_acl_lookup_t 	ip_other_ena;	/**<  ip_other_ena*/

kyland_acl_lookup_t 	ip_tcpudp_ena;	/**<  ip_tcpudp_ena*/

kyland_acl_lookup_t 	ip_mac_ena;	/**<  ip_mac_ena*/

kyland_acl_lookup_t 	ip_std_ena;		/**<  ip_std_ena*/

kyland_acl_lookup_t 	mpls_ena;		/**<  mpls_ena*/

kyland_acl_lookup_t 	custom_ena;		/**<  custom_ena*/

kyland_acl_lookup_t 	ip6_tcpudp_other_ena;	/**<  ip6_tcpudp_other_ena*/

ucBool 		route_handling_ena;	/**<  route_handling_ena*/

ucBool 		custom_stag_etype_ena;	/**<  custom_stag_etype_ena*/

ucBool 		npi_ena;		/**<  npi_ena*/

kyland_acl_lookup_t 	mpls_ip6_tcpudp_other_ena;/**<  mpls_ip6_tcpudp_other_ena*/

kyland_acl_lookup_t 	mpls_ip6_std_ena;	/**<  mpls_ip6_std_ena*/

kyland_acl_lookup_t 	mpls_ip_mac_ena;	/**<  mpls_ip_mac_ena*/

kyland_acl_lookup_t 	mpls_ip_tcpudp_ena;	/**<  mpls_ip_tcpudp_ena*/

kyland_acl_lookup_t 	mpls_ip_other_ena;	/**<  mpls_ip_other_ena*/

}kyland_acl_port_cfg_t;

### 端口默认ACL配置

#### 功能简介

基于端口的默认acl配置，包括配置和查询接口。不需要组KEY，只配置ACTION。

#### API接口

/**

* \brief acl default port get

*

* \param inst [IN] 	  		Target instance reference

* \param port [IN] 	  		port

* \param conf [OUT]			port cfg setup structure

*

* \return Return code

**/

kyland_rc kyland_acl_port_conf_get(const kyland_inst_t     inst,

const kyland_port_no_t  port_no,

kyland_acl_port_conf_t  *const conf);

/**

* \brief acl default port set

*

* \param inst [IN] 	  		Target instance reference

* \param port [IN] 	  		port

* \param conf [IN]			port cfg setup structure

*

* \return Return code

**/

kyland_rc kyland_acl_port_conf_set(const kyland_inst_t           inst,

const kyland_port_no_t        port_no,

const kyland_acl_port_conf_t  *const conf);

#### 数据结构

typedef struct

{

kyland_acl_action_cfg_t    action;    /**< Action */

} kyland_acl_port_conf_t;

typedef struct{

ucBool 	cpu;	/**< copy to cpu */

ucBool 	cpu_once;	/**< first hit copy to cpu */

kyland_packet_rx_queue_t 	cpu_queue;	/**< cpu queue */

ucBool 	police;	/**< police ena */

kyland_acl_policer_no_t 	policer_no;	/**< police id */

u16 	car_id;	/**< car id(= acl_police_template_id) */

ucBool 	rx_timestamp_ena;		/**< rx timestamp ena */

kyalnd_tx_timestamp_sel 	tx_timestamp;/**< tx timestamp sel */

ucBool 	forward;		/**< forward ena*/

ucBool 	loopback;		/**< forward ena*/

ucBool 	force_l2;		/**< force_l2 ena*/

ucBool 	force_l3;		/**< force_l3 ena*/

ucBool 	rt;		/**< rt ena*/

ucBool 	learn;		/**< learn ena*/

ucBool 	second_search_disable;	/**< second_search_disable*/

kyland_acl_redirect_cmd_t 	redir_cmd;	/**< redir_cmd*/

u16 	redir_id;		/**< redir_id*/

kyland_acl_remark_type_t 	remark_type; /**< remark type*/

u8 	remark_dscp;	/**< remark dscp val*/

u8 	remark_pcp;		/**< remark pcp val*/

u8 	remark_dei;		/**< remark dei val*/

ucBool 	remark_qos;		/**< remark qos ena*/

u8 	qos_cos;		/**< remark qos val*/

u8 	qos_dp;		/**< remark dp val*/

u8 	mirror_id;		/**< mirror probe*/

ucBool 	irq_trigger;		/**< irq_trigger*/

}kyland_acl_action_cfg_t;

### 统计

#### 功能简介

基于2k ACL的统计get和clear，基于端口ACL的统计get和clear。

#### API接口

/**

* \brief port acl counter get.

*

* \param inst [IN]     Target instance reference.

* \param port_no [IN]  Port number.

* \param state [OUT]    Counter.

*

* \return Return code.

**/

kyland_rc  kyland_acl_port_counter_get(const kyland_inst_t        inst,

const kyland_port_no_t     port_no,

kyland_acl_port_counter_t  *const counter);

/**

* \brief port acl counter clear.

*

* \param inst [IN]     Target instance reference.

* \param port_no [IN]  Port number.

*

* \return Return code.

**/

kyland_rc  kyland_acl_port_counter_clear(const kyland_inst_t     inst,

const kyland_port_no_t  port_no);

/**

* \brief Get ACL counter.

*

* \param inst [IN]      Target instance reference.

* \param ace_id [IN]    ACL ID.

* \param counter [OUT]  ACL counter.

*

* \return Return code.

**/

kyland_rc  kyland_acl_counter_get(const kyland_inst_t        inst,

const kyland_acl_t     acl_id,

kyland_ace_counter_t  *const counter);

/**

* \brief Clear ACL counter.

*

* \param inst [IN]    Target instance reference.

* \param ace_id [IN]  ACL ID.

*

* \return Return code.

**/

kyland_rc  kyland_acl_counter_clear(const kyland_inst_t        inst,

const kyland_acl_t     acl_id);

#### 数据结构

typedef  u64  kyland_acl_port_counter_t;

typedef  u64  kyland_ace_counter_t;

## 应用示例

### ETYPE_ENTRY

添加ETYPE_ENTRY类型ACL，index=100，key为dmac=00:00:00:00:00:20、smac=00:00:00:00:00:10，action为remark qos=5，dp=0。

kyland_rc kd5886_etype_entry_acl_add()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = 100;

conf.acl_key.type = KYLAND_ACL_TYPE_ETYPE;

conf.acl_key.first = KYLAND_ACE_BIT_1;

conf.acl_key.dmac_bc = KYLAND_ACE_BIT_ANY;

conf.acl_key.dmac_mc = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.cfi = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.tagged = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.usr_prio.mask = 0;

conf.acl_key.vlan.vid.mask = 0;

conf.acl_key.frame.etype.dmac.value[0] = 0x00;

conf.acl_key.frame.etype.dmac.value[1] = 0x00;

conf.acl_key.frame.etype.dmac.value[2] = 0x00;

conf.acl_key.frame.etype.dmac.value[3] = 0x00;

conf.acl_key.frame.etype.dmac.value[4] = 0x00;

conf.acl_key.frame.etype.dmac.value[5] = 0x20;

KYLAND_OS_MEMSET(conf.acl_key.frame.etype.dmac.mask,0xff,6);

conf.acl_key.frame.etype.smac.value[0] = 0x00;

conf.acl_key.frame.etype.smac.value[1] = 0x00;

conf.acl_key.frame.etype.smac.value[2] = 0x00;

conf.acl_key.frame.etype.smac.value[3] = 0x00;

conf.acl_key.frame.etype.smac.value[4] = 0x00;

conf.acl_key.frame.etype.smac.value[5] = 0x10;

KYLAND_OS_MEMSET(conf.acl_key.frame.etype.smac.mask,0xff,6);

conf.acl_action.forward = 1;

conf.acl_action.rt = 1;

conf.acl_action.remark_qos =1;

conf.acl_action.qos_cos = 5;

conf.acl_action.qos_dp = 0;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

### LLC_ENTRY

添加LLC_ENTRY类型ACL，index=100，key为dmac=00:00:00:00:00:55、smac=00:00:00:00:00:48、Dsap = 0xaa，ssap = 0xaa，Ctrl = 3，action为重定向到port11。

kyland_rc kd5886_llc_entry_acl_add()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = 100;

conf.acl_key.type = KYLAND_ACL_TYPE_LLC;

conf.acl_key.first = KYLAND_ACE_BIT_1;

conf.acl_key.dmac_bc = KYLAND_ACE_BIT_ANY;

conf.acl_key.dmac_mc = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.cfi = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.tagged = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.usr_prio.mask = 0;

conf.acl_key.vlan.vid.mask = 0;

conf.acl_key.frame.llc.dmac.value[0] = 0x00;

conf.acl_key.frame.llc.dmac.value[1] = 0x00;

conf.acl_key.frame.llc.dmac.value[2] = 0x00;

conf.acl_key.frame.llc.dmac.value[3] = 0x00;

conf.acl_key.frame.llc.dmac.value[4] = 0x00;

conf.acl_key.frame.llc.dmac.value[5] = 0x55;

KYLAND_OS_MEMSET(conf.acl_key.frame.llc.dmac.mask,0xff,6);

conf.acl_key.frame.llc.smac.value[0] = 0x00;

conf.acl_key.frame.llc.smac.value[1] = 0x00;

conf.acl_key.frame.llc.smac.value[2] = 0x00;

conf.acl_key.frame.llc.smac.value[3] = 0x00;

conf.acl_key.frame.llc.smac.value[4] = 0x00;

conf.acl_key.frame.llc.smac.value[5] = 0x48;

KYLAND_OS_MEMSET(conf.acl_key.frame.llc.smac.mask,0xff,6);

conf.acl_key.frame.llc.llc.value[0] = 0xaa;

conf.acl_key.frame.llc.llc.value[1] =0xaa;

conf.acl_key.frame.llc.llc.value[2] =0x3;

conf.acl_key.frame.llc.llc.value[3] = 0;

conf.acl_key.frame.llc.llc.mask[0] = 0xff;

conf.acl_key.frame.llc.llc.mask[1] = 0xff;

conf.acl_key.frame.llc.llc.mask[2] = 0xff;

conf.acl_key.frame.llc.llc.mask[3] = 0xff;

conf.acl_action.forward = 1;

conf.acl_action.rt = 1;

conf.acl_action.redir_cmd = KYLAND_ACL_REDIRECT_CMD_PORT;

conf.acl_action.redir_id = 11;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

### SNAP_ENTRY

添加SNAP_ENTRY类型ACL，index=100，key为dmac=00:00:00:00:00:55、smac=00:00:00:00:00:48、snap_type=0x88b5、snap_org_code=0，action为重定向到port11。

kyland_rc kd5886_snap_entry_acl_add()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = 100;

conf.acl_key.type = KYLAND_ACL_TYPE_SNAP;

conf.acl_key.first = KYLAND_ACE_BIT_1;

conf.acl_key.dmac_bc = KYLAND_ACE_BIT_ANY;

conf.acl_key.dmac_mc = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.cfi = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.tagged = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.usr_prio.mask = 0;

conf.acl_key.vlan.vid.mask = 0;

conf.acl_key.frame.snap.dmac.value[0] = 0x00;

conf.acl_key.frame.snap.dmac.value[1] = 0x00;

conf.acl_key.frame.snap.dmac.value[2] = 0x00;

conf.acl_key.frame.snap.dmac.value[3] = 0x00;

conf.acl_key.frame.snap.dmac.value[4] = 0x00;

conf.acl_key.frame.snap.dmac.value[5] = 0x55;

KYLAND_OS_MEMSET(conf.acl_key.frame.snap.dmac.mask,0xff,6);

conf.acl_key.frame.snap.smac.value[0] = 0x00;

conf.acl_key.frame.snap.smac.value[1] = 0x00;

conf.acl_key.frame.snap.smac.value[2] = 0x00;

conf.acl_key.frame.snap.smac.value[3] = 0x00;

conf.acl_key.frame.snap.smac.value[4] = 0x00;

conf.acl_key.frame.snap.smac.value[5] = 0x48;

KYLAND_OS_MEMSET(conf.acl_key.frame.snap.smac.mask,0xff,6);

conf.acl_key.frame.snap.snap.value[0] = 0;

conf.acl_key.frame.snap.snap.value[1] = 0;

conf.acl_key.frame.snap.snap.value[2] = 0;

conf.acl_key.frame.snap.snap.mask[0] = 0xff;

conf.acl_key.frame.snap.snap.mask[1] = 0xff;

conf.acl_key.frame.snap.snap.mask[2] = 0xff;

conf.acl_key.frame.snap.snap.value[3] = 0x88;

conf.acl_key.frame.snap.snap.value[4] = 0xb5;

conf.acl_key.frame.snap.snap.mask[3] = 0xff;

conf.acl_key.frame.snap.snap.mask[4] = 0xff;

conf.acl_action.forward = 1;

conf.acl_action.rt = 1;

conf.acl_action.redir_cmd = KYLAND_ACL_REDIRECT_CMD_PORT;

conf.acl_action.redir_id = 11;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

### ARP_ENTRY

添加ARP_ENTRY类型ACL，index=100，key为smac=00:00:00:00:00:48、arp=1、req=1，action为copy cpu。

kyland_rc kd5886_arp_entry_test()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = 100;

conf.acl_key.type = KYLAND_ACL_TYPE_ARP;

conf.acl_key.first = KYLAND_ACE_BIT_1;

conf.acl_key.dmac_bc = KYLAND_ACE_BIT_ANY;

conf.acl_key.dmac_mc = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.cfi = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.tagged = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.usr_prio.mask = 0;

conf.acl_key.vlan.vid.mask = 0;

conf.acl_key.frame.arp.smac.value[0] = 0x00;

conf.acl_key.frame.arp.smac.value[1] = 0x00;

conf.acl_key.frame.arp.smac.value[2] = 0x00;

conf.acl_key.frame.arp.smac.value[3] = 0x00;

conf.acl_key.frame.arp.smac.value[4] = 0x00;

conf.acl_key.frame.arp.smac.value[5] = 0x48;

KYLAND_OS_MEMSET(conf.acl_key.frame.arp.smac.mask,0xff,6);

conf.acl_key.frame.arp.arp = 1;

conf.acl_key.frame.arp.req = 1;

conf.acl_action.forward = 1;

conf.acl_action.rt = 1;

conf.acl_action.cpu = 1;

conf.acl_action.cpu_queue = 0;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

### IP_OTHER_ENTRY

添加IP_OTHER_ENTRY类型ACL，index=100，key为sip=1.1.1.1、dip=20.20.20.20，action为重定向port11。

kyland_rc kd5886_ip_other_entry_acl_add()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = 100;

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

conf.acl_action.forward = 1;

conf.acl_action.rt = 1;

conf.acl_action.redir_cmd = KYLAND_ACL_REDIRECT_CMD_PORT;

conf.acl_action.redir_id = 11;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

### IP_TCP_ENTRY

添加IP_TCP_ENTRY类型ACL，index=100，key为sip=1.1.1.1、dip=20.20.20.20、proto=6、L4_sport=123、L4_dport=456，action为重定向port11。

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

conf.acl_action.redir_cmd = KYLAND_ACL_REDIRECT_CMD_PORT;

conf.acl_action.redir_id = 11;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

### IP_UDP_ENTRY

添加IP_UDP_ENTRY类型ACL，index=100，key为sip=1.1.1.1、dip=20.20.20.20、proto=17、L4_sport=123、L4_dport=456，action为重定向port11。

kyland_rc kd5886_ip_udp_entry_acl_add()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = 100;

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

conf.acl_key.frame.ipv4.proto.value = 17;

conf.acl_key.frame.ipv4.proto.mask = 0xff;

conf.acl_action.forward = 1;

conf.acl_action.rt = 1;

conf.acl_action.redir_cmd = KYLAND_ACL_REDIRECT_CMD_PORT;

conf.acl_action.redir_id = 11;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

### IP_MAC_ENTRY

添加IP_MAC_ENTRY类型ACL，index=100，key为smac=00-00-00-00-00-48、dmac=00-00-00-00-00-55、Sip=1.1.1.1、Dip = 20.20.20.20、L4_sport=10000、L4_dport=800、proto=6，action为重定向port11

kyland_rc kd5886_ipmac_entry_acl_add()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

u32 i;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = 100;

conf.acl_key.type = KYLAND_ACL_TYPE_IPV4;

conf.acl_key.first = KYLAND_ACE_BIT_1;

conf.acl_key.dmac_bc = KYLAND_ACE_BIT_ANY;

conf.acl_key.dmac_mc = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.cfi = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.tagged = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.usr_prio.mask = 0;

conf.acl_key.vlan.vid.mask = 0;

conf.acl_key.ip_mac = 1;

conf.acl_key.ip_dmac.value[0] = 0xe0;

conf.acl_key.ip_dmac.value[1] = 0x11;

conf.acl_key.ip_dmac.value[2] = 0x22;

conf.acl_key.ip_dmac.value[3] = 0x33;

conf.acl_key.ip_dmac.value[4] = 0x44;

conf.acl_key.ip_dmac.value[5] = 0x55;

KYLAND_OS_MEMSET(conf.acl_key.ip_dmac.mask,0xff,6);

conf.acl_key.ip_smac.value[0] = 0x00;

conf.acl_key.ip_smac.value[1] = 0x00;

conf.acl_key.ip_smac.value[2] = 0x00;

conf.acl_key.ip_smac.value[3] = 0x00;

conf.acl_key.ip_smac.value[4] = 0x00;

conf.acl_key.ip_smac.value[5] = 0x48;

KYLAND_OS_MEMSET(conf.acl_key.ip_smac.mask,0xff,6);

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

conf.acl_action.redir_cmd = KYLAND_ACL_REDIRECT_CMD_PORT;

conf.acl_action.redir_id = 11;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

### IP6_STD_ENTRY

添加IP6_STD_ENTRY类型ACL，index=100，key为sip = 2000::2、dip=2000::1、sport=123、dport=456、proto=6，action为重定向port11。

kyland_rc kd5886_acl_ipv6_entry_add(u32 *param,u32 *other)

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = 100;

conf.acl_key.type = KYLAND_ACL_TYPE_IPV6_STD;

conf.acl_key.first = KYLAND_ACE_BIT_1;

conf.acl_key.dmac_bc = KYLAND_ACE_BIT_ANY;

conf.acl_key.dmac_mc = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.cfi = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.tagged = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.usr_prio.mask = 0;

conf.acl_key.vlan.vid.mask = 0;

conf.acl_key.frame.ipv6_std.sip.value[0] = 0x20;

conf.acl_key.frame.ipv6_std.sip.value[1] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[2] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[3] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[4] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[5] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[6] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[7] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[8] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[9] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[10] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[11] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[12] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[13] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[14] = 0x00;

conf.acl_key.frame.ipv6_std.sip.value[15] = 0x02;

conf.acl_key.frame.ipv6_std.sip.mask[0] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[1] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[2] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[3] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[4] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[5] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[6] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[7] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[8] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[9] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[10] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[11] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[12] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[13] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[14] = 0xff;

conf.acl_key.frame.ipv6_std.sip.mask[15] = 0xff;

conf.acl_key.frame.ipv6_std.dip.value[0] = 0x20;

conf.acl_key.frame.ipv6_std.dip.value[1] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[2] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[3] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[4] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[5] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[6] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[7] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[8] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[9] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[10] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[11] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[12] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[13] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[14] = 0x00;

conf.acl_key.frame.ipv6_std.dip.value[15] = 0x01;

conf.acl_key.frame.ipv6_std.dip.mask[0] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[1] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[2] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[3] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[4] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[5] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[6] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[7] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[8] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[9] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[10] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[11] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[12] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[13] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[14] = 0xff;

conf.acl_key.frame.ipv6_std.dip.mask[15] = 0xff;

conf.acl_key.frame.ipv6_std.proto.value = 6;

conf.acl_key.frame.ipv6_std.proto.mask = 0xff;

conf.acl_key.frame.ipv6_std.dport.in_range = 0;

conf.acl_key.frame.ipv6_std.dport.high = 456;

conf.acl_key.frame.ipv6_std.dport.low = 456;

conf.acl_key.frame.ipv6_std.sport.in_range = 0;

conf.acl_key.frame.ipv6_std.sport.high = 123;

conf.acl_key.frame.ipv6_std.sport.low = 123;

conf.acl_action.forward = 1;

conf.acl_action.rt = 1;

conf.acl_action.redir_cmd = param[6]&0x3;

conf.acl_action.redir_id = (param[6]>>8)&0xffff;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

### MPLS_ENTRY

添加MPLS_ENTRY类型ACL，index=100，key为label=48，action为copy cpu。

kyland_rc kd5886_mpls_entry_test()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_acl_t id;

kyland_acl_cfg_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_cfg_t));

id = 100;

conf.acl_key.type = KYLAND_ACL_TYPE_MPLS;

conf.acl_key.first = KYLAND_ACE_BIT_1;

conf.acl_key.dmac_bc = KYLAND_ACE_BIT_ANY;

conf.acl_key.dmac_mc = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.cfi = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.tagged = KYLAND_ACE_BIT_ANY;

conf.acl_key.vlan.usr_prio.mask = 0;

conf.acl_key.vlan.vid.mask = 0;

conf.acl_key.frame.mpls.label[0].val.value = 48;

conf.acl_key.frame.mpls.label[0].val.mask =0xff;

conf.acl_action.forward = 1;

conf.acl_action.rt = 1;

conf.acl_action.cpu = 1;

conf.acl_action.cpu_queue = 0;

KYLAND_RC(kyland_acl_add(inst, id, &conf));

return rc;

}

### 基于端口使能ACL

端口48使能ip_mac类型第一次查找

kyland_rc kd5886_acl_port_cfg()

{

kyland_rc rc = KYLAND_RC_OK;

kyland_inst_t inst;

inst = NULL;

kyland_port_t port;

kyland_acl_port_key_t conf;

KYLAND_OS_MEMSET(&conf,0,sizeof(kyland_acl_port_key_t));

port = 48;

conf.sec_ena = KYLAND_ACL_LOOKUP_FIRST;

conf.ip_mac_ena = KYLAND_ACL_LOOKUP_FIRST;

KYLAND_RC(kyland_acl_port_key_cfg(inst, port, &conf));

return rc;

}
