# kyland_sdk_2.0.0 OAM应用开发指南

kyland_sdk_2.0.0

OAM应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 OAM简介	8

1.1 维护域MD	8

1.2 维护联盟MA	9

1.3 维护端点MEP	9

1.4 BFD介绍	10

2 本芯片支持的OAM介绍	12

3 本芯片OAM规格介绍	13

4 OAM软件设计介绍	14

4.1 软件接口适配模型	14

5 Oam软件处理流程分析	15

5.1 Down port oam	17

5.2 Down ivport oam	18

5.3 Down mpls lsp	19

5.4 Down mpls segment	20

5.5 Down pw	21

5.6 Up vport	22

5.7 Up mpls (l2vpn 终结)	23

5.8 ip bfd	24

6 OAM相关接口介绍	26

6.1 本地表项操作接口	26

6.1.1 功能简介	26

6.1.2 接口及参数描述	26

6.1.3 相关数据结构	28

6.1.4 调用cil层接口	31

6.1.5 功能简介	31

6.1.6 接口及参数描述	31

6.1.7 相关数据结构	32

6.1.8 调用cil层接口	33

6.1.9 功能简介	33

6.1.10 接口及参数描述	33

6.1.11 相关数据结构	34

6.1.12 调用cil层接口	35

6.1.13 功能简介	35

6.1.14 接口及参数描述	35

6.1.15 相关数据结构	36

6.1.16 调用cil层接口	37

6.1.17 功能简介	37

6.1.18 接口及参数描述	38

6.1.19 相关数据结构	39

6.1.20 调用cil层接口	40

6.1.21 功能简介	40

6.1.22 接口及参数描述	40

6.1.23 相关数据结构	43

6.1.24 调用cil层接口	43

6.2 远端表项操作接口	44

6.2.1 功能简介	44

6.2.2 接口及参数描述	44

6.2.3 相关数据结构	46

6.2.4 2.1.4调用cil层接口	48

6.2.5 功能简介	48

6.2.6 接口及参数描述	48

6.2.7 相关数据结构	49

6.2.8 2.2.4调用cil层接口	49

6.3 dsp 表项操作接口	49

6.3.1 功能简介	49

6.3.2 接口及参数描述	49

6.3.3 相关数据结构	50

6.3.4 3.4调用cil层接口	51

6.4 oam 全局配置操作接口	51

6.4.1 功能简介	51

6.4.2 接口及参数描述	51

6.4.3 相关数据结构	52

6.4.4 调用cil层接口	54

6.5 报文发送及删除接口	54

6.5.1 功能简介	54

6.5.2 接口及参数描述	55

6.5.3 相关数据结构	57

6.5.4 调用cil层接口	60

6.5.5 功能简介	60

6.5.6 接口及参数描述	60

6.5.7 相关数据结构	63

6.5.8 调用cil层接口	64

6.5.9 功能简介	64

6.5.10 接口及参数描述	64

6.5.11 相关数据结构	65

6.5.12 调用cil层接口	65

6.6 bfd表项操作接口	65

6.6.1 功能简介	65

6.6.2 接口及参数描述	66

6.6.3 相关数据结构	68

6.6.4 调用cil层接口	70

6.6.5 功能简介	71

6.6.6 接口及参数描述	71

6.6.7 相关数据结构	72

6.6.8 调用cil层接口	72

6.6.9 功能简介	73

6.6.10 接口及参数描述	73

6.6.11 相关数据结构	74

6.6.12 调用cil层接口	74

6.6.13 功能简介	74

6.6.14 接口及参数描述	75

6.6.15 相关数据结构	76

6.6.16 调用cil层接口	76

6.7 OAM中断相关接口	77

6.7.1 功能简介	77

6.7.2 接口及参数描述	77

6.7.3 相关数据结构	78

6.7.4 调用cil层接口	80

6.8 OAM lm统计相关接口	80

6.8.1 功能简介	80

6.8.2 接口及参数描述	81

6.8.3 相关数据结构	86

6.8.4 调用cil层接口	87

6.8.5 功能简介	88

6.8.6 接口及参数描述	88

6.8.7 相关数据结构	95

6.8.8 调用cil层接口	96

6.9 查看OAM报文统计相关接口	97

6.9.1 功能简介	97

6.9.2 接口及参数描述	97

6.9.3 相关数据结构	101

6.9.4 调用cil层接口	102

6.10 查看OAM ccm 接收时间相关接口	103

6.10.1 功能简介	103

6.10.2 接口及参数描述	103

6.10.3 相关数据结构	104

6.10.4 调用cil层接口	104

6.11 Meg表项操作接口	105

6.11.1 功能简介	105

6.11.2 接口及参数描述	105

6.11.3 相关数据结构	106

6.11.4 调用cil层接口	106

7 OAM应用举例	107

7.1 eth oam	107

7.2 mpls lsp oam	111

7.3 ipv4 bfd	111

# OAM简介

OAM全称为Operations Administration and Maintenance，即操作管理和维护。

OAM主要功能可分为以下两部分：

故障管理

通过定时或手动发送检测报文来探测网络的连通性。

提供类似IP网络中的Ping和Traceroute的功能，对以太网进行故障诊断和定位。

与保护倒换协议配合，在OAM检测到连通性故障后触发设备或者链路的倒换，从而实现网络中断时间小于等于50毫秒的可靠性目标。

性能管理

性能管理主要是指对网络传输中的丢包、时延、抖动等参数的衡量，也包括对网络中各类流量（如接收发送字节数、错误帧数量等）进行统计（通常是在用户接入点实施）。通过性能管理，运营商可以监测网络运行情况，并根据收集到的数据进行实时、动态的调整，使得网络维护成本大大降低。

## 维护域MD

维护域MD（Maintenance Domain）指明了连通错误检测所覆盖的网络，其边界是由配置在端口上的一系列维护端点所定义的。维护域以“维护域名”来标识。

为了准确定位故障点，在维护域中引入了级别（层次）的概念。维护域共分为八级，用整数0～7来表示，数字越大级别越高，维护域的范围也就越大。不同维护域之间可以相邻或嵌套，但不能交叉，且嵌套时只能由高级别维护域向低级别维护域嵌套，即低级别维护域必须包含在高级别维护域内部。

维护域MD的分级使得故障定位更加便利和准确。如图所示，维护域MD2嵌套在维护域MD1中。如果维护域MD1检测到故障后，则可以判断PE2到PE7之间设备或者链路出现了故障。如果维护域MD2没有检测到故障，则可以表明PE2、PE3和PE4设备是正常的。从而将故障锁定在PE5、PE6、PE7设备或者之间的链路。

在实际应用中，如果某个维护域MD内还包含另一个范围较小的维护域MD，在对大的维护域MD进行连通性检测时，802.1ag协议报文需要穿越小的维护域MD，则可将大维护域MD的级别配置得比小维护域MD高，以实现802.1ag协议报文穿越。例如在图1所示网络中，MD2包含在MD1中，MD1的802.1ag协议报文需要穿越MD2。因此，将MD1的级别配置为6，MD2的级别配置为3，这样MD1内的802.1ag协议报文就可以穿越MD2实现整个MD1的连通性故障管理，而MD2的802.1ag协议报文不会扩散到MD1中。因此，通过对MD的合理规划可以对故障有效的分层和定责。

## 维护联盟MA

在维护域内根据需要可以配置多个维护联盟（Maintenance Association，MA），每个维护联盟是维护域内一些维护点的集合。维护联盟以“维护域名＋维护联盟名”来标识。

维护联盟服务于某个特定的业务(如VLAN)，维护联盟中的维护点所发送的报文都带有该业务的标签，同时维护联盟中的维护点可以接收由本维护联盟中其它维护点发来的报文。

## 维护端点MEP

维护端点MEP（Maintenance association End Point）确定了维护域MD的范围和边界，是维护联盟MA的边缘节点。维护端点所属的维护联盟和维护域确定了该维护端点所发出报文的业务和级别。维护端点的级别决定了其所能处理的报文的级别，维护端点所发出报文的级别就是该维护端点的级别。当维护端点收到高于自己级别的报文时，不会进行处理，而是将其按原有路径转发；而当维护端点收到小于或者等于自己级别的报文时，才会进行处理。

维护端点位于设备的接口上，手工创建。维护端点的级别等于它所在的维护域的级别。

维护端点具有方向型，分为inward型MEP和outward型，如图所示。

inward型MEP不向它所在端口发送报文，而是向设备的其它端口发送报文。

outward型MEP向它所在端口发送报文。

目前大多人使用UP MEP 或者DOWN MEP 来区分它们，UP MEP 在早期草案中用inward表示, DOWN MEP在早期的草案中用outward表示.

## BFD介绍

双向转发检测BFD（Bidirectional Forwarding Detection）是一种全网统一的检测机制，用于快速检测、监控网络中链路或者IP路由的转发连通状况。

BFD在两台网络设备上建立会话，用来检测网络设备间的双向转发路径，为上层应用服务。BFD本身并没有邻居发现机制，而是靠被服务的上层应用通知其邻居信息以建立会话。会话建立后会周期性地快速发送BFD报文，如果在检测时间内没有收到BFD报文则认为该双向转发路径发生了故障，通知被服务的上层应用进行相应的处理。

BFD有两种运行模式和一种辅助功能,辅助功能可以与两种运行模式联合使用.

异步模式是BFD的一种主要运行模式,在这种模式下,系统向邻居周期性的发送BFD控制报文,并且如果没有收到一定数量的来自对端的BFD控制报文(检测时间内应该收到的报文数量),则宣告会话down.

查询模式是BFD的另一种工作模式,在这种模式下,他假定系统有一个独立的路径来确定他与邻居之间的连通性.一旦BFD会话建立起来,系统便会询问他的邻居停止发送BFD控制报文,直到系统需要检验连通性的时候,会与邻居交互一连串的BFD控制报文.如果正常收到相应的BFD控制报文,则继续静默,否则,宣告会话down,查询模式中,两个方向会话是相互独立的.

这两个主要的工作模式有一个辅助功能就是回声功能.回声功能开启后,会发一串回声报文流并等待对端将该报文流环回回来.如果没有收到,宣告回话down.回声功能是和异步模式或者查询模式一起使用的,当开启回声功能后,回声功能承担了检测任务,异步模式的发包频率可以减小,查询模式可以完全不发包.

回声功能可以在一个方向开启.要求对端具有环回功能.

本芯片中在配置BFD表项时, coordinated mode 为查询模式,independent mode(coordinated_mode_ena = 0)为异步模式.回声报文上送cpu,由cpu处理.

# 本芯片支持的OAM介绍

以太业务 OAM 802.1ag/Y.1731，支持硬件处理 OAM PDU，service 支持 up

mep/down mep/mip，port 支持 down mep。Up mep 的以太 OAM 仅支持单播 DMAC 的 OAM 报文处理。

G.8113.1 MPLS-TP OAM，支持硬件处理 OAM PDU，支持 lsp segment、lsp tunnel、pw down mep/mip。

G.8113.2 MPLS-TP BFD CC/CV，支持硬件处理 OAM PDU，支持 Coordinated 模式和 Independent 模式，G.8113.2 的其他类型的 OAM PDU，送 CPU 处理。

RFC5085 VCCV OAM，支持 type1、type2、type3 方式识别 OAM 报文，支持硬件处理 channel type 为 0x8902 的 MPLS-TP OAM 报文及 BFD 报文（包括 RAW BFD 报文或 IPV4/IPV6 UDP BFD 报文），其他类型 OAM 报文送CPU 处理。

RFC5880/RFC881/RFC5883 IP/UDP BFD，支持硬件收发处理 BFD 报文。

RFC 5884 BFD for MPLS，支持硬件收发处理 BFD 报文。

RFC 5885 BFD for VCCV 支持硬件收发处理 BFD 报文。

Y.1711 MPLS OAM，硬件识别，送 CPU 处理。

G.8114 T-MPLS OAM ，硬件识别，送 CPU 处理。

RFC 8029/4379 MPLS-Ping ,MPLS -Trace ，硬件识别，送 CPU 处理。

以太链路 OAM 802.3ah，硬件识别，送 CPU

# 本芯片OAM规格介绍

OAM模块有4K lmep表项 和4K rmep 表项, 另外非g8113_2的BFD表项和 OAM表项共用4K个lmep表项,g8113_2的BFD表项与OAM共用4K rmep表项.

# OAM软件设计介绍

## 软件接口适配模型

产品接口创建kyland_lmep_t 表项,如果该lmep为up mep, 则需要先配置dsp表项再配置lmep表项.如果该lmep是down mep,则直接配置lmep表项.

