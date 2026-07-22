# Visual Design System (DESIGN.md)

## Theme & Mood
- **Style**: Modern Oriental & Astronomical Cybernetics (深色玄青月白/宋韵新中式)
- **Concept**: 静谧玄青背景衬托五行奇彩，融合天体罗盘、六气环轨与现代化玻璃质感。
- **Color Mode**: Dark mode preferred for high visual focus and cosmic astrolabe metaphors.

## Color Tokens (OKLCH Base)
- `--bg-base`: `oklch(0.13 0.02 245)` (Deep Obsidian Slate / 墨玄色 `#0b0f19`)
- `--bg-surface`: `oklch(0.18 0.025 245)` (Inkstone Glass / 砚台暗光 `#131926`)
- `--bg-card`: `oklch(0.22 0.03 245)` (Slate Card / 青石板 `#1a2234`)
- `--border-subtle`: `oklch(0.30 0.03 245)` (Ink Line / 澹墨边框 `#2a3449`)

### Text Tokens
- `--text-main`: `oklch(0.96 0.01 90)` (Moonlight White / 皎月白 `#f5f6f4`)
- `--text-muted`: `oklch(0.75 0.02 90)` (Silver Mist / 银雾灰 `#a8b0bd`)
- `--text-gold`: `oklch(0.82 0.14 80)` (Imperial Gold / 芒神帝黄 `#e5ba62`)

### WuXing (Five Elements) Color Tokens
- `--wood-green`: `oklch(0.72 0.16 150)` (碧翠木 `#34d399`)
- `--fire-red`: `oklch(0.68 0.20 30)` (朱砂火 `#f87171`)
- `--earth-yellow`: `oklch(0.78 0.15 85)` (琥珀土 `#fbbf24`)
- `--metal-white`: `oklch(0.88 0.04 80)` (太白金 `#e2e8f0`)
- `--water-blue`: `oklch(0.65 0.16 230)` (玄水蓝 `#38bdf8`)

## Typography
- **Display / Headings**: `"Noto Serif SC"`, `"Source Han Serif SC"`, `"Songti SC"`, serif (经典衬线/宋体)
- **Body & Controls**: `"Inter"`, `"PingFang SC"`, `"Microsoft YaHei"`, sans-serif
- **Ganzhi & Data**: `"Fira Code"`, `"JetBrains Mono"`, monospace

## Component Architecture
1. **Header & Astrolabe Date Picker (天时选择器)**: 年月日干支速览、大寒交气倒计时、城市气象对齐状态。
2. **Main YunQi Wheel (五运六气宇宙罗盘)**:
   - 外圈：六气客气/主气步位（厥阴风木、少阴君火、少阳相火、太阴湿土、阳明燥金、太阳寒水）
   - 中圈：司天/在泉与客主加临顺逆动态指示
   - 内圈：岁运（太过/不及）、天符岁会同化印章
3. **Current Season & Health Insights Grid (气宜与病机看板)**:
   - 当前步位气候特征与预警
   - 脏腑易发病机与五味治法（平治/胜复/郁发）
   - 三因司天方药推荐（带辨证提示与免责声明）
4. **Personal Natal Yunqi & Constitution Radar (个人运气与体质)**:
   - 输入出生日期计算五运六气先天格局
   - 体质倾向六角雷达图与养生宜忌
5. **RAG & Socratic AI Assistant (运气问答与学习智能体)**:
   - 交互式对话、检索《素问》七篇大论引文、思想地图生成
