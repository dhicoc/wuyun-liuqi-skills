# 天气数据对齐集成设计

> **模块**：advanced-alignment / weather_integration
> **版本**：1.0.0
> **定位**：五运六气优化计划 Step 5 — 高级对齐模块
> **依赖**：`yunqi-calc/`（运气推算结果）、`yunqi-pathogenesis/`（病机分析结果）

---

## 1. 设计理念：内外邪相合

### 1.1 核心思想

运气学说的本质是"推步气候以测病机"——通过天干地支推算年度气候偏胜偏衰，预判疾病倾向。然而运气推算描述的是**气运层面的宏观气候趋势**（大运主一年之大势，司天在泉主半年之偏胜），而非某一时间某一地点的**具体气象实况**。

中医病因学中，六淫（风、寒、暑、湿、燥、火）为外感病邪，其致病的实质是**气候变化超出人体调节范围**。《素问·至真要大论》云："百病之生也，皆生于风寒暑湿燥火，以之化之变也。"此处"化之变"即指气候的**实际变化**，而非理论推算值。

因此，将运气推算（理论气候趋势）与实时气象数据（实际气候实况）对齐，体现的正是中医"**内外邪相合**"的病理观：

- **内邪**：运气推算所揭示的年度气运偏胜（如水运太过则寒邪偏盛），为"运邪"
- **外邪**：实际气象数据所反映的当下气候实况（如实际气温偏低、降雪偏多），为"时邪"
- **相合**：当运邪与时邪方向一致时，内外合邪，病机加重；当方向相背时，需灵活调整运气推算的病机预判

### 1.2 对齐的理论依据

| 来源 | 原文 | 释义 |
|------|------|------|
| 《素问·六节藏象论》 | "不知年之所加，气之盛衰，虚实之所起，不可以为工矣" | 强调运气推算的必要性 |
| 《素问·至真要大论》 | "审查病机，无失气宜" | "气宜"包含运气推算与实际气候 |
| 《素问·八正神明论》 | "因天时而调血气" | 治疗须因实际天时而调整 |
| 历代运气家 | "运气有常，而天时多变" | 运气为常，实际气候为变，须知常达变 |

### 1.3 设计目标

```
运气推算（理论趋势）  +  实时气象（实际实况）  =  增强病机分析
       ↓                       ↓                      ↓
  宏观气候偏胜预测      微观当下气候实况       内外邪相合判断
  (yunqi-calc)         (weather API)         (enhanced pathogenesis)
```

通过天气数据对齐，Agent 可以实现：

1. **验证运气推算**：实际天气是否与运气推算的气候趋势一致
2. **量化偏胜程度**：将"湿土司天"从定性描述转化为可量化的湿度/降水数据
3. **动态调整建议**：当实际气候与运气推算相背时，灵活调整养生调理方向
4. **精准健康提示**：结合当下气象实况给出更有针对性的健康建议

---

## 2. 天气 API 选型

### 2.1 推荐方案

以下三家 API 经评估适合本模块使用，按推荐优先级排列：

| 对比维度 | 和风天气 (QWeather) | 心知天气 (Seniverse) | OpenWeatherMap |
|----------|---------------------|----------------------|----------------|
| **免费额度** | 1000 次/日（标准订阅） | 800 次/日（免费版） | 1000 次/日（Free plan） |
| **中国城市覆盖** | 优（覆盖全国3000+区县） | 优（覆盖全国2000+城市） | 良（主要城市，区县级不足） |
| **温度** | 支持 | 支持 | 支持 |
| **湿度** | 支持 | 支持 | 支持 |
| **降水量** | 支持（逐小时+逐日） | 支持（逐日） | 支持（rain.1h/rain.24h） |
| **风速/风向** | 支持（16方位风向） | 支持（8方位风向） | 支持（度数风向） |
| **空气质量(AQI)** | 支持（免费版含AQI） | 支持（免费版含AQI） | 支持（需Air Pollution API） |
| **UV指数** | 支持 | 不支持（免费版） | 支持 |
| **降雪/霜冻** | 支持 | 部分支持 | 支持 |
| **历史数据** | 支持（需付费） | 支持（免费版限10天） | 支持（需付费） |
| **API响应语言** | 中文 | 中文 | 英文 |
| **数据更新频率** | 10-20分钟 | 1小时 | 10分钟 |
| **推荐场景** | 国内用户首选 | 备选（数据简洁） | 海外用户备选 |

