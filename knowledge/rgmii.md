# RGMII 接口调试要点

## 时钟与电压

RGMII 由 GTXCLK（发送时钟）和 RXCLK（接收时钟）同步数据，125MHz。
上电前先确认 IOVDD 电压档位与 PHY 端匹配（1.8V/2.5V/3.3V），档位不符是最常见的不通原因。
示波器测 GTXCLK 幅度：VPP 应在 IOVDD 的 ±10% 内。

## 常见故障排查

- link 不起来：先查 GTXCLK 是否有输出，再查 RXDV/RXER 是否悬浮
- 吞吐减半：RXCLK 采样沿配置错，检查 RGMII_ID/RGMII_TXID/RGMII_RXID  delay 位
- CRC 错误间歇出现：走线过长未等长，TX 组与 RX 组各自等长 ±5mil

## 寄存器速查

| 寄存器 | 位 | 作用 |
|--------|----|------|
| BMCR   | bit8 | 双工模式（1=全双工） |
| ANAR   | -    | 自协商能力通告 |
| STATR  | bit2 | 链路状态（1=link up） |
