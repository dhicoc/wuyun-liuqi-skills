/**
 * 五运六气推算引擎 — 共享数据表 (JavaScript 版)
 * 对应 Python 版 yunqi_data.py
 * 
 * 依赖: lunar-javascript (npm install lunar-javascript)
 * P2: 核心常量从 yunqi_constants.json 加载，单一数据源
 */

const path = require('path');
const fs = require('fs');
const _constPath = path.join(__dirname, 'yunqi_constants.json');
const _C = JSON.parse(fs.readFileSync(_constPath, 'utf8'));

// ═══════════════════════════════════════════════════════════════
// 天干地支 (来自 JSON)
// ═══════════════════════════════════════════════════════════════

const TIANGAN = _C.TIANGAN;
const DIZHI = _C.DIZHI;
const TIANGAN_YINYANG = _C.TIANGAN_YINYANG;
const DIZHI_SHENGXIAO = _C.DIZHI_SHENGXIAO;
const DIZHI_WUXING = _C.DIZHI_WUXING;

// ═══════════════════════════════════════════════════════════════
// 五行 (来自 JSON)
// ═══════════════════════════════════════════════════════════════

const WUXING = _C.WUXING;
const WUXING_SHENG = _C.WUXING_SHENG;
const WUXING_KE = _C.WUXING_KE;

// ═══════════════════════════════════════════════════════════════
// 天干化五运 (来自 JSON)
// ═══════════════════════════════════════════════════════════════

const TIANGAN_HUAYUN = _C.TIANGAN_HUAYUN;
const WUYUN_STEP = { '木':1, '火':2, '土':3, '金':4, '水':5 };

// ═══════════════════════════════════════════════════════════════
// 六气 (来自 JSON)
// ═══════════════════════════════════════════════════════════════

const DIZHI_HUAQI_SITIAN = _C.DIZHI_HUAQI_SITIAN;
const SITIAN_ZAIQUAN_PAIR = _C.SITIAN_ZAIQUAN_PAIR;
const LIUQI_WUXING = _C.LIUQI_WUXING;
const LIUQI_YINYANG = _C.LIUQI_YINYANG;
const ZHUQI_STEPS = _C.ZHUQI_STEPS;
const KEQI_CYCLE = _C.KEQI_CYCLE;

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
  const [tg] = getGanzhi(year);
  return [TIANGAN_HUAYUN[tg], tg];
}

function isTaiguo(year) {
  const [tg] = getGanzhi(year);
  return TIANGAN_YINYANG[tg] === '阳';
}

function getSitian(year) {
  const [, dz] = getGanzhi(year);
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
  // 天符：大运五行 == 司天五行。依据《素问·六元正纪大论》天符十二年枚举。
  const [dayun] = getDayun(year);
  const sitian = getSitian(year);
  return dayun === LIUQI_WUXING[sitian];
}

// 岁会「运临本辰之位」判定表：大运五行 → 其本气所临地支（本辰）集合
// 木运临卯、火运临午、金运临酉、水运临子、土运临辰戌丑未（四季），共八年。
const DAYUN_BENCHEN = {
  '木': new Set(['卯']),
  '火': new Set(['午']),
  '土': new Set(['辰', '戌', '丑', '未']),
  '金': new Set(['酉']),
  '水': new Set(['子']),
};

function checkSuihui(year) {
  // 岁会是大运五行「临本辰之位」，非「大运五行 == 地支五行」的朴素判等
  // （后者会把寅/巳/申/亥等非本辰支多算进来，误报壬寅/癸巳/庚申/辛亥）。
  const [dayun] = getDayun(year);
  const [, dz] = getGanzhi(year);
  const bench = DAYUN_BENCHEN[dayun];
  return bench ? bench.has(dz) : false;
}

function checkPingqi(year) {
  // 平气判断（与 scripts/lib/yunqi_data.py check_pingqi 保持一致，三段规则）:
  //   规则一   太过被抑:   大运太过 且 司天五行 克 大运五行        → 平气
  //   规则二A  不及同气相助: 大运不及 且 司天五行 == 大运五行       → 平气
  //   规则二B  不及得司天生运: 大运不及 且 司天五行 生 大运五行     → 平气
  // 注: 太过 + 司天同气 属「天符」(同化更盛)，非平气；
  //     不及 + 司天克运 属「不及更衰」，非平气。
  const [dayun] = getDayun(year);
  const sitian = getSitian(year);
  const sitianElem = LIUQI_WUXING[sitian];
  const taiguo = isTaiguo(year);
  if (taiguo && wuxingKe(sitianElem, dayun)) return true;
  if (!taiguo) {
    if (sitianElem === dayun) return true; // 二A：司天同气相助
    if (wuxingSheng(sitianElem, dayun)) return true; // 二B：司天所生
  }
  return false;
}

// ═══════════════════════════════════════════════════════════════
// 运气同化补充：同天符 / 同岁会（中运与在泉同气）
// ═══════════════════════════════════════════════════════════════

function checkTongTianfu(year) {
  const [dayun] = getDayun(year);
  const zaiquan = getZaiquan(year);
  const zaiquanElem = LIUQI_WUXING[zaiquan];
  return isTaiguo(year) && dayun === zaiquanElem;
}

function checkTongSuihui(year) {
  const [dayun] = getDayun(year);
  const zaiquan = getZaiquan(year);
  const zaiquanElem = LIUQI_WUXING[zaiquan];
  return !isTaiguo(year) && dayun === zaiquanElem;
}

// ═══════════════════════════════════════════════════════════════
// 五运齐化兼化
// 太过 -> 齐化：克我者来齐；不及 -> 兼化：克我者来兼
// ═══════════════════════════════════════════════════════════════