产品接口配置kyland_cnt_t表项,表项的index是service id(ivport/evport),根据kyland_cnt_t表项的配置,硬件配置lm_cnt表项.如果是port类型的lm_cnt表项,产品接口配置kyland_lm_t表项,表项的index是port number, 根据kyland_lm_t表项的配置, 硬件配置port_lm_cnt表项

产品接口配置kyland_rmep_t表项,根据rmep_index 配置硬件rmep表项

# Oam软件处理流程分析

1.DOWN 类型的OAM接收处理：

OAM 报文识别主要在 CL、MPLS、IP 模块识别。然后交给OAM模块进行报文处理（丢弃，回应，上送cpu等）

2.DOWN类型的OAM报文发送处理：

OAM 报文发送由 CPU 下发到 ASM 或 AFI 模块插入到 OQS 队列，或接收处 理 OAM 模块 Reply 环回触发，进入到 OAM 发送处理模块，进行 OAM 报文的 编辑及 OAM 表的状态更新及统计信息更新。

CPU直接发送报文时,填写正确的报文信息,出口信息使用cpu下插报文时填写的出端口,或者进行转发后从转发模块获取到出口信息.

CPU发送报文模板给AFI模式,由AFI自动发包时,需要使用AFI发包模式的IFH头 ,报文的最终出端口是AFI 模块配置的dest port,或者转发后从转发模块获取出口信息.

3.UP类型OAM报文的接收处理：

UP MEP，单播以太 OAM 报文在上行 OAM 模块查 DSP 表，匹配后表示要对报文进行UP处理（丢弃，回应，上送cpu等）

4.UP类型OAM报文的发送处理：

OAM 报文发送由 CPU 下发到 ASM 或 AFI 模块插入到 OQS 队列，或接收处 理 OAM 模块 Reply 环回触发，进入到 OAM 发送处理模块，进行 OAM 报文的 编辑及 OAM 表的状态更新及统计信息更新。

UP类型的OAM报文发送时要在芯片内部进行一次环回，发送报文时报文需经过port  62（内部环回端口）环回到上行进行处理然后第二次经过下行时才会发送出去。

CPU直接发送报文时,fwd_mode 需要配置为0(llook_up)模式,不关心dest port,出口信息是从转发获取的.

CPU发送报文模板给AFI,然后由AFI自动发送报文时,CPU发送报文给AFI时的fw_mode为2(physical),dest port 为AFI port(port 62), 报文从AFI发送出来时AFI 模块指定的dest port需要配置为还回端口port 62

5.BFD报文的接收处理：

BFD 报文主要在l3模块进行识别后送给 OAM模块内的BFD模块进行处理,

对报文进行统计和采样以及更新bfd表项等.

6.BFD报文的发送处理：

BFD 报文发送由 CPU 下发到 ASM 或 AFI 模块插入到 OQS 队列进入到 BFD 发送处理模块，进行 BFD 报文的 编辑及 BFD 表的状态更新及统计信息更新。

CPU直接发送报文时,填写正确的报文信息,出口信息使用cpu下插报文时填写的出端口,或者进行转发后从转发模块获取到出口信息.

CPU发送报文模板给AF模式I,由AFI自动发包时,需要使用AFI发包模式的IFH头 ,报文的最终出端口是AFI 模块配置的dest port,或者转发后从转发模块获取出口信息.

## Down port oam

1.port类型的oam报文接收处理时,需要配置port(cl模块)表中的mel bitmap与需要做接收处理的oam报文mel对应.

2.配置lmep 表项,必须将lmep表项内port number(本mep所在port)配置为相应port, 不关心表项中vport(读表时vport == port), port 类型只支持down mep模式.

3.配置rmep表项,此时表项的index是port number,表项内的rmep_id 值需要与报文中的值对应

4.使用afi自动发送报文时需要cpu先发送报文模板给afi, afi收到报文后存在frame表项中,然后根据配置进行tti/dti发送报文,afi指定的报文出端口port number需要和oam表项所在的port相等.ccm报文发送时,需要将afi_tti发送周期设置的与ccm报文中的周期值一致,并且还要和tx.loc_timer选择的周期相等.

5.cpu直接发送报文时,需要软件处理,本文档不做介绍.

6.需要lm功能时,先配置lm表项,此时的lm表项为port lm表项, 表项index为相应的port number.

## Down ivport oam

1.ivport类型的oam报文接收处理时,需要配置vport(cl模块)表中的mel bitmap与需要做接收处理的oam报文mel对应.

2.配置lmep 表项,表项中的vport值需要和在vport表获得到的ivport值相等.

3.配置rmep表项,此时表项的index是ivport,表项内的rmep_id 值需要与报文中的值对应

4.使用afi自动发送报文时需要cpu先发送报文模板给afi, 报文模板中需要携带evport信息(下行发送使用evport),afi收到报文后存在frame表项中,然后根据配置进行tti/dti发送报文.ccm报文发送时,需要将afi_tti发送周期设置的与ccm报文中的周期值一致,并且还要和tx.loc_timer选择的周期相等.

5.cpu直接发送报文时,需要软件处理,本文档不做介绍.

6. lm功能配置,接收侧根据ivport进行统计. 发送侧根据evport进行统计. 也可以根据端口号进行某个端口的统计

## Down mpls lsp

1.down mpls lsp类型的oam报文做接收处理时.报文需要查询标签表, 报文在ilm 标签表获得mel bitmap 和ivport信息.要求配置该标签表时设置的mel bitmap和oam 报文携带的mel和oam 表项配置的mel 三者匹配. 标签表中的ivport 和 oam 表项中的ivport相匹配

2.配置lmep表项,表项模式配置为对应模式,表项内vport值需要和从ilm表中获得的ivport值相等,lmep表中的mel要和ilm表中的mel bitmap相匹配

3.配置rmep表项,表项中rmep_id 要和报文中的rmep_id相匹配.mel 要和ilm 表中的mel bitmap相匹配, 表项内vport值需要和从ilm表中获得的ivport值相等

4. 使用afi自动发送报文时需要cpu先发送报文模板给afi, 报文模板中需要携带token mpls lsp信息,afi收到报文后存在frame表项中,然后根据配置进行tti/dti发送报文.ccm报文发送时,需要将afi_tti发送周期设置的与ccm报文中的周期值一致,并且还要和tx.loc_timer选择的周期相等.

5.lm功能配置,接收侧根据ivport进行统计. 发送侧根据evport进行统计. 也可以根据端口号进行某个端口的统计

## Down mpls segment

1.down mpls segment 类型的oam报文做接收处理时需要查询ivport(is0)表,获得到ivport值和mel bitmap信息. 报文需要命中该ivport表项. 要求配置该ivport表时设置的mel bitmap和oam 报文携带的mel和oam 表项配置的mel 三者匹配.

2. 配置lmep表项,表项模式配置为对应模式, lmep表中的mel要和ivport表中的mel bitmap相匹配,报文需要命中ivport表,表项中ivport值要和ivport表匹配

3. 配置rmep表项,表项中rmep_id 要和报文中的rmep_id相匹配.mel 要和ivport表中的mel bitmap相匹配,表项中ivport值要和ivport表匹配

4. 使用afi自动发送报文时需要cpu先发送报文模板给afi, 报文模板中需要携带arp信息,afi收到报文后存在frame表项中,然后根据配置进行tti/dti发送报文.ccm报文发送时,需要将afi_tti发送周期设置的与ccm报文中的周期值一致,并且还要和tx.loc_timer选择的周期相等.

5. lm功能配置,接收侧根据ivport进行统计. 发送侧根据evport进行统计. 也可以根据端口号进行某个端口的统计

## Down pw

1. down pw 类型的oam报文做接收处理时需要查询ilm_pw表,获得到ivport值和mel bitmap信息. 报文需要命中该ivport表项. 要求配置该ilm_pw表时设置的mel bitmap和oam 报文携带的mel和oam 表项配置的mel 三者匹配. 支持vpls和vpws

2. 配置lmep表项,表项模式配置为对应模式, lmep表中的mel要和ilm_pw表中的mel bitmap相匹配,表项中ivport值要和ilm_pw表项中配置的ivport相等

3. 配置rmep表项,表项中rmep_id 要和报文中的rmep_id相匹配.mel 要和ilm_pw 表中的mel bitmap相匹配,表项中ivport值要和ilm_pw匹配

4. 使用afi自动发送报文时需要cpu先发送报文模板给afi, 报文模板中需要携带token_pw信息,afi收到报文后存在frame表项中,然后根据配置进行tti/dti发送报文.ccm报文发送时,需要将afi_tti发送周期设置的与ccm报文中的周期值一致,并且还要和tx.loc_timer选择的周期相等.

5. lm功能配置,接收侧根据ivport进行统计. 发送侧根据evport进行统计. 也可以根据端口号进行某个端口的统计

6. 支持pw vccv type类型oam. Type1—PW 控制字第一个四bit为0001, Type2—使用RAL标签识别（RAL标签在PW标签之上）, Type3—PW TTL=1识别

## Up vport

1.up vport类型oam报文接收的时候匹配mac表后使用evport值查询oam dsp表.表项中配置mel bitmap ,vlan pop cnt,vlan tag cnt, vlan push cnt. 报文的最终tag_cnt数（依据vlan tag cnt + vlan push cnt – vlan pop cnt）匹配. 报文的mel与 mel bitmap相匹配.

2. 配置lmep表项,表项模式配置为对应模式, lmep表中的mel要和dsp表中的mel bitmap相匹配,表项中vport值要和dsp表项的evport相等

3. 配置rmep表项,表项中rmep_id 要和报文中的rmep_id相匹配.mel 要和dsp 表中的mel bitmap相匹配,表项中vport值要和dsp表的evport相等

4. 使用afi自动发送报文时需要cpu先发送报文模板给afi, 报文模板中需要携带ivport信息,afi收到报文后存在frame表项中,然后根据配置进行tti/dti发送报文.ccm报文发送时,需要将afi_tti发送周期设置的与ccm报文中的周期值一致,并且还要和tx.loc_timer选择的周期相等.

5. lm功能配置,接收侧根据evport进行统计. 发送侧根据ivport进行统计. 也可以根据端口号进行某个端口的统计

注: up MEP OAM报文接收处理在PFS模块，up MEP OAM报文在下行OAM进行接收OAM统计。

## Up mpls (l2vpn 终结)

1. l2vpn终结,终结完是eth类型的oam报文,在l3模块进行终结, 终结动作结束后获得vsi值,

l2 模块使用 mac + vai 的方式查表获得evport值.

2.使用evport查 dsp表项, 表项的mel bitmap非 0 且要与报文中mel相匹配.

3. 配置lmep表项,表项模式配置为对应模式, lmep表中的mel要和dsp表中的mel bitmap相匹配,表项中vport值要和dsp表项的evport相等

4. 配置rmep表项,表项中rmep_id 要和报文中的rmep_id相匹配.mel 要和dsp 表中的mel bitmap相匹配,表项中vport值要和dsp表的evport相等

5. 使用afi自动发送报文时需要cpu先发送报文模板给afi, 报文模板中需要携带token_pw信息,afi收到报文后存在frame表项中,然后根据配置进行tti/dti发送报文.ccm报文发送时,需要将afi_tti发送周期设置的与ccm报文中的周期值一致,并且还要和tx.loc_timer选择的周期相等.

6. lm功能配置,接收侧根据evport进行统计. 发送侧根据ivport进行统计. 也可以根据端口号进行某个端口的统计

注: PW终结后识别出的以太OAM报文（L3模块，ILM表中inner_tag mode为1且报文携带1层tag，或inner_tag mode为0且报文不携带tag），OAM模块不需要进行tag_cnt的匹配

注: up MEP OAM报文接收处理在PFS模块，up MEP OAM报文在下行OAM进行接收OAM统计。

## ip bfd

1.ip类型的bfd, IP 命中本地路由(配置路由表时需要将local  route置起)，udp端口号为3784（单跳，TTL必须为255）或4784（多跳）送BFD接收硬件处理，或UDP端口号6784且 DMAC = 01005E900001（需要作为有效的接口MAC， BFD for LAG member）。udp端口号3785为bfd echo报文送CPU处理设置。

2.报文做接收处理时,使用报文中your discriminator 作为hash 表项的key 值信息进行查表.如果命中则按照表项配置进行报文处理,如果不命中则置起bfd miss sticky.

3.bfd接收表项内可以配置关联的保护组ID,发生loc 时是否切换保护组使能,以及对收到的bfd报文进行信息采样等功能.

