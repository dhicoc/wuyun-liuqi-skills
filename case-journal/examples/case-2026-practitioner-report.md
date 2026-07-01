# 示例案例：2026 丙午年临床版年度报告

> 示例用途：展示 `scripts/yunqi_report.py --audience practitioner` 的标准输出结构。  
> 安全说明：本示例仅作运气学理论学习与格式参考，不构成临床诊断或治疗建议。

## 一、输入

```bash
python scripts/yunqi_report.py 2026 --audience practitioner
```

## 二、核心结果摘要

- 年份：2026 丙午年
- 岁运：水运太过
- 司天：少阴君火
- 在泉：阳明燥金
- 客主加临：5 步相得，1 步不相得
- 证据链：报告含“经典与注家依据”章节，关联 asset1、asset2、asset3、asset5
- 安全策略：临床版含方药/针灸安全提示与急症提醒

## 三、标准输出

详见：

```text
reports/examples/yunqi-report-practitioner-sample.md
```

## 四、质量门禁

该报告由以下命令生成快照并校验：

```bash
python scripts/report_quality_gate.py \
  --file reports/snapshots/yunqi_report_2026_practitioner.md \
  --audience practitioner \
  --snapshot reports/snapshots/yunqi_report_2026_practitioner.md
```

⚠️ 免责声明：以上分析基于中医运气学说理论推算，仅供参考。运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。请勿据此自行用药或针灸。
