# kyland_sdk_2.0.0 MISC应用开发指南

kyland_sdk_2.0.0

MISC应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 SIO模块	5

1.1 1.1SIO Pins	5

1.2 1.2Access Timing	5

1.3 Loss of Signal Detection	7

2 SIO相关接口介绍	8

2.1 SIO功能配置接口	8

2.1.1 功能简介	8

2.1.2 接口及参数描述	8

2.1.3 相关数据结构	12

2.2 SIO 数据接收接口	16

2.2.1 功能简介	16

2.2.2 接口及参数描述	16

2.2.3 相关数据结构	16

2.3 SIO 中断接口	17

2.3.1 功能简介	17

2.3.2 接口及参数描述	17

2.3.3 相关数据结构	19

3 GPIO模块	21

3.1 概述	21

4 GPIO相关接口介绍	22

4.1 GPIO初始化接口介绍	22

4.1.1 功能简介	22

4.1.2 接口及参数描述	22

4.1.3 相关数据结构	23

4.2 GPIO方向接口介绍	23

4.2.1 功能简介	23

4.2.2 接口及参数描述	23

4.2.3 相关数据结构	24

4.3 GPIO数据接口介绍	24

4.3.1 功能简介	24

4.3.2 接口及参数描述	24

4.3.3 相关数据结构	26

# SIO模块

SIO主要用于连接SFP模块，同时也可以用于控制LED。

每个port有4组SGPIO，共计4 * port个GPIO

可用于和SFP模块通信，也可用于控制LED显示MAC工作状态

控制LED显示只需使用两个输出pin

## 1.1SIO Pins

表 1 SIO Pins

| Pin Name | Direction | Description |
| --- | --- | --- |
| SIO_CLK | O | SIO clock output, frequency is configurable |
| SIO_DO | O | SIO data output. |
| SIO_DI | I | SIO data input. |
| SIO_Latch | O | SIO load data, polarity is configurable |

## 1.2Access Timing

图 1 SIO时序

每个port下最多4组GPIO，可以配置某些端口使能/不使能，不使能的port/channel对应时隙clk不使能。可以配置4*port个GPIO通道各自是否产生中断及产生中断的条件，当用作LED控制器时，只有输出，没有输入信号。

4*port个channel数据输出之后 ，控制SIO_Latch信号变化，例如上图下降沿时确认数据发送完成一轮次，上升沿时用来确认数据接收完成一轮次。

对应SIO_DO，先接低输出时钟，再接高输出时钟，下降沿数据发送完成一bit，当发送完成使能的所有port所对应的gpio数据后，控制SIO_Latch信号，如上图所示，下降沿时确认数据发送完成一轮次，SIO进入burst_gap状态，等待下一次数据发送。

对应SIO_DI，SIO模块的对端模块需要先将要发送的第一笔数据放在SIO_DI线上，等待SIO_CLK的上升沿到来，然后将第二笔数据放在SIO_DI线上，即输出时钟SIO_CLK拉高时，上升沿确认接收完成一bit，如上图所示。当接受完成使能的所有port所对应的gpio数据后，所有接收数据被存入寄存器，仅仅只需关心INPUT_DATA对应port和gpio使能的数据。然后控制SIO_Latch信号，如上图所示，上升沿时确认数据接收完成一轮次，SIO进入burst_gap状态，等待下一次数据接收，此时SIO的对端模块在检测到SIO_Latch的上升沿后，就需要将要发送的下一组数据的第一笔数据放在SIO_DI线上了，循环以上接收操作。

Burst_gap可配置。

输出的数据有三种数据类型：

静态的0/1

Blink:按一定的频率生成闪烁的效果，频率可以配置2种模式：

最高频率对应5Hz，即一秒钟闪烁5次。

图 2 SIO Blink mode1 5Hz模式波形图

图 3 SIO Blink mode1 Burst toggle模式波形图

Link activity：当channel有rx/tx动作时闪烁