### 2.2 选型建议

- **首选：和风天气 (QWeather)**
  - 中国区县覆盖最全，免费额度充足，数据维度最丰富
  - 风向16方位有利于精确对齐"厥阴风木"之风向分析
  - 空气质量数据有利于"阳明燥金"之燥邪/霾邪分析
  - 官方文档完善，SDK 生态好

- **备选：心知天气 (Seniverse)**
  - 中国城市覆盖优秀，API 接口简洁
  - 免费版降水量数据可满足基本对齐需求
  - 适合轻量级集成场景

- **国际场景：OpenWeatherMap**
  - 全球覆盖最佳，适合非中国地区用户
  - 免费版数据维度基本满足对齐需求
  - 中国区县级覆盖不足，风向以度数表示需转换

### 2.3 接入注意事项

| 事项 | 说明 |
|------|------|
| API Key 管理 | MUST 安全存储，MUST NOT 硬编码在脚本中，建议使用环境变量 `WEATHER_API_KEY` |
| 调用频率控制 | 免费额度有限，建议按需调用（每日1-4次），非高频轮询 |
| 数据缓存 | 建议本地缓存1小时内的天气数据，避免重复请求 |
| 异常处理 | API 调用失败时 MUST 回退至纯运气推算模式，不得阻断主流程 |
| 隐私保护 | 用户位置数据 MUST 仅用于天气查询，MUST NOT 存储或传输至第三方 |

---

## 3. 六气—现代气象数据映射表

### 3.1 映射总表

| 六气 | 天干地支归属 | 对应气象指标 | 阈值参考（对齐判定） |
|------|-------------|-------------|---------------------|
| **厥阴风木** | 巳亥年（司天/在泉） | 风速（m/s）、风向（方位角） | 风速≥5.4m/s（4级风）为风邪偏盛；风向偏东偏南合厥阴之位 |
| **少阴君火** | 子午年（司天/在泉） | 气温（℃）、UV指数 | 气温高于同期常年均值2℃以上为君火偏盛；UV指数≥6为火邪偏盛 |
| **少阳相火** | 寅申年（司天/在泉） | 气温（℃）、UV指数、体感温度 | 气温高于同期常年均值3℃以上为相火偏盛；体感温度≥35℃为暑热邪盛 |
| **太阴湿土** | 丑未年（司天/在泉） | 相对湿度（%）、降水量（mm）、降水日数 | 湿度≥75%持续3天以上为湿邪偏盛；日降水量≥10mm为湿邪外侵 |
| **阳明燥金** | 卯酉年（司天/在泉） | 相对湿度（%）、空气质量（AQI/PM2.5） | 湿度≤40%持续3天以上为燥邪偏盛；AQI≥100为浊邪兼燥 |
| **太阳寒水** | 辰戌年（司天/在泉） | 气温（℃）、降雪/霜冻记录 | 气温低于同期常年均值2℃以上为寒邪偏盛；出现降雪/霜冻为寒邪外侵 |

### 3.2 映射逻辑说明

六气与气象指标的对应关系基于以下中医理论依据：

**厥阴风木 → 风速、风向**
- 《素问·五运行大论》："东方生风，风生木，木生酸，酸生肝……在天为风，在地为木。"
- 风为厥阴之本气，风速大小直接反映风邪盛衰。风向与厥阴方位（东偏南）相合时，风邪更易侵袭人体。

**少阴君火 / 少阳相火 → 气温、UV指数**
- 《素问·五运行大论》："南方生热，热生火，火生苦，苦生心……在天为热，在地为火。"
- 君火与相火同属火气，气温为火的直接气象表征。UV指数反映太阳辐射强度，与"火"的炎热属性吻合。君火偏于温（热之渐），相火偏于暑（热之极），故相火阈值更高。

**太阴湿土 → 湿度、降水量**
- 《素问·五运行大论》："中央生湿，湿生土，土生甘，甘生脾……在天为湿，在地为土。"
- 湿为太阴之本气，空气湿度与降水量是湿邪最直接的气象指标。持续高湿或连续降水即为湿邪外盛之象。

