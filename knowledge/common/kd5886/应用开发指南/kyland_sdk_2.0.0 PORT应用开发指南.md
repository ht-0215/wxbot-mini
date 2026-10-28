# kyland_sdk_2.0.0 PORT应用开发指南

kyland_sdk_2.0.0

PORT应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 简介	4

2 芯片支持	5

3 应用简介	6

4 SDK API及应用示例	9

4.1 SDK API	9

4.1.1 端口配置及端口状态获取接口	9

4.1.2 端口统计相关接口	14

4.1.3 端口Enable/Disable	18

4.1.4 端口Speed配置	19

4.1.5 端口双工模式配置	20

4.1.6 端口流控模式配置	21

4.1.7 端口frame配置	23

4.1.8 LED相关配置接口	24

4.1.9 自协商相关配置接口	26

4.2 应用示例	27

4.2.1 36*1000BASE-X + 4*SFI	27

4.2.2 端口使能流控	28

4.2.3 端口设置自协商	29

# 简介

KD5886包含两种MAC：GE MAC和10G MAC。分别处理1G和10G的速率MAC应用。

KD5886的端口模式包含C1、C2、C3模式。C1模式支持32GE+12XG；C2模式支持48GE+8XG；

C3模式支持48GE+8XG+IPSEC。

# 芯片支持

支持最多48个GE端口（10M\100M\1000M）

支持最多40个GE光口（1000M）

支持最多12个XG端口

支持全双工流控

半双工模式时支持载波侦听/冲突检测和报文重传

支持多种统计

支持QSGMII、SGMII、1000BASE-X和SFI接口类型

支持Clause 37自协商

支持TAXI 总线的外环和内环

支持PCS 的外环和内环

# 应用简介

无光口C1模式：32GE+12XG。

此时端口模式为C1模式，GE端口的接口类型为QSGMII，XG端口接口类型为SFI。Port_0~Port_31为GE端口，Port_48~Port_55为XG端口。

无光口C2/C3模式：48GE+8XG

此时端口模式为C2/C3模式，GE端口的接口类型为QSGMII，XG端口接口类型为SFI。Port_0~Port_47为GE端口，Port_48~Port_55为XG端口。

C1模式28GE光口+12XG

此时端口模式为C1模式，GE端口的接口类型为1000BASE-X，XG端口接口类型为SFI。Port_0~Port_27为GE光口，Port_48~Port_55为XG端口。

C2/C3模式40GE光口

此时端口模式为C1模式，GE端口的接口类型为1000BASE-X。Port_0~Port_39为GE光口，无XG端口。

端口模式和接口类型都需要在sdk初始化之前通过配置文件配置。在配置文件中调用kd_hal_sdk_config_set(int unit,char *name,char *strval)和kd_hal_sdk_port_config_set(int unit,int port,char *name,char *strval)接口，例如：

如果不配置sdk初始化时会使用默认配置，即C3模式48GE+8XG，端口模式为C3模式，GE端口接口类型为QSGMII，XG端口接口类型为SFI。

Sdk初始化前还需要配置端口有效bmp，例如:

不配置时默认所有端口有效。

端口流控

当入口流量大于出口带宽时，如果使能流控，则入端口会向对端设备发送pause帧，如果对端设备也使能流控，则对端设备发送速率会下降至本地设备出口速率。

端口自协商

配置Serdes的自协商，而不是phy芯片

端口强制速率双工

配置Serdes和MAC的速率双工，而不是phy芯片

# SDK API及应用示例

## SDK API

### 端口配置及端口状态获取接口

#### 功能简介

端口配置接口主要进行端口相关参数的配置，可以进行Mac芯片端口的速度，双工以及其相关配置。根据端口号以及相关映射，配置1G和10G端口。同时，也可以配置基于端口的可通过的最大的报文长度、流控、环回等功能。在SDK中，也是主要调用此接口进行端口初始化操作。kyland_port_conf_get接口可以获取端口相关配置参数。而kyland_port_status_get主要是获取端口link状态等实时参数，在端口link之后端口的速度双工状态，以及自协商状态等。

#### 接口及参数描述

/**

* \brief Set port configuration.

* Note: If if_type in the kyland_port_conf_t/kyland_port_interface_t

definition is set to KYLAND_PORT_INTERFACE_QSGMII, the ports are mapped together

in groups of four. If one of the four ports is used, all four ports in the group

must always be configured, but the four ports doesn't need to configured with

the same configuration.

* This is needed in order to achieve correct comma alignment at the QSGMII

interface. Which ports that are mapped together can be found in the chip datasheet.

*

* \param inst [IN] Target instance reference.

* \param port_no [IN] Port number.

* \param conf [IN] Port setup structure.

*

* \return Return code.

**/