# OAM相关接口介绍

OAM模块涉及到hash表项的操作时,hash表的key值信息不能修改,否则会导致映射的hash表项地址发生变化,所以表项在进行更新操作时不能对hash表项的key值信息进行更新,只能更新hash表项链接的线性表项内容.因此添加表项时的结构体信息和更新表项时的结构信息会有所不同

## 本地表项操作接口

### 功能简介

本地表项操作接口用来配置本地的mep表项，可以根据类型将本地mep配置为down或者up类型还有本地mep的level等级等信息。更新本地表项中的内容和删除某个mep功能。

### 接口及参数描述

kyland_rc   kyland_oam_lmep_add(const kyland_inst_t inst, u16 index, kyland_oam_lmep_t *lmep, kyland_oam_lmep_key_t *key);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index

kyland_oam_lmep_t *lmep 	//本地lmep表项的配置信息

kyland_oam_lmep_key_t *key	//添加完表项后 返回key值信息,用于读写表项

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc	 kyland_oam_lmep_update(const kyland_inst_t inst, u16 index, kyland_oam_update_lmep_t *lmep);

参数:

const kyland_inst_t inst  //芯片实例

u16 index 		//表项index

kyland_oam_update_lmep_t *lmep  //新的表项配置信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc	 kyland_oam_lmep_get(const kyland_inst_t inst, u16 index, kyland_oam_lmep_t*lmep, kyland_oam_lmep_key_t *key);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index

kyland_oam_lmep_t*lmep	//读取到的表项配置信息

kyland_oam_lmep_key_t *key	//key值信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc	 kyland_oam_lmep_del(const kyland_inst_t inst, u16 index, kyland_oam_ lmep_key_t *key);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index

kyland_oam_ lmep_key_t *key	//需要被删除的表项key值信息

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

/*表项添加相关数据结构*/

typedef struct {

ucBool 	oam_enable;		/**< Enable the lmep table */

kyland_oam_mep_level_t   mel;		/**< Local mep mep level */

kyland_oam_mode_t  mep_mode;		/**< Configure the mep mode */

kyland_port_no_t    port;	 	/**< The mep port number */

kyland_vport_t	vport; 		/**< vport */

u16	mep_id;			/**< mep id */

u16 meg_index;	/**< meg table index :12 bit (0-4) defect_flag index (5-11) meg_index */

u16 meg_id_digest;  /**< The low 16 bit of the ccm frame meg id CRC32 hash  (used for ccm frame check)*/

kyland_mac_t   mep_mac;		/**< Local mep mac addr */

kyland_oam_frame_pri_t	  ccm_pri;		/**< ccm priority (used for ccm frame check)*/

kyland_oam_ccm_period_t  ccm_period;	/**< ccm period (used for ccm frame check)*/

ucBool  down_up;			/**< 0:down 1:up */

ucBool 	mep_mip_flag;		/**< 0:mip 1:mep */

ucBool	g8113_2_flag;	/**< If set g8113_2_flag: lmep used for g8113_2 oam */

u16  mep_mpls_loop_index;	/**< 1)mpls: replay lsp token, 2)pw: replay pw token, 3)mpls segment: replay arp index */

kyland_oam_frame_pri_t   sl_pri;	/**< The slm/slr/1sl frame priority value */

kyland_oam_redi_cpu_ena_t  redi;	/**< The frame redirect to cpu enable */

u16  lbr_g8113_1_remote_mep_id;	/**< G8113_1 remote mep id*/

u32  g8113_1_mip_id[4];   /**< Mep: recive G8113_1 lbr remote mip_id, MIP: local MIP id*/

u32  sl_test_id;	/**< Set the slr/1sl frame test id (used for test id check)*/

kyland_oam_expect_seq_num_t  expect;	/**< Set the expect sequence number value */

kyland_oam_tx_cfg_t  tx_cfg;		/**< Configure the oam tx table */

kyland_oam_opcode_t opcode_table;		/**< Configure the opcode table */

}kyland_oam_lmep_t;

------------------------------------------------------------------------------------------------------------------------------------------

/*key值信息 相关数据结构*/

typedef struct

{

kyland_oam_mode_t 	mep_mode;

ucBool  down_up;

kyland_vport_t	vport;

kyland_oam_mep_level_t	mel;

}kyland_oam _lmep_key_t;

### 调用cil层接口

kyland_oam_lmep_add 	   ------->  oam_lmep_add

kyland_oam_lmep_update  ------->  oam_lmep_update

kyland_oam_lmep_get	  -------> 	oam_lmep_get

kyland_oam_lmep_del    -------->  oam_lmep_del

### 功能简介

本地表项frame check 表的配置接口, 通过该接口可以配置对oam frame进行哪些域的检查.从而判断该oam frame是否符合接收处理的条件

注: 此接口主要作为修改lmep 表项的接口,使用此接口前应该添加过至少一张lmep表项.

### 接口及参数描述

kyland_rc kyland_oam_check_set(const kyland_inst_t inst, u16 index, kyland_oam_rx_check_ena_t *check);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//本地表项index

kyland_oam_rx_check_ena_t *check 	//接收检查的配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_check_get(const kyland_inst_t inst, u16 index, kyland_oam_rx_check_ena_t *check)	;

参数:

const kyland_inst_t inst  //芯片实例

u16 index	//本地表项的index

kyland_oam_rx_check_ena_t *check	//读取到的检查配置

返回值:

操作码.

### 相关数据结构

/*表项配置相关数据结构*/

typedef struct{

ucBool 	ccm_period_chk_enable;

ucBool 	ccm_priority_chk_enable;

ucBool 	ccm_rx_seq_chk_ena;

ucBool 	dmac_chk_enable;

ucBool 	lbr_g8113_1_remote_mp_id_check_enable;

ucBool 	lbr_g_8113_1_lbk_indc_chk_ena;

ucBool 	lbr_rx_sequencenumberchk_enable;

ucBool 	meg_chk_enable;

ucBool 	slr_1sl_test_id_chk_ena;

ucBool 	sl_prio_chk_ena;

ucBool 	tst_rx_sequence_numberchk_enable;

ucBool 	version_check_enable;

}kyland_oam_rx_check_ena_t;

### 调用cil层接口

kyland_oam_check_set  	------->   oam_check_set

kyland_oam_check_get 		------->   oam_check_get

### 功能简介

本地表项 hmo 表的配置接口, 通过该接口可以配置接收到的oam frame 周期上送cpu 的周期值.

注: 此接口主要作为修改lmep 表项的接口,使用此接口前应该添加过至少一张lmep表项.

### 接口及参数描述

kyland_rc  kyland_oam_hmo_set(const kyland_inst_t inst, u16 index, kyland_oam_hmo_t *hmo);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//本地表项的index

kyland_oam_hmo_t *hmo	//hmo的配置信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc  kyland_oam_hmo_get(const kyland_inst_t inst, u16 index, kyland_oam_hmo_t *hmo);

参数:

const kyland_inst_t inst   //芯片实例

u16 index		//本地表项的index

kyland_oam_hmo_t *hmo 	//读取到的hmo配置信息

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

/*表项配置相关数据结构*/

typedef struct {

ucBool  pdu_extract_hit_me_once;		/**< Frame extract use hit me once(hmo) */

kyland_oam_hmo_period_t  timer_id;	/**< Hmo timer ID */

}kyland_oam_hmo_t;

### 调用cil层接口

kyland_oam_hmo_set	------->  oam_ hmo_set

kyland_oam_hmo_get	------->  oam_ hmo_get

### 功能简介

本地表项 oam frame copy to cpu表的配置接口, 通过该接口可以配置接收到的oam frame copy to cpu.

注: 此接口主要作为修改lmep 表项的接口,使用此接口前应该添加过至少一张lmep表项.

### 接口及参数描述

kyland_rc 	kyland_oam_frame_copy_to_cpu_set(const kyland_inst_t inst, u16 index,

kyland_oam_copy_cpu_t *copy_cpu);

参数:

const kyland_inst_t inst   //芯片实例

u16 index		//本地表项的index

kyland_oam_copy_cpu_t *copy_cpu  	//frame copy  to cpu的配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc 	kyland_oam_frame_copy_to_cpu_get(const kyland_inst_t inst, u16 index,

kyland_oam_copy_cpu_t *copy_cpu);

参数:

const kyland_inst_t inst  //芯片实例

u16 index 		//本地表项的index

kyland_oam_copy_cpu_t *copy_cpu	//读取到的 frame copy  to cpu的配置

返回值:

操作码.

### 相关数据结构

/*表项配置相关数据结构*/

typedef struct {

ucBool  ccm_copy_cpu_all_enable;		/**< All ccm frame copy to cpu. */

ucBool  ccm_lm_copy_cpu_all_enable;  /**< All ccm with lm information frame copy to cpu. */

ucBool  ccm_copy_cpu_next;	/**< Next ccm frame copy to cpu.SW set,HW clear */

ucBool  ccm_lm_copy_cpu_next;	/**< Next ccm with lm information frame copy to cpu.SW set,HW clear */

ucBool  dm_copy_cpu_next;	/**< Next dmx frame copy to cpu.SW set,HW clear */

ucBool  lbx_copy_cpu_next;	/**< Next lbx frame copy to cpu.SW set,HW clear */

ucBool  lm_copy_cpu_next;	/**< Next lmx frame copy to cpu.SW set,HW clear */

ucBool  slx_copy_cpu_next;	/**< Next slx frame copy to cpu.SW set,HW clear */

ucBool  tst_copy_cpu_next;	/**< Next tst frame copy to cpu.SW set,HW clear */

}kyland_oam_copy_cpu_t;

### 调用cil层接口

kyland_oam_frame_copy_to_cpu_set 	------->  oam_frame_copy_to_cpu_set

kyland_oam_frame_copy_to_cpu_get		------->  oam_frame_copy_to_cpu_get

### 功能简介

本地表项 oam frame error extract to cpu表的配置接口, 通过该接口可以配置接收到的error oam frame extract to cpu.

注: 此接口主要作为修改lmep 表项的接口,使用此接口前应该添加过至少一张lmep表项.

### 接口及参数描述

kyland_rc 	kyland_oam_frame_err_extr_set(const kyland_inst_t inst, u16 index,

kyland_oam_error_extr_t *error_extr);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//本地表项的index

kyland_oam_error_extr_t *error_extr 	//error frame extract to cpu 的配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc 	kyland_oam_frame_err_extr_get(const kyland_inst_t inst, u16 index,

kyland_oam_error_extr_t *error_extr);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//本地表项的index

kyland_oam_error_extr_t *error_extr)  //读取到的error frame extract to cpu 的配置

返回值:

操作码.

### 相关数据结构

/*表项配置相关数据结构*/

typedef struct {

ucBool ccm_megid_rx_err;

ucBool ccm_mepid_err;

ucBool ccm_period_rx_err;

ucBool ccm_prio_rx_err;

ucBool ccm_rx_rdi;

ucBool ccm_rx_tlv_non_zero;

ucBool ccm_rx_sequence_err;

ucBool dmac_rx_err;

ucBool ethoam_lbx_rx_tlv_non_zero;

ucBool g_8113_1_lbm_rx_err;

ucBool g_8113_1_lbr_rx_err;

ucBool lbr_rx_sequence_err;

ucBool pdu_version_rx_err;

ucBool rx_sl_err;

ucBool tst_rx_sequence_err;

}kyland_oam_error_extr_t;

### 调用cil层接口

kyland_oam_frame_err_extr_set 	------->  oam_frame_err_extr_set

kyland_oam_frame_err_extr_get	------->  oam_frame_err_extr_get

### 功能简介

本地表项 oam send frame with tlv表的配置接口, 通过该接口可以配置发送时候的ccm 报文携带port status tlv 或者 interface status tlv. 携带的tlv 内容是通过本小节介绍的接口配置的.

注: 此接口主要作为修改lmep 表项的接口,使用此接口前应该添加过至少一张lmep表项.

### 接口及参数描述

kyland_rc kyland_oam_tlv_set(const kyland_inst_t inst, u16 index, ucBool tx_with_port_tlv_ena,

ucBool tx_with_interface_tlv_ena, kyland_oam_tx_interface_status_t interface_status);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index

ucBool tx_with_port_tlv_ena	//发送ccm报文时是否携带port  tlv

ucBool tx_with_interface_tlv_ena		//发送ccm报文时是否携带interface tlv

kyland_oam_tx_interface_status_t interface_status  	//配置interface tlv status

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_tlv_get(const kyland_inst_t inst, u16 index, ucBool *tx_with_port_tlv_ena,

ucBool *tx_with_interface_tlv_ena, kyland_oam_tx_interface_status_t *interface_status);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index