**阳明燥金 → 湿度（低）、空气质量**
- 《素问·五运行大论》："西方生燥，燥生金，金生辛，辛生肺……在天为燥，在地为金。"
- 燥为阳明之本气，燥邪的本质是水分不足，故以低湿度（≤40%）为判定指标。现代空气污染（PM2.5/AQI偏高）虽非传统燥邪，但浊气犯肺与燥邪伤肺病位相同，故兼参空气质量。

**太阳寒水 → 气温（低）、降雪/霜冻**
- 《素问·五运行大论》："北方生寒，寒生水，水生咸，咸生肾……在天为寒，在地为水。"
- 寒为太阳之本气，气温偏低为寒邪直接表征。降雪与霜冻是寒邪极盛的气象表现，故特别标注。

### 3.3 司天在泉对齐规则

运气推算中，司天主上半年气候趋势，在泉主下半年气候趋势。对齐时须分时段验证：

| 运气推算 | 对齐时段 | 气象验证方法 |
|----------|----------|-------------|
| 司天之气（上半年） | 当年1月-6月（大寒至小暑） | 取上半年对应气象指标均值，与同期常年均值对比 |
| 在泉之气（下半年） | 当年7月-12月（大暑至小寒） | 取下半年对应气象指标均值，与同期常年均值对比 |
| 主气六步（各步约60日） | 按六步节气时段 | 取对应节气时段气象数据，与主气属性对齐 |
| 客气加临（各步约60日） | 按客气推移时段 | 客气属性对应的气象指标在该步是否偏盛 |

---

## 4. 对齐逻辑

### 4.1 对齐判定矩阵

对齐逻辑的核心是判断**运气推算的气候趋势**与**实际气象实况**是否一致，据此调整病机分析权重：

| 运气推算方向 | 实际气象方向 | 对齐状态 | 病机调整 | 健康建议调整 |
|-------------|-------------|----------|----------|-------------|
| 湿土司天（湿邪偏盛） | 实际多雨高湿 | **相合**（同向） | 湿邪内外相合，脾系风险显著加重 | 重点健脾化湿，减少生冷，注意防潮 |
| 湿土司天（湿邪偏盛） | 实际干燥少雨 | **不符**（相背） | 湿邪外在表现不显，但运邪仍在，降级处理 | 按实际燥邪调护，兼顾健脾但不重化湿 |
| 燥金司天（燥邪偏盛） | 实际干燥低湿 | **相合**（同向） | 燥邪内外相合，肺系风险显著加重 | 重点润肺生津，减少辛辣，注意保湿 |
| 燥金司天（燥邪偏盛） | 实际偏湿多雨 | **不符**（相背） | 燥邪被实际湿气缓解，但运邪仍在，灵活调整 | 按实际湿邪调护，兼顾润肺但不重燥湿 |
| 寒水司天（寒邪偏盛） | 实际寒冷多雪 | **相合**（同向） | 寒邪内外相合，肾系风险显著加重 | 重点温阳散寒，保暖固肾，减少寒凉 |
| 寒水司天（寒邪偏盛） | 实际偏暖少雪 | **不符**（相背） | 寒邪外在表现不显，运邪仍在，降级处理 | 按实际偏温调护，兼顾温阳但不重散寒 |
| 风木司天（风邪偏盛） | 实际多风 | **相合**（同向） | 风邪内外相合，肝系风险加重 | 重点平肝息风，减少辛散，注意防风 |
| 风木司天（风邪偏盛） | 实际少风 | **不符**（相背） | 风邪外在表现不显，但运邪仍在 | 按实际气候调护，兼顾疏肝但不重散风 |
| 君火/相火司天（火邪偏盛） | 实际高温 | **相合**（同向） | 火邪内外相合，心系风险显著加重 | 重点清心降火，减少辛热，注意防暑 |
| 君火/相火司天（火邪偏盛） | 实际偏凉 | **不符**（相背） | 火邪被实际凉气缓解，但运邪仍在 | 按实际偏凉调护，兼顾清心但不重苦寒 |

### 4.2 对齐判定算法