kyland_rc  kyland_port_conf_set(const kyland_inst_t inst,

const kyland_port_no_t  port_no,

const kyland_port_conf_t  *const conf);

/**

* \brief Get port setup.

*

* \param inst [IN] Target instance reference.

* \param port_no [IN] Port number.

* \param conf [OUT] Port configuration.

*

* \return Return code.

**/

kyland_rc  kyland_port_conf_get(const kyland_inst_t inst,

const kyland_port_no_t  port_no,

kyland_port_conf_t  *const conf);

/**

* \brief Get port status.

*

* \param inst [IN] Target instance reference.

* \param port_no [IN] Port number.

* \param status [OUT] Status structure.

*

* \return Return code.

**/

kyland_rc  kyland_port_status_get(const kyland_inst_t inst,

const kyland_port_no_t  port_no,

kyland_port_status_t  *const status);

#### 相关数据结构

/** \brief Port configuration structure */

typedef struct

{

kyland_port_interface_t  if_type; 	/**< Interface type */

ucBool  power_down; 		/**< Disable and power down the port */

kyland_port_speed_t  speed; 	/**< Port speed */

ucBool  fdx;		/**< Full duplex mode */

kyland_port_flow_control_conf_t  flow_control; /**< Flow control setup*/

u32  max_frame_length;	 /**< Maximum frame length*/

ucBool  frame_length_chk; 	/**< Enforce 802.3 frame length check (from ethertype field) */

kyland_port_max_tags_t  max_tags; /**< VLAN awareness for length check */

ucBool  exc_col_cont; 		/**< Excessive collision continuation */

} kyland_port_conf_t;

/** \brief Port status parameter struct */

typedef struct

{

kyland_event_t  link_down; 	/**< Link down event occurred since last call */

ucBool  link; 		/**< Link is up. Remaining fields only valid if TRUE */

kyland_port_speed_t  speed; 	/**< Speed */

ucBool  fdx; 		/**< Full duplex */

ucBool  remote_fault; 		/**< Remote fault signalled */

ucBool  aneg_complete; 	/**< Autoneg completed (for clause_37 and Cisco aneg) */

ucBool  unidirectional_ability; 	/**<TRUE: PHY able to transmit from media independent interface

regardless of whether the PHY has determined that a valid link has been established.

FALSE: PHY able to transmit from media independent interface only when the PHY has determined

that a valid link has been established.

Note This bit is only applicable to 100BASE-FX and 1000BASE-X fiber media modes.*/

kyland_aneg_t  aneg; 		/**< Auto negotiation result */

ucBool  mdi_cross; 		/**< Indication of if Auto-MDIX crossover is performed */

ucBool  fiber; 		/**< Indication of if the link is a fiber link, TRUE if link is a fiber link.

FALSE if link is cu link or No Media*/

ucBool  copper; 		/**< Indication of if the link is a copper link, TRUE if link is a copper link.

FALSE if link is fiber link or No Media */

} kyland_port_status_t;

### 端口统计相关接口

#### 功能简介

该模块接口提供端口统计的相关功能，kyland_port_counters_update接口可以将相关寄存器的端口统计更新到结构体中。kyland_port_counters_clear接口将软件中关于端口计数的结构体清0，以便下次读数能够重新累计。kyland_port_counters_get能够获取端口相关计数，具体计数类型可以查看结构体中的定义。kyland_port_basic_counters_get接口则是查看简单的端口统计，只看该端口的收报和发包个数，不看其他类型的端口统计。

#### 接口及参数

/**

* \brief Update counters for port.

*

* \param inst [IN] Target instance reference.

* \param port_no [IN] Port number.

*

* \return Return code.

**/

kyland_rc kyland_port_counters_update(const kyland_inst_t inst,

const kyland_port_no_t port_no);

/**

* \brief Clear counters for port.

*

* \param inst [IN] Target instance reference.

* \param port_no [IN] Port/aggregation number.

*

* \return Return code.

**/

kyland_rc kyland_port_counters_clear(const kyland_inst_t inst,

const kyland_port_no_t port_no);

/**

* \brief Get counters for port.

*

* \param inst [IN] Target instance reference.

* \param port_no [IN] Port/aggregation number.

* \param counters [OUT] Counter structure.

*

* \return Return code.

**/

kyland_rc kyland_port_counters_get(const kyland_inst_t inst,

const kyland_port_no_t port_no,

kyland_port_counters_t *const counters);

