/**
 * 五运六气统一计算接口 (JavaScript 版)
 * 对应 Python 版 calculate_yunqi_api.py
 * 
 * 核心函数: calculateYunqiApi(dateStr)
 * - 以大寒为年界，精确判断运气年份
 * - 返回标准化 JSON，可供 LLM Agent 直接解析
 * 
 * 用法:
 *   const { calculateYunqiApi } = require('./calculate_yunqi_api');
 *   const result = calculateYunqiApi('2026-06-27');
 *   console.log(JSON.stringify(result, null, 2));
 * 
 * 命令行:
 *   node calculate_yunqi_api.js 2026-06-27
 *   node calculate_yunqi_api.js 2026-06-27 --json
 * 
 * 依赖: lunar-javascript (npm install lunar-javascript)
 */

const path = require('path');
const D = require(path.join(__dirname, 'lib', 'yunqi_data.js'));

function calculateYunqiApi(dateStr) {
  // 1. 确定运气年份 (大寒定年)
  const yqYear = D.getYunqiYear(dateStr);

  // 2. 基本干支
  const [tg, dz] = D.getGanzhi(yqYear);
  const idx = D.getSexagenaryIndex(yqYear);
  const sx = D.DIZHI_SHENGXIAO[dz];

  // 3. 日干支
  const dayGz = D.getDayGanzhi(dateStr);

  // 4. 岁运
  const [dayun, dayunTg] = D.getDayun(yqYear);
  const taiguo = D.isTaiguo(yqYear);
  const suiyunCode = D.getSuiyunCode(yqYear);

  // 5. 司天在泉
  const sitian = D.getSitian(yqYear);
  const zaiquan = D.getZaiquan(yqYear);

  // 6. 当前步位
  const stepInfo = D.getCurrentQiStep(dateStr);
  const stepDetail = D.getKezhujialinDetail(yqYear, stepInfo.step_number);

  // 7. 运气同化
  const tianfu = D.checkTianfu(yqYear);
  const suihui = D.checkSuihui(yqYear);
  const taiyiTianfu = tianfu && suihui;
  const pingqi = D.checkPingqi(yqYear);

  // 8. 主运五步
  const zhuYun = D.getZhuyunFiveSteps(yqYear);

  // 9. 客运五步
  const keYun = D.getKeyunFiveSteps(yqYear);

  // 10. 客气六步
  const keQiSix = D.getKeqiSixSteps(yqYear);

  // 11. 客主加临六步
  const keZhuJiaLin = [];
  for (let s = 1; s <= 6; s++) {
    keZhuJiaLin.push(D.getKezhujialinDetail(yqYear, s));
  }

  // 12. 节气日期
  const jieqiDates = {};
  for (const name of ['大寒','春分','小满','大暑','秋分','小雪']) {
    const [y, m, d] = D.getJieqiDate(yqYear, name);
    jieqiDates[name] = `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
  }
  const [ny, nm, nd] = D.getJieqiDate(yqYear + 1, '大寒');
  jieqiDates['大寒(终)'] = `${ny}-${String(nm).padStart(2,'0')}-${String(nd).padStart(2,'0')}`;

  // 构建标准化输出
  return {
    date: dateStr,
    yunqi_year: yqYear,
    year_gz: `${tg}${dz}`,
    year_gan: tg,
    year_zhi: dz,
    sexagenary_index: idx,
    shengxiao: sx,
    day_gz: dayGz,
    sui_yun: {
      name: `${dayun}运`,
      element: dayun,
      status: taiguo ? '太过' : '不及',
      code: suiyunCode,
      tiangan: dayunTg,
    },
    si_tian: sitian,
    zai_quan: zaiquan,
    current_step: {
      step_number: stepInfo.step_number,
      name: stepInfo.step_name,
      zhu_qi: stepDetail.zhu_qi,
      ke_qi: stepDetail.ke_qi,
      relation: stepDetail.relation,
      shun_ni: stepDetail.shun_ni,
      keqi_is_sitian: stepDetail.keqi_is_sitian,
      keqi_is_zaiquan: stepDetail.keqi_is_zaiquan,
      date_range: {
        start: `${stepInfo.start[0]}-${String(stepInfo.start[1]).padStart(2,'0')}-${String(stepInfo.start[2]).padStart(2,'0')}`,
        end: `${stepInfo.end[0]}-${String(stepInfo.end[1]).padStart(2,'0')}-${String(stepInfo.end[2]).padStart(2,'0')}`,
      },
    },
    tong_hua: {
      tianfu, suihui, taiyi_tianfu: taiyiTianfu, pingqi,
    },
    zhu_yun: zhuYun,
    ke_yun: keYun,
    ke_qi_six_steps: keQiSix,
    ke_zhu_jia_lin: keZhuJiaLin,
    jieqi_dates: jieqiDates,
    rag_keys: {
      suiyun: suiyunCode,
      sitian: `${D.LIUQI_PINYIN[sitian]}_sitian`,
      zaiquan: `${D.LIUQI_PINYIN[zaiquan]}_zaiquan`,
      current_step: `zhu_${D.LIUQI_PINYIN[stepDetail.zhu_qi]}_ke_${D.LIUQI_PINYIN[stepDetail.ke_qi]}`,
    },
  };
}

function formatText(result) {
  const lines = [
    `日期: ${result.date}`,
    `运气年: ${result.yunqi_year}年 (${result.year_gz})`,
    `六十甲子: 第${result.sexagenary_index}甲子 | 生肖: ${result.shengxiao}`,
    `日干支: ${result.day_gz || '未安装lunar-javascript，无法计算'}`,
    '',
    `【岁运】${result.sui_yun.name}${result.sui_yun.status} (code: ${result.sui_yun.code})`,
    `【司天】${result.si_tian}`,
    `【在泉】${result.zai_quan}`,
    '',
    `【当前步位】${result.current_step.name}`,
    `  主气: ${result.current_step.zhu_qi}`,
    `  客气: ${result.current_step.ke_qi}`,
    `  关系: ${result.current_step.relation} → ${result.current_step.shun_ni}`,
  ];

  const th = result.tong_hua;
  const thParts = [];
  if (th.tianfu) thParts.push('天符');
  if (th.suihui) thParts.push('岁会');
  if (th.taiyi_tianfu) thParts.push('太乙天符');
  if (th.pingqi) thParts.push('平气');
  lines.push(`【运气同化】${thParts.length ? thParts.join('、') : '无特殊同化'}`);

  lines.push('', '【主运五步】');
  for (const s of result.zhu_yun) lines.push(`  ${s.step}. ${s.tai_shao}${s.element}运`);
  lines.push('【客运五步】');
  for (const s of result.ke_yun) lines.push(`  ${s.step}. ${s.tai_shao}${s.element}运`);

  lines.push('', '【客气六步】');
  for (const s of result.ke_qi_six_steps) {
    let tag = '';
    if (s.is_sitian) tag = ' ← 司天';
    else if (s.is_zaiquan) tag = ' ← 在泉';
    lines.push(`  ${s.step}. ${s.ke_qi}${tag}`);
  }

  lines.push('', '【客主加临】');
  let xiangde = 0, buxiangde = 0;
  for (const s of result.ke_zhu_jia_lin) {
    if (s.shun_ni.startsWith('相得')) xiangde++; else buxiangde++;
    let tag = '';
    if (s.keqi_is_sitian) tag = ' (司天)';
    else if (s.keqi_is_zaiquan) tag = ' (在泉)';
    lines.push(`  ${s.step_number}. 主${s.zhu_qi} 客${s.ke_qi}${tag} → ${s.relation} ${s.shun_ni}`);
  }
  lines.push(`  相得: ${xiangde}步 | 不相得: ${buxiangde}步`);

  lines.push('', '【RAG检索键】');
  for (const [k, v] of Object.entries(result.rag_keys)) lines.push(`  ${k}: ${v}`);

  return lines.join('\n');
}

// CLI
if (require.main === module) {
  const dateStr = process.argv[2];
  if (!dateStr) {
    console.log('用法: node calculate_yunqi_api.js <YYYY-MM-DD> [--json]');
    console.log('示例: node calculate_yunqi_api.js 2026-06-27 --json');
    process.exit(1);
  }
  const result = calculateYunqiApi(dateStr);
  if (process.argv.includes('--json')) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(formatText(result));
  }
}

module.exports = { calculateYunqiApi, formatText };
