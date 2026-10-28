# kyland_sdk_2.0.0 收发报文应用开发指南

kyland_sdk_2.0.0

收发报文应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

# PACKET支持特性

支持上层软件填写IFH头和SDK填写IFH头方式发送报文

支持指定端口发送报文

支持按业务端口转发报文方式发送报文

支持OAM报文特殊发送报文

支持根据接收报文类型设置上送优先级队列和设置队列速率

支持根据接收报文类型设置限速

# 2PACKET业务和表项

# PACKET API接口

## 3.1接收报文接口

### 功能简介

芯片内核驱动接收到报文，通过中断通知SDK，上层软件需要提供报文处理接口，通过初始化注册到SDK。

对于上层软件报文处理接口，建议的实现方式：

分配存储报文的buffer，将报文数据拷贝过去；

不要在报文处理接口中处理报文，建议通过队列等方式异步处理报文。

### API接口

typedef 	kyland_rc (*kyland_pkt_rx_process)(kyland_pkt_rx_st *rx_st,u8 * frame,u8 * ifh);

参数:

kyland_pkt_rx_st *rx_st	//收到的报文部分信息

u8 * frame	//收到的报文头指针

u8 * ifh	//收到的报文ifh头指针

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_pkt_init(kyland_inst_t inst,kyland_pkt_rx_process rxFunc);

参数:

kyland_inst_t inst	//芯片实例

kyland_pkt_rx_process rxFunc	//挂载的接收处理函数

返回值:

操作码.

### 数据结构

typedef struct

{

kyland_recv_type pktType;

u16 length;        	   //报文有效长度

u16 offset;        	   //从头开始偏移offset字节，为报文头开始位置

kyland_port_t src_port;     //报文进入的软件端口号

kyland_chipid_t   src_chip_id;   //报文进入的chipid,0/1

kyland_chipport_t src_chip_port;

kyland_vid_t cl_vid;	   //报文进入的转发vid

u8   cl_qos;

/*timestamp*/

u64 timestamp;

//以下信息主要用于lrn报文学习

bool lrn_isGlag;			  //报文源端口是否为glag

u8   lrn_glagid_lport;        //isGlag=1时，表示glagid;否则表示lport

u8   lrn_chipid;

bool lrn_hubspk;

bool lrn_isNhi;

u16  lrn_nhi_isdx;    //当lrn_nhi=0时，表示isdx;否则表示nhi,代表pw

u8 queue;

u8 code;

u16 acl_index;	//0xffff is invalid

} kyland_pkt_rx_st;

typedef enum {

pkt_type_bpdu 	= 1,

pkt_type_gxrp 	= 2,

pkt_type_ag     = 3,

pkt_type_igmp   = 4,

pkt_type_v4mc_ctrl 	= 5,

pkt_type_v6mc_ctrl 	= 6,

pkt_type_hop_by_hop = 7,

pkt_type_mld     = 8,

pkt_type_sv   = 9,

pkt_type_ttl_fail = 10,

pkt_type_fib_miss = 11,

pkt_type_ip_header_err = 12,

pkt_type_ip_option    = 13,

pkt_type_l3_non_ip    = 14,

pkt_type_label_miss    = 15,

pkt_type_l3_local     = 16,

pkt_type_bfd_echo     = 17,

pkt_type_cpu_lrn      = 18,

pkt_type_dip_no_match = 19,

pkt_type_sip_no_match = 20,

pkt_type_arp_invalid  = 21,

pkt_type_dst_mac_all_zero = 22,

pkt_type_ipmc_ctrl_miss   = 23,

pkt_type_ipmc_miss    = 24,

pkt_type_sflow        = 25,

pkt_type_vstax_fwd_err = 26,

pkt_type_zero_dst       = 27,

pkt_type_mirror         = 0xfd,

pkt_type_lrn_pkt        = 0xfe,

pkt_type_all            = 0xff   //sdk未分类

}kyland_recv_type;

## 发送报文接口

### 功能简介

芯片支持指定端口发送报文，支持按业务端口转发报文方式发送报文，支持OAM报文特殊发送报文。

SDK提供两种方式发送接口：

由SDK封装芯片需要的IFH头，软件提供报文内容和发送报文方式和基本信息；

由上层软件封装芯片需要的IFH头，SDK不做处理直接转发到芯片。