ucBool *tx_with_port_tlv_ena		//获得到的是否携带port  tlv

ucBool *tx_with_interface_tlv_ena		//获得到的是否携带interface tlv

kyland_oam_tx_interface_status_t *interface_status	//获得到的 interface tlv status

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_port_tlv_status_set(const kyland_inst_t inst, kyland_port_t port, ucBool status);

参数:

const kyland_inst_t inst  //芯片实例

kyland_port_t port	//port  number

ucBool status	//port status (0:psBlocked 1:psUp,对应到 tlv 中的值是 1 和 2 )

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_port_tlv_status_get(const kyland_inst_t inst, kyland_port_t port, ucBool *status);

参数:

const kyland_inst_t inst  //芯片实例

kyland_port_t port	//port  number

ucBool *status	//port status (0:psBlocked 1:psUp,对应到 tlv 中的值是 1 和 2 )

返回值:

操作码.

### 相关数据结构

typedef enum {

KYLAND_OAM_INTERFACE_STATUS_UP = 1,

KYLAND_OAM_INTERFACE_STATUS_DOWN,

KYLAND_OAM_INTERFACE_STATUS_TESTING,

KYLAND_OAM_INTERFACE_STATUS_UNKNOWN,

KYLAND_OAM_INTERFACE_STATUS_DORMANT,

KYLAND_OAM_INTERFACE_STATUS_NOT_PRESENT,

KYLAND_OAM_INTERFACE_STATUS_LOWER_LAYER_DOWN,

}kyland_oam_tx_interface_status_t;

### 调用cil层接口

kyland_oam_tlv_set 			-------> 	tr_oam_tlv_set

kyland_oam_tlv_get			-------> 	tr_oam_tlv_get

kyland_oam_port_tlv_status_set		-------> 	tr_oam_port_tlv_status_set

kyland_oam_port_tlv_status_get		------->	tr_oam_port_tlv_status_get

## 远端表项操作接口

### 功能简介

远端mep表项操作接口包括远端表项的添加，更新，删除操作，添加时可以对远端表项内容进行配置，包括保护组ID的配置和远端表项的mep level等级配置等信息，更新时可以对远端表项内容进行更新。使用获取表项内容接口可以读取该条表项的内容,删除一个远端表项时使用删除操作.

注:

远端表项在在第一次配置时, ccm_loc_timer_id 要配置为0, 并且需要配置loc中断,当ccm产生loc中断后,在中断内重新配置该rmep表项,在重新配置的时候将ccm_loc_timer_id 配置为想要的值.

### 接口及参数描述

kyland_rc kyland_oam_rmep_add(const kyland_inst_t inst, u16 index, kyland_oam_rmep_t *rmep,

kyland_oam_rmep_key_t *key);

参数:

const kyland_inst_t inst   //芯片实例

u16 index		//表项index

kyland_oam_rmep_t *rmep	//远端表项配置信息

kyland_oam_rmep_key_t *key	//添加完表项后 返回的key值信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_rmep_update(const kyland_inst_t inst, u16 index, kyland_oam_update_rmep_t *rmep);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index

kyland_oam_update_rmep_t *rmep	//远端表项配置信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc  kyland_oam_rmep_get(const kyland_inst_t inst, u16 index, kyland_oam_rmep_t *rmep);

参数:

const kyland_inst_t inst   //芯片实例

u16 index		//表项index

kyland_oam_rmep_t *rmep	//远端表项key值信息

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc  kyland_oam_rmep_del(const kyland_inst_t inst, u16 index, kyland_oam_ rmep_key_t *key);

参数:

const kyland_inst_t inst   //芯片实例

u16 index		//表项index

kyland_oam_ rmep_key_t *key	//删除表项的key值信息

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

//远端表项添加时需要的数据结构

typedef struct{

ucBool  rmep_enable;				/**< Enable rmep table */

kyland_oam_rmep_type_t  session_type;		/**< The rmep session type */

kyland_vport_t  vport;	  /**< Vport for session_type ==IVPORT or EVPORT,port number for session_type == PORT */

kyland_oam_mep_level_t  mel;		/**< Mep level */

u16  rmep_id;			/**< Remote mep id */

u16  meg_index;	/**< meg table index :12 bit (0-4) defect_flag index (5-11) meg_index */

kyland_oam_loc_period_t  ccm_loc_timer_id;	/**< The loc timer id */

u16  protect_group_id;		/**< The protect group id */

u32  ccm_expect_sequence_number;	/**< The expect ccm sequence number value */

kyland_oam_rmep_change_tab_ena_t  change;	/**< Change protect group status switch */

}kyland_oam_rmep_t;

------------------------------------------------------------------------------------------------------------------------------------------

/*表项key值信息*/

typedef  struct{

kyland_oam_rmep_type_t session_type;	/**< The rmep session type */

kyland_vport_t	vport;						/**< Vport for session_type ==IVPORT or EVPORT,port number for session_type == PORT */

kyland_oam_mep_level_t 	mel;	/**< Mep level */

u16	rmep_id;			/**< Remote mep id */

}kyland_oam_rmep_key_t;

### 2.1.4调用cil层接口

kyland_oam_rmep_add  	-------->oam_rmep_add

kyland_oam_rmep_update   	--------> oam_rmep_update

kyland_oam_rmep_get		--------> oam_rmep_get

kyland_oam_rmep_del		--------> oam_rmep_del

### 功能简介

读取链路上ccm的连通性状态,以便判断当前链路状态.

注: 此接口主要作为查看rmep 表项的接口,使用此接口前应该添加过至少一张rmep表项.

### 接口及参数描述

kyland_rc kyland_oam_ccm_loc_status_get(const kyland_inst_t inst, u16 index, ucBool *status);

参数:

const kyland_inst_t inst   //芯片实例

u16 index		//表项index

ucBool *status	//读取到的本条表项对应的ccm连通性状态

返回值:

操作码.

### 相关数据结构

ucBool 	*status ;     //状态指示

### 2.2.4调用cil层接口

kyland_oam_ccm_loc_status_get		------> oam_ccm_loc_status_get

## dsp 表项操作接口

### 功能简介

up mep类型的oam报文收发处理时需要配置oam dsp表项,dsp表项用来匹配up 类型的oam报文,使其可以被oam 模块正确处理

### 接口及参数描述

kyland_rc kyland_oam_dsp_cfg(const kyland_inst_t inst, u16 index, kyland_oam_dsp_tbl_t *dsp);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index.该index为evport值

kyland_oam_dsp_tbl_t *dsp 	//dsp表项配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_dsp_get(const kyland_inst_t inst, u16 index, kyland_oam_dsp_tbl_t *dsp);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index.该index为evport值

kyland_oam_dsp_tbl_t *dsp	//读取到的dsp表项配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_dsp_del(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index.该index为evport值

返回值:

操作码.

### 相关数据结构

typedef struct

{

ucBool 	valid;			/**< Enable table */

u8    	melbitmap;			/**< The frame mep level bitmap */

u8    	detect_oam_tag_cnts;  		/**< The frame vlan tag cnt */

u8    	vlan_push_cnt;		/**< The frame vlan push cnt */

}kyland_oam_dsp_tbl_t;

### 3.4调用cil层接口

kyland_oam_dsp_cfg     ------> oam_dsp_cfg

kyland_oam_dsp_get     ------> oam_dsp_get

kyland_oam_dsp_del     ------> oam_dsp_del

## oam 全局配置操作接口

### 功能简介

对oam 模块全局寄存器进行配置,其中包括hmo/loc的timer使能和选择以及用户自定义的周期配置. oam报文上送cpu通道的配置等

### 接口及参数描述

kyland_rc kyland_oam_global_cfg(const kyland_inst_t inst, kyland_oam_global_t *global);

参数:

const kyland_inst_t inst  //芯片实例

kyland_oam_global_t *global	//oam全局配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_global_get(const kyland_inst_t inst, kyland_oam_global_t *global);

参数:

const kyland_inst_t inst  //芯片实例

kyland_oam_global_t *global	//读取到的oam全局配置

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

typedef struct {

ucBool  g_8113_1_mel_chk_dis;		/**< Enable G.8113.1 oam don't check mel */

ucBool  low_mel_redi_to_cpu_next;		/**< The next low mel frame redirect to cpu (SW set, HW clear)*/

ucBool  lmep_mip_index_miss_redi_cpu;  /**< The lmep mip index miss frame deirect to cpu */

ucBool  rx_eth_mc_up_oam_copy_cpu;   /**< RX mc type ethernet oam frame copy to cpu */

ucBool  bfd_session_miss_redi_cpu;	     /**< The bfd session miss frame redirect to cpu */

ucBool  mel_independent;	     /**< If set,mel will not care */

ucBool  smac_chek_enable;	    /**< Enable check RX ethernet oam frame soucre mac */

kyland_oam_support_version_t  support_version;	/**< This chip support oam version */

kyland_oam_to_cpu_cfg_t  cpu_que;	/**< Choose the oam frame to cpu queue */

kyland_oam_mpls_generic_type_t  generic_type; 	/**< G8113.2 generic channel type */

ucBool  pw_reply_loop_ena;		/**< Pw oam reply frames go through loop port */

u8  my_upsid;			/**< This chip upsid */

u8  loc_scan_lmep_ena;	   /**< Enable loc timer scan lmep table(processig ccm or bfd),every bit represents a loc timer */

u8  loc_scan_rmep_ena;   /**< Enable loc timer scan rmep table(processig ccm),every bit represents a loc timer */

u32  loc_period_val; 	/**< Choose the lmep loc timer period */

u32  loc_timer_udf;	/**< If the loc_period_val == 7, use the loc_timer_udf * 128 cycle for the loc period */

u32  hmo_period_val;	/**< Choose the lmep hmo timer period */

u32  hmo_timer_udf;	/**< If the hmo_period_val == 7 ,use hmo_timer_udf * 128 cycle for the period */

u32  lmep_tx_hmo_period_val;	/**< Choose the tx lmep hmo timer period */

u32  lmep_tx_hmo_timer_udf;	/**< If the lmep_tx_hmo_period_val == 7, use lmep_tx_hmo_timer_udf * 128 cycle for the period */

}kyland_oam_global_t;

### 调用cil层接口

kyland_oam_global_cfg   ------>oam_global_cfg

kyland_oam_global_get   ------>oam_global_get

## 报文发送及删除接口

### 功能简介

cpu首先向AFI插一个报文模板,AFI将该模板保存起来,使用定时发送（TTI）发送报文，报文发送可以根据配置将报文按照配置的时间间隔发送报文。报文删除接口可以将报文进行删除。

### 接口及参数描述

kyland_rc  kyland_afi_remain_cell_number_get(const kyland_inst_t inst, u32 *afi_remain_cell);

参数:

const kyland_inst_t inst  	//芯片实例

u32 *afi_remain_cell		//读取到的剩余资源数

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_frame_set(const kyland_inst_t inst, u16 index, u16 next_ptr, u8 cnt, kyland_oam_frame_info_t *info, u8 * const frame);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//frame 表index

u16 next_ptr 	//only used for dti, tti时配置为0

u8 cnt		// only used for dti, 一条链在发送时这个报文发送几次

kyland_oam_frame_info_t *info	//cpu 给afi 发送报文模板时的frame 信息

u8 * const frame	//frame 指针, 指向要发送给afi 的报文模板

返回值:

操作码.

kyland_rc kyland_oam_tti_set(const kyland_inst_t inst, u16 index, kyland_oam_tti_t *tti);

参数:

const kyland_inst_t inst   //芯片实例

u16 index		//tti 表的index

kyland_oam_tti_t *tti	//tti表的配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc  kyland_oam_tti_switch(const kyland_inst_t inst, kyland_afi_tti_cmd_t cmd);

参数:

const kyland_inst_t inst   //芯片实例

