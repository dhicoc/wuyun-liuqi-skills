---
name: yunqi-calc
description: 五运六气推算核心子技能。根据年份计算天干地支、大运太过不及、主运客运、司天在泉、客气主气、客主加临顺逆及运气同化（天符岁会太一天符）。适用于中医运气学说推算、气候病机分析、运气年历生成、五运六气计算等场景。
---

## 运气推算核心子技能

### 适用范围

- 根据公历年份推算五运六气全套参数
- 大运太过不及判断及平气分析
- 主运五步与客运五步排列
- 司天在泉推算及客气六步排列
- 主气六步固定排列
- 客主加临顺逆分析
- 运气同化判断（天符、岁会、太一天符）
- 为病机分析和临床方案提供运气基础数据

### 脚本依赖

| 脚本 | 用途 | 必需 |
|------|------|------|
| calculate_yunqi_api.py | 统一推算：干支/大运/主运客运/司天在泉/客主加临，单次返回全部域 | 是 |

### 推荐工作流

Step 1/5: 干支推算
ACT: 调用 `python scripts/calculate_yunqi_api.py <年份>` 获取该年的天干地支（year_gz）

Step 2/5: 大运推算
ACT: 调用 `python scripts/calculate_yunqi_api.py <年份>` 获取大运五行、太过不及判断（sui_yun）

Step 3/5: 六气推算
ACT: 调用 `python scripts/calculate_yunqi_api.py <年份>` 获取司天在泉及客气六步排列（si_tian / zai_quan / ke_qi_six_steps）

Step 4/5: 客主加临
ACT: 调用 `python scripts/calculate_yunqi_api.py <年份>` 获取六步客主加临顺逆分析（ke_zhu_jia_lin）

Step 5/5: 运气同化判断
ACT: 查 references/yunqi_tonghua.md 判断天符/岁会/太一天符

### 常见误区

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 大运太过不及判断错误 | 阳干太过阴干不及 | 查 references/taiguo_buji.md |
| 客气初气定错 | 客气初气取决于司天位置 | 查 references/zhuqi_keqi.md |
| 司天在泉配对错误 | 不是简单的五行相克关系 | 查 references/sitian_zaiquan.md |
| 客主加临顺逆判断错误 | 需按五行生克关系判断 | 查 references/kezhujialin.md |

### 输出要求

- 明确标注年份及对应干支
- 大运需标注五行属性及太过/不及/平气
- 主运五步和客运五步需标注太少
- 司天在泉需标注六气名称
- 客气六步需按初气至终气顺序排列
- 客主加临需逐步标注顺逆及五行生克关系
- 运气同化需标注天符/岁会/太一天符（若有）
- 所有推算结果应可追溯至参考文档

### 路由上下文

- 上游入口: SKILL.md, routing.yaml
- 下游出口: 病机分析→modules/yunqi-pathogenesis/; 临床方案→modules/yunqi-clinical/
- 同级关联: 干支基础→modules/ganzhi-basics/

### ACTION REQUIRED

- [ ] 确认输入年份为公历纪年
- [ ] 确认所有脚本依赖已安装且可执行
- [ ] 确认参考文档目录结构完整

### 任务完成自检

- [ ] 干支推算结果已输出
- [ ] 大运太过不及已判断
- [ ] 主运客运五步已排列
- [ ] 司天在泉已推算
- [ ] 客气主气六步已排列
- [ ] 客主加临顺逆已分析
- [ ] 运气同化已判断
- [ ] 所有结果可追溯至参考文档