```
对齐判定算法（伪代码）：

输入：
  qi_prediction: 运气推算结果（含司天/在泉/客气属性及方向）
  weather_actual: 实际气象数据（含温度/湿度/风速/降水等）

输出：
  alignment_result: { status, severity, adjusted_pathogenesis, advice_adjustment }

步骤：
1. 从 qi_prediction 提取当前时段的主导客气属性（如"太阴湿土司天"）
2. 查映射表获取该客气对应的气象指标及阈值
3. 从 weather_actual 提取对应气象指标的实际值
4. 判定实际气象是否达到该客气属性的偏盛阈值
5. 比较运气推算方向与实际气象方向：
   - 同向 → alignment_status = "相合"（内外邪合）
   - 相背 → alignment_status = "不符"（需灵活调整）
   - 实际无显著偏盛 → alignment_status = "中性"（运邪为主）
6. 根据对齐状态调整病机分析权重：
   - 相合：对应脏腑风险权重 ×1.5
   - 不符：对应脏腑风险权重 ×0.6，但 MUST NOT 归零
   - 中性：对应脏腑风险权重 ×1.0（维持运气推算原值）
7. 生成调整后的病机分析与健康建议
```

### 4.3 特殊情况处理

| 特殊情况 | 处理方式 |
|----------|----------|
| 运气推算为"平气"之年 | 以实际气象为主，运气推算为辅（平气年运邪不盛，实况权重更大） |
| 运气推算为"太过"且实际也偏盛 | 相合程度最高，内外邪合最重，MUST 提升预警级别 |
| 运气推算为"不及"但实际偏盛 | 运气不及为虚，实况偏盛为实，须防"虚中夹实"，兼顾补虚与祛邪 |
| 天气API不可用 | 回退至纯运气推算模式，在输出中标注"未含实况对齐" |
| 实际气候极端异常（如暴雪、酷暑） | 无论运气推算如何，MUST 以实际极端气候为首要警示 |

---

## 5. API 调用示例

### 5.1 伪代码：获取天气数据并对齐