### API接口

kyland_rc kyland_pkt_send(kyland_inst_t inst,kyland_pkt_tx_st *tx_st,u8 * packet);

参数:

kyland_inst_t inst	//芯片实例

kyland_pkt_tx_st *tx_st	//报文发送时的信息

u8 * packet	//报文头指针

返回值:

操作码.

### 数据结构

typedef enum {

send_invalid     = 0,

send_by_port    = 1,		//发送到指定的端口

send_by_fwd    = 2,		//芯片按普通端口接收报文做转发处理

send_by_l3fwd   = 3,		//芯片做l3uc转发，sdk修改目的mac为本机mac

send_by_mask   = 4,		//修改cpu插入报文的软件端口号,报文按照面板端口插入报文处理

send_by_ifh     = 5,		//由软件填写ifh头(包括转发信息)，sdk不做修改直接发送到信息

send_to_ups     = 6,		//发送给单个cpu

send_to_gcpu    = 7		//发送给全部cpu ,只对kd6630有效

}kyland_send_mode;

typedef struct

{

kyland_send_mode sendMode;

u16 length;        	   //报文长度,包含报文尾部的4byte FCS,但不包括ifh头长度

u16 offset;        	   //从头开始偏移offset字节，为报文头开始位置

//以下字段在sendMode = send_by_port有效；其它情况无效,要求填写0

kyland_port_t dest_port; //报文转发的目的端口

kyland_vport_t  evport;//报文转发的逻辑端口，无填写0

//以下字段在sendMode = send_by_port/send_by_fwd有效；其它情况无效,要求填写0

kyland_vid_t vid;	   //报文进入的转发vid

u8   qos;              //报文转发的优先级0~7,7最高

ucBool tagged;         //报文是否携带需要处理的vlantag，可固定填写1

ucBool noRewrite;           //不修改报文任何内容

//以下字段在sendMode = send_by_mask有效；其它情况无效

kyland_port_t src_port;     //修改cpu插入报文的软件端口号,报文按照面板端口插入报文处理

//以下字段在sendMode = send_by_ifh有效；其它情况无效

u8 * pIFH;    //指向ifh头的指针

} kyland_pkt_tx_st;

## 端口协议报文处理接口

### 功能简介

SDK提供设置基于端口协议报文处理方式，包括正常转发，丢弃，上送cpu和copy to cpu。

### API接口

/*设置基于端口的协议报文处理配置*/

kyland_rc kyland_packet_rx_port_reg_set(const kyland_inst_t inst, const kyland_port_no_t  port_no,

const kyland_packet_rx_port_reg_t *const reg);

参数:

const kyland_inst_t inst	//芯片实例

const kyland_port_no_t  port_no	//端口号

const kyland_packet_rx_port_reg_t *const reg	//端口配置的数据结构

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

/*获取基于端口的协议报文处理配置*/

kyland_rc kyland_packet_rx_port_reg_get(const kyland_inst_t inst, const kyland_port_no_t port_no,

kyland_packet_rx_port_reg_t *const conf);

参数:

const kyland_inst_t inst	//芯片实例

const kyland_port_no_t port_no	//端口号

kyland_packet_rx_port_reg_t *const conf	//获取到的配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

/*设置全局的协议报文处理配置*/

kyland_rc kyland_packet_rx_reg_set(const kyland_inst_t inst, const kyland_packet_rx_global_reg_t  *const reg);

参数:

const kyland_inst_t inst	//芯片实例

const kyland_packet_rx_global_reg_t  *const reg	//全局配置结构体

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

/*获取全局的协议报文处理配置*/

kyland_rc kyland_packet_rx_reg_get(const kyland_inst_t inst, kyland_packet_rx_global_reg_t  *const reg);

参数:

const kyland_inst_t inst	//芯片实例

kyland_packet_rx_global_reg_t  *const reg	//获取到的全局配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

/*设置全局的协议报文上送cpu的队列*/

kyland_rc kyland_packet_rx_queue_set(const kyland_inst_t inst,

const kyland_packet_rx_queue_map_t  *const map);

参数:

const kyland_inst_t inst	//芯片实例

const kyland_packet_rx_queue_map_t  *const map	//全局配置协议报文上送cpu的队列

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

/*获取全局的协议报文上送cpu的队列信息*/