例如下图用5Hz的闪烁举例，统计每100ms内的channel动作，如有动作，在下一个100ms内使能输出。

图 4 SIO Link activity

## Loss of Signal Detection

使用SFP时，如果每个port/channel和SFP的对应，则输入信号可用于检测外部模块的变化，从而产生中断，通知CPU进行配置。

各Port输入的第[0]组信号与int_pol配置及port_ena组合输出loss of signal信号。

# SIO相关接口介绍

SIO功能默认是不使能状态,如果用户需要使用SIO功能,需要对SIO模块进行配置,使其可以正常工作.

## SIO功能配置接口

### 功能简介

通过该接口可实现对SIO的初始化功能配置,例如时钟分频值,端口使能,循环输出,输出间隙大小等功能的配置.亦可通过读取接口获取芯片内的配置信息.

### 接口及参数描述

kyland_rc kyland_misc_sio_cfg(const kyland_inst_t inst,kyland_sio_cfg_t *cfg);

参数:

const kyland_inst_t inst  //芯片实例

kyland_sio_cfg_t *cfg	//需要配置的SIO功能参数

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_misc_sio_get(const kyland_inst_t inst,kyland_sio_cfg_t *cfg);

参数:

const kyland_inst_t inst  //芯片实例

kyland_sio_cfg_t *cfg	//从芯片中读取到的SIO功能参数配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_burst_gap_cfg(const kyland_inst_t inst,u8 burst_gap);

参数:

const kyland_inst_t inst  //芯片实例

u8 burst_gap	//两次输出之间的间隙大小寄存器值,实际值需要根据时钟频率计算一下

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_burst_gap_get(const kyland_inst_t inst,u8 *burst_gap);

参数:

const kyland_inst_t inst  //芯片实例

u8 *burst_gap	//从芯片中获取到的两次输出之间的间隙大小寄存器值

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_port_gpio_width_cfg(const kyland_inst_t inst,kyland_sio_port_gpio_width_t width);

参数:

const kyland_inst_t inst  //芯片实例

kyland_sio_port_gpio_width_t width	//每个port对应的gpio数量,最大为4

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_port_gpio_width_get(const kyland_inst_t inst,kyland_sio_port_gpio_width_t *width);

参数:

const kyland_inst_t inst  //芯片实例

kyland_sio_port_gpio_width_t  *width  //获取到的芯片汇中每个port对应的gpio数量

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_auto_repeat_cfg(const kyland_inst_t inst,ucBool auto_repeat);

参数:

const kyland_inst_t inst  //芯片实例

ucBool auto_repeat  //循环输出的功能配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_auto_repeat_get(const kyland_inst_t inst,ucBool *auto_repeat);

参数:

const kyland_inst_t inst  //芯片实例

ucBool *auto_repeat  //芯片中获取到的循环输出的功能配置

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_one_time_cfg(const kyland_inst_t inst,ucBool one_time);

参数:

const kyland_inst_t inst  //芯片实例

ucBool one_time  //sio单次输出功能

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_misc_api.h文件

typedef struct{

u16 clk_frequency;                       /**< SIO Clock frequency - divides system clock with register value.

0 : disables tic generation

1 : illegal value

others : clock divide value*/

u32 port_ena_high;                       /**< Use the bitmap to enable some ports from port number[32,63] */

u32 port_ena_low;                        /**< Use the bitmap to enable some ports from port number[0,31] , bit0 :port 0 */

ucBool auto_repeat;                      /**< Use this to output repeated bursts interleaved with burst gaps.*/

kyland_sio_blink_mode_0_t bmode_0;

kyland_sio_blink_mode_1_t bmode_1;

kyland_sio_port_gpio_width_t width;      /**<Number of gpios pr. port.*/

u8 burst_gap;                            /**< Length of burst gap.

For a system clock of 560MHz this results in the following burst gaps:

0.262144 * T_sysclk * sio_burst_gap (ms)

burst_gap = 00000 => 0.468 ms burst gap.

burst_gap = 00001 => 0.936 ms burst gap.

burst_gap = 11111 => 14.980 ms burst gap.*/

ucBool ld_polarity;                     /**< Polarity of the "Ld" signal  0 : load signal is active low  1 : load signal is active high*/

ucBool output_reverse;                  /**< Reverse the output bitstream.*/

ucBool input_reverse;                   /**< Reverse the input bitstream.*/

u32 int_pol_low[4];

u32 int_pol_high[4];                    /**< Interrupt polarity. Bit n from all ports.

This register defines at which logic value an interrupt is generated.

0 : interrupt at logic value '1'

1 : interrupt at logic value '0'*/

}kyland_sio_cfg_t;

