# 示例案例：出生运气 × 天气 × 体质三维叠加

> 示例用途：展示 `scripts/advanced_alignment.py` 的标准输出结构。  
> 数据说明：出生日期、地点与体质分数均为演示数据；天气使用 mock，不对应真实个人。  
> 安全说明：本示例不构成医学诊断或治疗建议。

## 一、输入

```bash
python scripts/advanced_alignment.py \
  --date 2026-06-29 \
  --birth-date 2003-04-19 \
  --city 杭州 \
  --constitution-demo \
  --mock
```

## 二、核心结果摘要

- 运气年：2026 丙午年
- 岁运：水运太过
- 司天 / 在泉：少阴君火 / 阳明燥金
- 出生年运气：2003 癸未年，火运不及
- 先天体质倾向：阳虚质
- 九种体质量表示例：阳虚质为主，兼气虚倾向
- mock 天气六气：湿热
- 综合等级：量表体质、出生运气与天气实况三重同向

## 三、标准 Markdown 输出

详见：

```text
reports/examples/advanced-alignment-sample.md
```

## 四、机器可读 JSON 输出

详见：

```text
reports/examples/advanced-alignment-sample.json
```

## 五、说明

本案例展示了：

1. 出生年火运不及与阳虚质倾向的关联；
2. 当前水运太过对阳虚、气虚、血瘀等体质的牵动；
3. mock 湿热天气与个体体质的交叉影响；
4. 高级对齐模块如何输出 `advanced_synthesis`。

⚠️ 免责声明：以上分析基于中医运气学说与体质学说理论推演，仅供学习和演示，不构成医学诊断或治疗建议。具体诊疗须由执业医师辨证处理。