kyland_afi_tti_cmd_t cmd 	//tti功能的开关

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc  kyland_oam_tti_del(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst   //操作实例

u16 index 		//需要删除的tti表项index

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

//frame info 相关数据结构

typedef struct {

kyland_vid_t vid;		/**< Vlan id */

union{

kyland_vport_t ivport;	/**< Ivport */

kyland_vport_t evport;	/**< Evport */

}vport;

kyland_frame_tag_t tag;		/**< Frame tag information */

kyland_oam_mep_level_t mel;	/**< Set mep level, range[0,7] */

kyland_oam_frame_mode_t oam_mode;/**< Choose the frame IFH header mode, not used for bfd */

kyland_mep_type_t mep_type;	/**< Set local mep type */

kyland_frame_mpls_t mpls;	/**< Frame mpls information */

ucBool up_oam_lm_cnt_dis;	/**< Statistical up oam frames or not */

u32 length;			/**< frame length(include 4 bytes CRC) */

u16 bfd_session_id; 		/**< Bfd table index */

kyland_oam_bfd_mode_t bfd_encap_type;	/**< Choose how to encapsulate bfd frames */

kyland_bfd_ifh_type_t bfd_type;		/**< Select the IFH header of the bfd frame */

}kyland_oam_frame_info_t;

------------------------------------------------------------------------------------------------------------------------------------------

//tti  table部分相关结构体

typedef struct{

ucBool tti_ena;			/**< TTI enable, if use TTI,it must be enable */

kyland_oam_afi_packet_pri_t 	pri; 		/**< TTI inject frame priority */

kyland_oam_afi_packet_period_t	period; 		/**< TTI inject frame period */

kyland_port_no_t	port; 			/**< Choose the chip out of port */

u16  frame_ptr;				/**< Point to frame table */

u16   timer_len;	/**< Number of ticks of configured tick_idx between frame injections. except value of 0x1ff(for remove)*/

u8  tupe_ctrl;		/**< Control value for table update engine(TUPE) */

u8  solt_index;		/**< Solt table index: rang[0,3] */

u16  slot_end_ptr;		/**< Solt table end addr in frame table */

u16 slot_start_ptr;		/**< Solt table start addr in frame table */

u8 slot_cnt;	/**< Number of TTIs to service in slot before moving to next TTI calendar slot */

kyland_oam_tti_solt_cal_len_t solt_cal_len;	/**< Length of TTI Calendar. */

}kyland_oam_tti_t;

------------------------------------------------------------------------------------------------------------------------------------------

//tti 功能使能开关相关数据结构

typedef enum {

KYLAND_AFI_TTI_DISABLE,		/**< Oam AFI TTI  machine disable */

KYLAND_AFI_TTI_ENA			/**< Oam AFI TTI  machine enable */

} kyland_afi_tti_cmd_t;

### 调用cil层接口

kyland_oam_frame_set 		------>oam_frame_set

kyland_oam_tti_set		------>oam_tti_set

kyland_oam_tti_switch		------> oam_tti_enable_or_disable

kyland_oam_tti_del		------>oam_tti_del

kyland_afi_remain_cell_number_get	------>afi_remain_cell_number_get

### 功能简介

DTI模式发送报文，三种发送模式:

并联发送(32个dti可同时工作)

串联发送(根据配置当第一个状态机执行完frame发送完后自动使能第二个状态机进行frame发送....)

发送cnt次

### 接口及参数描述

kyland_rc kyland_oam_frame_set(const kyland_inst_t inst, u16 index, u16 next_ptr, u8 cnt,

kyland_oam_frame_info_t *info, u8 * const frame);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//frame表项index

u16 next_ptr 	//指向这条链中的下一个

u8 cnt		//该报文在这条链被发送时 发送的次数

kyland_oam_frame_info_t *info	//cpu 给的报文模板 info

u8 * const frame	//报文模板指针

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_dti_delay_set(const kyland_inst_t inst, u16 index, u16 next_ptr, u32 delay);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//frame 表index

u16 next_ptr 	//指向这条链中的下一个

u32 delay		//两个frame 之间的delay 值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_dti_set(const kyland_inst_t inst, u8 dti_num, kyland_oam_dti_t *dti);

参数:

const kyland_inst_t inst   //芯片实例

u8 dti_num		//使用哪个dti 状态机

kyland_oam_dti_t *dti	//dti 状态机的配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc  kyland_oam_dti_switch(const kyland_inst_t inst, u8 dti_num, kyland_afi_dti_cmd_t cmd);

参数:

const kyland_inst_t inst  //芯片实例

u8 dti_num		//dti状态机index

kyland_afi_dti_cmd_t cmd	//打开关闭命令

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc  kyland_oam_dti_del(const kyland_inst_t inst, u16 index, u8 dti_num);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//使用dti 删除frame 表(目前只能删除一个报文,不能删除一条链)

u8 dti_num		//使用哪个dti

返回值:

操作码.

### 相关数据结构

//dti表项部分相关数据结构

typedef struct{

ucBool  dti_ena;			/**< DTI machine enable */

kyland_oam_dti_mode_t  mode;		/**< DTI machine mode selection */

kyland_oam_afi_packet_pri_t  pri;		/**< Frame's AFI out of priority*/

u8  dti_next; 			/**< Point to the next DTI machine which need start, only used for mode == SERIAL */

kyland_port_no_t  port;			/**< Frame chain's chip out of port */

u32  cnt;				/**< Frame chain's inject timers, only used for DTI mode == CNT_TIMERS or mode == SERIAL */

u8  trailing_delay_cnt;			/**< One delay after cnt frame chain */

u16  first_frm_ptr;			/**< Point to the first frame in the frame chain */

ucBool  dti_end_dly_ena;		/**< DTI end delay enable */

}kyland_oam_dti_t;

### 调用cil层接口

kyland_oam_dti_delay_set 		------> oam_dti_delay_set

kyland_oam_dti_set			------> oam_dti_set

kyland_oam_dti_switch			------> oam_dti_enable_or_disable

kyland_oam_dti_del			------> oam_dti_del

### 功能简介

Cpu直接发送oam frame.

### 接口及参数描述

kyland_rc kyland_oam_cpu_send_frame(const kyland_inst_t inst, kyland_port_no_t port,

kyland_oam_frame_info_t *info, u8 * const frame);

参数:

const kyland_inst_t inst  //芯片实例

kyland_port_no_t port	//cpu发送oam frame的dest port.(使用限制请查看kyland_oam_api.h)

kyland_oam_frame_info_t *info	// oam frame info

u8 * const frame		// frame point

返回值:

操作码.

### 相关数据结构

//frame info 数据结构请看5.1.3章节

### 调用cil层接口

kyland_oam_cpu_send_frame		------> oam_frame_send_by_cpu

## bfd表项操作接口

### 功能简介

bfd表项配置接口提供了操作bfd表项的各种方法.由于bfd表项和lmep表项使用的是同一块ram,所以bfd表项的index 不能和lmep表项的index相同.

### 接口及参数描述

kyland_rc kyland_oam_bfd_add(const kyland_inst_t inst, u16 index, kyland_oam_bfd_t *bfd,

kyland_oam_bfd_key_t  *key);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//bfd表项index

kyland_oam_bfd_t *bfd		//bfd表项配置

kyland_oam_bfd_key_t  *key	//添加完bfd表项后,返回的表项key值信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_bfd_update(const kyland_inst_t inst, u16 index, kyland_oam_update_bfd_t *bfd);

参数;

const kyland_inst_t inst  //芯片实例

u16 index		//bfd表项index

kyland_oam_update_bfd_t *bfd	 //需要更新的bfd表项配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_bfd_get(const kyland_inst_t inst, u16 index, kyland_oam_bfd_t * bfd,

kyland_oam_bfd_key_t  *key);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//bfd表项index

kyland_oam_bfd_t * bfd		//读取到的bfd表项配置信息

kyland_oam_bfd_key_t  *key	//表项key值信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_bfd_del(const kyland_inst_t inst, u16 index, kyland_oam_bfd_key_t  *key);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//表项index

kyland_oam_bfd_key_t  *key	//需要删除的bfd表项key值信息

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

typedef struct {

ucBool bfd_ena;		/**< Bfd table enable */

ucBool	g8113_2_flag;	/**< If set g8113_2_flag: vport must be set*/

union{

kyland_vport_t  ivport;  /**< service id :only used for g8113_2_flag == 1 */

u32 discriminator; /**< Bfd your discriminator :only used for g8113_2_flag == 0 */

}info;

ucBool auth_bfd_pkt_redi_cpu;	/**< Bfd frames sith auth redirect CPU */

kyland_port_no_t port_num;	/**< Bfd frames RX port number */

ucBool bfd_rx_sample_ena;	/**< Enable RX bfd frames is save state */

ucBool extract_hit_me_once;	/**< Frame EXTR to CPU use hit me once */

ucBool loc_protect_switch_ena;	/**< Enable if LOC then change protect group */

u16 protect_group_id;		/**< protect group id */

ucBool state_protect_switch_ena;	/**< Enable if RX down state or admin down frames then change portect group */

ucBool bfd_coordinated_mode_ena;	/**< Enable BFD coordinated mode */

kyland_oam_bfd_cc_t cc;	/**< Bfd cc frames configuration */

kyland_oam_bfd_cv_t cv;	/**< Bfd cv frames configuration */

u8 generic_copy_mask;		/**< Copy which generic channel type frame to CPU */

u32 bfd_local_discr_src;		/**< Bfd source local discriminator */

u32 bfd_remote_discr_src;	/**< Bfd source remote discriminator */

u32 bfd_local_discr_sink;	/**< Bfd sink local discriminator */

u32 bfd_remote_discr_sink;	/**< Bfd sink remote discriminator */

u8 bfd_detect_mult;		/**< Bfd detect mult */

ucBool bfd_loc_detect_ena;	/**< Bfd LOC check enable */

kyland_oam_loc_period_t bfd_loc_timer;		/**< Bfd_local mep timer id */

u8 generic_cpt_cnt_sel_mask;	/**< Select generic channel type oam enable */

ucBool unk_cpt_cpu_copy_ena;	/**< Copy unknow channel type oam frames to CPU */

ucBool unk_cpt_cnt_sel_ena;	/**< Select unknow channel type oam frames enable */

kyland_oam_bfd_tx_t bfd_tx;	/**< Bfd frames TX configuration */

}kyland_oam_bfd_t;

------------------------------------------------------------------------------------------------------------------------------------------

/*key 值信息结构体*/

typedef struct{

ucBool	g8113_2_flag; /**< If set g8113_2_flag: vport must be set*/

union{

kyland_vport_t  ivport;  /**< service id :only used for g8113_2_flag == 1 */

u32 discriminator; /**< Bfd your discriminator :only used for g8113_2_flag == 0 */

}info;

}kyland_oam_bfd_key_t;

### 调用cil层接口

kyland_oam_bfd_add		------> oam_bfd_add

kyland_oam_bfd_update		------> oam_bfd_update

kyland_oam_bfd_get		------> oam_bfd_get

kyland_oam_bfd_del		------> oam_bfd_del

### 功能简介

bfd frame接收时报文检查表项配置,可以配置对bfd报文进行哪些位域的检查,确保接收的bfd报文正确性

注: 此接口主要作为修改bfd 表项的接口,使用此接口前应该添加过至少一张bfd表项.

### 接口及参数描述

kyland_rc kyland_oam_bfd_check_set(const kyland_inst_t inst, u16 index, kyland_oam_bfd_check_t *check);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//bfd表项index

kyland_oam_bfd_check_t *check	//check表项的配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_bfd_check_get(const kyland_inst_t inst, u16 index, kyland_oam_bfd_check_t *check);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//bfd表项index

kyland_oam_bfd_check_t *check	//读取到的bfd  check表项配置

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

typedef struct {

ucBool bfd_rx_port_chk_ena;

kyland_oam_bfd_rx_len_check_t  len;

ucBool  bfd_rx_verify_discr_ena;	/**< Enable bfd frame RX check discriminator */

ucBool  bfd_rx_verify_flags_ena;	/**< Enable bfd frame RX check flag */

ucBool  bfd_rx_verify_version_ena;	 /**< Enable bfd frame RX check version */

}kyland_oam_bfd_check_t;

### 调用cil层接口

kyland_oam_bfd_check_set		------> oam_bfd_check_set

kyland_oam_bfd_check_get		------> oam_bfd_check_get

### 功能简介

Bfd 接收报文时extract to cpu 的表项配置和读取接口.

### 接口及参数描述

kyland_rc kyland_oam_bfd_rx_extr_set(const kyland_inst_t inst,u16 index,kyland_oam_bfd_rx_extr_t *extr);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//bfd表项index

kyland_oam_bfd_rx_extr_t *extr	//extract to cpu 的配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------ kyland_rc kyland_oam_bfd_rx_extr_get(const kyland_inst_t inst,u16 index,kyland_oam_bfd_rx_extr_t *extr);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//bfd表项index

kyland_oam_bfd_rx_extr_t *extr	//读取到的extract to cpu 的配置

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

typedef struct{

ucBool cc_good_extr;

ucBool cv_good_extr;

ucBool param_change_extr;

ucBool p_set_extr;

ucBool f_set_extr;

ucBool error_extr;

}kyland_oam_bfd_rx_extr_t;