kyland_rc kyland_packet_rx_queue_get(const kyland_inst_t inst,

kyland_packet_rx_queue_map_t  *const map);

参数:

const kyland_inst_t inst	//芯片实例

kyland_packet_rx_queue_map_t  *const map	//获取到的协议报文全局上送cpu的队列信息

返回值:

操作码.

### 数据结构

typedef enum {

KYLAND_PACKET_REG_FORWARD,  /**< Forward normally */

KYLAND_PACKET_REG_DISCARD,  /**< Discard */

KYLAND_PACKET_REG_CPU_COPY, /**< Copy to CPU */

KYLAND_PACKET_REG_CPU_ONLY  /**< Redirect to CPU */

} kyland_packet_reg_type_t;

------------------------------------------------------------------------------------------------------------------------------------------

/*全局配置信息数据结构*/

typedef struct

{

ucBool label_15_cpu_only;

ucBool label_14_cpu_only;

ucBool label_13_cpu_only;

ucBool label_12_cpu_only;

ucBool label_11_cpu_only;

ucBool label_10_cpu_only;

ucBool label_9_cpu_only;

ucBool label_8_cpu_only;

ucBool label_7_cpu_only;

ucBool label_6_cpu_only;

ucBool label_5_cpu_only;

ucBool label_4_cpu_only;

ucBool label_3_cpu_only;

ucBool label_2_cpu_only;

ucBool label_1_cpu_only;

ucBool label_0_cpu_only;

ucBool ipv6_mc_ctrl_cpu_copy;

ucBool ipv4_mc_ctrl_cpu_copy;

ucBool ipv4_bc_cpu_copy;

ucBool dip6_addr_violation_cpu_only;  /**< Redirect ipv6 frame's DIP falls into the given range frames to the CPU  IPv6 DIP[127:24] = 104'hFFFF7F  */

ucBool mpls_term_to_ip_or_l3vpn_nonip_cpu_only;	/**< Redirect ip or mpls term to ip/l3vpn with internal header is not ipv4/ipv6 frames to the CPU*/

ucBool lpm_lookup_miss_cpu_only;	/**< Redirect ip ormpls term to ip/l3vpn lpm miss frames to the CPU*/

ucBool ip_bfd_cpu_only;	/**< Redirect ip bfd echo frames to the CPU*/

ucBool mpls_bfd_cpu_only;

ucBool ipv6_local_route_cpu_only;

ucBool ipv4_local_route_cpu_only;

ucBool mpls_swap_ttl_cpu_only;	/**< Redirect mpls going swap processing with ttl < 2 failure frames to the CPU*/

ucBool mc_rpf_filter_cpu_only;	/**< Redirect IPv4 or IPv6 packet with RPF check failure frames to the CPU*/

ucBool dip4_addr_violation_cpu_only[4];

ucBool sip_addr_violation_cpu_only[3];

ucBool rleg_ip_hrd_fail_cpu_only;	/**< Redirect IPv4 error frames to the CPU*/

ucBool ip6_hopbyhop_cpu_only;	/**< Redirect IPv6 frames with HOP by HOP options frames to the CPU*/

ucBool ip4_hopbyhop_cpu_only;	/**< Redirect IPv4 frames with IP4 options frames to the CPU*/

ucBool ip6_hc_cpu_only;	/**< Redirect IPv6 UC  with a hop-limit less than 2 frames to the CPU*/

ucBool ip4_ttl_cpu_only;	/**< Redirect IPV4 TTL < 2 frames to the CPU*/

ucBool ipmc_ttl_cpu_copy;	/**< IP multicast frames with TTL less than 2 Copy to CPU */

ucBool cw_msb4_not_zero_cpu_only;	/**< CW hihg 4bit not 0 Copy to CPU */

ucBool pw_ttl_less_cpu_only;	/**< Redirect pw label ttl < 2 frames to the CPU */

ucBool ipmc_ctrl_cpu_copy;            /**< IP MC control (DIP 224.0.0.x) Copy to CPU */

ucBool igmp_cpu_only;        	/**< Redirect IGMP frames to the CPU */

ucBool mld_cpu_only;         	 /**< Redirect MLD frames to the CPU */

ucBool dmac_cpu_copy;		/**< Forwarded frames that have the CPU_COPY flag frames Copy to CPU */

ucBool flood_cpu_copy;		/**< Flooded frames Copy to CPU */

ucBool lrn_limit_cpu_copy;	/**< Frames exceeding learn limits Copy to CPU */

ucBool locked_portmove_cpu_copy;	/**< frames from known stations with changed port Copy to CPU */

ucBool smac_cpu_copy;		/**< frames from known stations with the CPU_COPY bit set in the SOURCE entry Copy to CPU */

kyland_packet_reg_type_t sip_no_match_reg;	/**< When sip check is fail, action will be excuted*/

kyland_packet_reg_type_t dip_no_match_reg;	/**< When dip check is fail, action will be excuted*/

ucBool next_lrn_all_cpu_copy;	/**< Frames received on a front port with SMAC entry nxt_lrn_all set, Copy to CPU */

ucBool refresh_stack_cpu_copy;	/**< Frames received on a stack port with SMAC address which cause a refresh of the age bit Copy to CPU */

ucBool refresh_front_cpu_copy;	/**< Frames received on a front port with SMAC address which cause a refresh of the age bit Copy to CPU */

ucBool move_stack_cpu_copy;	/**< Frames received on a stack port with SMAC address previous learned on another port Copy to CPU */

ucBool new_stack_cpu_copy;	/**< Frames received on a stack port with new SMAC address Copy to CPU */

ucBool move_front_cpu_copy;	/**< Frames received on a front port with SMAC address previous learned on another port Copy to CPU */

ucBool new_front_cpu_copy;	/**< Frames with new SMAC address received on a front port Copy to CPU */

kyland_packet_reg_type_t ipmc_miss_reg;	/**< Controls ipmc control packet's operation when lookup mac table mis*/

ucBool zero_dest_cpu_only;

} kyland_packet_rx_global_reg_t;

