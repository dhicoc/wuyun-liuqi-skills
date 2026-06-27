/**
 * 五运六气推算引擎 — 共享数据表 (JavaScript 版)
 * 对应 Python 版 yunqi_data.py
 * 
 * 依赖: lunar-javascript (npm install lunar-javascript)
 */

// ═══════════════════════════════════════════════════════════════
// 天干地支
// ═══════════════════════════════════════════════════════════════

const TIANGAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸'];
const DIZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥'];

const TIANGAN_YINYANG = {
  '甲':'阳','丙':'阳','戊':'阳','庚':'阳','壬':'阳',
  '乙':'阴','丁':'阴','己':'阴','辛':'阴','癸':'阴',
};

const DIZHI_SHENGXIAO = {
  '子':'鼠','丑':'牛','寅':'虎','卯':'兔',
  '辰':'龙','巳':'蛇','午':'马','未':'羊',
  '申':'猴','酉':'鸡','戌':'狗','亥':'猪',
};

const DIZHI_WUXING = {
  '子':'水','丑':'土','寅':'木','卯':'木',
  '辰':'土','巳':'火','午':'火','未':'土',
  '申':'金','酉':'金','戌':'土','亥':'水',
};

// ═══════════════════════════════════════════════════════════════
// 五行
// ═══════════════════════════════════════════════════════════════

const WUXING = ['木','火','土','金','水'];

const WUXING_SHENG = {
  '木':'火','火':'土','土':'金','金':'水','水':'木',
};

const WUXING_KE = {
  '木':'土','土':'水','水':'火','火':'金','金':'木',
};

// ═══════════════════════════════════════════════════════════════
// 天干化五运
// ═══════════════════════════════════════════════════════════════

const TIANGAN_HUAYUN = {
  '甲':'土','己':'土',    // 甲己化土
  '乙':'金','庚':'金',    // 乙庚化金
  '丙':'水','辛':'水',    // 丙辛化水
  '丁':'木','壬':'木',    // 丁壬化木
  '戊':'火','癸':'火',    // 戊癸化火
};

const WUYUN_STEP = { '木':1, '火':2, '土':3, '金':4, '水':5 };

// ═══════════════════════════════════════════════════════════════
// 六气
// ═══════════════════════════════════════════════════════════════

const DIZHI_HUAQI_SITIAN = {
  '子':'少阴君火','午':'少阴君火',
  '丑':'太阴湿土','未':'太阴湿土',
  '寅':'少阳相火','申':'少阳相火',
  '卯':'阳明燥金','酉':'阳明燥金',
  '辰':'太阳寒水','戌':'太阳寒水',
  '巳':'厥阴风木','亥':'厥阴风木',
};

const SITIAN_ZAIQUAN_PAIR = {
  '厥阴风木':'少阳相火',
  '少阴君火':'阳明燥金',
  '太阴湿土':'太阳寒水',
  '少阳相火':'厥阴风木',
  '阳明燥金':'少阴君火',
  '太阳寒水':'太阴湿土',
};

const LIUQI_WUXING = {
  '厥阴风木':'木','少阴君火':'火','少阳相火':'火',
  '太阴湿土':'土','阳明燥金':'金','太阳寒水':'水',
};

const LIUQI_YINYANG = {
  '厥阴风木':'一阴','少阴君火':'二阴','太阴湿土':'三阴',
  '少阳相火':'一阳','阳明燥金':'二阳','太阳寒水':'三阳',
};

// 主气六步 (固定, 按季节顺序)
const ZHUQI_STEPS = [
  '厥阴风木','少阴君火','少阳相火','太阴湿土','阳明燥金','太阳寒水',
];

// 客气循环序列 (按阴阳推移: 一阴→二阴→三阴→一阳→二阳→三阳)
const KEQI_CYCLE = [
  '厥阴风木','少阴君火','太阴湿土','少阳相火','阳明燥金','太阳寒水',
];

// ═══════════════════════════════════════════════════════════════
// Step 1 增强: 代码/映射表
// ═══════════════════════════════════════════════════════════════

const SUIYUN_CODE = {
  'wood_true':'wood_excess', 'wood_false':'wood_deficient',
  'fire_true':'fire_excess', 'fire_false':'fire_deficient',
  'earth_true':'earth_excess', 'earth_false':'earth_deficient',
  'metal_true':'metal_excess', 'metal_false':'metal_deficient',
  'water_true':'water_excess', 'water_false':'water_deficient',
};