/**

* \brief Get basic counters for port.

*

* \param inst [IN] Target instance reference.

* \param port_no [IN] Port/aggregation number.

* \param counters [OUT] Counter structure.

*

* \return Return code.

**/

kyland_rc kyland_port_basic_counters_get(const kyland_inst_t inst,

const kyland_port_no_t port_no,

kyland_basic_counters_t *const counters);

#### 相关数据结构

/** \brief Port counter structure */

typedef struct

{

kyland_port_rmon_counters_t  rmon; 	/**< RMON counters */

kyland_port_if_group_counters_t  if_group; 	/**< Interfaces Group counters */

kyland_port_ethernet_like_counters_t  ethernet_like; 	/**< Ethernet-like Interface counters */

kyland_port_bridge_counters_t  bridge; 	/**< Bridge counters */

kyland_port_proprietary_counters_t  prop; 	/**< Proprietary counters */

} kyland_port_counters_t;

/** \brief Basic counters structure */

typedef struct

{

u32  rx_frames; 	/**< Rx frames */

u32  tx_frames; 	/**< Tx frames */

} kyland_basic_counters_t;

### 端口Enable/Disable

#### 功能简介

配置端口使能

#### 接口及参数描述

/**

* \brief Set port enable/disable.

*

* \param inst [IN]     Target instance reference.

* \param port_no [IN]  Port number.

*

* \return Return code.

**/

kyland_rc kyland_port_enable(const kyland_inst_t       inst,

const kyland_port_no_t    port_no);

kyland_rc kyland_port_disable(const kyland_inst_t       inst,

const kyland_port_no_t    port_no);

#### 相关数据结构

### 端口Speed配置

#### 功能简介

配置端口速率，仅GE端口需要配置，可配置为10M、100M、1000M。

#### 接口及参数描述

/**

* \brief Set port speed.

*

* \param inst [IN]     Target instance reference.

* \param port_no [IN]  Port number.

* \param speed [IN]    Port speed.

*

* \return Return code.

**/

kyland_rc kyland_port_speed_set(const kyland_inst_t       inst,

const kyland_port_no_t    port_no,

const kyland_port_speed_t  speed);

#### 相关数据结构

/** \brief Port speed */

typedef enum

{

KYLAND_SPEED_UNDEFINED,   /**< Undefined */

KYLAND_SPEED_10M,         /**< 10 M */

KYLAND_SPEED_100M,        /**< 100 M */

KYLAND_SPEED_1G,          /**< 1 G */

KYLAND_SPEED_2500M,       /**< 2.5G */

KYLAND_SPEED_5G,          /**< 5G or 2x2.5G */

KYLAND_SPEED_10G,         /**< 10 G */

KYLAND_SPEED_12G          /**< 12G */

} kyland_port_speed_t;

### 端口双工模式配置

#### 功能简介

配置端口为全双工或半双工。

#### 接口及参数

/**

* \brief Set port fdx.

*

* \param inst [IN]     Target instance reference.

* \param port_no [IN]  Port number.

* \param fdx [IN]      Port Full duplexc/Half Duplex.

* \param exc_col_cont [IN]      Excessive collision continuation.

*

* \return Return code.

**/

kyland_rc kyland_port_fdx_set(const kyland_inst_t       inst,

const kyland_port_no_t    port_no,

const ucBool fdx,

const ucBool exc_col_cont);

#### 相关数据结构

### 端口流控模式配置

#### 功能简介

配置端口流控模式

#### 接口及参数

/**

* \brief Set port configuration.

*

* \param inst [IN]     Target instance reference.

* \param port_no [IN]  Port number.

* \param obey [IN]     TRUE if 802.3x PAUSE frames should be obeyed.

* \param generate [IN]     TRUE if 802.3x PAUSE frames should generated.

*

* \return Return code.

**/

kyland_rc kyland_port_flow_control_set(const kyland_inst_t       inst,

const kyland_port_no_t    port_no,

const ucBool       obey,

const ucBool       generate);

#### 相关数据结构

### 端口frame配置

#### 功能简介

配置端口支持报文最大长度

#### 接口及参数

/**

* \brief Set port frame.

*

* \param inst [IN]     Target instance reference.

* \param port_no [IN]  Port number.

* \param max_frame_length [IN]    Maximum frame length.

* \param frame_length_chk [IN]    Enforce 802.3 frame length check (from ethertype field).

* \param max_tags [IN]		VLAN awareness for length check.

*

* \return Return code.

**/

