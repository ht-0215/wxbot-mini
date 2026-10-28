# kyland_sdk_2.0.0 MPLS应用开发指南

kyland_sdk_2.0.0

MPLS应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 应用简介	5

1.1 MPLS基本业务	5

1.2 MPLS VPN业务	5

1.3 VPWS业务	6

1.4 VPLS业务	6

1.5 组播VPN业务	7

1.6 保护1:1模型	8

2 SDK API及应用示例	10

2.1 SDK API	10

2.1.1 LSP标签配置接口	10

2.1.2 PW标签配置接口	12

2.1.3 LSP下一跳配置接口	14

2.1.4 LSP封装配置接口	15

2.1.5 MPLS ARP配置接口	17

2.1.6 PW下一跳配置接口	18

2.1.7 PW封装配置接口	19

2.1.8 VSI配置接口	22

2.1.9 SERVICE配置接口	23

2.2 SDK应用示例	25

2.2.1 MPLS VPN业务	25

2.2.2 VPWS业务	33

2.2.3 VPLS业务	42

2.2.4 组播VPN业务	51

2.2.5 保护1:1模型	57

3 芯片设计	61

3.1 MPLS报文的主处理流程	62

3.1.1 MPLS Label Hash Lookup	63

3.1.2 Terminate To L3VPN Process	63

3.1.3 Terminate To VPLS Process	65

3.1.4 SWAP To NHI Process	66

3.1.5 QOS MAPPING and DSCP UPDATE	67

3.2 报文入隧道流程	68

3.2.1 IP报文入隧道流程	68

3.2.2 L2报文入VPLS/VPWS 隧道流程	69

3.3 VPLS/VPWS常见问题	70

3.3.1 VPLS组播源剪枝	70

3.3.2 VPLS水平分割	71

3.3.3 vlan tag	73

# 应用简介

## MPLS基本业务

由于IP转发需要查找最长匹配路由，效率低；同时由于IP的best eFfort转发，不利于部署流量工程，所以引入了MPLS，MPLS通过一个20bits的label来表示转发信息，这个转发信息是本地使用，而不是全局的,同一个label值在不同设备上代表的意义不同，只有分配label的设备自己可以正确解释label的含义。

KD5886新增加了ILM表和PW TOKEN/LSP TOKEN表来处理MPLS转发，ILM通过报文label查找，得到转发目的信息，TOKEN表用于新LABEL的封装。

## MPLS VPN业务

由于label的局部意义，label可以表示隧道，业务，QOS等含义；而MPLS VPN正是基于label的这些特性，将网络设备虚拟化为多个转发实例来应用。

MPLS VPN按实现层次分，可分为MPLS L3VPN、MPLS L2VPN，其中MPLS L2VPN可分为VPLS和VLL/PWE3。

MPLS VPN中按照设备功能可以划分为： CE,PE,P； CE为用户侧边缘设备，接入运营商网络；PE为运营商边缘设备，为CE设备提供接入服务；P为运营商网络中间设备。 与普通MPLS转发区别在于，需要加上区分VPN的VC LABEL。

MPLSL3VPN：从L3VPN的用户角度看，共享网络（公网）就像一台路由器，将VPN各站点连接起来。公网为每个VPN建立专用的路由表和转发表。

KD5886基于L3接口 VLANIF接入L3VPN,VPN instance通过vmid中vrf_id字段来表示，FIB的key为vrf_id+ip。

## VPWS业务

基于MPLS的l2vpn，点到点的连接，与E-LINE业务模型类似，只是隧道不是基于VLAN的隧道，而是基于MPLS的隧道，引入PW（pesudowire）来带区分PE之间的不同VPN。

分段PW,CE之间的PW分成多段PW，在芯片层面可以不感知。

通过基于ISDX/ESDX的转发来实现VPWS的转发。

## VPLS业务

基于MPLS的l2vpn，多点到多点的连接，与E-BRIDGE业务模型类似，只是隧道不是基于VLAN的隧道，而是基于MPLS的隧道，引入PW（pesudowire）来带区分PE之间的不同VPN。

PE之间全连接(HUB连接)，从PE1的流量，直接到PE2/PE3,不会经过中间PE，需要考虑PE之间的广播环路，这个不能用stp来解决，引入水平分割来实现：从PE1来的流量，不能转发到PE2。

在VPLS组网的时候，由于PE之间是全连接，如果PE设备多，则连接数量增加快；引入SPOKE PW来解决这个问题，这个PW只与某一个HUB PE连接，不与其它PE连接，流量经过这个PE转发到其它PW，可以将这个PW看做一个普通service-instance接入。

通过VSI来表示转发实例，与VLAN表的功能类似。

AC侧MAC地址学习内容为src port+isdx，PW侧MAC地址学习内容为lrn_nhi。

## 组播VPN业务

组播 VPN（Virtual Private Network，虚拟专用网络）是一项在VPN 网络中实现组播传输的技术。KD5886组播VPN采用mLDP方案：公网运行mLDP协议，使用MPLS P2MP组播隧道。每VPN的每root节点建立P2MP隧道，业务模型采用IP入P2MP隧道模型。转发表项模型请参考MPLS组播模型。

mLDP协议定义了组播LSP，包括P2MP和MP2MP；KD5886支持P2MP隧道（下游分配label方式）,不支持MP2MP隧道。

P2MP LSP由一个根节点，零个或多个传输节点以及一个或多个叶节点组成。由叶节点负责P2MP LSP的建立和撤销。根节点需要建立转发状态，并将业务流映射到P2MP LSP。一条P2MP LSP允许业务流从一个根节点（或入口节点）传输到多个叶节点（或出口节点）。

P2MP包括以下4类节点：

Ingress节点：P2MP的root节点，将业务映射到P2MP LSP；IP组播业务通过查FIB表映射到P2MP隧道。

Transmit节点：P2MP隧道的中间节点，按照label做mpls转发，将业务分发到多个下游节点。

Leaf节点：P2MP隧道的终点，隧道终结后按照内层信息转发；IP组播业务做IP组播转发。

Baud节点：承担Transmit节点和Leaf节点功能，业务流程需要转发到LSP的下游节点，同时还需要转发到非P2MP域的接收者。

KD5886在Baud节点时，采用环回方式来实现Leaf节点功能。配置增加一个本地节点到LSP　swap组中，按照正常的Transmit节点转发，这样会复制一份流量到本地节点，通过环回到上行，做IP组播转发。

## 保护1:1模型

IP Frr/ MPLS Frr/ VPN Frr等1:1保护模型：存在主备路径，当主路径UP,选择主路径，否则选择备路径转发。

通过查找路由表/ILM表/ISDX表(VPWS)/MAC表，得到NHI；查NHI保护表PROT_NHI，获得主NHI/备份NHI和prot_group_id。

通过prot_group_id查状态表PROT_ST，获得主路径(主NHI)的状态，进行选路，得到下一跳出口nexthop。

PROT_ST表示PROT_NHI主路径的状态，可以由芯片根据OAM状态做关联，也可以由软件修改。

# SDK API及应用示例

## SDK API

### LSP标签配置接口

#### 功能简介