const LIUQI_PINYIN = {
  '厥阴风木':'jueyin_fengmu',
  '少阴君火':'shaoyin_junhuo',
  '太阴湿土':'taiyin_shitu',
  '少阳相火':'shaoyang_xianghuo',
  '阳明燥金':'yangming_zaojin',
  '太阳寒水':'taiyang_hanshui',
};

const QI_STEP_NAMES = {
  1:'初之气(主大寒~春分)',
  2:'二之气(主春分~小满)',
  3:'三之气(主小满~大暑)',
  4:'四之气(主大暑~秋分)',
  5:'五之气(主秋分~小雪)',
  6:'终之气(主小雪~大寒)',
};

const JIEQI_EN_MAP = {
  '大寒':'DA_HAN','春分':'CHUN_FEN','小满':'XIAO_MAN',
  '大暑':'DA_SHU','秋分':'QIU_FEN','小雪':'XIAO_XUE',
};

const JIEQI_FALLBACK = {
  '大寒':[1,20],'春分':[3,20],'小满':[5,21],
  '大暑':[7,23],'秋分':[9,23],'小雪':[11,22],
};

// ═══════════════════════════════════════════════════════════════
// 核心推算函数
// ═══════════════════════════════════════════════════════════════

function getGanzhi(year) {
  const tgIdx = ((year - 4) % 10 + 10) % 10;
  const dzIdx = ((year - 4) % 12 + 12) % 12;
  return [TIANGAN[tgIdx], DIZHI[dzIdx]];
}

function getSexagenaryIndex(year) {
  return ((year - 4) % 60 + 60) % 60 + 1;
}

function getDayun(year) {
  const [tg, _] = getGanzhi(year);
  return [TIANGAN_HUAYUN[tg], tg];
}

function isTaiguo(year) {
  const [tg, _] = getGanzhi(year);
  return TIANGAN_YINYANG[tg] === '阳';
}

function getSitian(year) {
  const [_, dz] = getGanzhi(year);
  return DIZHI_HUAQI_SITIAN[dz];
}

function getZaiquan(year) {
  return SITIAN_ZAIQUAN_PAIR[getSitian(year)];
}

function getKeqiSixSteps(year) {
  const sitian = getSitian(year);
  const sitianIdx = KEQI_CYCLE.indexOf(sitian);
  const zaiquan = getZaiquan(year);
  const steps = [];
  for (let step = 1; step <= 6; step++) {
    const idx = ((sitianIdx + step - 3) % 6 + 6) % 6;
    const qi = KEQI_CYCLE[idx];
    steps.push({
      step, ke_qi: qi,
      is_sitian: qi === sitian,
      is_zaiquan: qi === zaiquan,
    });
  }
  return steps;
}

function getZhuqiSixSteps() {
  return ZHUQI_STEPS.map((qi, i) => ({
    step: i + 1, zhu_qi: qi, is_sitian: false, is_zaiquan: false,
  }));
}

function wuxingSheng(a, b) { return WUXING_SHENG[a] === b; }
function wuxingKe(a, b) { return WUXING_KE[a] === b; }

function kezhujialinRelation(keqi, zhuqi) {
  const keqiElem = LIUQI_WUXING[keqi];
  const zhuqiElem = LIUQI_WUXING[zhuqi];
  if (keqiElem === zhuqiElem) return ['客主同气', '相得（顺）'];
  if (wuxingSheng(keqiElem, zhuqiElem)) return ['客气生主气', '相得（顺）'];
  if (wuxingSheng(zhuqiElem, keqiElem)) return ['主气生客气', '不相得（逆）'];
  if (wuxingKe(keqiElem, zhuqiElem)) return ['客气克主气', '不相得（逆）'];
  if (wuxingKe(zhuqiElem, keqiElem)) return ['主气克客气', '不相得（逆）'];
  return ['未知关系', '未知'];
}

function checkTianfu(year) {
  const [dayun, _] = getDayun(year);
  const sitian = getSitian(year);
  return dayun === LIUQI_WUXING[sitian];
}

function checkSuihui(year) {
  const [dayun, _] = getDayun(year);
  const [_, dz] = getGanzhi(year);
  return dayun === DIZHI_WUXING[dz];
}