------------------------------------------------------------------------------------------------------------------------------------------

typedef enum{

KYLAND_BMODE_0_5HZ,

KYLAND_BMODE_0_2_5HZ,

KYLAND_BMODE_0_1_25HZ,

KYLAND_BMODE_0_0_625HZ,

KYLAND_BMODE_0_MAX

}kyland_sio_blink_mode_0_t;

------------------------------------------------------------------------------------------------------------------------------------------

typedef enum{

KYLAND_BMODE_1_5HZ,

KYLAND_BMODE_1_2_5HZ,

KYLAND_BMODE_1_1_25HZ,

KYLAND_BMODE_1_BURST_TOGGLE,

KYLAND_BMODE_1_MAX

}kyland_sio_blink_mode_1_t;

------------------------------------------------------------------------------------------------------------------------------------------

typedef enum{

KYLAND_SIO_PORT_GPIO_WIDTH_1,		/**< Number of gpios per port*/

KYLAND_SIO_PORT_GPIO_WIDTH_2,

KYLAND_SIO_PORT_GPIO_WIDTH_3,

KYLAND_SIO_PORT_GPIO_WIDTH_4,

KYLAND_SIO_PORT_GPIO_WIDTH_MAX

}kyland_sio_port_gpio_width_t;

## SIO 数据接收接口

### 功能简介

通过该接口可以获取外部输入的数据,该接口固定为4*port(含内部端口)个bit有效,获取到的数据需要根据实际情况使用某些bit,其他bit不需要关心.

### 接口及参数描述

kyland_rc kyland_sio_input_data_get(const kyland_inst_t inst,kyland_sio_input_data_t *data);

参数:

const kyland_inst_t inst  //芯片实例

kyland_sio_input_data_t *data	/外部输入的数据

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_misc_api.h文件

typedef struct{

u8 flag;

u32 data_low[4];

u32 data_high[4];

}kyland_sio_input_data_t;

## SIO 中断接口

### 功能简介

SIO可以实现按bit进行中断触发,共有4*port 个bit,可根据配置实现某端口下1bit或者多个端口下的多个bit.

### 接口及参数描述

kyland_rc kyland_sio_intr_width_cfg(const kyland_inst_t inst,u8 width_bitmap);

参数:

const kyland_inst_t inst  //芯片实例

u8 width_bitmap	//以bitmap的方式进行port下的某些bit中断监控,0:不监控任一bit,0xf监控使能端口下的4bit.

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_intr_width_get(const kyland_inst_t inst,u8 *width_bitmap);

参数:

const kyland_inst_t inst  //芯片实例

u8 *width_bitmap	//获取到的芯片内使能了port下那些bit的监控

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_intr_mask_cfg(const kyland_inst_t inst,ucBool mask);

参数:

const kyland_inst_t inst  //芯片实例

ucBool mask	//芯片内sio总中断,mask为1是不关心,mask为0是关心

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_sio_intr_mask_get(const kyland_inst_t inst,ucBool *mask);

参数:

const kyland_inst_t inst  //芯片实例

ucBool *mask	//获取到的芯片内sio总中断状态

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_devcpu_interrupt_notify_request(const kyland_inst_t inst,

const kyland_devcpu_intr_type type,

const unsigned int port_num,

devcpu_intr_notify_function_t cb_func);

