# 高级对齐模块

`advanced-alignment/` 用于将五运六气宏观推算与更具体的个人、地域、天气信息进行交叉分析。

## 当前可执行入口

| 能力 | 状态 | 执行入口 | 说明 |
|------|------|----------|------|
| 天气对齐 | ✅ 已接入 | `scripts/weather_alignment.py` | 使用 Open-Meteo 或 mock 天气数据，将实况气象转译为六气倾向，与运气格局对齐 |
| 个人体质 | ✅ 已接入 | `scripts/personal_yunqi_profile.py` | 出生年运气体质映射、当前岁运调理、地域修正 |
| 天气 × 体质叠加 | 🟡 设计中 | `weather_alignment.py` + `personal_yunqi_profile.py` | 目前可由 Agent 组合调用，后续可封装为统一脚本 |

## 天气对齐用法

```bash
# 使用城市名调用真实 Open-Meteo API
python scripts/weather_alignment.py 2026-06-29 --city 杭州

# JSON 输出
python scripts/weather_alignment.py 2026-06-29 --city 杭州 --json

# 使用经纬度
python scripts/weather_alignment.py 2026-06-29 --lat 30.2741 --lon 120.1551 --json

# 测试 / CI：不访问外网
python scripts/weather_alignment.py 2026-06-29 --city 杭州 --mock --json
```

## 设计文档

| 文件 | 用途 |
|------|------|
| `weather_integration.md` | 天气数据对齐理论、映射表与设计说明 |
| `constitution_alignment.md` | 体质对齐理论、九种体质矩阵与接口说明 |
| `api_specs.json` | 高级对齐 API 规格草案 |

## 安全边界

天气对齐只用于判断“运气宏观趋势”与“此时此地天气实况”的同向、相背或兼夹关系，不可作为医学诊断依据。涉及调理、方药、针灸时，必须附加医学免责声明。
