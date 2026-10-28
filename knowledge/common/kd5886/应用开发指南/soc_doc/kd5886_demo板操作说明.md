# kd5886_demo板操作说明

kd5886_demo板操作说明

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

# 环境介绍

## 默认串口配置

# KD5886 内部CPU

## 分区介绍

Spi flash：目前只放uboot。

Emmc flash：大小4GB，512B/setctor, 目前放uimage 和rootfs。分区如下：

Uimage 分区无格式化：

Mmcblk0pX: ext4 类型。

## 相关升级镜像介绍

u-boot.img:  uboot,目前放在spiflash中，可以通过cpu内部rom程序通过串口进行升级。

kd5886_evb_gmii.dtb：dtb文件， image启动需要的dtb文件。注: kd5886_evb_rgmii.dtb 文件会导致kernel nfs挂载失败启不来.

rootfs.ext4：rootfs ext4格式镜像，放在emmc的rootfs分区，起始地址必须放在0x20000 sector的位置。

uImage：kernel程序，放在emc 的image分区，起始地址放在0x2000 sector 的位置。

uImage_ramfs：带ramdisk rootfs的kernel镜像文件，如果emmc 存放的rootfs系统异常，可以使用uImage_ramfs临时启动，然后进行emmc分区和格式化操作。

## CPU启动简介

该CPU支持内部ROM启动模式和外部boot启动模式，可以通过硬件配置。

ROM启动模式一般是在没有外部boot时使用，可以通过菜单命令升级外部boot。

外部boot目前只支持uboot，升级/加载uimage。

## 内部ROM启动

通过硬件配置ROM启动模式，串口打印如下：

选择菜单1，同ymodem升级uboot,等待升级完成：

## uboot启动

硬件修改外部启动模式，上电启动uboot。

### uboot默认env

baudrate=115200

bootargs=clk_ignore_unused loglevel=7 console=ttyS0,115200 init=/sbin/init root=/dev/nfs rw nfsroot=192.168.40.40:/usr/nfsRoot/fs2,v3,tcp,nolock ip=192.168.50.219:192.168.40.40:192.168.50.1:255.255.255.0

bootcmd=mmc read ${dtb_load_addr_phys} ${dtb_start_sector} ${dtb_size_sectors} ; mmc read ${linux_load_addr_phys} ${linux_start_sector} ${linux_size_sectors} ; bootm ${linux_load_addr_virt}

bootdelay=7

dtb_load_addr_phys=0x0f000000

dtb_load_addr_virt=0x8f000000

dtb_size_sectors=a

dtb_start_sector=0x1000

ethact=dwmac.fffc0000

ethaddr=00:00:23:34:45:70

etx4_load_addr_phys=0x0

etx4_load_addr_virt=0x80000000

ext4_size_sectors=40001

ext4_start_sector=0x20000

fileaddr=80000000

filesize=8000000

fw_sz=40001

ipaddr=192.168.0.25

linux_load_addr_phys=0x10000000

linux_load_addr_virt=0x90000000

linux_size_sectors=15af

linux_start_sector=0x2000

netmask=255.255.255.0

serverip=192.168.0.20

stderr=serial

stdin=serial

stdout=serial

update_dtb=tftpboot ${dtb_load_addr_virt} kd5886_evb_gmii.dtb ; setexpr fw_sz ${filesize} / 0x200 ; setexpr fw_sz ${fw_sz} + 1 ; mmc write ${dtb_load_addr_phys} ${dtb_start_sector} ${fw_sz} ; setenv dtb_size_sectors ${fw_sz} ; saveenv ;

update_etx4=tftpboot ${etx4_load_addr_virt} rootfs.ext4 ; setexpr fw_sz ${filesize} / 0x200 ; setexpr fw_sz ${fw_sz} + 1 ; mmc write ${etx4_load_addr_phys} ${ext4_start_sector} ${fw_sz} ; setenv ext4_size_sectors ${fw_sz} ; saveenv ;

update_linux=tftpboot ${linux_load_addr_virt} uImage ; setexpr fw_sz ${filesize} / 0x200 ; setexpr fw_sz ${fw_sz} + 1 ; mmc write ${linux_load_addr_phys} ${linux_start_sector} ${fw_sz} ; setenv linux_size_sectors ${fw_sz} ; saveenv ;

### 配置默认uboot env脚本

setenv baudrate 115200

setenv bootargs 'clk_ignore_unused loglevel=7 console=ttyS0,115200 init=/sbin/init root=/dev/nfs rw nfsroot=192.168.40.40:/usr/nfsRoot/fs2,v3,tcp,nolock ip=192.168.50.219:192.168.40.40:192.168.50.1:255.255.255.0'

setenv bootcmd 'mmc read ${dtb_load_addr_phys} ${dtb_start_sector} ${dtb_size_sectors} ; mmc read ${linux_load_addr_phys} ${linux_start_sector} ${linux_size_sectors} ; bootm ${linux_load_addr_virt}'

setenv bootdelay 7

setenv dtb_load_addr_phys 0x0f000000