```python
# ============================================================
# 五运六气 × 天气数据对齐 — 伪代码示例
# 实际实现时需替换为真实API SDK调用
# ============================================================

import os
import json
from datetime import datetime

# --- 配置 ---
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY", "")
WEATHER_API_BASE = "https://devapi.qweather.com/v7/weather/now"  # 和风天气示例

# --- 六气-气象指标映射表 ---
QI_WEATHER_MAPPING = {
    "厥阴风木": {
        "metrics": ["wind_speed", "wind_direction"],
        "threshold": {"wind_speed": 5.4},  # 4级风
        "qi_organ": "肝",
    },
    "少阴君火": {
        "metrics": ["temperature", "uv_index"],
        "threshold": {"temperature_deviation": 2},  # 高于常年均值2℃
        "qi_organ": "心",
    },
    "少阳相火": {
        "metrics": ["temperature", "uv_index", "feels_like"],
        "threshold": {"temperature_deviation": 3, "feels_like": 35},
        "qi_organ": "心包/三焦",
    },
    "太阴湿土": {
        "metrics": ["humidity", "precipitation"],
        "threshold": {"humidity": 75, "precipitation_daily": 10},
        "qi_organ": "脾",
    },
    "阳明燥金": {
        "metrics": ["humidity", "aqi"],
        "threshold": {"humidity_low": 40, "aqi": 100},
        "qi_organ": "肺",
    },
    "太阳寒水": {
        "metrics": ["temperature", "snow"],
        "threshold": {"temperature_deviation": -2},  # 低于常年均值2℃
        "qi_organ": "肾",
    },
}


def fetch_weather(location_lat, location_lon):
    """
    获取用户所在位置的实时天气数据。
    使用和风天气API（或其他已配置的天气API）。
    """
    # 伪代码：实际调用天气API
    # params = {"location": f"{location_lon},{location_lat}", "key": WEATHER_API_KEY}
    # response = http_get(WEATHER_API_BASE, params)
    # return parse_weather_response(response)

    # 模拟返回结构
    return {
        "temperature": 12.5,         # ℃
        "humidity": 82,               # %
        "precipitation": 15.3,        # mm/24h
        "wind_speed": 3.2,            # m/s
        "wind_direction": "NE",       # 方位
        "uv_index": 3,                # UV指数
        "aqi": 65,                    # 空气质量指数
        "feels_like": 10.0,           # 体感温度 ℃
        "snow": False,                # 是否降雪
        "timestamp": datetime.now().isoformat(),
    }


def fetch_climate_normal(location_lat, location_lon, period):
    """
    获取该位置同期常年气候均值（用于偏差计算）。
    可使用历史天气API或气候统计数据。
    """
    # 伪代码：返回同期常年均值
    return {
        "temperature_normal": 14.0,
        "humidity_normal": 70,
        "precipitation_normal": 8.0,
        "period": period,
    }


def align_qi_with_weather(qi_prediction, weather_actual, climate_normal):
    """
    将运气推算结果与实际天气数据对齐。

    参数:
        qi_prediction: 运气推算结果（来自 yunqi-calc 脚本的 --json 输出）
        weather_actual: 实时天气数据（来自 fetch_weather）
        climate_normal: 同期常年气候均值（来自 fetch_climate_normal）

    返回:
        alignment_result: 对齐分析结果
    """
    # 1. 提取当前时段主导客气属性
    dominant_qi = qi_prediction["sitian"]["qi_name"]  # 如 "太阴湿土"

    # 2. 查映射表
    mapping = QI_WEATHER_MAPPING.get(dominant_qi)
    if not mapping:
        return {"status": "无映射", "message": f"未找到{dominant_qi}的气象映射"}

    # 3. 计算气象偏差
    temp_deviation = weather_actual["temperature"] - climate_normal["temperature_normal"]
    humidity_deviation = weather_actual["humidity"] - climate_normal["humidity_normal"]

    # 4. 判定实际气象是否偏盛
    actual_qi_excess = False
    if dominant_qi == "太阴湿土":
        if weather_actual["humidity"] >= mapping["threshold"]["humidity"]:
            actual_qi_excess = True
        if weather_actual["precipitation"] >= mapping["threshold"]["precipitation_daily"]:
            actual_qi_excess = True

    elif dominant_qi == "阳明燥金":
        if weather_actual["humidity"] <= mapping["threshold"]["humidity_low"]:
            actual_qi_excess = True

    elif dominant_qi == "太阳寒水":
        if temp_deviation <= mapping["threshold"]["temperature_deviation"]:
            actual_qi_excess = True
        if weather_actual["snow"]:
            actual_qi_excess = True

    # ... 其他六气的判定逻辑

    # 5. 判定对齐状态
    qi_predicted_excess = qi_prediction.get("qi_excess", False)  # 运气推算是否偏盛

    if qi_predicted_excess and actual_qi_excess:
        alignment_status = "相合"  # 内外邪相合
        risk_multiplier = 1.5
    elif qi_predicted_excess and not actual_qi_excess:
        alignment_status = "不符"  # 气候与运气不符
        risk_multiplier = 0.6
    else:
        alignment_status = "中性"
        risk_multiplier = 1.0

    # 6. 生成增强分析
    result = {
        "dominant_qi": dominant_qi,
        "qi_organ": mapping["qi_organ"],
        "alignment_status": alignment_status,
        "risk_multiplier": risk_multiplier,
        "weather_summary": {
            "temperature": weather_actual["temperature"],
            "humidity": weather_actual["humidity"],
            "precipitation": weather_actual["precipitation"],
            "wind_speed": weather_actual["wind_speed"],
            "temp_deviation": round(temp_deviation, 1),
            "humidity_deviation": round(humidity_deviation, 1),
        },
        "adjusted_pathogenesis": generate_adjusted_pathogenesis(
            qi_prediction, alignment_status, risk_multiplier
        ),
        "enhanced_advice": generate_enhanced_advice(
            qi_prediction, weather_actual, alignment_status
        ),
    }
    return result


def generate_enhanced_advice(qi_prediction, weather_actual, alignment_status):
    """
    基于对齐结果生成增强健康建议。
    Agent将此结果作为Context传递给大模型进行自然语言生成。
    """
    advice_context = {
        "qi_prediction": qi_prediction,
        "weather_actual": weather_actual,
        "alignment_status": alignment_status,
        "instruction": (
            "请基于以上运气推算与实际天气对齐分析，"
            "生成面向用户的健康调理建议。"
            "要求：结合内外邪相合理论，使用中医术语，"
            "区分理论分析与具体建议，附加免责声明。"
        ),
    }
    return advice_context


# --- 主流程 ---
def main(year, location_lat, location_lon):
    """
    主流程：运气推算 → 天气获取 → 对齐分析 → 增强建议
    """
    # Step 1: 运气推算（调用已有脚本）
    # import subprocess
    # qi_result = subprocess.run(
    #     ["python", "scripts/yunqi_report.py", str(year), "--json"],
    #     capture_output=True, text=True
    # )
    # qi_prediction = json.loads(qi_result.stdout)
    qi_prediction = {"sitian": {"qi_name": "太阴湿土"}, "qi_excess": True}

    # Step 2: 获取实时天气
    weather = fetch_weather(location_lat, location_lon)

    # Step 3: 获取同期常年均值
    climate_normal = fetch_climate_normal(
        location_lat, location_lon, period="current_season"
    )

    # Step 4: 对齐分析
    alignment = align_qi_with_weather(qi_prediction, weather, climate_normal)

    # Step 5: 输出增强分析结果
    print(json.dumps(alignment, ensure_ascii=False, indent=2))
    return alignment
```