### 调用cil层接口

kyland_oam_bfd_rx_extr_set	------> oam_bfd_rx_extr_set

kyland_oam_bfd_rx_extr_get	------> oam_bfd_rx_extr_get

### 功能简介

bfd 本地和远端状态获取接口.通过该接口可以获取到本地和远端bfd的实时状态信息.

### 接口及参数描述

kyland_rc kyland_oam_bfd_loc_state_get(const kyland_inst_t inst,u16 index,ucBool *loc_state);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//bfd表项index

kyland_oam_bfd_remote_state_t *state	//获取到的本地bfd状态

返回值:

操作码.

-------------------------------------------------------------------------------

kyland_rc kyland_oam_bfd_remote_state_get(const kyland_inst_t inst,u16 index,kyland_oam_bfd_remote_state_t *state);

参数:

const kyland_inst_t inst  //芯片实例

u16 index		//bfd表项index

kyland_oam_bfd_remote_state_t *state	//获取到的远端bfd状态

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

typedef struct{

u8 source_remote_state;	/**< BFD source的remote state,接收时采样报文中的远端的状态*/

u8 source_remote_diag;	/**< BFD source的remote diag,接收时采样报文中的远端的状态*/

u8 source_remote_dm;	/**< BFD source的remote DM,接收时采样报文中的远端的状态*/

u8 sink_remote_state;	/**< BFD sink的remote state,接收时采样报文中的远端的状态*/

u8 sink_remote_diag;	/**< BFD sink的remote diag,接收时采样报文中的远端的状态*/

u8 sink_remote_dm;	/**< BFD sink的remote DM,接收时采样报文中的远端的状态*/

}kyland_oam_bfd_remote_state_t;

### 调用cil层接口

kyland_oam_bfd_loc_state_get		------> oam_bfd_loc_state_get

kyland_oam_bfd_remote_state_get	------> oam_bfd_remote_state_get

## OAM中断相关接口

### 功能简介

OAM中断接口包括本地表项中断,远端表项中断,bfd表项中断.初始化后oam中断功能默认打开,将中断服务函数挂载后就可实现中断功能.所有表项相同的中断类型使用同一个中断回调函数,SDK会将发生中断的表项index传给回调函数,使用使能或关闭接口可以将指定index的oam表项内指定中断类型打开或者关闭.

### 接口及参数描述

kyland_rc kyland_oam_intr_cfg(const kyland_inst_t inst, kyland_oam_intr_cmd_t cmd);

参数:

const kyland_inst_t inst  //芯片实例

kyland_oam_intr_cmd_t cmd	//oam 中断打开关闭命令

返回值:

操作码.

-------------------------------------------------------------------------------

kyland_rc kyland_oam_interrupt_notify_request(const kyland_inst_t inst,

const kyland_oam_intr_type type,

oam_intr_notify_function_t cb_func);

参数:

const kyland_inst_t inst  //芯片实例

const kyland_oam_intr_type type 		//oam中断类型选择

oam_intr_notify_function_t cb_func  	//oam中断回调函数

返回值:

操作码.

-------------------------------------------------------------------------------

kyland_rc kyland_oam_interrupt_enable(const kyland_inst_t inst,

u16 index,

kyland_oam_intr_type type);

参数:

const kyland_inst_t inst  //芯片实例

u16 index //oam表项index

const kyland_oam_intr_type type 	//需要打开的oam中断类型选择

返回值:

操作码.

-------------------------------------------------------------------------------

kyland_rc kyland_oam_interrupt_disable(const kyland_inst_t inst,

u16 index,

kyland_oam_intr_type type);

参数:

const kyland_inst_t inst  //芯片实例

u16 index //oam表项index

const kyland_oam_intr_type type 	//需要关闭的oam中断类型选择

返回值:

操作码.

### 相关数据结构

//中断功能的相关数据结构

//中断开关相关数据结构

typedef enum {

KYLAND_OAM_INTR_ENABLE,		/**< Oam interrupt function enable */

KYLAND_OAM_INTR_DISABLE		/**< Oam interrupt function disable */

}kyland_oam_intr_cmd_t;

-------------------------------------------------------------------------------

//oam中断类型相关数据结构

typedef enum{

KYLAND_OAM_INTR_LMEP_MISS,			            /**<  Generate interrupt when lmep miss */

KYLAND_OAM_INTR_VERSION_ERR,		            /**<  Generate interrupt when rx oam frame version error */

KYLAND_OAM_INTR_DMAC_ERR,			            /**<  Generate interrupt when rx oam frame dmac error */

KYLAND_OAM_INTR_LMEP_CCM_ERROR_PERIOD,		    /**<  Generate interrupt when lmep rx ccm frame error period */

KYLAND_OAM_INTR_LMEP_CCM_ERROR_PRIORITY,		/**<  Generate interrupt when lmep rx ccm frame error priority */

KYLAND_OAM_INTR_LMEP_CCM_ERROR_RMEP_ID,		    /**<  Generate interrupt when lmep rx ccm frame error rmep id */

KYLAND_OAM_INTR_LMEP_CCM_XCON,		            /**<  Generate interrupt when lmep rx ccm frame xcon */

KYLAND_OAM_INTR_LMEP_LBR_ERROR_SEQUENCE,		/**<  Generate interrupt when lmep rx lbr frame error sequence */

KYLAND_OAM_INTR_LMEP_TST_ERROR_SEQUENCE,		/**<  Generate interrupt when lmep rx tst frame error sequence */

KYLAND_OAM_INTR_LMEP_SL_ERROR_PRIORITY,		    /**<  Generate interrupt when lmep rx sl frame error priority */

KYLAND_OAM_INTR_LMEP_SL_ERROR_TEST_ID,		    /**<  Generate interrupt when lmep rx sl frame error test id */

KYLAND_OAM_INTR_LMEP_SL_ERROR_MEP_ID,		    /**<  Generate interrupt when lmep rx sl frame error mep id */

KYLAND_OAM_INTR_G8113_1_LBX_ERROR_MXP_ID,	    /**<  Generate interrupt when rx g_8113_1 frame error mxp id */

KYLAND_OAM_INTR_G8113_1_LBX_ERROR_INDC,	        /**<  Generate interrupt when rx g_8113_1 frame error indc */

KYLAND_OAM_INTR_G8113_1_LBX_MISSING_TLV,	    /**<  Generate interrupt when rx g_8113_1 frame missing tlv */

KYLAND_OAM_INTR_G8113_1_LBX_ERROR_SUBTYPE,	    /**<  Generate interrupt when rx g_8113_1 frame error sbutype */

KYLAND_OAM_INTR_RMEP_CCM_LOC,		            /**<  Generate interrupt when rmep ccm loc state changed */

KYLAND_OAM_INTR_RMEP_CCM_RDI,		            /**<  Generate interrupt when rmep rx ccm frame rdi not equal to before */

KYLAND_OAM_INTR_RMEP_CCM_ERROR_SEQUENCE,		/**<  Generate interrupt when rmep rx ccm frame error */

KYLAND_OAM_INTR_RMEP_CCM_PORT_STATE_CHANGE,		/**<  Generate interrupt when rmep rx ccm frame port state change */

KYLAND_OAM_INTR_RMEP_CCM_INTERFACE_STATE_CHANGE,/**<  Generate interrupt when rmep rx ccm frame interface state change */

KYLAND_OAM_BFD_LOC,					            /**<  Generate interrupt when bfd table loc state changed */

KYLAND_OAM_BFD_SOURCE_RX_P_SET,		            /**<  Generate interrupt when bfd mode cordinated  received frame p set */

KYLAND_OAM_BFD_SOURCE_RX_F_SET,		            /**<  Generate interrupt when bfd mode cordinated  received frame f set */

KYLAND_OAM_BFD_SOURCE_RX_STATE_CHANGE,	        /**<  Generate interrupt when bfd mode cordinated  received frame state change */

KYLAND_OAM_BFD_SOURCE_RX_DIAG_CHANGE,	        /**<  Generate interrupt when bfd mode cordinated  received frame diag change */

KYLAND_OAM_BFD_SOURCE_RX_DM_CHANGE, 	        /**<  Generate interrupt when bfd mode cordinated  received frame dm change */

KYLAND_OAM_BFD_SINK_RX_P_SET,			        /**<  Generate interrupt when bfd mode independent received frame p set */

KYLAND_OAM_BFD_SINK_RX_F_SET,			        /**<  Generate interrupt when bfd mode independent received frame f set */

KYLAND_OAM_BFD_SINK_RX_STATE_CHANGE,	        /**<  Generate interrupt when bfd mode independent received frame state change */

KYLAND_OAM_BFD_SINK_RX_DIAG_CHANGE,		        /**<  Generate interrupt when bfd mode independent received frame diag change */

KYLAND_OAM_BFD_SINK_RX_DM_CHANGE,		        /**<  Generate interrupt when bfd mode independent received frame dm change */

KYLAND_OAM_INTR_MAX

}kyland_oam_intr_type;

//中断事件类型结构体

typedef struct  {

ucBool version_error; 			        /**< oam version error interrupt */

ucBool dmac_error;          		    /**< oam frame dmac error interrupt */

ucBool lmep_ccm_error_period;       	/**< oam lmep ccm frame period error interrupt */

ucBool lmep_ccm_error_priority;       	/**< oam lmep ccm frame priority error interrupt */

ucBool lmep_ccm_error_rmep_id;       	/**< oam lmep ccm frame rmep_id error interrupt */

ucBool lmep_ccm_xcon;       	        /**< oam lmep ccm frame meg_id error interrupt */

ucBool lmep_lbr_error_sequence;			/**< oam lmep lbr frame error interrupt */

ucBool lmep_tst_error_sequence;			/**< oam lmep tst frame error interrupt */

ucBool lmep_sl_error_priority;			/**< oam lmep sl frame error interrupt */

ucBool lmep_sl_error_test_id;			/**< oam lmep sl frame error interrupt */

ucBool lmep_sl_error_mep_id;			/**< oam lmep sl frame error interrupt */

ucBool g_8113_1_error_mxp_id;			/**< oam g_8_113_1 error interrupt */

ucBool g_8113_1_error_indc;			    /**< oam g_8_113_1 error interrupt */

ucBool g_8113_1_missing_tlv;	        /**< oam g_8_113_1 error interrupt */

ucBool g_8113_1_error_subtype;	        /**< oam g_8_113_1 error interrupt */

ucBool rmep_ccm_loc;			        /**< oam rmep ccm loc state changed interrupt */

ucBool rmep_ccm_rdi;			        /**< oam rmep ccm received rdi interrupt */

ucBool rmep_ccm_error_sequence;			/**< oam rmep received ccm frame sequence number error interrupt */

ucBool rmep_ccm_port_state_change;		/**< oam rmep received ccm frame port state change  interrupt */

ucBool rmep_ccm_interface_state_change; /**< oam rmep received ccm frame interface state change  interrupt */

ucBool bfd_loc; 				        /**< bfd  loc state changed  interrupt */

ucBool bfd_source_rx_p_set;             /**< bfd  mode Cordinated received frames p set interrupt */

ucBool bfd_source_rx_f_set;             /**< bfd  mode Cordinated received frames f set interrupt */

ucBool bfd_source_rx_state_change;      /**< bfd  mode Cordinated received frames state change interrupt */

ucBool bfd_source_rx_diag_change;       /**< bfd  mode Cordinated received frames diag change interrupt */

ucBool bfd_source_rx_dm_change;         /**< bfd  mode Cordinated received frames dm change interrupt */

ucBool bfd_sink_rx_p_set;   		    /**< bfd  mode independent received frames p set error interrupt */

ucBool bfd_sink_rx_f_set;   		    /**< bfd  mode independent received frames f set error interrupt */

ucBool bfd_sink_rx_state_change;   	    /**< bfd  mode independent received frames state change interrupt */

ucBool bfd_sink_rx_diag_change;   	    /**< bfd  mode independent received frames diag change interrupt */

ucBool bfd_sink_rx_dm_change;   	    /**< bfd  mode independent received frames dm change interrupt */

u8 *reserved;

} kyland_oam_event_status_t;

### 调用cil层接口

## OAM lm统计相关接口

### 功能简介

OAM统计相关接口可以配置统计那种报文，将该种报文统计在port/path/services表中。通过读统计功能可以查看统计的具体值，通过清除接口可以将某个统计清空。如要删除一个统计表项可以通过删除操作实现删除某个统计表项

### 接口及参数描述