------------------------------------------------------------------------------------------------------------------------------------------

/*基于port的配置信息数据结构*/

typedef struct {

kyland_packet_reg_type_t bpdu_reg[16];  	   	/**< BPDU range: 01-80-C2-00-00-0X */

kyland_packet_reg_type_t garp_reg[16];  	   	/**< GARP range: 01-80-C2-00-00-2X */

kyland_packet_reg_type_t bpdu_1ag_reg[16];     /**< BPDU range: 01-80-C2-00-00-3X */

ucBool ipv6_mc_ctrl_cpu_only;     	/**< Redirect IP6_ICMP_HOP_BY_HOP frames to the CPU*/

ucBool hop_by_hop_icmp_cpu_only;  /**< Redirect IP6_HOP_BY_HOP and ICMP frames to the CPU*/

ucBool sv_cpu_copy;		/**< SV packets Copy to CPU */

ucBool ipmc_ctrl_cpu_copy; 	/**<  IP MC Control frames Copy to CPU*/

ucBool igmp_cpu_only; 	/**< Redirect IGMP frames to the CPU*/

ucBool mld_cpu_only;		 /**< Redirect MLD frames to the CPU*/

ucBool ipv6_mc_cpu_copy;	/**< IPv6 Multicast control packets Copy to CPU */

ucBool lrn_cpu_copy;		/**< Bit mask with ports which configures CPU copy operation of Frames  received from unknown or known stations with changed port. */

} kyland_packet_rx_port_reg_t;

------------------------------------------------------------------------------------------------------------------------------------------

/*全局上送队列信息数据结构*/

typedef struct

