# kyland_sdk_2.0.0 打印函数开发指南

简介：

本SDK是一套独立开发软件，提供自定义的打印函数，禁止直接使用printf之类的系统函数。选择合理的打印函数，对sdk的调试、维护、专业化有很大的作用。

基本打印函数：

kd_sal_printf：

功能同printf，打印不受控制，SDK中禁止直接使用printf。

kd_cli_out：

kd_cli_out(const char* fmt, ...)

命令行打印函数，只能用在cli文件中。

kd_sal_log：

int kd_sal_log(int log_level, const char* file, int line, const char* fmt,...)

可以按照log level 进行打印，一共有如下几个level。

默认level：

kd_sal_log相关的封装定义：

#define KD_SAL_LOG_FATAL(fmt, args...) \

kd_sal_log(KD_SAL_LL_FATAL, __FILE__, __LINE__, fmt, ##args)

#define KD_SAL_LOG_ERROR(fmt, args...) \

kd_sal_log(KD_SAL_LL_ERROR, __FILE__, __LINE__, fmt, ##args)

#define KD_SAL_LOG_WARN(fmt, args...) \

kd_sal_log(KD_SAL_LL_WARN, __FILE__, __LINE__, fmt, ##args)

#define KD_SAL_LOG_INFO(fmt, args...) \

kd_sal_log(KD_SAL_LL_INFO, __FILE__, __LINE__, fmt, ##args)

#define KD_SAL_LOG_DEBUG(fmt, args...) \

kd_sal_log(KD_SAL_LL_DEBUG, __FILE__, __LINE__, fmt, ##args)

#define KD_SAL_LOG_TRACE(fmt, args...) \

kd_sal_log(KD_SAL_LL_TRACE, __FILE__, __LINE__, fmt, ##args)

支持logbuffer功能，FATAL/ERROR/WARN/INFO 级别会保存到logbuffer。

相关的配置命令：

log [(level (fatal|error|warn|info|debug|trace))]

显示或修改当前level。

kd_debug_print：

支持按照模块、level进行打印。

模块定义：

level 定义：

支持logbuffer功能，FATAL/ERROR/WARN/INFO 级别会保存到logbuffer。

相关命令：

debug-print  xxxx xxxxx

显示或修改当前debug-print配置：

高级打印函数：

建议每个模块单独有自定义的打印函数，通过封装基础打印函数实现：

如kd 层：

如IPC：

如网卡：

logbuffer：

用来记录sdk中重要的打印信息，默认支持1000条记录，每条最大支持1024字节。所以logbuffer资源有限，只保存重要的信息。如一些错误、状态变化等。

kd_sal_log 与kd_debug_print 支持logbuffer功能。

相关命令：

show log-buffer

log-buffer clear

打印函数选择：

在调试阶段可以先用printf，在代码整理时再替换成合适的打印函数。

在cli中使用kd_cli_out

错误检查中如果是error等重要打印，建议使用kd_sal_log 的封装函数

调试级的打印建议使用kd_debug_print。

kd_sal_printf 尽量少使用，一般没有合适的打印函数时使用。

建议每个模块都有独立的封装过的打印函数。