function checkPingqi(year) {
  const [dayun, _] = getDayun(year);
  const sitian = getSitian(year);
  const sitianElem = LIUQI_WUXING[sitian];
  const taiguo = isTaiguo(year);
  if (taiguo && wuxingKe(sitianElem, dayun)) return true;
  if (!taiguo && wuxingSheng(sitianElem, dayun)) return true;
  return false;
}

function getZhuyunFiveSteps(year) {
  const [dayun, _] = getDayun(year);
  const dayunStep = WUYUN_STEP[dayun];
  const taiguo = isTaiguo(year);
  const steps = [];
  for (let i = 0; i < 5; i++) {
    const stepNum = i + 1;
    const elem = WUXING[i];
    const diff = ((stepNum - dayunStep) % 2 + 2) % 2;
    const isTai = diff === 0 ? taiguo : !taiguo;
    steps.push({ step: stepNum, element: elem, tai_shao: isTai ? '太' : '少' });
  }
  return steps;
}

function getKeyunFiveSteps(year) {
  const [dayun, _] = getDayun(year);
  const taiguo = isTaiguo(year);
  let elem = dayun;
  const elements = [];
  for (let i = 0; i < 5; i++) {
    elements.push(elem);
    elem = WUXING_SHENG[elem];
  }
  let isTai = taiguo;
  const steps = [];
  for (let i = 0; i < 5; i++) {
    steps.push({ step: i + 1, element: elements[i], tai_shao: isTai ? '太' : '少' });
    isTai = !isTai;
  }
  return steps;
}

function getSuiyunCode(year) {
  const [dayun, _] = getDayun(year);
  const taiguo = isTaiguo(year);
  const key = `${SUIYUN_EN[dayun] || dayun}_${taiguo}`;
  // Use direct mapping
  const codeMap = {
    '木_true':'wood_excess','木_false':'wood_deficient',
    '火_true':'fire_excess','火_false':'fire_deficient',
    '土_true':'earth_excess','土_false':'earth_deficient',
    '金_true':'metal_excess','金_false':'metal_deficient',
    '水_true':'water_excess','水_false':'water_deficient',
  };
  return codeMap[`${dayun}_${taiguo}`] || 'unknown';
}

const SUIYUN_EN = { '木':'wood','火':'fire','土':'earth','金':'metal','水':'water' };

// ═══════════════════════════════════════════════════════════════
// Step 1: 大寒定年 + 日期推算
// ═══════════════════════════════════════════════════════════════

let _Solar = null;
function getSolarClass() {
  if (_Solar !== null) return _Solar;
  try {
    _Solar = require('lunar-javascript').Solar;
    return _Solar;
  } catch (e) {
    _Solar = false;
    return null;
  }
}

function getJieqiDate(year, jieqiName) {
  const Solar = getSolarClass();
  if (!Solar) {
    const [m, d] = JIEQI_FALLBACK[jieqiName] || [1, 20];
    return [year, m, d];
  }
  // 大寒在年初: 从前一年7月的 Lunar 表获取
  const solar = Solar.fromYmd(jieqiName === '大寒' ? year - 1 : year, 7, 1);
  const lunar = solar.getLunar();
  const jqTable = lunar.getJieQiTable();
  const jqEn = JIEQI_EN_MAP[jieqiName];
  if (jqEn && jqTable[jqEn]) {
    const val = jqTable[jqEn];
    // JieQiTable 值可能是 Solar 对象或字符串
    if (typeof val === 'string') {
      const parts = val.split('-');
      return [parseInt(parts[0]), parseInt(parts[1]), parseInt(parts[2])];
    } else if (val && val.getYear) {
      // Solar 对象
      return [val.getYear(), val.getMonth(), val.getDay()];
    }
  }
  // 兜底: 遍历法
  for (let month = 1; month <= 12; month++) {
    for (let day = 1; day <= 28; day++) {
      try {
        const s = Solar.fromYmd(year, month, day);
        const l = s.getLunar();
        const jq = l.getJieQi();
        if (jq && jq.includes(jieqiName)) return [year, month, day];
      } catch (e) {}
    }
  }
  const [m, d] = JIEQI_FALLBACK[jieqiName] || [1, 20];
  return [year, m, d];
}

