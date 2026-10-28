# kyland_sdk_2.0.0 进程通讯IPC开发指南

kyland_sdk_2.0.0 进程通讯IPC开发指南

简介:

sdk 提供ipc api 功能,满足用户多进程操作sdk的需求.

软件框架:

采用cs机制,有server,client端.Server一般是由SDK所在的进程创建,client由其它进程创建.消息采用request/reply机制。

IPC数据通讯层: 主要负责消息的底层交互，实现与操作系统有关。用户不需要关心。

IPC api表示层：主要负责api格式的消息类型处理，同时进行一些检查。与系统无关。用户不需要关心。

ipc api实现层：主要负责个各个IPC api的实现，用户根据需求创建api，用户需要关心的地方。

使用介绍：

通过编译sdk，在output 目录下，

libsdk_ipcs.a/libsdk_ipcs.so 为ipc server库，server端需要使用。

libsdk_ipcc.a/libsdk_ipcc.so  为ipc client库，client端需要使用。

代码介绍：

3.1． 目录介绍：

server：主要放server侧相关的代码。

client：主要放client侧相关的代码。

为了方便维护和管理，里面的api相关的文件按照sdk模块进行分类：

kd_ipc_common： common模块中的api。

kd_ipc_kdapi：kd 模块中的api。

kd_ipc_kylandapi：kyland 模块中的api.

3.2． 主要函数接口介绍：

int kd_ipc_server_create(void)：

创建ipc server：返回值：成功返回0，失败返回错误号。

int kd_ipc_server_destry(void)

销毁ipc server：返回值：成功返回0，失败返回错误号。

int kd_ipc_client_create(int *cid);

创建ipc client，cid 为服务id。返回值：成功返回0，失败返回错误号。

int kd_ipc_client_create2(void);

创建ipc client，同一进程只能创建一个。返回值：成功返回0，失败返回错误号。

int kd_ipc_client_destry(int cid);

销毁ipc client。返回值：成功返回0，失败返回错误号。

int kd_ipc_client_destry2(void);

销毁ipc client。返回值：成功返回0，失败返回错误号。

int kd_ipc_client_send(int cid,kd_api_ipc_inmsg_t *in,kd_api_ipc_outmsg_t *out);

client 发送消息，cid为服务id，in为请求消息，out为replay消息。返回值：成功返回0，失败返回错误号。

int kd_ipc_client_send2(kd_api_ipc_inmsg_t *in,kd_api_ipc_outmsg_t *out);

client 发送消息， in为请求消息，out为replay消息。返回值：成功返回0，失败返回错误号。

ipc api 添加方法：

ipc api 需要添加server端和client端。

如添加int kd_cli_node_execute(kd_cli_inst_t inst,int node,char *cmd,kd_cmd_node_conf_t *conf,int outbuflen,void *outbuf,int *outlen)  api为例：

4.1．数据结构设计：

设计合理的入参和出参结构（注：不一定要用结构体，只要client和server 数据能互相识别就行），该结构体为内部私有，不对外开放。

结构体的命名规则：函数名_s

4.2．server 代码：

对kd_cli_node_execute 函数进行封装。

函数命名格式为：函数名_server

必要的头文件：

函数key添加 ：

命名格式：函数名_k

封装函数注册：

将函数注册到ipc_handle_table 处理中。

4.3．client代码：

client 函数命名及参数要求与原始api完全一样，让用户调用改函数和调用原始函数一样。

必要的头文件：

4.4．client测试代码：

void web_send(void)

{

char obuf[100];

int outlen = 0;

int cid = 0;

int rv = 0;

char *cmd;

kd_common_init();

kd_ipc_client_create(&cid);

cmd = "show status";

rv = kd_cli_node_execute(2, 0,cmd, NULL, 100, obuf, &outlen);

printf("rv=%d,len=%d: %s\n",rv,outlen,obuf);

}

makefile:

all:

gcc c.c -o c  -I/home/zyh/work/kyland_sdk_2.0.0/ipc/include   -I/home/zyh/work/kyland_sdk_2.0.0/appl/include -I./ -I/home/zyh/work/kyland_sdk_2.0.0/kd/include  -DLINUX -Dlinux -D_SAL_LINUX_UM   -I/home/zyh/work/kyland_sdk_2.0.0/common/include -I/home/zyh/work/kyland_sdk_2.0.0/common/include/sal -I/home/zyh/work/kyland_sdk_2.0.0/common/include/lib -L/home/zyh/work/kyland_sdk_2.0.0/output/linux/kd5886/x86/libipc  -lsdk_ipcc  -lpthread –lm

ipc api 介绍：

int kd_cli_node_execute(kd_cli_inst_t inst,int node,char *cmd,kd_cmd_node_conf_t *conf,int outbuflen,void *outbuf,int *outlen)

功能：cli执行函数。

参数：inst：  cli实例。

node：cli 安装node。

cmd： cli 字符串。

conf： cli 行节点属性。如果是interface 模式，通过void kd_cli_port_nodeconf_setup(int unit,int port,kd_cmd_node_conf_t *nconf) 函数进行setup，否则为NULL。

outbuflen：cli 输出buf 大小。

outbuf：cli 输出buf。

outlen： cli输出实际大小。

注：只要cli 通过调用int kd_cli_out_set(kd_cli_inst_t inst,void *buf,int len) 函数才有输出。

返回值：成功返回0，失败返回错误号。

ipc api实现方案：

封装ipc api，即添加对应的client和server的处理。

使用cli机制，将api函数做成cli，client 执行该api对应的cli。