kyland_rc kyland_port_frame_set(const kyland_inst_t     inst,

const kyland_port_no_t  port_no,

u32 max_frame_length,

ucBool frame_length_chk,

kyland_port_max_tags_t max_tags);

#### 相关数据结构

### LED基础配置接口

#### 功能简介

KD6630的LED基础配置接口,包括闪烁模式配置,输出翻转配置,时钟频率配置等.

#### 接口及参数

//led配置接口

kyland_rc kyland_led_cfg(const kyland_inst_t inst,

kyland_led_blink_mode_t mode,   //闪烁模式

ucBool inversed,	//输出翻转

kyland_led_clk_freq_t frequency);//时钟频率

//获取当前led配置的接口

kyland_rc kyland_led_get(const kyland_inst_t inst,

kyland_led_blink_mode_t *mode, //闪烁模式

ucBool *inversed,		//输出翻转

kyland_led_clk_freq_t *frequency); //时钟频率

//端口link状态相关的led配置接口

kyland_rc kyland_led_port_cfg(const kyland_inst_t inst,

kyland_port_no_t port, 	//端口号

ucBool link);	//link状态

/led 闪烁模式mode0配置的接口

kyland_rc kyland_led_mode0_cfg(const kyland_inst_t inst, 			  			kyland_led_blink_mode0_t mode); //mode0闪烁模式

//获取当前led 闪烁模式mode0配置的接口

kyland_rc kyland_led_mode0_get(const kyland_inst_t inst,

kyland_led_blink_mode0_t *mode); //mode0闪烁模式

//led 闪烁模式mode1配置的接口

kyland_rc kyland_led_mode1_cfg(const kyland_inst_t inst,

kyland_led_blink_mode1_t mode); //mode1闪烁模式

//获取当前led 闪烁模式mode1配置的接口

kyland_rc kyland_led_mode1_get(const kyland_inst_t inst,

kyland_led_blink_mode1_t *mode); //mode1闪烁模式

//led 分频值配置的接口

kyland_rc kyland_led_clk_frequency_cfg(const kyland_inst_t inst,

u32 frequency);// led分频值

//获取当前led 分频值配置的接口

kyland_rc kyland_led_clk_frequency_get(const kyland_inst_t inst,

u32 *frequency); // led分频值

#### 相关数据结构

//闪烁模式相关数据结构

typedef enum{

KYLAND_LED_BLINK_MODE_5HZ,

KYLAND_LED_BLINK_MODE_2_5HZ,

KYLAND_LED_BLINK_MODE_1_25HZ,

KYLAND_LED_BLINK_MODE_0_625HZ,

KYLAND_LED_BLINK_MODE_BURST_TOGGLE

}kyland_led_blink_mode_t;

typedef enum{

KYLAND_LED_BLINK_MODE1_5HZ=0,

KYLAND_LED_BLINK_MODE1_2_5HZ=1,

KYLAND_LED_BLINK_MODE1_1_25HZ=2,

KYLAND_LED_BLINK_MODE1_BURST_TOGGLE=3

}kyland_led_blink_mode1_t;

typedef enum{

KYLAND_LED_BLINK_MODE0_5HZ=0,

KYLAND_LED_BLINK_MODE0_2_5HZ=1,

KYLAND_LED_BLINK_MODE0_1_25HZ=2,

KYLAND_LED_BLINK_MODE0_0_625HZ=3

}kyland_led_blink_mode0_t;

//时钟频率相关数据结构

typedef enum{

KYLAND_LED_CLK_1M,

KYLAND_LED_CLK_2M,

KYLAND_LED_CLK_3M,

KYLAND_LED_CLK_4M,

KYLAND_LED_CLK_5M

}kyland_led_clk_freq_t;

### LED端口UP/DOWN配置接口

#### 功能简介

SDK内部默认会初始化LED的功能,默认使用gpio 0做为link, gpio 1做为active. 当端口UP/DOWN发生变化时使用如下接口进行link灯的控制.

#### 接口及参数

//端口link状态相关的led配置接口

kyland_rc kyland_led_port_cfg(const kyland_inst_t inst,

kyland_port_no_t port, 	//端口号

ucBool link);	//link状态

#### 相关数据结构

无

### LED数据间隙配置接口

#### 功能简介

修改LED灯流之间的数据间隙或者获取当前LED灯流之间的数据间隙,不同芯片类型的间隙不一致.具体请查看kyland_port_api.h.

#### 接口及参数

kyland_rc kyland_led_data_gap_set(const kyland_inst_t inst,

u8 gap); //间隙大小配置

