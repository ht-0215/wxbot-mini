# kyland_sdk_2.0.0 交换芯片寄存器介绍及操作命令手册

kyland_sdk_2.0.0

交换芯片寄存器介绍及操作命令手册

版本 V1.0

北京物芯科技有限责任公司

修订记录

| 日期 | 修订内容 | 版本 | 作者 |
| --- | --- | --- | --- |
| 2021.11.24 | 完成初稿 | V1.0 | 熊新永 |
|  |  |  |  |
|  |  |  |  |

目录

1 寄存器管理模型：	4

2 模块类型：	5

3 寄存器类型：	6

4 寄存器属性：	7

5 寄存器相关命令：	8

5.1 reg list [MODNAME] [REGNAME]	8

5.2 reg dump [MODNAME] [REGNAME]	8

5.3 reg read MODNAME REGNAME [INDEX0  INDEX1]	8

5.3.1 reg read MODNAME REGNAME	8

5.3.2 reg read MODNAME REGNAME INDEX0  INDEX1	8

5.4 reg write MODNAME REGNAME [INDEX0  INDEX1]  [DATEOFFSET  VAL]	9

5.4.1 reg write MODNAME REGNAME	9

5.4.2 reg write MODNAME REGNAME INDEX0  INDEX1	9

5.4.3 reg write MODNAME REGNAME  INDEX0  INDEX1  DATEOFFSET  VAL	9

5.5 reg hw-sticky (dump|clear)	10

# 寄存器管理模型

适用芯片：KD5886、KD6630

芯片中的寄存器按照模块->寄存器来进行分类管理。

模块使用Target ID寻址，Target ID为模块所在芯片中的偏移基地址，偏移地址计算公式：

PI：Target ID<<16,SI: Target ID<<14。

寄存器使用addr寻址，addr为寄存器所在模块的偏移基地址。偏移地址计算公式：

PI：addrID<<2,SI: addr。

描述方式：mod::reg。偏移地址计算公式：PI：Target ID<<16+ addrID<<2；

SI：Target ID<<14+ addrID。

注：PI：并行总线访问，内部cpu或通过pcie访问。 SI：串行总线访问，如spi,i2c 等。

# 模块类型

单一模块：该模块只有一个target ID，表示为mod。

模块表：  该模块有多个target ID，表示为mod[index]. 目前该类型的模块只有与port 号相关的模块，即index=port。与port有关的模块有： MAC1G、MAC10G、MAC_ADP, PCS。

# 寄存器类型

单一寄存器：只有一个地址, 表示方为reg。如：crg模块中的版本寄存器：

寄存表：有多个相同的寄存器组成一张表，表示方式为reg[index]，index为索引。如：asm模块中的：

寄存器2维表：有多个相同的寄存器组成一张表，表示方式为

reg[index][offset]，index为索引，offset为偏移：如cl模块中的：

# 寄存器属性

R/W: 读写

R/O: 只读

W/O: 只写

One-shot: 软件写1，硬件完成操作后清零

Sticky: 硬件置1，软件写1清0。

# 寄存器相关命令

视图：chip-shell：

支持通过modname 和regname 进行寄存器寻址。如下：

modname regname index0  index1

如果是端口相关模块，为了方便大家操作，通过port号来索引模块。

modname regname port  index1

## reg list [MODNAME] [REGNAME]

可以列出所有模块、所有模块下的寄存器等。

## reg dump [MODNAME] [REGNAME]

dump 出所有/指定的寄存器内容。

## reg read MODNAME REGNAME [INDEX0  INDEX1]

### reg read MODNAME REGNAME

指出配置信息，如 INDEX0  INDEX1 的范围。如：

### reg read MODNAME REGNAME INDEX0  INDEX1

读寄存器的值并格式化输出。如

如果INDEX 处显示的是PORT，表示为port 号。如：

## reg write MODNAME REGNAME [INDEX0  INDEX1]  [DATEOFFSET  VAL]

### reg write MODNAME REGNAME

同reg read。

### reg write MODNAME REGNAME INDEX0  INDEX1

如果不指定写的内容，为读，同reg read MODNAME REGNAME INDEX0  INDEX1如：

### reg write MODNAME REGNAME  INDEX0  INDEX1  DATEOFFSET  VAL

写寄存器某一字段，并支持写完后回读。

DATEOFFSET 表示格式化输出后的偏移，从0开始。

VAL：写入的数据。

将上图ABORT_PAUSE_ENA 改成0，DATEOFFSET=2，VAL=0，如下：

## reg hw-sticky (dump|clear)

dump/clear 所有sticky类型的寄存器。