kyland_rc kyland_oam_sport_lm_cfg(const kyland_inst_t inst, kyland_port_t port_num,	kyland_oam_lm_t *cnt)	;

参数:

const kyland_inst_t inst  	//芯片实例

kyland_port_t port_num		//入口port number

kyland_oam_lm_t *cnt		//统计表项配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_sport_lm_get(const kyland_inst_t inst, kyland_port_t port_num, kyland_oam_lm_t *cnt);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t  port_num	//需要读取配置的入端口port number

kyland_oam_lm_t *cnt		//读取到的lm表项配置信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_sport_lm_del(const kyland_inst_t inst, kyland_port_t port_num);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num	 	//需要删除的入端口统计表项的port number

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_dport_lm_cfg(const kyland_inst_t inst, kyland_port_t port_num,	kyland_oam_lm_t *cnt);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num		//入口port number

kyland_oam_lm_t *cnt		//统计表项配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_dport_lm_get(const kyland_inst_t inst, kyland_port_t port_num, kyland_oam_lm_t *cnt);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num	//需要读取配置的出端口port number

kyland_oam_lm_t *cnt		//读取到的lm表项配置信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_dport_lm_del(const kyland_inst_t inst, kyland_port_t port_num)	;

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num		//需要删除的入端口统计表项的port number

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_ivport_lm_cfg(const kyland_inst_t inst, u16 index, kyland_oam_cnt_t *cnt)	;

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//需要统计的ivport 值

kyland_oam_cnt_t *cnt		//统计表项配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_ivport_lm_get(const kyland_inst_t inst, u16 index, kyland_oam_cnt_t *cnt);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//需要读取配置的ivport值

kyland_oam_cnt_t *cnt		//读取到的lm表项配置信息

返回值:

操作码.

kyland_rc kyland_oam_ivport_lm_del(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//需要删除的统计表项ivport值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_evport_lm_cfg(const kyland_inst_t inst, u16 index, kyland_oam_cnt_t *cnt)	;

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//需要统计的evport 值

kyland_oam_cnt_t *cnt		//统计表项配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_evport_lm_get(const kyland_inst_t inst, u16 index, kyland_oam_cnt_t *cnt);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//需要读取配置的evport值

kyland_oam_cnt_t *cnt		//读取到的lm表项配置信息

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_evport_lm_del(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//需要删除的统计表项evport值

返回值:

操作码.

### 相关数据结构

//port 类型的lm表项相关数据结构

typedef struct {

ucBool  lm_cnt_enable;		/**< Lm cnt table enable or disable */

kyland_oam_color_map_source  color_map_souce;/**< Choose the color table map source */

kyland_oam_cosid_map_source  cosid_map_source;/**< Choose the cosid table map source */

ucBool  yellow_ena ; 			/**< Statistics yellow packets or not */

u8	dp_yellow_value; 		/**< Yellow packets dp value */

u8 	down_mel; 			/**< Down mep level */

u8 	up_mel;			/**< Up mep level */

}kyland_oam_lm_t;

------------------------------------------------------------------------------------------------------------------------------------------

typedef struct{

ucBool  service_valid;		/**< The service table valid or not */

u16  service_index;		/**< The service table index */

ucBool  path_valid;		/**< The path table valid or not */

u16  path_index;		/**< The path table index */

kyland_oam_lm_t  path;	/**< The path table configuration */

kyland_oam_lm_t  service;	/**< The service table configuration */

}kyland_oam_cnt_t;

### 调用cil层接口

kyland_oam_sport_lm_cfg		------>  oam_sport_lm_cfg

kyland_oam_sport_lm_get		------>  oam_sport_lm_get

kyland_oam_sport_lm_del		------>  oam_sport_lm_del

kyland_oam_dport_lm_cfg		------>  oam_dport_lm_cfg

kyland_oam_dport_lm_get		------>  oam_dport_lm_get

kyland_oam_dport_lm_del		------>  oam_dport_lm_del

kyland_oam_ivport_lm_cfg		------>  oam_ivport_lm_cfg

kyland_oam_ivport_lm_get		------>  oam_ivport_lm_get

kyland_oam_ivport_lm_del		------>  oam_ivport_lm_del

kyland_oam_evport_lm_cfg		------>  oam_evport_lm_cfg

kyland_oam_evport_lm_get		------>  oam_evport_lm_get

kyland_oam_evport_lm_del		------>  oam_evport_lm_del

### 功能简介

统计查看功能接口,可以查看统计值,清空某个统计值.

### 接口及参数描述

kyland_rc kyland_oam_sport_lm_cnt_get(const kyland_inst_t inst, kyland_port_t port_num,

kyland_oam_lm_cnt_t *xgrlm);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num		//表项所在port

kyland_oam_lm_cnt_t *xgrlm	//获取到的统计值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_sport_lm_cnt_clear(const kyland_inst_t inst, kyland_port_t port_num);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num		//表项所在port

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_dport_lm_cnt_get(const kyland_inst_t inst, kyland_port_t port_num,

kyland_oam_lm_cnt_t *xgrlm);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num		//表项所在port

kyland_oam_lm_cnt_t *xgrlm	//获取到的统计值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland _oam_dport_lm_cnt_clear(const kyland_inst_t inst, kyland_port_t port_num);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num		//表项所在port

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland _oam_ivport_lm_cnt_get(const kyland_inst_t inst, u16 index, kyland_oam_lm_cnt_t *xgrlm);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

kyland_oam_lm_cnt_t *xgrlm	//获取到的统计值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland _oam_ivport_lm_cnt_clear(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland _oam_evport_lm_cnt_get(const kyland_inst_t inst, u16 index, kyland_oam_lm_cnt_t *xgrlm);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

kyland_oam_lm_cnt_t *xgrlm	//获取到的统计值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland _oam_evport_lm_cnt_clear(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyalnd_oam_port_sample_lm_cnt_get(const kyland_inst_t inst, kyland_port_t port_num,

kyland_oam_sample_t *sample);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num		//表项所在port

kyland_oam_sample_t *sample	//读取到的值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_port_sample_lm_cnt_clear(const kyland_inst_t inst, kyland_port_t port_num);

参数:

const kyland_inst_t inst		//芯片实例

kyland_port_t port_num	//表项所在port

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyalnd_oam_ivport_sample_lm_cnt_get(const kyland_inst_t inst, u16 index,

kyland_oam_sample_t *sample);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

kyland_oam_sample_t *sample	//读取到的值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_ivport_sample_lm_cnt_clear(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyalnd_oam_evport_sample_lm_cnt_get(const kyland_inst_t inst, u16 index,

kyland_oam_sample_t *sample);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

kyland_oam_sample_t *sample	//读取到的值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_sample_lm_cnt_clear(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_oam_api.h文件

//xgrlm表相关数据结构

typedef struct {

u32 cos0_fci;	/**< Receiving packets statistics by priority 0 */

u32 cos1_fci;	/**< Receiving packets statistics by priority 1 */

u32 cos2_fci;	/**< Receiving packets statistics by priority 2 */

u32 cos3_fci;	/**< Receiving packets statistics by priority 3 */

u32 cos4_fci;	/**< Receiving packets statistics by priority 4 */

u32 cos5_fci;	/**< Receiving packets statistics by priority 5 */

u32 cos6_fci;	/**< Receiving packets statistics by priority 6 */

u32 cos7_fci;	/**< Receiving packets statistics by priority 7 */

}kyland_oam_lm_cnt_t;

------------------------------------------------------------------------------------------------------------------------------------------

//sample 表相关数据结构

typedef struct {

u32 ccm_send_rxfcb;		/**< Send ccm packet rxfcb */

u32 ccm_send_txfcb;		/**< Send ccm packet txfcb */

}kyland_oam_sample_t;

### 调用cil层接口

kyland_oam_sport_lm_cnt_get		------>  oam_sport_lm_cnt_get

kyland_oam_sport_lm_cnt_clear		------>  oam_sport_lm_cnt_clear

kyland_oam_dport_lm_cnt_get		------>  oam_dport_lm_cnt_get

kyland_oam_dport_lm_cnt_clear		------>  oam_dport_lm_cnt_clear

kyland_oam_ivport_lm_cnt_get		------>  oam_ivport_lm_cnt_get

kyland_oam_ivport_lm_cnt_clear		------>  oam_ivport_lm_cnt_clear

kyland_oam_evport_lm_cnt_get		------>  oam_evport_lm_cnt_get

kyland_oam_evport_lm_cnt_clear		------>  oam_evport_lm_cnt_clear

kyalnd_oam_port_sample_lm_cnt_get	------>  oam_port_sample_lm_cnt_get

kyland_oam_port_sample_lm_cnt_clear	------>  oam_port_sample_lm_cnt_clear

kyalnd_oam_ivport_sample_lm_cnt_get	------>  oam_ivport_sample_lm_cnt_get

kyland_oam_ivport_sample_lm_cnt_clear	------>  oam_ivport_sample_lm_cnt_clear

kyalnd_oam_evport_sample_lm_cnt_get	------>  oam_evport_sample_lm_cnt_get

kyland_oam_evport_sample_lm_cnt_clear	------>  oam_evport_sample_lm_cnt_clear

## 查看OAM报文统计相关接口

### 功能简介

查看oam模块收到的报文统计相关接口,包括收到的报文和收到的错误报文等

### 接口及参数描述

kyland_rc kyland_oam_rx_error_count_get(const kyland_inst_t inst, u16 index, kyland_oam_rx_error_t *cnt);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

kyland_oam_rx_error_t *cnt	//读取到的错误报文统计值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_rx_error_count_clear(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst		//芯片实例

u16 index	 		// 表项index

返回值:

操作码.
------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_frame_count_get(const kyland_inst_t inst, u16 index, kyland_oam_frame_cnt_t *cnt);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

kyland_oam_frame_cnt_t *cnt	//收到的报文统计值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_frame_count_clear(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_bfd_rx_miss_count_get(const kyland_inst_t inst, u16 *bfd_miss_cnt);

参数:

const kyland_inst_t inst		//芯片实例

u16 *bfd_miss_cnt	 	//收到的bfd报文 miss 统计

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_bfd_rx_miss_count_clear(const kyland_inst_t inst)

参数:

const kyland_inst_t inst		//芯片实例

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_bfd_count_get(const kyland_inst_t inst, u16 index, kyland_oam_bfd_count_t *cnt);

参数:

const kyland_inst_t inst		//芯片实例

u16 index 			//表项index

kyland_oam_bfd_count_t *cnt	//读取到的bfd统计值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_bfd_count_clear(const kyland_inst_t inst, u16 index);

参数;

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

返回值:

操作码.

### 相关数据结构

//收到错误报文相关数据结构

typedef struct{

u16 rx_discard_cnt_1;                /**< Rx oam frame error discard count */

u16 rx_discard_cnt_2;                /**< Rx oam frame error discard count */

u16 lbr_tst_seq_err_cnt;		     /**< Rx lbr or tst frame sequence id error count */

}kyland_oam_rx_error_t;

------------------------------------------------------------------------------------------------------------------------------------------

//收到的报文统计相关数据结构

typedef struct{

u16 rx_dm_cnt;		 		 /**< Rx dmm/dmr/1dm frame cnt*/

u16 rx_lm_cnt;              			 /**< Rx lmm/lmr frame cnt*/

u16 rx_lbm_cnt;		         		 /**< Rx lbm frame cnt*/

u16 rx_lbr_cnt;		         		 /**< Rx lbr frame cnt*/

u16 rx_tst_cnt;		         		 /**< Rx tst frame cnt*/

u16 tx_sl_cnt; 				 /**< Tx slm/1sl cnt*/

u16 tx_dm_cnt;				 /**< Tx dmm/dmr/1dm frame cnt*/

u16 tx_lm_cnt;              			 /**< Tx lmm/lmr frame cnt*/

u16 tx_lbr_cnt;		         		 /**< Tx lbr frame cnt*/

u16 tx_tst_cnt;		         		 /**< Tx tst frame cnt*/

}kyland_oam_frame_cnt_t;

### 调用cil层接口

kyland_oam_rx_error_count_get		------> oam_rx_error_count_get

kyland_oam_rx_error_count_clear		------> oam_rx_error_count_clear

kyland_oam_frame_count_get		------> oam_frame_count_get

kyland_oam_frame_count_clear		------> oam_frame_count_clear

kyland_oam_bfd_rx_miss_count_get		------> oam_bfd_rx_miss_count_get

kyland_oam_bfd_rx_miss_count_clear	------> oam_bfd_rx_miss_count_clear

kyland_oam_bfd_count_get		------> oam_bfd_count_get