包括lsp标签添加、删除和查询API接口。与PW标签共用6*1024芯片ilm表项资源，由上层软件管理芯片ilm表项资源。

#### API接口

kyland_rc kyland_mpls_lsp_cfg(kyland_inst_t inst,

kyland_lsp_index_t lspIndex,

kyland_lsp_st *lsp)

kyland_rc kyland_mpls_lsp_del(kyland_inst_t inst,

kyland_lsp_index_t lspIndex)

kyland_rc kyland_mpls_lsp_get(kyland_inst_t inst,

kyland_lsp_index_t lspIndex,

kyland_lsp_st *lsp)

#### 数据结构

typedef struct

{

ucBool valid;		/*0:invalid,1:valid*/

kyland_mpls_qos_domain_t  domain_id;

kyland_qos_exp_t  exp;		/*exp_cmd=exp_pipe时有效*/

kyland_lsp_mode_t  lsp_mode;

kyland_exp_cmd_t   exp_cmd;	/*exp_uniform for mapping exp, other for set exp value*/

kyland_ttl_cmd_t   ttl_cmd;	/*ttl_uniform for copy exp, other for set ttl value*/

u8	  ttl_id;              /*ttl_cmd = ttl_pipe,选择ttl配置值,范围0~3*/

u32 tunnel_esdx_en;  /*PW ESDX最高位*/

kyland_vport_t vport;   /*tunnel_esdx */

u8  labelNum;   		/* 0: no label(swap3),1: one label, 2: two labels*/

kyland_label_t label0;		/* labelNum=1/2时有效*/

kyland_label_t label1;		/* labelNum=2时有效*/

kyland_lsp_arp_index_t arpIndex;

}kyland_lsp_st;

### PW标签配置接口

#### 功能简介

包括PW/VC标签添加、删除和查询API接口。与LSP标签共用6*1024芯片ilm表项资源，由上层软件管理芯片ilm表项资源。

#### API接口

kyland_rc kyland_mpls_pw_cfg(kyland_inst_t inst,

kyland_pw_index_t pwIndex,

kyland_pw_st *pw)

kyland_rc kyland_mpls_pw_del(kyland_inst_t inst,

kyland_pw_index_t pwIndex)

kyland_rc kyland_mpls_pw_get(kyland_inst_t inst,

kyland_pw_index_t pwIndex,

kyland_pw_st *pw)

#### 数据结构

typedef struct

{

ucBool valid;		/*0:invalid,1:valid*/

kyland_mpls_qos_domain_t  domain_id;

kyland_qos_exp_t  exp;		/*exp_cmd=exp_pipe时有效*/

kyland_lsp_mode_t  lsp_mode;

kyland_exp_cmd_t   exp_cmd;	/*exp_uniform for mapping exp, other for set exp value*/

kyland_ttl_cmd_t   ttl_cmd;	/*ttl_uniform for copy exp, other for set ttl value*/

u8  ttl_id;                     /*ttl_cmd = ttl_pipe,选择ttl配置值,范围0~3*/

kyland_vport_t vport;

ucBool  cw ;		/*0:no cw,1:cw*/

ucBool  hub_spk ;		 /*0:spk pw, 1:hub pw*/

ucBool	entropy;		 /*0:no entropy label,1:entropy label enable*/

kyland_pw_tag_mode_t tag_mode;

kyland_vccv_type_t	vccv_type;

u8  tpid_id;		/*tag_mode = pw_tag_mode_vlan,选择tpid配置值,范围0~3*/

u16 s_vlan;

u32 pw_esdx_en;

kyland_vport_t evport;          /* this is pw_esdx */

kyland_lsp_index_t lspIndex;

kyland_label_t label;

}kyland_pw_st;

### LSP下一跳配置接口

#### 功能简介

包括nhi-lsp表添加、删除和查询API接口。与ip-arp和nhi-pw共用8*1024芯片nhi表项资源，由上层软件管理芯片nhi表项资源。

#### API接口

kyland_rc kyland_nhi_lsp_cfg(kyland_inst_t inst,

kyland_nhi_index_t nhiIndex,

kyland_lsp_nhi_st *nhi)

kyland_rc kyland_nhi_lsp_del(kyland_inst_t inst,

kyland_nhi_index_t nhiIndex)

kyland_rc kyland_nhi_lsp_get(kyland_inst_t inst,

kyland_nhi_index_t nhiIndex,

kyland_lsp_nhi_st *nhi)

#### 数据结构

typedef struct {

ucBool  p2mp;      		/*p2mp隧道时使用*/

kyland_outport_t outport;      /*p2mp=false时有效*/

kyland_lsp_index_t token;      /*p2mp=false时有效,0~2k-1*/

kyland_mc_index_t  mcIndex;  /*p2mp=true时有效*/

kyland_rleg_t      evmid;

ucBool             check_rleg;

u16 tunnel_policer_id;

} kyland_lsp_nhi_st;

### LSP封装配置接口

#### 功能简介

包括lsp封装添加、删除和查询API接口。2*1024芯片LSP封装表项资源，由上层软件管理芯片LSP封装表项资源。

#### API接口

kyland_rc kyland_mpls_lsp_cfg(kyland_inst_t inst,

kyland_lsp_index_t lspIndex,

kyland_lsp_st *lsp);

kyland_rc kyland_mpls_lsp_get(kyland_inst_t inst,

kyland_lsp_index_t lspIndex,

kyland_lsp_st *lsp);

kyland_rc kyland_mpls_lsp_del(kyland_inst_t inst,

kyland_lsp_index_t lspIndex);

#### 数据结构

typedef struct

{

ucBool valid;			/*0:invalid,1:valid*/

kyland_mpls_qos_domain_t  domain_id;

kyland_qos_exp_t  exp;			/*exp_cmd=exp_pipe时有效*/

kyland_lsp_mode_t  lsp_mode;

kyland_exp_cmd_t   exp_cmd;	/*exp_uniform for mapping exp, other for set exp value*/

kyland_ttl_cmd_t   ttl_cmd;	/*ttl_uniform for copy exp, other for set ttl value*/

u8	  ttl_id;              /*ttl_cmd = ttl_pipe,选择ttl配置值,范围0~3*/

u32 tunnel_esdx_en;               /*PW ESDX最高位*/

kyland_vport_t vport;           /*tunnel_esdx */

u8  labelNum;   		/* 0: no label(swap3),1: one label, 2: two labels*/

kyland_label_t label0;		/* labelNum=1/2时有效*/

kyland_label_t label1;		/* labelNum=2时有效*/

kyland_lsp_arp_index_t arpIndex;

}kyland_lsp_st;

### MPLS ARP配置接口

#### 功能简介

包括MPLS-ARP添加、删除和查询API接口。芯片包含MPLS-ARP 1*1024表项资源，由上层软件管理芯片ARP表项资源。

#### API接口

kyland_rc kyland_mpls_arp_cfg(kyland_inst_t inst,

kyland_lsp_arp_index_t arpIndex,

kyland_lsp_arp_st *arp);

kyland_rc kyland_mpls_arp_get(kyland_inst_t inst,

kyland_lsp_arp_index_t arpIndex,

kyland_lsp_arp_st *arp);