### 5.2 对齐结果数据结构

```json
{
  "dominant_qi": "太阴湿土",
  "qi_organ": "脾",
  "alignment_status": "相合",
  "risk_multiplier": 1.5,
  "weather_summary": {
    "temperature": 12.5,
    "humidity": 82,
    "precipitation": 15.3,
    "wind_speed": 3.2,
    "temp_deviation": -1.5,
    "humidity_deviation": 12.0
  },
  "adjusted_pathogenesis": {
    "primary_risk": "脾系湿困",
    "risk_level": "高（内外湿邪相合）",
    "pathogenesis_detail": "运气推算太阴湿土司天，实际天气湿度82%（高于常年均值12个百分点），日降水15.3mm，内外湿邪相合，脾土受困尤甚。可见脘腹胀满、纳呆便溏、肢体困重等症。",
    "secondary_risk": "湿郁化热，波及肝胆"
  },
  "enhanced_advice": {
    "dietary": "宜薏苡仁、赤小豆、陈皮等健脾化湿之品；忌生冷瓜果、肥甘厚腻",
    "lifestyle": "注意防潮祛湿，居所通风除湿；避免淋雨涉水；适度运动助脾运化",
    "emotional": "湿困脾土易致气机不畅，注意情志舒畅，勿忧思过度"
  }
}
```

---

## 6. 输出增强示例

### 6.1 场景设定

- **年份**：2026年（丙午年）
- **运气推算**：水运太过，太阳寒水司天，太阴湿土在泉
- **用户位置**：上海（北纬31.23，东经121.47）
- **实际天气**（2026年2月）：气温3.2℃（低于常年均值2.8℃），湿度85%，降雪2次

### 6.2 对齐前（无天气集成）

> **运气分析报告（2026年丙午年）**
>
> **大运**：水运太过。水运太过则寒气偏盛，寒邪通于肾，可见寒郁下焦、腰膝冷痛、小便清长等症。
>
> **司天在泉**：太阳寒水司天（上半年寒气偏盛），太阴湿土在泉（下半年湿气偏盛）。
>
> **病机倾向**：
> - 上半年：寒水司天，寒邪偏盛，肾系受邪风险高。可见腰膝冷痛、关节拘急、畏寒肢冷等症。
> - 下半年：湿土在泉，湿邪偏盛，脾系受邪风险高。可见脘腹胀满、纳呆便溏、肢体困重等症。
>
> **养生建议**：上半年注意温阳散寒，保暖固肾；下半年注意健脾化湿，减少生冷。
>
> ⚠️ 免责声明：以上分析基于中医运气学说理论推算，仅供参考……

### 6.3 对齐后（含天气集成）