kyland_rc kyland_led_data_gap_get(const kyland_inst_t inst,

u8 *gap); //间隙大小配置

#### 相关数据结构

无

### LEDgpio位宽配置接口

#### 功能简介

修改LED灯流输出的每个端口下的gpio位宽,默认配置输出两个bit,可通过如下接口进行配置/获取当前输出的gpio位宽.

#### 接口及参数

kyland_rc kyland_led_port_gpio_cfg(const kyland_inst_t inst,

kyland_led_port_gpio_width_t width)//输出位宽

kyland_rc kyland_led_port_gpio_get(const kyland_inst_t inst,

kyland_led_port_gpio_width_t *width) //输出位宽

#### 相关数据结构

typedef enum{

KYLAND_LED_PORT_GPIO_WIDTH_1,		/**< Number of gpios per port*/

KYLAND_LED_PORT_GPIO_WIDTH_2,

KYLAND_LED_PORT_GPIO_WIDTH_3,

KYLAND_LED_PORT_GPIO_WIDTH_4,

KYLAND_LED_PORT_GPIO_WIDTH_MAX

}kyland_led_port_gpio_width_t;

### LED 指定端口的gpio配置接口

#### 功能简介

如果不使用默认配置,需要用户自行配置每个端口的每个gpio模式.使用如下接口可以配置/获取当前端口的模式.

#### 接口及参数

kyland_rc kyland_led_gpio_cfg(const kyland_inst_t inst,

kyland_port_no_t port, 	//端口号

kyland_led_gpio_cfg_t *cfg) //gpio的配置

kyland_rc kyland_led_gpio_get(const kyland_inst_t inst,

kyland_port_no_t port, //端口号

kyland_led_gpio_cfg_t *cfg) //gpio的配置

#### 相关数据结构

typedef enum{

KYLAND_LED_MODE_FORCED_0,

KYLAND_LED_MODE_FORCED_1,

KYLAND_LED_MODE_BLINK_MODE_0,

KYLAND_LED_MODE_BLINK_MODE_1,

KYLAND_LED_MODE_LINK_ACTIVITY_BLINK_MODE_0,

KYLAND_LED_MODE_LINK_ACTIVITY_BLINK_MODE_1,

KYLAND_LED_MODE_LINK_ACTIVITY_BLINK_MODE_0_INVERSED,

KYLAND_LED_MODE_LINK_ACTIVITY_BLINK_MODE_1_INVERSED,

KYLAND_LED_MODE_MAX

}kyland_led_gpio_mode_t;

typedef struct{

u8 flag;

kyland_led_gpio_mode_t gpio[4];		/**< Mode per gpio.*/

}kyland_led_gpio_cfg_t;

### 自协商相关配置接口

#### 功能简介

自协商配置相关API接口.

#### 接口及参数

kyland_rc kyland_port_auto_negotiate_set(const kyland_inst_t inst,

kyland_port_no_t port,

ucBool aneg);

kyland_rc kyland_port_auto_negotiate_get(const kyland_inst_t inst,

kyland_port_no_t port,

ucBool *aneg);

#### 相关数据结构

ucBool aneg; // auto negotiate

## 应用示例

### 36*1000BASE-X + 4*SFI

配置端口模式为C3模式，Port_0~Port_35的接口类型为1000BASE-X，配置Port_52~Port_55的接口类型为SFI。

int kyland_sdk_config_36x1000baseX_4xSFI()

{

int unit = 0,port,phy_addr;

char * name;

char  strval[8];

char bus_id;

kd_hal_sdk_config_set(unit, spn_KD5886_SWITCH_MODE, "c3");

kd_hal_sdk_config_set(unit, spn_PBMP_VLD, "0xFFF0000FFFFFFFFF");

for(port = 0; port < 64;port ++){

if(port < 36){

kd_hal_sdk_port_config_set(0, port,spn_PORT_INTERFACE,"1000basex");

}else if(port > 51 && port < 56){

kd_hal_sdk_port_config_set(0, port,spn_PORT_INTERFACE,"sfi");

}

}

return 0;

}

### 端口使能流控

Port_1使能流控

u32 port = 1;

ucBool enable = 1;

u8 smac[6];

smac[0] = 0;

smac[1] = 0;

smac[2] = 0;

smac[3] = 0;

smac[4] = 0;

smac[5] = 0x01;

kyland_port_flow_control_set(NULL, port, enable, enable, smac[6]);

### 端口设置自协商

Port1设置为自协商

u32 port = 1;

ucBool aneg = 1;

kyland_rc kyland_port_auto_negotiate_set(NULL, port, aneg);