function getYunqiYear(dateStr) {
  const parts = dateStr.split('-');
  const solarYear = parseInt(parts[0]);
  const solarMonth = parseInt(parts[1]);
  const solarDay = parseInt(parts[2]);
  const [_, dahanM, dahanD] = getJieqiDate(solarYear, '大寒');
  if (solarMonth < dahanM || (solarMonth === dahanM && solarDay < dahanD)) {
    return solarYear - 1;
  }
  return solarYear;
}

function getCurrentQiStep(dateStr) {
  const yqYear = getYunqiYear(dateStr);
  const parts = dateStr.split('-');
  const dateY = parseInt(parts[0]);
  const dateM = parseInt(parts[1]);
  const dateD = parseInt(parts[2]);
  const dateTuple = [dateY, dateM, dateD];
  
  const jieqiDates = {};
  for (const name of ['大寒','春分','小满','大暑','秋分','小雪']) {
    jieqiDates[name] = getJieqiDate(yqYear, name);
  }
  const nextDahan = getJieqiDate(yqYear + 1, '大寒');
  
  const boundaries = [
    [1, jieqiDates['大寒'], jieqiDates['春分']],
    [2, jieqiDates['春分'], jieqiDates['小满']],
    [3, jieqiDates['小满'], jieqiDates['大暑']],
    [4, jieqiDates['大暑'], jieqiDates['秋分']],
    [5, jieqiDates['秋分'], jieqiDates['小雪']],
    [6, jieqiDates['小雪'], nextDahan],
  ];
  
  for (const [stepNum, start, end] of boundaries) {
    if (cmpDate(dateTuple, start) >= 0 && cmpDate(dateTuple, end) < 0) {
      return { step_number: stepNum, step_name: QI_STEP_NAMES[stepNum], start, end };
    }
  }
  return { step_number: 1, step_name: QI_STEP_NAMES[1], start: jieqiDates['大寒'], end: jieqiDates['春分'] };
}

function cmpDate(a, b) {
  for (let i = 0; i < 3; i++) {
    if (a[i] < b[i]) return -1;
    if (a[i] > b[i]) return 1;
  }
  return 0;
}

function getDayGanzhi(dateStr) {
  const Solar = getSolarClass();
  if (!Solar) return null;
  const parts = dateStr.split('-');
  const solar = Solar.fromYmd(parseInt(parts[0]), parseInt(parts[1]), parseInt(parts[2]));
  return solar.getLunar().getDayInGanZhi();
}

function getKezhujialinDetail(year, stepNum) {
  const zhuqi = ZHUQI_STEPS[stepNum - 1];
  const keqiSteps = getKeqiSixSteps(year);
  const keqiInfo = keqiSteps[stepNum - 1];
  const [relation, shunNi] = kezhujialinRelation(keqiInfo.ke_qi, zhuqi);
  return {
    step_number: stepNum,
    step_name: QI_STEP_NAMES[stepNum],
    zhu_qi: zhuqi,
    ke_qi: keqiInfo.ke_qi,
    relation, shun_ni: shunNi,
    keqi_is_sitian: keqiInfo.is_sitian,
    keqi_is_zaiquan: keqiInfo.is_zaiquan,
  };
}

// ═══════════════════════════════════════════════════════════════
// 导出
// ═══════════════════════════════════════════════════════════════

module.exports = {
  // 数据表
  TIANGAN, DIZHI, TIANGAN_YINYANG, DIZHI_SHENGXIAO, DIZHI_WUXING,
  WUXING, WUXING_SHENG, WUXING_KE,
  TIANGAN_HUAYUN, WUYUN_STEP,
  DIZHI_HUAQI_SITIAN, SITIAN_ZAIQUAN_PAIR, LIUQI_WUXING, LIUQI_YINYANG,
  ZHUQI_STEPS, KEQI_CYCLE,
  SUIYUN_CODE, SUIYUN_EN, LIUQI_PINYIN, QI_STEP_NAMES,
  // 核心函数
  getGanzhi, getSexagenaryIndex, getDayun, isTaiguo,
  getSitian, getZaiquan, getKeqiSixSteps, getZhuqiSixSteps,
  kezhujialinRelation, checkTianfu, checkSuihui, checkPingqi,
  getZhuyunFiveSteps, getKeyunFiveSteps, getSuiyunCode,
  // Step 1 增强
  getJieqiDate, getYunqiYear, getCurrentQiStep, getDayGanzhi, getKezhujialinDetail,
};