{

kyland_packet_rx_queue_t bpdu_1ag_queue[16];    /**< 802.1ag frames */

kyland_packet_rx_queue_t bpdu_queue[16];      	/**< BPDUs */

kyland_packet_rx_queue_t garp_queue[16];    	/**< GARP frames */

kyland_packet_rx_queue_t learn_queue;       	/**< Learn frames */

kyland_packet_rx_queue_t igmp_queue;        	/**< IGMP/MLD frames */

kyland_packet_rx_queue_t ipmc_ctrl_queue;   	/**< IP multicast control frames */

kyland_packet_rx_queue_t mac_vid_queue;     	/**< MAC address table */

kyland_packet_rx_queue_t stack_queue;       	/**< CPU-generated VStaX traffic */

kyland_packet_rx_queue_t sflow_queue;       	/**< SFlow-marked frames */

kyland_packet_rx_queue_t lrn_all_queue;     	/**< Learn-all queue - JR-48 and JR-Stacking only */

kyland_packet_rx_queue_t ipv6_hop_by_hop_icmp_queue;

kyland_packet_rx_queue_t sv_queue;

kyland_packet_rx_queue_t dst_mac_all_zero_queue;

kyland_packet_rx_queue_t arp_invalid_queue;

kyland_packet_rx_queue_t cpu_uc_fail_qu;   	//包括cpu_ip_ttl_fail_qu/cpu_uc_fail_qu/cpu_rleg_ip_hdr_fail_qu/mpls_route_fail_qu/cpu_rleg_qu(non-ip)

kyland_packet_rx_queue_t cpu_mc_fail_qu; 		//rpf check fail

kyland_packet_rx_queue_t cpu_rleg_ip_opt_qu;

kyland_packet_rx_queue_t ip_local_route_qu;

kyland_packet_rx_queue_t mpls_bfd_echo_qu;

kyland_packet_rx_queue_t label_excp_queue;

kyland_packet_rx_queue_t ipv6_mc_ctrl_queue;

kyland_packet_rx_queue_t ipv4_mc_ctrl_queue;

kyland_packet_rx_queue_t vccv_ctrl_queue;

kyland_packet_rx_queue_t dmac_queue;

kyland_packet_rx_queue_t smac_queue;

kyland_packet_rx_queue_t dip_no_match_queue;

kyland_packet_rx_queue_t sip_no_match_queue;

kyland_packet_rx_queue_t vstax_to_triggered_queue; /**< Configures the CPU queue for VSTAX2 triggered events*/

kyland_packet_rx_queue_t ipmc_data_miss_queue;

kyland_packet_rx_queue_t ipmc_ctrl_miss_queue;

kyland_packet_rx_queue_t zero_dest_queue;

} kyland_packet_rx_queue_map_t;

## 发包器接口

### 功能简介

芯片支持自动发包功能,构造完报文后使用自动发包api接口可以实现报文的自动发送.报文发送时可以指定端口和模式

分为三种发送模式:
1.发送N次, 发包间隔为1s

2.按照帧速率发送报文(fps)

3.按照比特率发送报文(bps)

### API接口

/*自动发包接口,需要指定使用的afi frame table index */

kyland_rc kyland_pkt_afi_send(kyland_inst_t inst,u16 index,kyland_pkt_afi_tx_t *afi_tx_t,u8 * packet);

参数:

kyland_inst_t inst	//芯片实例

u16 index	//afi frame index

kyland_pkt_afi_tx_t *afi_tx_t	//发送报文的信息

u8 * packet	//发送报文的头指针

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

/*自动发包时占用afi资源, 当不需要再进行报文发送时建议将afi资源释放掉*/

kyland_rc kyland_pkt_afi_frame_del(kyland_inst_t inst,u16 index,u8 dti_index,kyland_pkt_tx_mode_t mode);

参数:

kyland_inst_t inst	//芯片实例

u16 index	//frame table index

kyland_pkt_tx_mode_t mode	//发包模式

返回值:

操作码.

### 数据结构

/*自动发包相关结构体*/

typedef struct{

u16 length;        	   //报文有效长度,不包括ifh头长度

u16 offset;        	   //从头开始偏移offset字节，为报文头开始位置

u8   qos;               //报文转发的优先级0~7,7最高

kyland_port_t dest_port;    //报文转发的目的端口

kyland_pkt_tx_mode_t mode;

ucBool dti_bw;	   //DTI bandwidth : 1 >= 5Gbps , 0 < 5Gbps

union{

u32 burstSize; 	//only used for mode == KYLAND_PKT_TX_BURSTS

u32 fps;		//only used for mode == KYLAND_PKT_TX_FPS

u32 bps;		//only used for mode == KYLAND_PKT_TX_BPS

}info;

u8 dti_index; 		//DTI index 0~31, 最大值为 31

}kyland_pkt_afi_tx_t;

------------------------------------------------------------------------------------------------------------------------------------------

/*mode 选择数据结构*/

typedef enum{

KYLAND_PKT_TX_BURSTS,

KYLAND_PKT_TX_FPS,

KYLAND_PKT_TX_BPS

}kyland_pkt_tx_mode_t;