kyland_rc kyland_mpls_arp_del(kyland_inst_t inst,

kyland_lsp_arp_index_t arpIndex);

#### 数据结构

typedef struct

{

ucBool valid;

kyland_rleg_t    evmid;

kyland_mac_t     dst_mac;

}kyland_lsp_arp_st;

### PW下一跳配置接口

#### 功能简介

包括nhi-pw表添加、删除和查询API接口。与ip-arp和nhi-lsp共用8*1024芯片nhi表项资源，由上层软件管理芯片nhi表项资源。

#### API接口

kyland_rc kyland_nhi_pw_cfg(kyland_inst_t inst,

kyland_nhi_index_t nhiIndex,

kyland_pw_nhi_st *nhi);

kyland_rc kyland_nhi_pw_get(kyland_inst_t inst,

kyland_nhi_index_t nhiIndex,

kyland_pw_nhi_st *nhi);

kyland_rc kyland_nhi_pw_del(kyland_inst_t inst,

kyland_nhi_index_t nhiIndex);

#### 数据结构

typedef struct {

kyland_outport_t outport;

kyland_pw_index_t token;/*0~4k-1*/

kyland_rleg_t      evmid;

ucBool             check_rleg;

u16 tunnel_policer_id;

} kyland_pw_nhi_st;

### PW封装配置接口

#### 功能简介

包括PW封装添加、删除和查询API接口。 4*1024芯片PW封装表项资源，由上层软件管理芯片PW封装表项资源。

#### API接口

kyland_rc kyland_mpls_pw_cfg(kyland_inst_t inst,

kyland_pw_index_t pwIndex,

kyland_pw_st *pw);

kyland_rc kyland_mpls_pw_get(kyland_inst_t inst,

kyland_pw_index_t pwIndex,

kyland_pw_st *pw);

kyland_rc kyland_mpls_pw_del(kyland_inst_t inst,

kyland_pw_index_t pwIndex);

#### 数据结构

typedef struct

{

ucBool valid;				/*0:invalid,1:valid*/

kyland_mpls_qos_domain_t  domain_id;

kyland_qos_exp_t  exp;			/*exp_cmd=exp_pipe时有效*/

kyland_lsp_mode_t  lsp_mode;

kyland_exp_cmd_t   exp_cmd;	/*exp_uniform for mapping exp, other for set exp value*/

kyland_ttl_cmd_t   ttl_cmd;		/*ttl_uniform for copy exp, other for set ttl value*/

u8	  ttl_id;              /*ttl_cmd = ttl_pipe,选择ttl配置值,范围0~3*/

kyland_vport_t vport;

ucBool  cw ;			 /*0:no cw,1:cw*/

ucBool  hub_spk ;			 /*0:spk pw, 1:hub pw*/

ucBool	entropy;			 /*0:no entropy label,1:entropy label enable*/

kyland_pw_tag_mode_t tag_mode;

kyland_vccv_type_t	vccv_type;

u8  tpid_id;		/*tag_mode = pw_tag_mode_vlan,选择tpid配置值,范围0~3*/

u16 s_vlan;

u32 pw_esdx_en;

kyland_vport_t evport;

kyland_lsp_index_t lspIndex;

kyland_label_t label;

}kyland_pw_st;

### VSI配置接口

#### 功能简介

包括VSI添加、删除和查询API接口。2*1024芯片VSI表项资源，由上层软件管理芯片表项资源。

#### API接口

kyland_rc kyland_vsi_cfg(kyland_inst_t inst,

kyland_vsi_t vsiid,

kyland_vsi_st *vsi);

kyland_rc kyland_vsi_get(kyland_inst_t inst,

kyland_vsi_t vsiid,

kyland_vsi_st *vsi);

kyland_rc kyland_vsi_del(kyland_inst_t inst,

kyland_vsi_t vsiid);

#### 数据结构

typedef struct {

kyland_msti_t msti;                      /* MSTP instance */

ucBool        learning;              	 /* Learning for EVC */

ucBool       flood_disable;

ucBool       mirror;   /**< Enable/disable mirroring */

ucBool       sec_fwd_ena;

u8           gid;

u8       	mc_miss_opc;

ucBool       ipv4_l2_mc_ena;

ucBool       ipv6_l2_mc_ena;

kyland_vid_t fid;      /**< Forwarding ID for SVL/IVL control */

kyland_mc_index_t         flood_mcIndex;

} kyland_vsi_st;

### SERVICE配置接口

#### 功能简介

Service与vport一一对应，可以配置service业务类型vpws/vpls，API接口包括service添加、删除和查询API接口。8*1024芯片service表项资源，由上层软件管理芯片表项资源。

#### API接口

kyland_rc kyland_service_cfg(kyland_inst_t inst,

kyland_vport_t ivport,

kyland_service_st *service);

kyland_rc kyland_service_get(kyland_inst_t inst,

kyland_vport_t ivport,

kyland_service_st *service);

kyland_rc kyland_service_del(kyland_inst_t inst,

kyland_vport_t ivport);

#### 数据结构

typedef struct

{

kyland_service_type_t service_type;

kyland_service_p2p_fwd_t fwd_type;     /*service_type=service_type_p2p时有效*/

ucBool lrn_vport_ena;

ucBool lrn_mac_ena;

u16 policy_id;

union

{

kyland_outport_t 	outport;   /*fwd_type=p2p_fwd_to_ac时有效*/

kyland_nhi_index_t  nhiIndex; /*fwd_type=p2p_fwd_to_pw时有效*/

kyland_mc_index_t	mcIndex;  /*fwd_type=p2p_fwd_to_multi_pw时有效*/

}dst;

} kyland_service_st;

## SDK应用示例

### MPLS VPN业务

#### IP报文入隧道

IP报文入隧道，指的是IP报文进入芯片端口，从芯片其它端口出去的时候IP报文作为payload，外层封装的是MPLS标签。

KD5886芯片对IP报文入隧道的要求是必须要命中LPM。

所以下面不重复介绍LPM/RE相关的配置。