参数:

const kyland_inst_t inst  //芯片实例

const kyland_devcpu_intr_type type	//devcpu的中断类型,sio的中断需要选sgio的类型

const unsigned int port_num	//使能那个端口的中断

devcpu_intr_notify_function_t cb_func	//中断回调函数,底层中断会将端口号的和gpio_bitmap放在参数上面传给回调函数,param[0]是端口号,param[1]是gpio的bitmap 1:gpio1, 2:gpio2 4:gpio3 8:gpio4

返回值:

操作码.

### 相关数据结构

此处仅展示部分相关数据结构,具体数据结构请查看kyland_misc_api.h文件

typedef enum{

KYLAND_DEVCPU_SGPIO = 4,

KYLAND_DEVCPU_MIIM,

KYLAND_DEVCPU_MAX

}kyland_devcpu_intr_type;

# GPIO模块

## 概述

KD5886 芯片支持32个GPIO, 软件中体现为32bit.目前可以通过接口配置GPIO的方向,输出值和获取外部输出给本芯片GPIO的值.

# GPIO相关接口介绍

## GPIO初始化接口介绍

### 功能简介

GPIO作为一个设备,芯片内默认不初始化,如果需要使用,需要手动初始化.不使用时可以通过接口去初始化GPIO,去初始化接口同时会将I2C,UART,SPI等设备(当前只提供了GPIO,其他设备后续提供接口)也去初始化,请谨慎使用.

另,可通过show接口来查看设备创建是否出错.

### 接口及参数描述

kyland_rc kyland_misc_gpio_init(const kyland_inst_t inst);

参数:

const kyland_inst_t inst  //芯片实例

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_misc_devmem_uninit(const kyland_inst_t inst);

参数:

const kyland_inst_t inst  //芯片实例

返回值:

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_misc_devmem_show(const kyland_inst_t inst);

参数:

const kyland_inst_t inst  //芯片实例

返回值:

操作码.

### 相关数据结构

无.

## GPIO方向接口介绍

### 功能简介

可以通过接口控制GPIO的方向,当方向设置为输出的时候,由本芯片向外界输出预设的值.方向设置为输入时,可以通过接口获取外界输入的值。

另,本芯片共有32个GPIO,函数参数为32bit的变量,与GPIO一一对应。

### 接口及参数描述

kyland_rc kyland_misc_gpio_direction_cfg(const kyland_inst_t inst,u32 output);

参数:

const kyland_inst_t inst  //芯片实例

u32 output 		//每1bit代表1个GPIO,32个GPIO的方向可以单独控制.

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_misc_gpio_direction_get(const kyland_inst_t inst,u32 *output);

参数:

const kyland_inst_t inst  //芯片实例

u32 *output		//获取到的芯片内配置的GPIO方向信息

返回值:

操作码.

### 相关数据结构

无.

## GPIO数据接口介绍

### 功能简介

可以通过接口控制GPIO的输出的数据或者获取输入的数据。

另,本芯片共有32个GPIO,函数参数为32bit的变量,与GPIO一一对应。

### 接口及参数描述

kyland_rc kyland_misc_gpio_output_value_cfg(const kyland_inst_t inst,u32 value);

参数:

const kyland_inst_t inst  //芯片实例

u32 value 		//每1bit代表1个GPIO,32个GPIO的数据可以单独控制.

返回值:

操作码.

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_misc_gpio_output_value_get(const kyland_inst_t inst,u32 *value);

参数:

const kyland_inst_t inst  //芯片实例

u32 *value		//获取到的芯片内配置的GPIO数据信息

返回值:

------------------------------------------------------------------------------------------------------------------------------------------

kyland_rc kyland_misc_gpio_input_value_get(const kyland_inst_t inst,u32 *value);

参数:

const kyland_inst_t inst  //芯片实例

u32 *value		//获取到的芯片外部输入到本芯片的GPIO数据

返回值:

操作码.

### 相关数据结构

无.