// 五行相克反向映射：谁克我
const _WUXING_KEME = {};
for (const [k, v] of Object.entries(WUXING_KE)) { _WUXING_KEME[v] = k; }

function getQihua(year) {
  const [dayun] = getDayun(year);
  if (!isTaiguo(year)) return null;
  return _WUXING_KEME[dayun] || null;
}

function getJianhua(year) {
  const [dayun] = getDayun(year);
  if (isTaiguo(year)) return null;
  return _WUXING_KEME[dayun] || null;
}

// ═══════════════════════════════════════════════════════════════
// 六气正化对化
// ═══════════════════════════════════════════════════════════════

const DIZHI_ZHENGDUI = {
  '午': ['少阴君火', '正化'], '子': ['少阴君火', '对化'],
  '未': ['太阴湿土', '正化'], '丑': ['太阴湿土', '对化'],
  '寅': ['少阳相火', '正化'], '申': ['少阳相火', '对化'],
  '酉': ['阳明燥金', '正化'], '卯': ['阳明燥金', '对化'],
  '辰': ['太阳寒水', '正化'], '戌': ['太阳寒水', '对化'],
  '巳': ['厥阴风木', '正化'], '亥': ['厥阴风木', '对化'],
};

function getZhengduiHuaqi(year) {
  const [, dz] = getGanzhi(year);
  return DIZHI_ZHENGDUI[dz] || [null, null];
}

function getZhuyunFiveSteps(year) {
  const [dayun] = getDayun(year);
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
  const [dayun] = getDayun(year);
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
  const [dayun] = getDayun(year);
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

// 简单内存缓存（对应 Python lru_cache）
const _jieqiCache = new Map();
function getJieqiDate(year, jieqiName) {
  const key = `${year}|${jieqiName}`;
  if (_jieqiCache.has(key)) {
    return _jieqiCache.get(key);
  }

  const Solar = getSolarClass();
  if (!Solar) {
    const [m, d] = JIEQI_FALLBACK[jieqiName] || [1, 20];
    const res = [year, m, d];
    _jieqiCache.set(key, res);
    return res;
  }

  // 大寒在年初: 从前一年7月的 Lunar 表获取
  const solar = Solar.fromYmd(jieqiName === '大寒' ? year - 1 : year, 7, 1);
  const lunar = solar.getLunar();
  const jqTable = lunar.getJieQiTable();
  const jqEn = JIEQI_EN_MAP[jieqiName];
  if (jqEn && jqTable[jqEn]) {
    const val = jqTable[jqEn];
    // JieQiTable 值可能是 Solar 对象或字符串
    let res;
    if (typeof val === 'string') {
      const parts = val.split('-');
      res = [parseInt(parts[0]), parseInt(parts[1]), parseInt(parts[2])];
    } else if (val && val.getYear) {
      // Solar 对象
      res = [val.getYear(), val.getMonth(), val.getDay()];
    }
    if (res) {
      _jieqiCache.set(key, res);
      return res;
    }
  }

  // 兜底: 遍历法（修复：支持到每月最后一天）
  let res = null;
  for (let month = 1; month <= 12 && !res; month++) {
    // 简单每月最多31天
    for (let day = 1; day <= 31; day++) {
      try {
        const s = Solar.fromYmd(year, month, day);
        const l = s.getLunar();
        const jq = l.getJieQi();
        if (jq && jq.includes(jieqiName)) {
          res = [year, month, day];
          break;
        }
      } catch (e) {}
    }
  }
  if (!res) {
    const [m, d] = JIEQI_FALLBACK[jieqiName] || [1, 20];
    res = [year, m, d];
  }
  _jieqiCache.set(key, res);
  return res;
}

function getYunqiYear(dateStr) {
  const parts = dateStr.split('-');
  const solarYear = parseInt(parts[0]);
  const solarMonth = parseInt(parts[1]);
  const solarDay = parseInt(parts[2]);
  const [, dahanM, dahanD] = getJieqiDate(solarYear, '大寒');
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

// 日干支（干支纪日）纯算法，不依赖 lunar-javascript。
// 日干支是连续 60 天一循环的纪日法；以 2000-01-07（甲子，index 0）为锚点，
// 任意日期的日干支 = (锚点序号 + 距锚点天数) mod 60。
// 锚点序号已对照 lunar_python.getDayInGanZhi() 校准（2000-01-07 = 甲子），
// 从而 JS 端在不安装 lunar-javascript 时仍能给出与 Python 真相源一致的日干支。
const _DAY_GZ_ANCHOR = { y: 2000, m: 1, d: 7, idx: 0 };

function _utcDays(y, m, d) {
  // m：1-based；JS Date.UTC 月份 0-based。用 UTC 午夜避免时区/夏令时误差。
  return Math.floor(Date.UTC(y, m - 1, d) / 86400000);
}

function getDayGanzhi(dateStr) {
  const parts = dateStr.split('-');
  const y = parseInt(parts[0], 10);
  const m = parseInt(parts[1], 10);
  const d = parseInt(parts[2], 10);
  const delta = _utcDays(y, m, d) - _utcDays(_DAY_GZ_ANCHOR.y, _DAY_GZ_ANCHOR.m, _DAY_GZ_ANCHOR.d);
  const idx = (((delta + _DAY_GZ_ANCHOR.idx) % 60) + 60) % 60; // 0 = 甲子
  return TIANGAN[idx % 10] + DIZHI[idx % 12];
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
  checkTongTianfu, checkTongSuihui, getQihua, getJianhua, getZhengduiHuaqi,
  getZhuyunFiveSteps, getKeyunFiveSteps, getSuiyunCode,
  // Step 1 增强
  getJieqiDate, getYunqiYear, getCurrentQiStep, getDayGanzhi, getKezhujialinDetail,
};