(完整代码可以参考CLI： KD-CLI(MPLS)#mpls test ingress)

#### 示例组网

Port4      Port5

Port4进入的报文内容为：

e0 11 22 33 44 01 00 00 00 12 30 10 81 00 00 04

08 00 45 00 00 14 00 7b 00 00 80 fd 00 00 c0 a8

00 02 01 02 03 04

IP报文从Port4进入，封装为MPLS的报文从Port5出。

#### 配置RE表中的NHI

这里的NHI表的表项类型为1（token），而不是0（arp），表示token值域为13bits，最高位用来区分指向的是lsp token还是 pw token（pw高位置1）。

kyland_pw_nhi_st nhi;

unsigned int  nhi_index;

KYLAND_OS_MEMSET(&nhi,0,sizeof(kyland_pw_nhi_st));

nhi_index = 1000;//RE table中的NHI index

nhi.token = 1000;

nhi.outport.port = 5;

kyland_nhi_pw_cfg(0,nhi_index,&nhi);

#### 配置PW token

根据上面配置的token index=1000,配置pw token表,并且需要指定lsp的索引

kyland_pw_st  pw;

unsigned int  pw_index;

KYLAND_OS_MEMSET(&pw,0,sizeof(kyland_pw_st));

pw_index = 1000;

pw.valid = 1;

pw.label = 100;

pw.lspIndex = 1000;

kyland_mpls_pw_cfg(0,pw_index,&pw);

#### 配置LSP token

根据上面配置的lspIndex =1000,配置lsp token表,并且需要指定ARP 索引

kyland_lsp_st lsp;

unsigned int  lsp_index;

KYLAND_OS_MEMSET(&lsp,0,sizeof(kyland_lsp_st));

lsp_index = 1000;

lsp.valid = 1;

lsp.labelNum = 1;

lsp.label0 = 1000;

lsp.arpIndex = 100;

kyland_mpls_lsp_cfg(0,lsp_index,&lsp);

#### 配置ARP table

根据上面配置的arpIndex =100,配置ARP表

kyland_lsp_arp_st arp;

unsigned int arp_index;

unsigned char arp_mac[6] = {0xe0,0x11,0x22,0x33,0x44,0x02};//对端三层接口的MAC

KYLAND_OS_MEMSET(&arp,0,sizeof(kyland_lsp_arp_st));

arp_index = 100;

arp.valid = 1;

/*配置为出接口的arp.evmid，需要根据kyland_l3_rleg_add(0, &rleg_conf)

获得的rleg_conf.rleg_id配置arp.evmid

*/

arp.evmid = 5;//配置为出接口的evmid

KYLAND_OS_MEMCPY(arp.dst_mac.addr,arp_mac,6);

kyland_mpls_arp_cfg(0,arp_index,&arp);

#### IP报文出隧道

IP报文出隧道，指的是payload为IP的mpls报文进入芯片端口，从芯片其它端口出去的时候为IP报文，匹配LPM,根据RE选择NHI。

KD5886芯片对IP报文出隧道的要求是进入端口的MPLS报文的MAC地址匹配三层MAC,剥离标签后的动作为匹配LPM,所以下面不重复介绍LPM/RE相关的配置。(完整代码可以参考CLI： KD-CLI(MPLS)#mpls test egress)

#### 示例组网

Port4      Port5

Port5进入的报文内容为：

e0 11 22 33 44 01 00 00 00 12 30 10 81 00 00 05

88 47 00 06 41 40 00 3e 81 40 45 00 00 14 00 7b

00 00 80 fd 00 00 c0 a8 00 02 01 02 03 05

封装为MPLS的报文从Port5入，IP报文从Port4出，

#### 配置外层标签动作为pop

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 100;

ilm_index = 100;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_pop;

kyland_ilm_add(0,label,ilm_index,&ilm);

#### 配置内层标签动作为l3vpn

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 1000;

ilm_index = 1000;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_l3vpn;

ilm.fwdinfo.ip.vrf_id = 5;//入端口的三层接口vrf id

kyland_ilm_add(0,label,ilm_index,&ilm);

#### MPLS SWAP

KD5886芯片对MPLS报文SWAP的要求是进入端口的MPLS报文的MAC地址匹配三层MAC.

同时需要创建不同的三层接口,参照LPM的配置. (完整代码可以参考CLI： KD-CLI(MPLS)#mpls test swap)

#### 示例组网

Port4      Port5

Port5进入的报文内容为：

e0 11 22 33 44 01 00 00 00 12 30 10 81 00 00 05

88 47 00 06 41 40 00 3e 81 40 45 00 00 14 00 7b

00 00 80 fd 00 00 c0 a8 00 02 01 02 03 05

封装为MPLS的报文从Port5入，SWAP后MPLS报文从Port4出。

#### 配置需要匹配交换的label, ILM为swap的动作,同时需要指定NHI

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 100;

ilm_index = 1000;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_swap;

ilm.fwdinfo.mpls.nhiIndex = 1000;

kyland_ilm_add(0,label,ilm_index,&ilm);

#### 配置ILM表中指定的NHI

这里的NHI表的表项类型为1（token），并且指向lsp token。

kyland_lsp_nhi_st nhi;

unsigned int  nhi_index;

KYLAND_OS_MEMSET(&nhi,0,sizeof(kyland_lsp_nhi_st));

nhi_index = 1000;//RE table中的NHI index

nhi.token = 1000;

nhi.outport.port = 4;

kyland_nhi_lsp_cfg (0,nhi_index,&nhi);

#### 配置LSP token

根据上面配置的lspIndex =1000,配置lsp token表,并且需要指定ARP index

kyland_lsp_st lsp;

unsigned int  lsp_index;

KYLAND_OS_MEMSET(&lsp,0,sizeof(kyland_lsp_st));

lsp_index = 1000;

lsp.valid = 1;

lsp.labelNum = 1;

lsp.label0 = 1000;

lsp.arpIndex = 100;

kyland_mpls_lsp_cfg(0,lsp_index,&lsp);

#### 配置ARP table

根据上面配置的arpIndex =100,配置ARP表

kyland_lsp_arp_st arp;

unsigned int arp_index;

unsigned char arp_mac[6] = {0xe0,0x11,0x22,0x33,0x44,0x02};//对端三层接口的MAC

KYLAND_OS_MEMSET(&arp,0,sizeof(kyland_lsp_arp_st));

arp_index = 100;

arp.valid = 1;

/*配置为出接口的arp.evmid，需要根据kyland_l3_rleg_add(NULL, &rleg_conf)

获得的rleg_conf.rleg_id配置arp.evmid

*/

arp.evmid = 4; KYLAND_OS_MEMCPY(arp.dst_mac.addr,arp_mac,6);

kyland_mpls_arp_cfg(0,arp_index,&arp);

### VPWS业务

KD5886通过ISDX table的配置实现VPWS的转发，AC到PW的ISDX由S0分配，PW到AC的ISDX由ILM分配。入隧道的报文需要根据is0规则匹配，出隧道的要求是进入端口的MPLS报文的MAC地址匹配三层MAC。(完整代码可以参考CLI： KD-CLI(MPLS)#mpls test vpws)

#### 示例组网

Port4      Port5

Port4进入的报文内容为：

00 00 00 00 00 01 00 00 00 00 00 02 81 00 00 04

08 00 45 00 00 14 00 7b 00 00 80 fd 00 00 c0 a8

00 02 01 02 03 04

Port5进入的报文内容为：

e0 11 22 33 44 01 00 00 00 12 30 10 81 00 00 05

88 47 00 06 41 40 00 3e 81 40 00 00 00 00 00 02

00 00 00 00 00 01 81 00 00 0a 08 00 45 00 00 14 00

7b 00 00 80 fd 00 00 c0 a8 00 02 01 02 03 05

L2报文从Port4入，封装后的MPLS报文从Port5出。

封装为MPLS报文从Port5入，解封装后的L2报文从Port4出。

#### 配置VSI,用于S0分配ISDX

kyland_vsi_st vsi_conf;

KYLAND_OS_MEMSET(&vsi_conf,0,sizeof(kyland_vsi_st));

vsi_conf.msti = 0;

vsi_conf.flood_disable = 1;

vsi_conf.fid = 0x17ff;

kyland_vsi_cfg(0, 2047, &vsi_conf);

#### 绑定AC到PW的ISDX=1002

根据报文的vlan+port创建is0/es0

具体实现可以参考L2应用开发指南

kyland_is0_entry_t ivport;

KYLAND_OS_MEMSET(&ivport,0,sizeof(kyland_is0_entry_t));

ivport.action.s1_dmac_ena = 0;

ivport.key.type = KYLAND_PA_TCM0_TYPE_DBL_VID; /* match type: double vlan */

ivport.key.data.dbl_vid.outer_tag.tagged = KYLAND_VCAP_BIT_1;

ivport.key.data.dbl_vid.outer_tag.vid.value = 4; /* match outer vlan */

ivport.key.data.dbl_vid.outer_tag.vid.mask = 0xfff;

ivport.key.data.dbl_vid.outer_tag.dei = KYLAND_VCAP_BIT_ANY;

ivport.key.data.dbl_vid.outer_tag.s_tag = KYLAND_VCAP_BIT_ANY;

ivport.key.port_no = 4; /* match ingress port */

ivport.action.valid = 1;

ivport.action.vid_ena = 1;

ivport.action.isdx = 1002; /* isdx */

ivport.action.vid = 0x17ff; /* forward vlan */

//hwIndex = 1002; /* is0 index to be set */

//vport_no =1002; /* isdx */

kyland_ivport_cfg(0, 1002, 1002, &ivport);

//端口4使能is0

kyland_l2_port_conf_t s0_conf;

KYLAND_OS_MEMSET(&s0_conf,0,sizeof(kyland_l2_port_conf_t));;

s0_conf.dlb_vid_ena = 1;

s0_conf.is0_ena = 1;

kyland_l2_port_conf_set(0, 4, &s0_conf);

//创建es0

kyland_es0_entry_t evport;

KYLAND_OS_MEMSET(&evport,0,sizeof(evport));

evport.key.onlyAction = 1;

evport.action.tag = KYLAND_PES_EPVT_TAG_PES_EPVT;

evport.action.vid_a = 0xfff;

evport.action.tag_sel = 1;

evport.action.valid = 1;

evport.action.tpid = 0;

evport.action.qos = KYLAND_PES_EPVT_QOS_PES_EPVT;

evport.action.esdx = 1002;

kyland_evport_cfg(0, 1002, 1002, &evport);

#### 创建PW到AC的ISDX=701

MPLS报文匹配label获得ISDX

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 1000;

ilm_index = 1000;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_vpws;//6

ilm.vport = 701;

ilm.fwdinfo.l2vpn.vsi_id = 2047;

kyland_ilm_add(0,label,ilm_index,&ilm);

#### 对于进入的mpls报文还需要pop外层标签

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 100;

ilm_index = 100;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_pop;

kyland_ilm_add(0,label,ilm_index,&ilm);

#### 配置入隧道

#### 配置NHI表

kyland_pw_nhi_st nhi;

unsigned int  nhi_index;

KYLAND_OS_MEMSET(&nhi,0,sizeof(kyland_pw_nhi_st));

nhi_index = 1210;//service.dst中的NHI index

nhi.token = 1000;

nhi.outport.port = 5;

kyland_nhi_pw_cfg(0,nhi_index,&nhi);

#### 配置PW token

根据上面配置的token index=1000,配置pw token表,并且需要指定lsp的索引

kyland_pw_st  pw;

unsigned int  pw_index;

KYLAND_OS_MEMSET(&pw,0,sizeof(kyland_pw_st));

pw_index = 1000;

pw.valid = 1;

pw.label = 100;

pw.lspIndex = 1000;

kyland_mpls_pw_cfg(0,pw_index,&pw);

#### 配置LSP token

根据上面配置的lspIndex =1000,配置lsp token表,并且需要指定ARP 索引

kyland_lsp_st lsp;

unsigned int  lsp_index;

KYLAND_OS_MEMSET(&lsp,0,sizeof(kyland_lsp_st));

lsp_index = 1000;

lsp.valid = 1;

lsp.labelNum = 1;

lsp.label0 = 1000;

lsp.arpIndex = 100;

kyland_mpls_lsp_cfg(0,lsp_index,&lsp);

#### 配置ARP table

根据上面配置的arpIndex =100,配置ARP表

kyland_lsp_arp_st arp;

unsigned int arp_index;

unsigned char arp_mac[6] = {0xe0,0x11,0x22,0x33,0x44,0x02};//对端三层接口的MAC

KYLAND_OS_MEMSET(&arp,0,sizeof(kyland_lsp_arp_st));

arp_index = 100;

arp.valid = 1;

arp.evmid = 5;//配置为出接口的evmid

KYLAND_OS_MEMCPY(arp.dst_mac.addr,arp_mac,6);

kyland_mpls_arp_cfg(0,arp_index,&arp);

#### 配置ISDX表

#### 配置ISDX=1002入隧道，入隧道的NHI=1210

kyland_service_st  service;

kyland_vport_t     vport_no = 0;

KYLAND_OS_MEMSET(&service,0,sizeof(kyland_service_st));

service.service_type = service_type_p2p;

service.fwd_type = p2p_fwd_to_pw;

service.dst.nhiIndex = 1210;

vport_no = 1002;

service.lrn_vport_ena = 1;

service.lrn_mac_ena = 1;

kyland_service_cfg(0, vport_no, &service);

#### 配置ISDX=701出隧道，入隧道的esdx=1002

kyland_service_st  service;

kyland_vport_t     vport_no = 0;

KYLAND_OS_MEMSET(&service,0,sizeof(kyland_service_st));

service.service_type = service_type_p2p;

service.fwd_type = p2p_fwd_to_ac;

service.dst.outport.evport = 1002;

service.dst.outport.port = 4;

vport_no = 701;

kyland_service_cfg(0, vport_no, &service);

### VPLS业务

KD5886通过VSI实现VPLS的转发，对于已知单播，如果是入隧道可以在VSI内查找到的MAC entry中的nhi_index; 如果是出隧道可以在VSI内查找到的MAC entry中的esdx。

如下图：

未知单播/广播/多播报文的实现，需要将端口加入组播叶子。请参考L3应用开发指南。(完整代码可以参考CLI： KD-CLI(MPLS)#mpls test vpls)

#### 示例组网

Port4      Port5

Port4进入的报文内容为：

00 00 00 00 00 01 00 00 00 00 00 02 81 00 00 04

08 00 45 00 00 14 00 7b 00 00 80 fd 00 00 c0 a8

00 02 01 02 03 04

Port5进入的报文内容为：

e0 11 22 33 44 01 00 00 00 12 30 10 81 00 00 05

88 47 00 06 41 40 00 3e 81 40 00 00 00 00 00 02

00 00 00 00 00 01 81 00 00 0a 08 00 45 00 00 14 00

7b 00 00 80 fd 00 00 c0 a8 00 02 01 02 03 05

L2报文从Port4入，封装后的MPLS报文从Port5出。

封装为MPLS报文从Port5入，解封装后的L2报文从Port4出。

#### 配置VSI

kyland_vsi_st vsi_conf;

KYLAND_OS_MEMSET(&vsi_conf,0,sizeof(kyland_vsi_st));

vsi_conf.learning = 1;

vsi_conf.flood_disable = 0;

vsi_conf.ipv4_l2_mc_ena =1;

vsi_conf.ipv6_l2_mc_ena = 1;

vsi_conf.fid = 4+4096;

vsi_conf.flood_mcIndex = 4+4096;

kyland_vsi_cfg(0, 4, &vsi_conf);

#### 绑定AC到PW的ISDX=2102

根据报文的vlan+port创建is0和es0

具体实现可以参考L2应用开发指南

kyland_is0_entry_t ivport;

KYLAND_OS_MEMSET(&ivport,0,sizeof(kyland_is0_entry_t));;

ivport.action.s1_dmac_ena = 0;

ivport.key.type = KYLAND_PA_TCM0_TYPE_DBL_VID; /* match type: double vlan */

ivport.key.data.dbl_vid.outer_tag.tagged = KYLAND_VCAP_BIT_1;

ivport.key.data.dbl_vid.outer_tag.vid.value = 4; /* match outer vlan */

ivport.key.data.dbl_vid.outer_tag.vid.mask = 0xfff;

ivport.key.data.dbl_vid.outer_tag.dei = KYLAND_VCAP_BIT_ANY;

ivport.key.data.dbl_vid.outer_tag.s_tag = KYLAND_VCAP_BIT_ANY;

ivport.action.valid = 1;

ivport.action.vid_ena = 1;

ivport.action.isdx = 2102; /* isdx */

ivport.action.vid = 4+4096; /* forward vlan */

ivport.key.port_no = portid; /* match ingress port */

//hwIndex = 2102; /* is0 index to be set */

//vport_no =2102; /* isdx */

kyland_ivport_cfg(0, 2102, 2102, &ivport);

//使能端口4的s0

kyland_l2_port_conf_t s0_conf;

KYLAND_OS_MEMSET(&s0_conf,0,sizeof(kyland_l2_port_conf_t));;

s0_conf.dlb_vid_ena = 1;

s0_conf.is0_ena = 1;

kyland_l2_port_conf_set(0, 4, &s0_conf);

//创建es0

kyland_es0_entry_t evport;

KYLAND_OS_MEMSET(&evport,0,sizeof(evport));

evport.key.onlyAction = 1;

evport.action.tag = KYLAND_PES_EPVT_TAG_PES_EPVT;

evport.action.vid_a = 0xfff;

evport.action.tag_sel = 1;

evport.action.valid = 1;

evport.action.tpid = 0;

evport.action.qos = KYLAND_PES_EPVT_QOS_PES_EPVT;

evport.action.esdx = 2102;

kyland_evport_cfg(0, 2102, 2102, &evport);

#### 配置ISDX表

这里的ISDX不像VPWS中的ISDX直接用于指定转发

kyland_service_st  service;

kyland_vport_t     vport_no = 0;

KYLAND_OS_MEMSET(&service,0,sizeof(kyland_service_st));

service.service_type = service_type_bridge;

service.lrn_vport_ena = 1;

service.lrn_mac_ena = 1;

vport_no = 2102;

kyland_service_cfg(0, vport_no, &service);

#### 配置类型为VPLS的ILM

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 1000;

ilm_index = 1000;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_vpls;

ilm.fwdinfo.l2vpn.vsi_id = 4;

ilm.fwdinfo.l2vpn.lrn_nhi = 1110;

kyland_ilm_add(0,label,ilm_index,&ilm);

#### 对于进入的mpls报文还需要pop外层标签

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 100;

ilm_index = 100;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_pop;

kyland_ilm_add(0,label,ilm_index,&ilm);

#### 配置入隧道

#### 配置NHI表

kyland_pw_nhi_st nhi;

unsigned int  nhi_index;

KYLAND_OS_MEMSET(&nhi,0,sizeof(kyland_pw_nhi_st));

nhi_index = 1110;// leaf.outInfo.l2pw.lrn_nhi,ilm.fwdinfo.l2vpn.lrn_nhi

nhi.token = 1000;

nhi.outport.port = 5;

kyland_nhi_pw_cfg(0,nhi_index,&nhi);

#### 配置PW token

根据上面配置的token index=1000,配置pw token表,并且需要指定lsp的索引

kyland_pw_st  pw;

unsigned int  pw_index;

KYLAND_OS_MEMSET(&pw,0,sizeof(kyland_pw_st));

pw_index = 1000;

pw.valid = 1;

pw.label = 100;

pw.lspIndex = 1000;

kyland_mpls_pw_cfg(0,pw_index,&pw);

#### 配置LSP token

根据上面配置的lspIndex =1000,配置lsp token表,并且需要指定ARP 索引

kyland_lsp_st lsp;

unsigned int  lsp_index;

KYLAND_OS_MEMSET(&lsp,0,sizeof(kyland_lsp_st));

lsp_index = 1000;

lsp.valid = 1;

lsp.labelNum = 1;

lsp.label0 = 1000;

lsp.arpIndex = 100;

kyland_mpls_lsp_cfg(0,lsp_index,&lsp);

#### 配置ARP table

根据上面配置的arpIndex =100,配置ARP表

kyland_lsp_arp_st arp;

unsigned int arp_index;

unsigned char arp_mac[6] = {0xe0,0x11,0x22,0x33,0x44,0x02};//对端三层接口的MAC

KYLAND_OS_MEMSET(&arp,0,sizeof(kyland_lsp_arp_st));

arp_index = 100;

arp.valid = 1;

arp.evmid = 5;//配置为出接口的evmid

KYLAND_OS_MEMCPY(arp.dst_mac.addr,arp_mac,6);

kyland_mpls_arp_cfg(0,arp_index,&arp);

#### 配置组播及叶子

在这里实现组播源剪枝。具体请参考l3应用开发指南

kyland_mc_init(0, 4 + 4096);

kyland_leaf_st leaf;

KYLAND_OS_MEMSET(&leaf,0,sizeof(kyland_leaf_st));

leaf.valid = 1;

leaf.type = leaf_type_l2_pw;

leaf.outInfo.l2pw.vport.port = 5;

leaf.outInfo.l2pw.token = 1000+4096;

leaf.outInfo.l2pw.lrn_nhi = 1110; //to source prune

//mc_index = 4 + 4096;

kyland_mc_leaf_add(0, 4 + 4096, &leaf);

KYLAND_OS_MEMSET(&leaf,0,sizeof(kyland_leaf_st));

leaf.valid = 1;

leaf.type = leaf_type_l2_ac;

leaf.outInfo.l2ac.lag_en = 0;

leaf.outInfo.l2ac.port = 4;

leaf.outInfo.l2ac.evport = 2102;//to source prune

kyland_mc_leaf_add(0, 4 + 4096, &leaf);

### 组播VPN业务

组播VPN业务有4种类型：

Ingress节点：

叶子节点类型为lsp token类型，根据lsp token加上LSP 标签入隧道。参考2.2.1.1

Transmit节点：

参考2.2.1.3

Leaf节点：

参考2.2.1.2

Baud节点：

KD5886在实现Baud节点的时候需要引入端口63做为换回端口，将MPLS IP组播流引入端口63做swap，从端口63出去的时候再将标签弹掉。

端口5收到的MPLS报文(payload为IPv4组播 )，标签交换后从端口4/6发去，同时产生一份IPv4组播从端口7/8出去。

见下图：(完整代码可以参考CLI： KD-CLI(MPLS)#mpls test p2mp)

#### 示例组网

Port7/8

Port5   Port4/6

Port5进入的报文内容为：

e0 11 22 33 44 01 00 00 00 12 30 10 81 00 00 05

88 47 00 06 41 40 45 00 00 14 00 7b 00 00 80 fd

00 00 01 02 03 04 e1 00 00 01

#### 配置ILM swap

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 100;

ilm_index = 100;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_swap;

ilm.fwdinfo.mpls.nhiIndex = 1000;

kyland_ilm_add(0,label,ilm_index,&ilm);

#### 配置ILM表中指定的NHI

NHI类型为p2mp

kyland_lsp_nhi_st nhi;

unsigned int  nhi_index;

KYLAND_OS_MEMSET(&nhi,0,sizeof(kyland_lsp_nhi_st));

nhi_index = 1000;// ilm.fwdinfo.mpls

nhi.p2mp = 1;

nhi.mcIndex = 100;

kyland_nhi_lsp_cfg (0,nhi_index,&nhi);

#### 配置组播组100及叶子

kyland_mc_init(0,100);

kyland_leaf_st leaf;

KYLAND_OS_MEMSET(&leaf,0,sizeof(kyland_leaf_st));

leaf.valid = 1;

leaf.type = leaf_type_l3_lsp;

leaf.outInfo.l3lsp.vport.port= 4;

leaf.outInfo.l3lsp.token   = 4;

kyland_mc_leaf_add(0,100,&leaf);

leaf.outInfo.l3lsp.vport.port= 6;

leaf.outInfo.l3lsp.token   = 6;

kyland_mc_leaf_add(0,100,&leaf);

leaf.outInfo.l3lsp.vport.port = 63;

leaf.outInfo.l3lsp.token = 63;

kyland_mc_leaf_add(0,100,&leaf);

#### 配置KEEP_IFH_SEL

kyland_port_ifh_t conf;

conf.ena_ifh_header = 1;

conf.keep_invalid_ifh_chksum_ena = 1;

kyland_port_ifh_conf_set(0, 63, &conf);

#### 配置lsp token

kyland_lsp_st lsp;

unsigned int  lsp_index;

KYLAND_OS_MEMSET(&lsp,0,sizeof(kyland_lsp_st));

lsp_index = 4;

lsp.valid = 1;

lsp.labelNum = 1;

lsp.label0 = 400;

lsp.arpIndex = 4;

kyland_mpls_lsp_cfg(0,lsp_index,&lsp);

lsp_index = 6;

lsp.label0 = 600;

lsp.arpIndex = 6;

kyland_mpls_lsp_cfg(0,lsp_index,&lsp);

lsp_index = 63;

lsp.label0 = 63;

lsp.arpIndex = 63;

kyland_mpls_lsp_cfg(0,lsp_index,&lsp);

#### 配置ARP table

根据上面配置的arpIndex ,配置ARP表

kyland_lsp_arp_st arp;

unsigned int arp_index;

unsigned char arp_mac[6] = {0xe0,0x11,0x22,0x33,0x44,0x04};//perr MAC

KYLAND_OS_MEMSET(&arp,0,sizeof(kyland_lsp_arp_st));

arp_index = 4;

arp.valid = 1;

arp.evmid = rleg_conf_4.rleg_id;//egress evmid

KYLAND_OS_MEMCPY(arp.dst_mac.addr,arp_mac,6);

kyland_mpls_arp_cfg(0,arp_index,&arp);

arp_mac[5] = 0x6;

KYLAND_OS_MEMSET(&arp,0,sizeof(kyland_lsp_arp_st));

arp_index = 6;

arp.valid = 1;

arp.evmid = rleg_conf_6.rleg_id;//egress evmid

KYLAND_OS_MEMCPY(arp.dst_mac.addr,arp_mac,6);

kyland_mpls_arp_cfg(0,arp_index,&arp);

arp_mac[5] = 0x1;

KYLAND_OS_MEMSET(&arp,0,sizeof(kyland_lsp_arp_st));

arp_index = 63;

arp.valid = 1;

arp.evmid = rleg_conf_5.rleg_id;//egress evmid， 跟入端口的evmid匹配

KYLAND_OS_MEMCPY(arp.dst_mac.addr,arp_mac,6);

kyland_mpls_arp_cfg(0,arp_index,&arp);

#### 配置从端口63换回的mpls报文pop

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 63;

ilm_index = 63;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_pop;

ilm.fwdinfo.ip.vrf_id = 5;//端口63的三层接口vrf id

kyland_ilm_add(0,label,ilm_index,&ilm);

#### 配置IP组播组

根据从端口63换回出来的mpls报文payload中的IP 组播地址配置组播及组播叶子

将端口7/8加入组播叶子，具体实现参考l3应用开发指南

### 保护1:1模型

KD5886芯片对保护1:1的实现都是通过NHI实现的，参考VPLS业务配置，这里只实现备份路径的配置和保护组的配置（完整代码可以参考CLI： KD-CLI(MPLS)# mpls test protect） 。对于FRR功能需要配合OAM的CC功能，请参考OAM应用开发指南。

#### 示例组网

Port6

Port4   Port5

Port4进入的报文内容为：

00 00 00 00 00 01 00 00 00 00 00 02 81 00 00 04

08 00 45 00 00 14 00 7b 00 00 80 fd 00 00 c0 a8

00 02 01 02 03 04

L2报文从Port4入，封装后的MPLS报文从Port5出。

当Port5的链路出现故障，封装后的MPLS报文从Port6出。

FRR只能对单播报文生效，如果是组播报文（包括未知单播和广播报文），需要软件删除原有的叶子，创建Port6的叶子

#### 配置备份路径

kyland_pw_nhi_st nhi;

unsigned int  nhi_index;

KYLAND_OS_MEMSET(&nhi,0,sizeof(kyland_pw_nhi_st));

nhi_index = 1111;//备份的NHI index

nhi.token = 1001;//备份的token

nhi.outport.port = 6;//备份端口号

kyland_nhi_pw_cfg(0,nhi_index,&nhi);

#### 配置PW token

根据上面配置的token index=1001,配置pw token表,并且需要指定lsp的索引

kyland_pw_st  pw;

unsigned int  pw_index;

KYLAND_OS_MEMSET(&pw,0,sizeof(kyland_pw_st));

pw_index = 1001;

pw.valid = 1;

pw.label = 101;

pw.lspIndex = 1001;

kyland_mpls_pw_cfg(0,pw_index,&pw);

#### 配置LSP token

根据上面配置的lspIndex =1000,配置lsp token表,并且需要指定ARP 索引

kyland_lsp_st lsp;

unsigned int  lsp_index;

KYLAND_OS_MEMSET(&lsp,0,sizeof(kyland_lsp_st));

lsp_index = 1001;

lsp.valid = 1;

lsp.labelNum = 1;

lsp.label0 = 1001;

lsp.arpIndex = 101;

kyland_mpls_lsp_cfg(0,lsp_index,&lsp);

#### 配置ARP table

根据上面配置的arpIndex =101,配置ARP表

kyland_lsp_arp_st arp;

unsigned int arp_index;

unsigned char arp_mac[6] = {0xe0,0x11,0x22,0x33,0x44,0x03};//对端三层接口的MAC

KYLAND_OS_MEMSET(&arp,0,sizeof(kyland_lsp_arp_st));

arp_index = 101;

arp.valid = 1;

arp.evmid = 101;//配置为出接口的evmid

KYLAND_OS_MEMCPY(arp.dst_mac.addr,arp_mac,6);

kyland_mpls_arp_cfg(0,arp_index,&arp);

#### 配置保护组

kyland_l3_prot_nhi_conf_t prot_nhi_conf;

kyland_l3_prot_group_conf_t prot_group_conf;

prot_nhi_conf.prot_group_index = 1;

prot_nhi_conf.backup_nh_index = 1111;

kyland_l3_prot_nhi_set(0, 1110, &prot_nhi_conf);

prot_group_conf.status = 1;

prot_group_conf.type = 0;

kyland_l3_prot_group_set(0, 1, &prot_group_conf);

# 芯片设计

## MPLS报文的主处理流程

### MPLS Label Hash Lookup

### Terminate To L3VPN Process

下图连接主流程图中“Terminate To L3VPN”

Terminate To VPWS Process

下图连接主流程图中“Terminate To VPWS”

### Terminate To VPLS Process

下图连接主流程图中“Terminate To VPLS”

### SWAP To NHI Process

下图连接主流程图中“SWAP To NHI”

### QOS MAPPING and DSCP UPDATE

## 报文入隧道流程

### IP报文入隧道流程

下图是 IP报文进入MPLS，省略了进MPLS无关的分支。

### L2报文入VPLS/VPWS 隧道流程

入口报文进入L2后，如果PFS_L2::ISDX_LOOKUP_ENA配置使能且ISDX索引不为0，则根据请求的ISDX索引读取ISDX Table。通常入VPLS/VPWS隧道及出VPLS/VPWS隧道，ISDX不为0。PFS_L2::ISDX_BASED_FWD_ENA为1入VPWS隧道，否则入VPLS隧道。

## VPLS/VPWS常见问题

### VPLS组播源剪枝

VPLS对于未知单播、广播和组播需要在VSI域内广播，成员包括AC侧的端口和PE侧的端口。这时候需要避免端口注入的流量又发回原端口，引入源剪枝的概念。如下图：

port4为AC端口，port5/6为PE端口，port4接收到的报文可以泛洪到port5/6，但不能再从port4发送出去。

示例组网

Port5

Port4   Port6

进行源端口剪枝, 使用ISDX = ESDX?/ ILM.lrn_nhi = MC_LEAF.lrn_nhi ?来判断是否进行源剪枝，相等则剪枝。具体实现请参考配置组播及叶子

### VPLS水平分割

VPLS水平分割用hub/spoke剪枝实现，如果入口携带的报文来自于hub，并且查找命中后的结果也为hub，则进行剪枝操作。

示例组网

Port5

Port4   Port6

Port4为AC端口，Port5/6为PE端口

Port5/6收到的数据不能转到Port6/5，只能转发到Port4。

Port5/6接收到数据是通过ILM，所以在ILM. FWD_INFO上标记HUB；发送数据是通过token，所以在PW token. Hubspk上标记HUB。

#### 配置ILM. FWD_INFO上标记HUB

kyland_ilm_st ilm;

unsigned int  label;

unsigned int  ilm_index;

label = 1000;

ilm_index = 1000;

KYLAND_OS_MEMSET(&ilm,0,sizeof(kyland_ilm_st));

ilm.valid = 1;

ilm.fwd_cmd = mpls_fwd_cmd_vpls;

ilm.fwdinfo.l2vpn.vsi_id = 4;

ilm.fwdinfo.l2vpn.lrn_nhi = 1110;

ilm.fwdinfo.l2vpn.hub_spk = 1;

kyland_ilm_add(0,label,ilm_index,&ilm);

#### 配置PW token. Hubspk上标记HUB

kyland_pw_st  pw;

unsigned int  pw_index;

KYLAND_OS_MEMSET(&pw,0,sizeof(kyland_pw_st));

pw_index = 1000;

pw.valid = 1;

pw.label = 100;

pw.hub_spk = 1;

pw.lspIndex = 1000;

kyland_mpls_pw_cfg(0,pw_index,&pw);

### vlan tag

#### 对于mpls_termination模式中的VPLS/VPWS终结

VPLS/VPWS终结会对内层tag进行处理，报文是否携带tag，根据ILM.FWD_INFO.TAG_MODE来决定:

| ILM.FWD_INFO.TAG_MODE | Result |
| --- | --- |
| TAG_MODE=0 | 不删除 |
| TAG_MODE=1 | 报文携带stag, 则删除stag |

#### 对于mpls_tunnel_encap模式下的入L2VPN隧道

入L2VPN隧道则根据pw_token表中的tag_mode以及is0.vlan_pop_cnt对内层tag进行操作。

| Tag_mode | is0.vlan_pop_cnt | Result |
| --- | --- | --- |
| Tag_mode=0 | vlan_pop_cnt =0 | 报文没有携带stag,不需要处理 |
| Tag_mode=0 | vlan_pop_cnt =1/2 | 报文携带stag，则根据pop_cnt删除1~2层tag |
| Tag_mode=1 | vlan_pop_cnt =0 | 报文没有携带stag，则需要添加一个stag |
| Tag_mode=1 | vlan_pop_cnt =1 | 报文携带stag,删掉该stag,如果查pw表s-vlan!=0xfff，则根据PW表生成stag，否则保留原s-tag |
| Tag_mode=1 | vlan_pop_cnt =2 | 报文携带stag，删掉两层tag,根据PW表生成stag |

#### 对于mpls_tunnel_encap模式下的入L2VPN隧道(先终结，再入隧道)

入L2VPN隧道则根据pw_token表中的tag_mode以及ILM.FWD_INFO.TAG_MODE对内层tag进行操作。

| PW_token.Tag_mode | ILM.FWD_INFO.TAG_MODE | Result |
| --- | --- | --- |
| Tag_mode=0 | TAG_MODE =0 | 报文没有携带stag,不需要处理 |
| Tag_mode=0 | TAG_MODE =1 | 报文携带stag，则删除stag |
| Tag_mode=1 | TAG_MODE =0 | 报文没有携带stag，则需要添加一个stag |
| Tag_mode=1 | TAG_MODE =1 | 报文携带stag,删掉该stag,如果查pw表s-vlan!=0xfff，则根据PW表生成stag，否则保留原s-tag |
