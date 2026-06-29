# 高级对齐模块

`advanced-alignment/` 用于将五运六气宏观推算与更具体的个人、地域、天气信息进行交叉分析。

## 当前可执行入口

| 能力 | 状态 | 执行入口 | 说明 |
|------|------|----------|------|
| 天气对齐 | ✅ 已接入 | `scripts/weather_alignment.py` | 支持 Open-Meteo、QWeather、Seniverse、mock；含缓存、历史同期均值、气象六气转译与运气对齐 |
| 个人体质 | ✅ 已接入 | `scripts/personal_yunqi_profile.py` | 出生年运气体质映射、当前岁运调理、地域修正 |
| 天气 × 体质叠加 | ✅ 已接入 | `scripts/yunqi_weather_constitution.py` | 组合天气对齐与个人运气体质，输出先天体质 × 当前岁运 × 天气实况三维叠加判断 |

## 天气对齐用法

```bash
# 自动选择天气源：若配置 QWeather / Seniverse 密钥则优先使用，否则回退 Open-Meteo
python scripts/weather_alignment.py 2026-06-29 --city 杭州

# JSON 输出
python scripts/weather_alignment.py 2026-06-29 --city 杭州 --json

# 指定天气源
python scripts/weather_alignment.py 2026-06-29 --city 杭州 --provider open-meteo --json

# 使用经纬度
python scripts/weather_alignment.py 2026-06-29 --lat 30.2741 --lon 120.1551 --json

# 加入历史同期均值（默认 5 年，可调整）
python scripts/weather_alignment.py 2026-06-29 --city 杭州 --baseline-years 10 --json

# 关闭历史同期均值或缓存
python scripts/weather_alignment.py 2026-06-29 --city 杭州 --no-baseline --no-cache --json

# 测试 / CI：不访问外网
python scripts/weather_alignment.py 2026-06-29 --city 杭州 --mock --json
```

### 可选天气源配置

| 天气源 | 参数 | 密钥环境变量 | 说明 |
|--------|------|--------------|------|
| Open-Meteo | `--provider open-meteo` | 无需密钥 | 默认可用，支持当前/历史/预报与历史同期均值 |
| QWeather | `--provider qweather` | `QWEATHER_API_KEY` 或 `WEATHER_API_KEY` | 当前实现用于实时天气 |
| Seniverse | `--provider seniverse` | `SENIVERSE_API_KEY` | 当前实现用于实时天气 |
| Mock | `--provider mock` 或 `--mock` | 无需密钥 | 用于测试和 CI |

缓存目录：`.cache/weather_alignment/`，默认缓存 60 分钟，可用 `--cache-ttl` 调整。

## 天气 × 体质叠加用法

```bash
# 三维叠加：分析日期 + 出生日期 + 城市
python scripts/yunqi_weather_constitution.py 2026-06-29 --birth-date 2003-04-19 --city 杭州

# JSON 输出
python scripts/yunqi_weather_constitution.py 2026-06-29 --birth-date 2003-04-19 --city 杭州 --json

# 测试 / CI：不访问外网
python scripts/yunqi_weather_constitution.py 2026-06-29 --birth-date 2003-04-19 --city 杭州 --mock --json
```

该脚本会同时调用个人运气体质分析与天气对齐模块，输出：

- 出生年先天运气体质倾向
- 当前岁运易感体质
- 天气实况六气倾向
- 先天体质 × 当前岁运 × 天气实况的叠加级别
- 综合调摄原则


## 设计文档

| 文件 | 用途 |
|------|------|
| `weather_integration.md` | 天气数据对齐理论、映射表与设计说明 |
| `constitution_alignment.md` | 体质对齐理论、九种体质矩阵与接口说明 |
| `api_specs.json` | 高级对齐 API 规格草案 |

## 安全边界

天气对齐只用于判断“运气宏观趋势”与“此时此地天气实况”的同向、相背或兼夹关系，不可作为医学诊断依据。涉及调理、方药、针灸时，必须附加医学免责声明。