> **运气 × 天气增强分析报告（2026年丙午年 · 上海）**
>
> **大运**：水运太过。水运太过则寒气偏盛，寒邪通于肾，可见寒郁下焦、腰膝冷痛、小便清长等症。
>
> **司天在泉**：太阳寒水司天（上半年寒气偏盛），太阴湿土在泉（下半年湿气偏盛）。
>
> **天气实况对齐**（2026年2月 · 上海）：
>
> | 气象指标 | 实际值 | 常年均值 | 偏差 | 对齐判定 |
> |----------|--------|----------|------|----------|
> | 气温 | 3.2℃ | 6.0℃ | -2.8℃ | 寒邪偏盛（达寒水对齐阈值） |
> | 湿度 | 85% | 72% | +13% | 湿气偏盛（兼见湿象） |
> | 降雪 | 2次 | 0.3次 | +1.7次 | 寒邪极盛之象 |
>
> **对齐结果**：☀ **相合**（内外邪相合）
>
> 运气推算太阳寒水司天，实际气温较常年偏低2.8℃且出现2次降雪，运气推算方向与实际气象方向**高度一致**，内外寒邪相合，肾系风险**显著加重**（风险系数 ×1.5）。
>
> 兼见湿气偏盛（湿度85%，高于常年13个百分点），寒湿相合，更易痹阻关节、困遏脾阳。
>
> **增强病机分析**：
> - 寒邪内外相合，肾系受邪风险显著加重。寒邪直中少阴，可见腰膝冷痛、小便清长、畏寒肢冷、关节拘急冷痛等症。
> - 寒湿相搏，痹阻经络关节，可见关节冷痛重着、屈伸不利等症（寒湿痹证）。
> - 寒湿困脾，脾阳受遏，可见脘腹冷痛、纳呆便溏、肢体困重等症。
>
> **增强养生建议**：
> - **温阳散寒**（重点）：宜食羊肉、桂圆、生姜、肉桂等温阳之品；忌生冷瓜果、寒凉饮料。居所注意保暖，尤其腰腹、足部保暖。
> - **健脾化湿**（兼重）：宜食薏苡仁、茯苓、白术等健脾化湿之品；注意防潮祛湿。
> - **温通经络**：适度艾灸关元、命门、足三里等穴（须由执业针灸师操作）；泡脚温通经络。
> - **情志调护**：寒邪偏盛易致情志沉郁，注意保持心情舒畅，适度晒太阳。
>
> ⚠️ 免责声明：以上分析基于中医运气学说理论推算与实时气象数据对齐，仅供参考。运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。请勿据此自行用药或针灸。
>
> *注：本报告含天气数据对齐增强分析，数据来源：和风天气API（2026-02-XX 上海实况）。*

### 6.4 增强效果对比

| 对比维度 | 对齐前 | 对齐后 |
|----------|--------|--------|
| **病机精准度** | 仅理论趋势，无实况验证 | 理论+实况双重验证，精准度高 |
| **风险等级** | 定性描述（"风险高"） | 定量判定（"相合""×1.5"） |
| **邪气分析** | 单一运邪分析 | 内外邪相合分析（寒+湿相搏） |
| **建议针对性** | 通用性建议（按运气大方向） | 结合实况的精准建议（如"降雪2次→重点温通经络"） |
| **用户感知** | 抽象（"寒气偏盛"） | 具象（"今日3.2℃，较常年低2.8℃，有降雪"） |
| **动态性** | 年度固定（全年不变） | 随天气更新（每日可刷新） |

---

## 与技能包集成方式

### Agent 调用流程

```
用户请求（含位置信息）
  ↓
[yunqi-calc] 运气推算（调用 Python 脚本获取 --json 结果）
  ↓
[weather_integration] 天气获取（调用天气API获取实时气象）
  ↓
[weather_integration] 对齐分析（运气推算 × 实际天气 → 对齐判定）
  ↓
[yunqi-pathogenesis] 增强病机分析（在对齐结果基础上分析）
  ↓
[yunqi-clinical] 增强养生建议（结合对齐结果给出调护方向）
  ↓
[docs-generator] 生成增强报告（含天气对齐章节）
```

### 集成约束

- **MUST**：天气API调用失败时回退至纯运气推算模式，不得阻断主流程
- **MUST**：天气对齐结果作为 Context 传递给 Agent，不替代运气推算
- **MUST**：对齐结果中的临床建议 MUST 附加医学免责声明
- **SHOULD**：天气数据缓存1小时，避免频繁调用API
- **MUST NOT**：存储或传输用户位置数据至任何第三方（仅用于天气查询）

---

## 相关文件

| 文件 | 用途 |
|------|------|
| `api_specs.json` | 本模块的机器可读API规范（含映射表、对齐逻辑的JSON结构化定义） |
| `constitution_alignment.md` | 体质对齐模块（与天气对齐可叠加使用） |
| `../yunqi-calc/SKILL.md` | 运气推算子技能（提供对齐所需的运气推算结果） |
| `../yunqi-pathogenesis/SKILL.md` | 病机分析子技能（接收对齐结果进行增强分析） |
| `../case-journal/precedent-disclaimer.md` | 医学免责声明（MUST 前置读取） |
