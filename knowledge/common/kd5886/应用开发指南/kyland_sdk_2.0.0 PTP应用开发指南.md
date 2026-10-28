# kyland_sdk_2.0.0 PTP应用开发指南

kyland_sdk_2.0.0

PTP应用开发指南

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 特性简介	4

2 API介绍	5

2.1 秒计数管理	5

2.2 纳秒计数管理	5

2.3 外部输出和输入控制	5

2.4 事件管理	6

2.5 端口时间戳获取	6

2.6 请求一次性中断	6

3 应用举例	8

# 特性简介

硬件时间戳功能在报文到达和离开时记录了精确的秒计数和纳秒计数，可以用来做精确的时间同步和时钟分发。相比纯软件实现的时间同步，硬件时间戳的精度要高的多。

接收报文在MAC模块被打上时间戳，在ACL模块根据ACL Action决定是否保留时间戳并且将报文重定向或者复制到CPU，ACL Action同时也指明了是否在发送报文时保留时间戳以及保留时间戳到三组寄存器中的哪一组。对于不需要上送CPU的报文，在PES模块会剥离时间戳信息。在报文离开设备时，在MAC模块会根据ACL Action的指示将发送时间戳保存在指定的寄存器中。

# API介绍

硬件时间戳相关的API都在kyland_ts_api.h中，文件中有数据结构和API的详细介绍。kyland_acl_api.h中有ACL相关的配置接口，我们关注的是kyland_acl_action_cfg_t中的cpu、cpu_queue、rx_timestamp_ena、tx_timestamp、redir_cmd、redir_id字段。

## 秒计数管理

| kyland_ts_init_second_value_set | 设置初始的秒计数 |
| --- | --- |
| kyland_ts_init_second_value_get | 获取初始的秒计数 |
| kyland_ts_current_second_value_get | 获取当前的秒计数 |
| kyland_ts_second_value_adjust_set | 设置秒计数调节 |
| kyland_ts_second_value_adjust_get | 获取秒计数调节 |

初始秒计数通常只设置一次，在时间同步过程中，使用者需要使用adjust接口达到秒计数同步的目的。

## 纳秒计数管理

| kyland_ts_current_nanosecond_value_get | 获取当前的纳秒计数 |
| --- | --- |
| kyland_ts_nanosecond_value_adjust_set | 设置纳秒计数调节 |
| kyland_ts_nanosecond_value_adjust_get | 获取纳秒计数调节 |
| kyland_ts_one_time_adjust | 设置一次性的调节 |

纳秒计数不需要设置初始值，纳秒计数一直在每1纳秒加1，当计数值达到HW_CLK_CNT_PR_SEC后，秒计数加1。芯片支持一次性调节秒计数和纳秒计数，此时需要kyland_ts_current_nanosecond_value_get获取当前的clock计数，然后计算出kyland_ts_one_time_adjust需要的入参clk_cnt_limit。

## 外部输出和输入控制

| kyland_ts_generate_ext_clk_set | 外部时钟输出使能及频率控制 |
| --- | --- |
| kyland_ts_generate_ext_clk_get | 获取当前的时钟输出控制参数 |
| kyland_ts_ext_syn_pulse_set | 设置使用外部输入同步或者输出同步到外部 |
| kyland_ts_ext_syn_pulse_get | 获取外部输出和输入参数 |
| kyland_ts_captured_nanosecond_value_get | 输入同步使能时，获取同步信息到达时本地时钟的纳秒计数 |

芯片支持输出时钟到外部，注意设置时频率不能随意指定。

芯片也支持使用外部的同步输入，当外部同步到达时，可以将本地时钟的纳秒计数存储在寄存器中，然后可以根据与外部时钟的差距调整纳秒计数。

芯片同样支持输出同步信号到外部。

## 事件管理

| kyland_ts_event_status_get | 获取时间戳相关的事件状态 |
| --- | --- |
| kyland_ts_event_status_clear | 清除时间戳相关的事件状态 |
| kyland_ts_port_state_get | 获取端口发送时间戳状态 |
| kyland_ts_port_state_clear | 清除端口发送时间戳状态 |

使用者可以通过轮询的方式获取某些事件是否已发生，其中部分事件会触发中断（见2.6）。端口在发送时间戳记录完成后会有相应的状态指示，使用者在获取到发送时间戳后要及时清除状态标记，否则时间戳信息不会再次更新。

## 端口时间戳获取

| kyland_ts_tx_timestamp_get | 获取某个端口的发送时间戳 |
| --- | --- |

可以通过轮询的方式感知到端口发送时间戳已被记录，然后使用此接口获取时间戳数值。

可以通过中断的方式等待某个端口的时间戳被记录后调用ISR，在ISR中得到端口号信息，然后通过kyland_ts_port_state_get和kyland_ts_tx_timestamp_get获取时间戳数值。

## 请求一次性中断

| kyland_ts_interrupt_notify_request | 请求一次性中断 |
| --- | --- |

使用者可以同时请求多种类型的中断，每种类型的中断对应的ISR都由使用者指定，中断事件发生后，相应的ISR会得到调用，然后这个中断就会被关掉，如果使用者还想继续处理这种类型的中断，需要使用者再次调用这个API。

# 应用举例

如上图: slave 设备要和 master 设备进行时钟同步。

master 设备上面的时钟需要根据高级时钟源的时钟值,配置master设备的初始秒计数值(kyland_ts_init_second_value_set)。

通过使用外部输入同步(kyland_ts_ext_syn_pulse_set),然后获取到外部输入的参数(kyland_ts_ext_syn_pulse_get)。

外部输入同步使能的时候,master接收到外部同步信号时,获取本地的纳秒计数值(kyland_ts_captured_nanosecond_value_get)。

根据本地的纳秒计数与外部输入的差距进行纳秒调节,完成master的时钟与高级时钟源同步(kyland_ts_nanosecond_value_adjust_set)。

Master设备产生ptp协议报文(sync 和follow_up)周期性的发送给slave设备。

中间设备需要配置acl识别ptp协议报文,copy sync 报文给cpu,redirec  follow_up报文给cpu,cpu计算sync报文的驻留时间,将sync报文的驻留时间更新进follow_up报文中并发送出去。

Slave设备接收到ptp协议报文后根据报文内容进行本地时钟调节。完成与master 设备的时钟同步。