setenv dtb_load_addr_virt 0x8f000000

setenv dtb_size_sectors a

setenv dtb_start_sector 0x1000

setenv ethact dwmac.fffc0000

setenv ethaddr 00:00:23:34:45:70

setenv etx4_load_addr_phys 0x0

setenv etx4_load_addr_virt 0x80000000

setenv ext4_size_sectors 40001

setenv ext4_start_sector 0x20000

setenv fileaddr 80000000

setenv filesize 8000000

setenv fw_sz 40001

setenv ipaddr 192.168.0.25

setenv linux_load_addr_phys 0x10000000

setenv linux_load_addr_virt 0x90000000

setenv linux_size_sectors 15af

setenv linux_start_sector 0x2000

setenv netmask 255.255.255.0

setenv serverip 192.168.0.20

setenv stderr serial

setenv stdin serial

setenv stdout serial

setenv update_dtb 'tftpboot ${dtb_load_addr_virt} kd5886_evb_gmii.dtb ; setexpr fw_sz ${filesize} / 0x200 ; setexpr fw_sz ${fw_sz} + 1 ; mmc write ${dtb_load_addr_phys} ${dtb_start_sector} ${fw_sz} ; setenv dtb_size_sectors ${fw_sz} ; saveenv ;'

setenv update_etx4 'tftpboot ${etx4_load_addr_virt} rootfs.ext4 ; setexpr fw_sz ${filesize} / 0x200 ; setexpr fw_sz ${fw_sz} + 1 ; mmc write ${etx4_load_addr_phys} ${ext4_start_sector} ${fw_sz} ; setenv ext4_size_sectors ${fw_sz} ; saveenv ; '

setenv update_linux 'tftpboot ${linux_load_addr_virt} uImage ; setexpr fw_sz ${filesize} / 0x200 ; setexpr fw_sz ${fw_sz} + 1 ; mmc write ${linux_load_addr_phys} ${linux_start_sector} ${fw_sz} ; setenv linux_size_sectors ${fw_sz} ; saveenv ; '

saveenv

### 配置网络参数

## 内存启动uImage_ramfs

tftpboot ${linux_load_addr_virt} uImage_ramfs

tftpboot ${dtb_load_addr_virt} kd5886_evb_gmii_ramfs.dtb

bootm ${linux_load_addr_virt} - ${dtb_load_addr_virt}

如果emmc 中的文件系统被破坏，需要进行重新分区和格式化。

分区：相关参数参考分区图。

fdisk /dev/mmcblk0

格式化：

mkfs.ext4 /dev/mmcblk0p1

mkfs.ext4 /dev/mmcblk0p2

见: 附1: 分区与格式化:

## 烧写到emmc并启动

kd5886_evb_gmii.dtb 升级：run update_dtb

rootfs.ext4 升级：run update_etx4

uImage 升级：run update_linux

加载运行：run bootcmd

## 启动脚本配置

修改配置文件 /etc/init.d/rcS

## Buildroot login

用户名： root ,密码：root

# 龙芯2k+KD5886

在demo板上插入龙芯2k扣板，龙芯2k 通过pcie1port0与KD5886连接。

## 龙芯扣板分区

Spi flash： 主要放pmon

Nand flash：分区如下：

mtdparts = nand-flash:50M@0(kernel),-(rootfs)

在kernel中的挂载位置：

/dev/mtdblock0 on /boot type yaffs (rw,relatime)

/dev/mtdblock1 on /mnt/flash0 type yaffs (rw,relatime)

mtdblock0：kernel和rootfs分区。

Mtdblock1：其它数据分区。

## 相关升级镜像介绍

gzrom-dtb.bin ： 带dtb的pmon 镜像。

vmlinuz ： 带rootfs的 vmlinuz镜像。

## Pmon 相关操作介绍

配置网络：

ifconfig syn1 192.168.0.2

网口升级pmon：

load -r -f 0xbfc00000 tftp://192.168.0.20/gzrom-dtb.bin

串口升级pmon：

ymodem base=0x81800000

load -r -f 0xbfc00000 /dev/ram/ymodem

vmlinuz加载到内存并启动：

load tftp://192.168.0.20/vmlinuz

g console=ttyS0,115200 rdinit=/sbin/init

vmlinuz烧写到flash：

devcp tftp://192.168.0.20/vmlinuz /dev/fs/yaffs2@mtd0/vmlinuz

## linux系统操作相关介绍

### ftpd 服务

目录/tmp/ftp，用户名： root ,密码：无

### Telnetd服务

### 用户启动脚本

用户在/mnt/flashX 目录下创建start.sh文件，用户可以自定义启动配置，如网络参数。

### 升级vmlinuz

先将vmlinuz通过ftp或其它工具下载到设备，然后在cp 到/boot目录下。如：

cp /tmp/ftp/vmlinuz /boot/

# SDK demo应用启动

在/app 或 /mnt/flash0/sdk 目录下：

./loadsoc.sh

./demo –y

# 附1: 分区与格式化