kyland_oam_bfd_count_clear		------> oam_bfd_count_clear

## 查看OAM ccm 接收时间相关接口

### 功能简介

查看oam模块收到的ccm报文接收到的时间相关接口

### 接口及参数描述

kyland_rc kyland_oam_ccm_time_get(const kyland_inst_t inst, u16 index, kyland_oam_ccm_time_t *time);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

kyland_oam_ccm_time_t *time	//接收到到的时间值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_ccm_time_clear(const kyland_inst_t inst, u16 index);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//表项index

返回值:

操作码.

### 相关数据结构

typedef struct{

u32 rx_meg_err_time;			 /**< Rx ccm meg error time */

u32 rx_ccm_err_time_1;              	 /**< Rx oam ccm frame error time_1 */

u32 rx_ccm_err_time_2;		        	 /**< Rx oam ccm frame error time_2 */

u32 tx_ccm_time;		 	  /**< Tx oam ccm frame time */

}kyland_oam_ccm_time_t;

### 调用cil层接口

kyland_oam_ccm_time_get		------> oam_ccm_time_get

kyland_oam_ccm_time_clear		------> oam_ccm_time_clear

## Meg表项操作接口

### 功能简介

当ccm检测到链路状态由loc变为连通时,cpu需要通过meg表项操作接口来更改对应meg表项中的rdi flag状态(将rdi flag状态清0).否则本芯片发送出去的ccm报文依然携带rdi flag.

### 接口及参数描述

kyland_rc kyland_oam_meg_set(const kyland_inst_t inst, u16 index, ucBool flag);

参数:

const kyland_inst_t inst		//芯片实例

u16 index			//oam  meg表项index

ucBool flag			//oam meg表项flag状态

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_oam_meg_get(const kyland_inst_t inst, u16 index, ucBool *flag);

参数:

const kyland_inst_t inst		//芯片实例

u16 index		  	//oam meg表项index

ucBool *flag		//读取到的rdi flag状态

返回值:

操作码.

### 相关数据结构

无

### 调用cil层接口

kyland_oam_meg_set			------> oam_meg_set

kyland_oam_meg_get			------> oam_meg_get

# OAM应用举例

## eth oam

如图所示:企业网络和运营商网络各自的边缘设备Device A 和Device B进行连接.使用以太网OAM功能,监控Device A和Device B间链路的状态,从而可确定运营商所提供的网络链路可靠性是否符合与企业签订的SLA(Service Level Agreement),具体需求:

实现自动检测Device A和Device B之间链路的连通性;

网络管理员可以查看是否Device A 和 Device B之间链路是否发生紧急链路事件;

网络管理员可以通过观察一般链路事件统计信息动态的了解链路状态;

具体配置:

1在Device A上面配置本地mep表项.

添加一张down port类型的 oam lmep表项.其中本地mep_id = 123, mel = 3, 使用的表项 index = 0, meg表项的index = 0,ccm period = 3.3ms,所在port = 0,本地的mac 地址是00-11-22-33-44-55,ccm的priority = 0. 添加完成后函数会将hash表的key值信息填写在key结构体中,以便后续读写使用.

代码示范:

kyland_oam_lmep_t lmep;

KYLAND_OS_MEMSET(&lmep,0,sizeof(kyland_oam_lmep_t));

lmep.oam_enable = 1;

lmep.mep_mip_flag = 1;

lmep.down_up = 0;

lmep.mep_mode = KYLAND_OAM_MODE_PORT;

lmep.meg_index = 0;

lmep.mel = 3;

lmep.mep_id = 123;

lmep.port = 0;

lmep.mep_mac.addr[0] = 0x00;

lmep.mep_mac.addr[1] = 0x11;

lmep.mep_mac.addr[2] = 0x22;

lmep.mep_mac.addr[3] = 0x33;

lmep.mep_mac.addr[4] = 0x44;

lmep.mep_mac.addr[5] = 0x55;

lmep.ccm_period = KYLAND_OAM_CCM_PERIOD_3_3_MS;

lmep.ccm_pri = 0;

lmep.tx_cfg.update.ccm_tx_rdmeg = 1;

lmep.tx_cfg.update.ccm_tx_seq_update_ena = 1;

lmep.tx_cfg.ccm_lm_insert_loc_timer_id = KYLAND_OAM_HMO_3_3_MS;

lmep.tx_cfg.auto_ccmlm_insert_enable = 1;

kyland_oam_lmep_key_t key;

rc |= kyland_oam_lmep_add(NULL,0,&lmep,&key);

2在Device A上面配置远端mep表项.

添加一张down port类型的远端表.表项 index = 0, 关联的meg表项index = 0,保护组id = 1,发生ccm 连通loc 时设置meg 表项的rdi位,同时关闭保护组, 在收到携带rdi的ccm报文时关闭保护组.loc 周期是3.3ms. 表项的mel 是3,表项vport 是0. Rmep_id = 456.变相添加完成后会获取到hash 表项的key信息.

kyland_oam_rmep_t rmep;

KYLAND_OS_MEMSET(&rmep,0,sizeof(kyland_oam_rmep_t));

rmep.rmep_enable = 1;

rmep.meg_index = 0;

rmep.ccm_expect_sequence_number = 0;

rmep.ccm_loc_timer_id = KYLAND_OAM_LOC_3_3_MS;

rmep.change.loc_set_meg_rdi = 1;

rmep.change.loc_set_group_status = 1;

rmep.change.rcv_rdi_change_group_status = 1;

rmep.mel = 3;

rmep.protect_group_id = 1;

rmep.session_type = KYLAND_OAM_RMEP_TYPE_PORT;

rmep.vport = 0;

rmep.rmep_id = 456;

kyland_oam_rmep_key_t key;

rc |= kyland_oam_rmep_add(inst,0,&rmep,&key);

3在Device A上面配置AFI TTI自动发送ccm报文功能.

首先需要cpu构造ccm报文模板.下面的配置举例中,ccm的发送间隔 = 3.3ms,报文的优先级 = 4,报文的出端口 = port 0, 报文的mel = 3,oam mode = KYLAND_OAM_FRAME_MODE_ETH_PORT, 本地 mep type = KYLAND_OAM_MEP_DOWN,报文的vlan id 是100. 报文的发送长度最后要 + 4字节(crc 32 检验位).

kyland_oam_ccm_frame frame;

KYLAND_OS_MEMSET(&frame,0,sizeof(kyland_oam_ccm_frame));

…(报文赋值);

kyland_oam_tti_t tti;

KYLAND_OS_MEMSET(&tti,0,sizeof(kyland_oam_tti_t));

tti.period = KYLAND_OAM_PACKET_PERIOD_3_3_MS;

tti.port = 0;

tti.frame_ptr = 0;

tti.pri = KYLAND_OAM_PACKET_PRI_4;

tti.slot_cnt = 1;

tti.slot_end_ptr = 0;

tti.slot_start_ptr = 0;

tti.solt_cal_len = 0;

tti.solt_index = 0;

tti.tick_idx = 1;

tti.timer_len = 1;

tti.tti_ena = 1;

kyland_oam_frame_info_t info;

KYLAND_OS_MEMSET(&info,0,sizeof(kyland_oam_frame_info_t));

info.oam_mode = KYLAND_OAM_FRAME_MODE_ETH_PORT;

info.mel = 3;

info.mep_type = KYLAND_OAM_MEP_DOWN;

info.vid = 100;

info.length = sizeof(frame)+4;

u8 * send_frame = (u8 *)&frame;

rc |= kyland_oam_frame_set(0,0,0,0,&info,send_frame);

rc |= kyland_oam_tti_set(0,0,&tti);

1.4 Device B的配置

Device B的配置与Device A的配置方式一样,mep_id 和 rmep_id 需要正确填写Device A的信息.

## mpls lsp oam

存在一条lsp链路(PE-A  ->  P-1   ->   PE-B),为了对该lsp进行保护,需要再建立一条与该lsp具有相同源宿节点的备lsp(PE-A  ->  P-2  ->  PE-B)指定倒换方式是1:1,并在主lsp(红色) 上实施oam ccm检测功能.

具体配置:

Mpls lsp oam 的配置方式与 eth oam 的配置方式相同. 主要区别在于配置时type 需要选择 mpls lsp 类型,需要正确填写标签表的index 信息.

## ipv4 bfd

PC – 1 与 PC – 2之间存在一条主链路(PE-A -> P-1 -> PE-B),为了保障该链路的稳定性,需要另外一条备份链路(PE-A -> P-2 -> PE-B).在主链路(红色)上面配置ipv4 bfd 功能,监测链路状态.

1 PE-A的表项配置.

配置本地loc timer id = KYLAND_OAM_LOC_3_3_MS ,detect mult = 3,即丢失三个报文后进入loc状态,	使能loc 时切换保护组loc_protect_switch_ena = 1,保护组ID protect_group_id = 1, 使能接收报文时进行采样bfd_rx_sample_ena = 1,配置发送报文时本地的 bfd_local_diag_src = 0, bfd_local_dm_src = 3,

bfd_local_state_src = 2.使能发送报文时更新报文内容bfd_tx_update_ena = 1,配置bfd模式为coordinated, bfd_coordinated_mode_ena = 1,bfd表项index = 0.

kyland_oam_bfd_t bfd;

KYLAND_OS_MEMSET(&bfd,0,sizeof(kyland_oam_bfd_t));

bfd.bfd_ena = 1;

bfd.loc_protect_switch_ena = 1;

bfd.protect_group_id = 1;

bfd.bfd_coordinated_mode_ena = 1;

bfd.bfd_rx_sample_ena = 1;

bfd.cc.bfd_rx_verify_cc_ena = 1;

bfd.bfd_detect_mult = 3;

bfd.port_num = 0;

bfd.bfd_loc_detect_ena = 1;

bfd.bfd_loc_timer = KYLAND_OAM_LOC_3_3_MS;

bfd.info.discriminator = 12;

bfd.bfd_local_discr_src = 12;

bfd.bfd_remote_discr_src = 34;

bfd.bfd_tx.bfd_local_diag_src = 0;

bfd.bfd_tx.bfd_local_dm_src = 3;

bfd.bfd_tx.bfd_local_state_src = 2;

bfd.bfd_tx.bfd_tx_update_ena = 1;

bfd.bfd_tx.bfd_coordinated_mode_ena = 1;

bfd.bfd_tx.bfd_local_discr_src = 12;

kyland_oam_bfd_key_t key;

rc |= kyland_oam_bfd_add(inst,0,&bfd,&key);

2 PE-A的发包配置

报文的发送周期是period = KYLAND_OAM_PACKET_PERIOD_3_3_MS,优先级是pri = KYLAND_OAM_PACKET_PRI_4,出端口是port = 0,AFI的frame表和tti表的index是0,mep type 是mep_type = KYLADN_OAM_MEP_BFD,bfd 报文类型是bfd_type = BFD_FOR_IP,bfd的encap 类型是bfd_encap_type =

KYLAND_OAM_BFD_V4UDP,bfd session表的index 是bfd_session_id = 0,报文的vid 是vid = 100.

kyland_oam_bfd_ipv4_frame frame;

KYLAND_OS_MEMSET(&frame,0,sizeof(kyland_oam_bfd_ipv4_frame));

…(报文赋值)

kyland_oam_tti_t tti;

KYLAND_OS_MEMSET(&tti,0,sizeof(kyland_oam_tti_t));

tti.period = KYLAND_OAM_PACKET_PERIOD_3_3_MS;

tti.port = 0;

tti.frame_ptr = 0;

tti.pri = KYLAND_OAM_PACKET_PRI_4;

tti.slot_cnt = 1;

tti.slot_end_ptr = 0;

tti.slot_start_ptr = 0;

tti.solt_cal_len = 0;

tti.solt_index = 0;

tti.timer_len = 1;

tti.tti_ena = 1;

kyland_oam_frame_info_t info;

KYLAND_OS_MEMSET(&info,0,sizeof(kyland_oam_frame_info_t));

info.mep_type = KYLADN_OAM_MEP_BFD;

info.bfd_type = BFD_FOR_IP;

info.bfd_encap_type = KYLAND_OAM_BFD_V4UDP;

info.bfd_session_id = 0;

info.vid = 100;

info.length = sizeof(frame)+4;

u8 * send_frame = (u8 *)&frame;

rc|= kyland_oam_frame_set(inst,0,0,0,&info,send_frame);

rc |= kyland_oam_tti_set(inst,0,&tti);

3 PE-B的配置

PE-B的配置和PE-A的配置方式相同,需要注意把my discriminator和your discriminator填写正确.
