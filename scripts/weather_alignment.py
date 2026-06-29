#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气 × 天气实况对齐模块

定位：高级对齐层。先用 calculate_yunqi_api.py 获取宏观运气格局，再获取指定地点天气实况，
将现代气象指标转译为六气倾向，输出“运气趋势 × 天气实况”的内外邪相合判断。

用法：
  python scripts/weather_alignment.py 2026-06-29 --city 杭州
  python scripts/weather_alignment.py 2026-06-29 杭州 --json
  python scripts/weather_alignment.py 2026-06-29 --lat 30.2741 --lon 120.1551 --json
  python scripts/weather_alignment.py 2026-06-29 --city 杭州 --mock --json
  python scripts/weather_alignment.py 2026-06-29 --city 杭州 --provider open-meteo --baseline-years 10 --json

说明：
  - Python 主链路：调用 calculate_yunqi_api.calculate_yunqi_api。
  - 天气 API：默认 auto；优先可用密钥源（QWeather/Seniverse），否则 Open-Meteo；Open-Meteo 无需 API Key。
  - 历史同期均值：默认使用 Open-Meteo Archive 取过去 5 年同日均值，用于判断距平。
  - 缓存：默认启用本地缓存，降低外部 API 频率；可用 --no-cache 关闭。
  - 测试/CI：使用 --mock，避免依赖外网。
"""
import argparse
import hashlib
import json
import math
import os
import sys
import io
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date as date_cls, datetime

if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
CACHE_DIR = os.path.join(BASE_DIR, '.cache', 'weather_alignment')
sys.path.insert(0, SCRIPT_DIR)
from calculate_yunqi_api import calculate_yunqi_api  # noqa: E402

OPEN_METEO_FORECAST_URL = 'https://api.open-meteo.com/v1/forecast'
OPEN_METEO_ARCHIVE_URL = 'https://archive-api.open-meteo.com/v1/archive'
OPEN_METEO_GEOCODE_URL = 'https://geocoding-api.open-meteo.com/v1/search'
QWEATHER_NOW_URL = 'https://devapi.qweather.com/v7/weather/now'
SENIVERSE_NOW_URL = 'https://api.seniverse.com/v3/weather/now.json'

CITY_COORDS = {
    '北京': (39.9042, 116.4074, '北京'), '北京市': (39.9042, 116.4074, '北京'),
    '上海': (31.2304, 121.4737, '上海'), '上海市': (31.2304, 121.4737, '上海'),
    '杭州': (30.2741, 120.1551, '杭州'), '杭州市': (30.2741, 120.1551, '杭州'),
    '广州': (23.1291, 113.2644, '广州'), '广州市': (23.1291, 113.2644, '广州'),
    '深圳': (22.5431, 114.0579, '深圳'), '深圳市': (22.5431, 114.0579, '深圳'),
    '成都': (30.5728, 104.0668, '成都'), '成都市': (30.5728, 104.0668, '成都'),
    '重庆': (29.5630, 106.5516, '重庆'), '重庆市': (29.5630, 106.5516, '重庆'),
    '南京': (32.0603, 118.7969, '南京'), '南京市': (32.0603, 118.7969, '南京'),
    '武汉': (30.5928, 114.3055, '武汉'), '武汉市': (30.5928, 114.3055, '武汉'),
    '西安': (34.3416, 108.9398, '西安'), '西安市': (34.3416, 108.9398, '西安'),
    '天津': (39.3434, 117.3616, '天津'), '天津市': (39.3434, 117.3616, '天津'),
    '苏州': (31.2989, 120.5853, '苏州'), '苏州市': (31.2989, 120.5853, '苏州'),
    '长沙': (28.2282, 112.9388, '长沙'), '长沙市': (28.2282, 112.9388, '长沙'),
    '郑州': (34.7466, 113.6254, '郑州'), '郑州市': (34.7466, 113.6254, '郑州'),
    '青岛': (36.0671, 120.3826, '青岛'), '青岛市': (36.0671, 120.3826, '青岛'),
    '厦门': (24.4798, 118.0894, '厦门'), '厦门市': (24.4798, 118.0894, '厦门'),
    '福州': (26.0745, 119.2965, '福州'), '福州市': (26.0745, 119.2965, '福州'),
    '昆明': (25.0389, 102.7183, '昆明'), '昆明市': (25.0389, 102.7183, '昆明'),
    '哈尔滨': (45.8038, 126.5349, '哈尔滨'), '哈尔滨市': (45.8038, 126.5349, '哈尔滨'),
    '沈阳': (41.8057, 123.4315, '沈阳'), '沈阳市': (41.8057, 123.4315, '沈阳'),
    '长春': (43.8171, 125.3235, '长春'), '长春市': (43.8171, 125.3235, '长春'),
    '乌鲁木齐': (43.8256, 87.6168, '乌鲁木齐'), '乌鲁木齐市': (43.8256, 87.6168, '乌鲁木齐'),
    '拉萨': (29.6520, 91.1721, '拉萨'), '拉萨市': (29.6520, 91.1721, '拉萨'),
    'Hong Kong': (22.3193, 114.1694, '香港'), '香港': (22.3193, 114.1694, '香港'),
    'Macau': (22.1987, 113.5439, '澳门'), '澳门': (22.1987, 113.5439, '澳门'),
    'Taipei': (25.0330, 121.5654, '台北'), '台北': (25.0330, 121.5654, '台北'),
}

LIUQI_ATTRS = {
    '厥阴风木': {'风'},
    '少阴君火': {'火热'},
    '少阳相火': {'火热'},
    '太阴湿土': {'湿'},
    '阳明燥金': {'燥'},
    '太阳寒水': {'寒'},
}

SUIYUN_ATTRS = {
    '木': {'风'},
    '火': {'火热'},
    '土': {'湿'},
    '金': {'燥'},
    '水': {'寒'},
}

OPPOSITES = [({'寒'}, {'火热', '暑热'}), ({'湿'}, {'燥'})]

DISCLAIMER = (
    '⚠️ 免责声明：以上分析基于中医运气学说与实时气象数据的理论对齐，'
    '仅供参考。运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。'
    '请勿据此自行用药或针灸。'
)


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError as exc:
        raise ValueError(f'日期格式必须为 YYYY-MM-DD，当前: {date_str}') from exc


def round_float(value, digits=2):
    if value is None:
        return None
    try:
        if math.isnan(value):
            return None
    except TypeError:
        pass
    return round(float(value), digits)


def as_float(value):
    if value in (None, ''):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def cache_path(url, params):
    normalized = json.dumps({'url': url, 'params': params}, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    return os.path.join(CACHE_DIR, f'{digest}.json')


def read_cache(path, ttl_minutes):
    if ttl_minutes is None or ttl_minutes <= 0 or not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        fetched_at = payload.get('_cache', {}).get('fetched_at')
        if not fetched_at:
            return None
        age_seconds = time.time() - float(fetched_at)
        if age_seconds <= ttl_minutes * 60:
            data = payload.get('data')
            if isinstance(data, dict):
                data.setdefault('_cache_hit', True)
            return data
    except Exception:
        return None
    return None


def write_cache(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        payload = {'_cache': {'fetched_at': time.time()}, 'data': data}
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False)
    except Exception:
        pass


def http_get_json(url, params, timeout=10, retries=2, cache_ttl=60, no_cache=False):
    query = urllib.parse.urlencode(params, doseq=True)
    full_url = f'{url}?{query}'
    path = cache_path(url, params)
    if not no_cache:
        cached = read_cache(path, cache_ttl)
        if cached is not None:
            return cached

    last_error = None
    headers = {'User-Agent': 'wuyun-liuqi-skills/1.0 weather-alignment'}
    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                charset = response.headers.get_content_charset() or 'utf-8'
                data = json.loads(response.read().decode(charset))
                if not no_cache:
                    write_cache(path, data)
                return data
        except Exception as exc:  # 网络波动或 API 错误均降级处理
            last_error = exc
            if attempt < retries:
                time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f'天气 API 请求失败: {last_error}')


def resolve_location(city=None, lat=None, lon=None, timeout=10, cache_ttl=1440, no_cache=False):
    if lat is not None and lon is not None:
        return {
            'name': city or f'{lat},{lon}',
            'latitude': float(lat),
            'longitude': float(lon),
            'source': 'cli_coordinates',
        }

    if not city:
        raise ValueError('请提供 --city 城市名，或同时提供 --lat 与 --lon。')

    city = city.strip()
    if city in CITY_COORDS:
        c_lat, c_lon, canonical = CITY_COORDS[city]
        return {'name': canonical, 'latitude': c_lat, 'longitude': c_lon, 'source': 'built_in_city_table'}

    params = {'name': city, 'count': 1, 'language': 'zh', 'format': 'json'}
    data = http_get_json(OPEN_METEO_GEOCODE_URL, params, timeout=timeout, retries=1, cache_ttl=cache_ttl, no_cache=no_cache)
    results = data.get('results') or []
    if not results:
        raise ValueError(f'无法解析城市坐标: {city}。请改用 --lat / --lon。')
    item = results[0]
    name = item.get('name') or city
    country = item.get('country')
    admin1 = item.get('admin1')
    label_parts = [p for p in [name, admin1, country] if p]
    return {
        'name': ' / '.join(label_parts),
        'latitude': float(item['latitude']),
        'longitude': float(item['longitude']),
        'source': 'open_meteo_geocoding',
    }


def mock_weather(date_str, location):
    # 稳定测试数据：夏季高温高湿，适合验证“湿热/暑湿”判断。
    return {
        'status': 'ok',
        'source': 'mock',
        'date': date_str,
        'temperature_2m': 31.2,
        'relative_humidity_2m': 78,
        'precipitation': 0.0,
        'wind_speed_10m': 9.5,
        'weather_code': 1,
        'is_current': False,
        'raw_summary': 'mock: warm-humid summer weather',
    }


def mock_climatology(date_str, location, years=5):
    return {
        'status': 'ok',
        'source': 'mock-baseline',
        'baseline_years': years,
        'sample_count': years,
        'dates': [f'mock-year-{i + 1}' for i in range(years)],
        'temperature_2m_mean': 28.0,
        'relative_humidity_2m_mean': 72.0,
        'precipitation_mean': 0.5,
        'wind_speed_10m_mean': 8.0,
        'anomalies': {},
    }


def mean(values):
    values = [float(v) for v in values if v is not None]
    return sum(values) / len(values) if values else None


def mode(values):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]


def fetch_open_meteo_weather(date_str, location, timeout=10, cache_ttl=60, no_cache=False):
    target_date = parse_date(date_str)
    today = date_cls.today()
    lat = location['latitude']
    lon = location['longitude']

    if target_date == today:
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
            'timezone': 'auto',
        }
        data = http_get_json(OPEN_METEO_FORECAST_URL, params, timeout=timeout, retries=2, cache_ttl=cache_ttl, no_cache=no_cache)
        current = data.get('current') or {}
        return {
            'status': 'ok',
            'source': 'open-meteo-current',
            'date': date_str,
            'temperature_2m': round_float(current.get('temperature_2m')),
            'relative_humidity_2m': round_float(current.get('relative_humidity_2m')),
            'precipitation': round_float(current.get('precipitation')),
            'wind_speed_10m': round_float(current.get('wind_speed_10m')),
            'weather_code': current.get('weather_code'),
            'is_current': True,
            'raw_summary': current.get('time'),
            'cache_hit': bool(data.get('_cache_hit')),
        }

    url = OPEN_METEO_ARCHIVE_URL if target_date < today else OPEN_METEO_FORECAST_URL
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': date_str,
        'end_date': date_str,
        'hourly': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
        'timezone': 'auto',
    }
    data = http_get_json(url, params, timeout=timeout, retries=2, cache_ttl=cache_ttl, no_cache=no_cache)
    hourly = data.get('hourly') or {}
    precipitation_values = [float(v) for v in hourly.get('precipitation', []) if v is not None]
    wind_values = [float(v) for v in hourly.get('wind_speed_10m', []) if v is not None]
    return {
        'status': 'ok',
        'source': 'open-meteo-archive' if target_date < today else 'open-meteo-forecast',
        'date': date_str,
        'temperature_2m': round_float(mean(hourly.get('temperature_2m', []))),
        'relative_humidity_2m': round_float(mean(hourly.get('relative_humidity_2m', []))),
        'precipitation': round_float(sum(precipitation_values) if precipitation_values else 0.0),
        'wind_speed_10m': round_float(max(wind_values) if wind_values else None),
        'weather_code': mode(hourly.get('weather_code', [])),
        'is_current': False,
        'raw_summary': f'{len(hourly.get("time", []))} hourly records',
        'cache_hit': bool(data.get('_cache_hit')),
    }


def fetch_qweather_now(date_str, location, timeout=10, cache_ttl=60, no_cache=False):
    if parse_date(date_str) != date_cls.today():
        raise RuntimeError('QWeather 当前实现仅支持今日实时天气；历史/未来日期请使用 Open-Meteo。')
    key = os.environ.get('QWEATHER_API_KEY') or os.environ.get('WEATHER_API_KEY')
    if not key:
        raise RuntimeError('缺少 QWEATHER_API_KEY 或 WEATHER_API_KEY。')
    params = {
        'location': f'{location["longitude"]},{location["latitude"]}',
        'key': key,
        'lang': 'zh',
        'unit': 'm',
    }
    data = http_get_json(QWEATHER_NOW_URL, params, timeout=timeout, retries=2, cache_ttl=cache_ttl, no_cache=no_cache)
    if str(data.get('code')) != '200':
        raise RuntimeError(f'QWeather 返回异常: {data.get("code")}')
    now = data.get('now') or {}
    return {
        'status': 'ok',
        'source': 'qweather-current',
        'date': date_str,
        'temperature_2m': round_float(as_float(now.get('temp'))),
        'relative_humidity_2m': round_float(as_float(now.get('humidity'))),
        'precipitation': round_float(as_float(now.get('precip'))),
        'wind_speed_10m': round_float(as_float(now.get('windSpeed'))),
        'weather_code': now.get('icon'),
        'weather_text': now.get('text'),
        'is_current': True,
        'raw_summary': now.get('obsTime'),
        'cache_hit': bool(data.get('_cache_hit')),
    }


def fetch_seniverse_now(date_str, location, timeout=10, cache_ttl=60, no_cache=False):
    if parse_date(date_str) != date_cls.today():
        raise RuntimeError('Seniverse 当前实现仅支持今日实时天气；历史/未来日期请使用 Open-Meteo。')
    key = os.environ.get('SENIVERSE_API_KEY')
    if not key:
        raise RuntimeError('缺少 SENIVERSE_API_KEY。')
    params = {
        'key': key,
        'location': f'{location["latitude"]}:{location["longitude"]}',
        'language': 'zh-Hans',
        'unit': 'c',
    }
    data = http_get_json(SENIVERSE_NOW_URL, params, timeout=timeout, retries=2, cache_ttl=cache_ttl, no_cache=no_cache)
    results = data.get('results') or []
    if not results:
        raise RuntimeError('Seniverse 返回结果为空。')
    now = (results[0].get('now') or {})
    return {
        'status': 'ok',
        'source': 'seniverse-current',
        'date': date_str,
        'temperature_2m': round_float(as_float(now.get('temperature'))),
        'relative_humidity_2m': round_float(as_float(now.get('humidity'))),
        'precipitation': None,
        'wind_speed_10m': round_float(as_float(now.get('wind_speed'))),
        'weather_code': now.get('code'),
        'weather_text': now.get('text'),
        'is_current': True,
        'raw_summary': results[0].get('last_update'),
        'cache_hit': bool(data.get('_cache_hit')),
    }


def fetch_weather(date_str, location, mock=False, timeout=10, strict=False, provider='auto', cache_ttl=60, no_cache=False):
    if mock or provider == 'mock':
        return mock_weather(date_str, location)

    provider = provider or 'auto'
    errors = []
    try_order = []
    today = parse_date(date_str) == date_cls.today()

    if provider == 'auto':
        if today and (os.environ.get('QWEATHER_API_KEY') or os.environ.get('WEATHER_API_KEY')):
            try_order.append('qweather')
        if today and os.environ.get('SENIVERSE_API_KEY'):
            try_order.append('seniverse')
        try_order.append('open-meteo')
    else:
        try_order = [provider]

    for item in try_order:
        try:
            if item == 'open-meteo':
                return fetch_open_meteo_weather(date_str, location, timeout=timeout, cache_ttl=cache_ttl, no_cache=no_cache)
            if item == 'qweather':
                return fetch_qweather_now(date_str, location, timeout=timeout, cache_ttl=cache_ttl, no_cache=no_cache)
            if item == 'seniverse':
                return fetch_seniverse_now(date_str, location, timeout=timeout, cache_ttl=cache_ttl, no_cache=no_cache)
            raise RuntimeError(f'不支持的天气源: {item}')
        except Exception as exc:
            errors.append(f'{item}: {exc}')
            if strict or provider != 'auto':
                if strict:
                    raise
                break

    return {
        'status': 'unavailable',
        'source': provider,
        'date': date_str,
        'error': '; '.join(errors) or 'unknown error',
        'temperature_2m': None,
        'relative_humidity_2m': None,
        'precipitation': None,
        'wind_speed_10m': None,
        'weather_code': None,
        'is_current': False,
    }


def date_with_year(base_date, year):
    try:
        return base_date.replace(year=year)
    except ValueError:
        # 2 月 29 日回退到 2 月 28 日
        return base_date.replace(year=year, day=28)


def fetch_climatology(date_str, location, years=5, mock=False, timeout=10, no_cache=False):
    years = int(years or 0)
    if years <= 0:
        return {'status': 'disabled', 'source': 'none', 'baseline_years': 0, 'sample_count': 0, 'anomalies': {}}
    if mock:
        return mock_climatology(date_str, location, years=years)

    target = parse_date(date_str)
    records = []
    errors = []
    for offset in range(1, years + 1):
        hist_date = date_with_year(target, target.year - offset).isoformat()
        try:
            rec = fetch_open_meteo_weather(hist_date, location, timeout=timeout, cache_ttl=7 * 24 * 60, no_cache=no_cache)
            if rec.get('status') == 'ok':
                records.append(rec)
        except Exception as exc:
            errors.append(f'{hist_date}: {exc}')

    if not records:
        return {
            'status': 'unavailable',
            'source': 'open-meteo-archive-baseline',
            'baseline_years': years,
            'sample_count': 0,
            'dates': [],
            'error': '; '.join(errors) or 'no baseline records',
            'anomalies': {},
        }

    return {
        'status': 'ok' if len(records) == years else 'partial',
        'source': 'open-meteo-archive-baseline',
        'baseline_years': years,
        'sample_count': len(records),
        'dates': [r['date'] for r in records],
        'temperature_2m_mean': round_float(mean([r.get('temperature_2m') for r in records])),
        'relative_humidity_2m_mean': round_float(mean([r.get('relative_humidity_2m') for r in records])),
        'precipitation_mean': round_float(mean([r.get('precipitation') for r in records])),
        'wind_speed_10m_mean': round_float(mean([r.get('wind_speed_10m') for r in records])),
        'errors': errors,
        'anomalies': {},
    }


def add_climatology_anomalies(weather, climatology):
    if not climatology or climatology.get('status') not in ('ok', 'partial') or weather.get('status') != 'ok':
        if climatology is not None:
            climatology['anomalies'] = {}
        return climatology

    anomalies = {}
    mappings = [
        ('temperature_2m', 'temperature_2m_mean', 'temperature_2m_anomaly'),
        ('relative_humidity_2m', 'relative_humidity_2m_mean', 'relative_humidity_2m_anomaly'),
        ('precipitation', 'precipitation_mean', 'precipitation_anomaly'),
        ('wind_speed_10m', 'wind_speed_10m_mean', 'wind_speed_10m_anomaly'),
    ]
    for cur_key, base_key, out_key in mappings:
        cur = weather.get(cur_key)
        base = climatology.get(base_key)
        if cur is not None and base is not None:
            anomalies[out_key] = round_float(float(cur) - float(base))
    if weather.get('precipitation') is not None and climatology.get('precipitation_mean') not in (None, 0):
        anomalies['precipitation_ratio'] = round_float(float(weather['precipitation']) / float(climatology['precipitation_mean']))
    climatology['anomalies'] = anomalies
    return climatology


def infer_weather_qi(weather, climatology=None):
    if weather.get('status') != 'ok':
        return {
            'pattern': '未取得实况',
            'qi': [],
            'evidence': ['天气 API 不可用，已回退至纯运气推算'],
            'confidence': 'none',
            'score': 0,
        }

    temp = weather.get('temperature_2m')
    humidity = weather.get('relative_humidity_2m')
    precip = weather.get('precipitation') or 0
    wind = weather.get('wind_speed_10m')
    anomalies = (climatology or {}).get('anomalies') or {}

    qi = []
    evidence = []

    if temp is not None:
        if temp >= 35:
            qi.append('暑热')
            evidence.append(f'气温显著偏热：{temp}℃ ≥ 35℃')
        elif temp >= 30:
            qi.append('火热')
            evidence.append(f'气温偏高：{temp}℃ ≥ 30℃')
        elif temp <= 8:
            qi.append('寒')
            evidence.append(f'气温偏低：{temp}℃ ≤ 8℃')

    temp_anomaly = anomalies.get('temperature_2m_anomaly')
    if temp_anomaly is not None:
        if temp_anomaly >= 3:
            qi.append('暑热')
            evidence.append(f'较历史同期明显偏热：+{temp_anomaly}℃')
        elif temp_anomaly >= 2:
            qi.append('火热')
            evidence.append(f'较历史同期偏热：+{temp_anomaly}℃')
        elif temp_anomaly <= -2:
            qi.append('寒')
            evidence.append(f'较历史同期偏冷：{temp_anomaly}℃')

    if humidity is not None:
        if humidity >= 75:
            qi.append('湿')
            evidence.append(f'湿度偏高：{humidity}% ≥ 75%')
        elif humidity <= 35:
            qi.append('燥')
            evidence.append(f'湿度偏低：{humidity}% ≤ 35%')

    humidity_anomaly = anomalies.get('relative_humidity_2m_anomaly')
    if humidity_anomaly is not None:
        if humidity_anomaly >= 10:
            qi.append('湿')
            evidence.append(f'较历史同期偏湿：+{humidity_anomaly}%')
        elif humidity_anomaly <= -10:
            qi.append('燥')
            evidence.append(f'较历史同期偏燥：{humidity_anomaly}%')

    precip_ratio = anomalies.get('precipitation_ratio')
    if precip is not None and precip > 0.2:
        qi.append('湿')
        evidence.append(f'有降水或降水累积：{precip} mm')
    if precip_ratio is not None and precip_ratio >= 2 and precip > 1:
        qi.append('湿')
        evidence.append(f'降水为历史同期约 {precip_ratio} 倍')

    if wind is not None and wind >= 20:
        qi.append('风')
        evidence.append(f'风速偏大：{wind} km/h ≥ 20 km/h')
    wind_anomaly = anomalies.get('wind_speed_10m_anomaly')
    if wind_anomaly is not None and wind_anomaly >= 8:
        qi.append('风')
        evidence.append(f'较历史同期风速偏大：+{wind_anomaly} km/h')

    qi_set = set(qi)
    if {'火热', '湿'} <= qi_set or {'暑热', '湿'} <= qi_set:
        pattern = '湿热' if '火热' in qi_set else '暑湿'
    elif {'寒', '湿'} <= qi_set:
        pattern = '寒湿'
    elif ({'火热', '燥'} <= qi_set) or ({'暑热', '燥'} <= qi_set):
        pattern = '燥热'
    elif {'寒', '风'} <= qi_set:
        pattern = '风寒'
    elif {'风', '湿'} <= qi_set:
        pattern = '风湿'
    elif {'风', '火热'} <= qi_set or {'风', '暑热'} <= qi_set:
        pattern = '风热'
    elif qi:
        pattern = '兼'.join(sorted(qi_set))
    else:
        pattern = '平和'
        evidence.append('温度、湿度、风速、降水及历史同期距平均未见明显偏盛阈值')

    score = len(qi_set)
    if pattern in ('湿热', '暑湿', '寒湿', '燥热', '风寒', '风湿', '风热'):
        score += 1
    if anomalies:
        score += 1
    confidence = 'high' if score >= 3 else ('medium' if score >= 1 else 'low')
    return {
        'pattern': pattern,
        'qi': sorted(qi_set),
        'evidence': evidence,
        'confidence': confidence,
        'score': score,
    }


def attrs_for_liuqi(qi_name):
    return set(LIUQI_ATTRS.get(qi_name, set()))


def extract_yunqi_tendency(yunqi):
    current = yunqi['current_step']
    half_dominant = yunqi['si_tian'] if current['step_number'] <= 3 else yunqi['zai_quan']
    suiyun = yunqi['sui_yun']
    suiyun_attrs = set(SUIYUN_ATTRS.get(suiyun['element'], set()))
    if suiyun['status'] != '太过':
        suiyun_strength = 'weak_deficient'
    else:
        suiyun_strength = 'strong_excess'

    immediate_attrs = attrs_for_liuqi(current['ke_qi']) | attrs_for_liuqi(current['zhu_qi'])
    half_attrs = attrs_for_liuqi(half_dominant)
    weighted_attrs = list(immediate_attrs | half_attrs | suiyun_attrs)
    return {
        'year_gz': yunqi['year_gz'],
        'sui_yun': yunqi['sui_yun'],
        'si_tian': yunqi['si_tian'],
        'zai_quan': yunqi['zai_quan'],
        'current_step': current,
        'dominant_half_qi': half_dominant,
        'immediate_attrs': sorted(immediate_attrs),
        'half_attrs': sorted(half_attrs),
        'suiyun_attrs': sorted(suiyun_attrs),
        'suiyun_strength': suiyun_strength,
        'combined_attrs': sorted(set(weighted_attrs)),
        'rag_keys': yunqi['rag_keys'],
    }


def has_opposition(a, b):
    a = set(a)
    b = set(b)
    for left, right in OPPOSITES:
        if (a & left and b & right) or (a & right and b & left):
            return True
    return False


def align_yunqi_weather(tendency, weather_qi):
    weather_attrs = set(weather_qi.get('qi', []))
    if '暑热' in weather_attrs:
        weather_attrs.add('火热')
    immediate_attrs = set(tendency['immediate_attrs'])
    half_attrs = set(tendency['half_attrs'])
    suiyun_attrs = set(tendency['suiyun_attrs'])
    predicted_attrs = immediate_attrs | half_attrs | suiyun_attrs

    if not weather_attrs:
        return {
            'type': 'fallback' if weather_qi.get('confidence') == 'none' else 'neutral',
            'label': '未对齐' if weather_qi.get('confidence') == 'none' else '中性',
            'severity': 'baseline',
            'weight': 1.0,
            'matched_attrs': [],
            'opposed': False,
            'summary': '未取得可靠天气实况，当前仅保留五运六气理论推算作为参考。' if weather_qi.get('confidence') == 'none' else '天气实况未见明显六气偏盛，运气趋势按基础权重参考。',
            'care_principle': '顺时调摄，平调阴阳。',
        }

    matched = weather_attrs & predicted_attrs
    immediate_match = bool(weather_attrs & immediate_attrs)
    half_match = bool(weather_attrs & half_attrs)
    year_match = bool(weather_attrs & suiyun_attrs and tendency['suiyun_strength'] == 'strong_excess')
    opposed = has_opposition(weather_attrs, predicted_attrs)

    if matched and (immediate_match or half_match or year_match):
        if len(weather_attrs - predicted_attrs) > 0:
            typ = 'mixed'
            label = '兼夹相合'
            severity = 'moderate'
            weight = 1.25
            summary = '天气实况与部分运气趋势同向，但另有其他气象偏性并见，宜按“兼夹”处理。'
        else:
            typ = 'amplified' if weather_qi.get('score', 0) >= 2 else 'aligned'
            label = '内外相合' if typ == 'aligned' else '内外相合偏盛'
            severity = 'high' if typ == 'amplified' else 'moderate'
            weight = 1.5 if typ == 'amplified' else 1.25
            summary = '天气实况与运气推算方向一致，提示运邪与时邪相合，对应病机权重上调。'
    elif opposed:
        typ = 'opposed'
        label = '实况相背'
        severity = 'variable'
        weight = 0.65
        summary = '天气实况与运气推算存在相背之处，运气趋势不归零，但调摄需优先参考当下实况。'
    else:
        typ = 'weather_dominant'
        label = '实况主导'
        severity = 'moderate'
        weight = 1.0
        summary = '天气实况有明显偏性，但与当前运气主导气不完全同向，建议以实况为主、运气为辅。'

    care_principle = care_principle_for_weather(weather_attrs, typ)
    return {
        'type': typ,
        'label': label,
        'severity': severity,
        'weight': weight,
        'matched_attrs': sorted(matched),
        'opposed': opposed,
        'summary': summary,
        'care_principle': care_principle,
    }


def care_principle_for_weather(attrs, alignment_type):
    attrs = set(attrs)
    if '暑热' in attrs:
        attrs.add('火热')
    if {'火热', '湿'} <= attrs:
        return '清暑化湿，护阳不伤正；少冰饮，避湿热郁蒸。'
    if {'寒', '湿'} <= attrs:
        return '温阳散寒，兼顾化湿；避寒潮湿，护腰腹足部。'
    if {'火热', '燥'} <= attrs:
        return '清润养阴，防燥热伤津；少辛辣燥烈。'
    if {'寒', '风'} <= attrs:
        return '防风散寒，注意头颈背部保暖。'
    if '风' in attrs:
        return '防风护表，舒展筋脉，避免汗出当风。'
    if '寒' in attrs:
        return '温阳避寒，少食生冷，注意腰腹与足部保暖。'
    if '湿' in attrs:
        return '健脾化湿，饮食清淡，居处通风防潮。'
    if '燥' in attrs:
        return '润燥生津，护肺润肤，少食辛燥。'
    if '火热' in attrs:
        return '清热养阴，避免熬夜、辛辣与过劳。'
    return '顺时调摄，平衡作息饮食。'


def generate_result(date_str, location, weather, climatology=None, as_mock=False, provider='auto', cache_enabled=True, cache_ttl=60):
    yunqi = calculate_yunqi_api(date_str)
    climatology = add_climatology_anomalies(weather, climatology)
    tendency = extract_yunqi_tendency(yunqi)
    weather_qi = infer_weather_qi(weather, climatology=climatology)
    alignment = align_yunqi_weather(tendency, weather_qi)
    return {
        'date': date_str,
        'location': location,
        'yunqi': tendency,
        'weather': weather,
        'climatology': climatology,
        'weather_qi': weather_qi,
        'alignment': alignment,
        'provider': provider,
        'mock': bool(as_mock),
        'cache': {
            'enabled': bool(cache_enabled),
            'directory': CACHE_DIR if cache_enabled else None,
            'ttl_minutes': cache_ttl,
        },
        'disclaimer': DISCLAIMER,
    }


def format_markdown(result):
    loc = result['location']
    yq = result['yunqi']
    weather = result['weather']
    climatology = result.get('climatology') or {}
    wq = result['weather_qi']
    al = result['alignment']
    current = yq['current_step']

    lines = [
        '# 五运六气 × 天气对齐报告',
        '',
        '## 基本信息',
        f"- 日期：{result['date']}",
        f"- 地点：{loc['name']}（{loc['latitude']:.4f}, {loc['longitude']:.4f}；来源：{loc['source']}）",
        f"- 天气源：{result['provider']}；缓存：{'启用' if result['cache']['enabled'] else '关闭'}",
        f"- 运气年：{yq['year_gz']}",
        f"- 岁运：{yq['sui_yun']['name']}{yq['sui_yun']['status']}",
        f"- 司天 / 在泉：{yq['si_tian']} / {yq['zai_quan']}",
        f"- 当前步位：{current['name']}；主气 {current['zhu_qi']}，客气 {current['ke_qi']}（{current['shun_ni']}）",
        '',
        '## 天气实况',
    ]
    if weather.get('status') == 'ok':
        lines.extend([
            f"- 数据来源：{weather['source']}{'（缓存命中）' if weather.get('cache_hit') else ''}",
            f"- 气温：{weather.get('temperature_2m')}℃",
            f"- 相对湿度：{weather.get('relative_humidity_2m')}%",
            f"- 降水：{weather.get('precipitation')} mm",
            f"- 风速：{weather.get('wind_speed_10m')} km/h",
            f"- 天气代码：{weather.get('weather_code')}",
        ])
    else:
        lines.append(f"- 天气 API 不可用：{weather.get('error', 'unknown error')}")

    if climatology.get('status') in ('ok', 'partial'):
        anomalies = climatology.get('anomalies') or {}
        lines.extend([
            '',
            '## 历史同期均值',
            f"- 基线来源：{climatology.get('source')}；样本：{climatology.get('sample_count')}/{climatology.get('baseline_years')} 年",
            f"- 同期均温：{climatology.get('temperature_2m_mean')}℃；距平：{anomalies.get('temperature_2m_anomaly')}",
            f"- 同期湿度：{climatology.get('relative_humidity_2m_mean')}%；距平：{anomalies.get('relative_humidity_2m_anomaly')}",
            f"- 同期降水：{climatology.get('precipitation_mean')} mm；距平：{anomalies.get('precipitation_anomaly')}",
            f"- 同期风速：{climatology.get('wind_speed_10m_mean')} km/h；距平：{anomalies.get('wind_speed_10m_anomaly')}",
        ])
    elif climatology.get('status') == 'unavailable':
        lines.extend(['', '## 历史同期均值', f"- 暂不可用：{climatology.get('error', 'unknown error')}"])

    lines.extend([
        '',
        '## 气象六气转译',
        f"- 实况六气倾向：{wq['pattern']}",
        f"- 六气要素：{', '.join(wq['qi']) if wq['qi'] else '无明显偏盛'}",
        f"- 置信度：{wq['confidence']}",
    ])
    for item in wq['evidence']:
        lines.append(f"  - {item}")

    lines.extend([
        '',
        '## 对齐判断',
        f"- 对齐类型：{al['label']}（{al['type']}）",
        f"- 病机权重：{al['weight']}",
        f"- 判断摘要：{al['summary']}",
        f"- 调摄原则：{al['care_principle']}",
        '',
        '## 使用提示',
        '- 天气实况用于校正“当下此地”的气候偏性，不替代五运六气宏观推算。',
        '- 历史同期均值用于判断距平，不等同于长期气候学严格常年值；样本年数越多越稳定。',
        '- 若实况与运气相背，养生调理宜先顺应当下天气，再兼顾年度运气底色。',
        '',
        result['disclaimer'],
    ])
    return '\n'.join(lines)


def build_arg_parser():
    parser = argparse.ArgumentParser(description='五运六气 × 天气实况对齐模块')
    parser.add_argument('date', help='日期，格式 YYYY-MM-DD')
    parser.add_argument('location', nargs='?', help='城市名（可选，也可用 --city）')
    parser.add_argument('--city', help='城市名，如 杭州、北京、上海')
    parser.add_argument('--lat', type=float, help='纬度')
    parser.add_argument('--lon', type=float, help='经度')
    parser.add_argument('--provider', choices=['auto', 'open-meteo', 'qweather', 'seniverse', 'mock'], default='auto', help='天气源，默认 auto')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    parser.add_argument('--summary', action='store_true', help='输出 Markdown 摘要（默认）')
    parser.add_argument('--mock', action='store_true', help='使用固定 mock 天气数据，适合测试/CI')
    parser.add_argument('--baseline-years', type=int, default=5, help='历史同期均值年数，默认 5；设为 0 可关闭')
    parser.add_argument('--no-baseline', action='store_true', help='关闭历史同期均值')
    parser.add_argument('--cache-ttl', type=int, default=60, help='天气 API 缓存分钟数，默认 60')
    parser.add_argument('--no-cache', action='store_true', help='关闭本地缓存')
    parser.add_argument('--strict', action='store_true', help='天气 API 失败时直接报错退出')
    parser.add_argument('--timeout', type=int, default=10, help='天气 API 超时时间（秒），默认 10')
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        parse_date(args.date)
        city = args.city or args.location
        use_mock = args.mock or args.provider == 'mock'
        if use_mock and not city and (args.lat is None or args.lon is None):
            city = '杭州'
        location = resolve_location(city=city, lat=args.lat, lon=args.lon, timeout=args.timeout, cache_ttl=24 * 60, no_cache=args.no_cache)
        weather = fetch_weather(
            args.date,
            location,
            mock=use_mock,
            timeout=args.timeout,
            strict=args.strict,
            provider=args.provider,
            cache_ttl=args.cache_ttl,
            no_cache=args.no_cache,
        )
        baseline_years = 0 if args.no_baseline else args.baseline_years
        climatology = fetch_climatology(
            args.date,
            location,
            years=baseline_years,
            mock=use_mock,
            timeout=args.timeout,
            no_cache=args.no_cache,
        )
        result = generate_result(
            args.date,
            location,
            weather,
            climatology=climatology,
            as_mock=use_mock,
            provider=args.provider,
            cache_enabled=not args.no_cache,
            cache_ttl=args.cache_ttl,
        )
        if args.json:
            sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        else:
            sys.stdout.write(format_markdown(result) + '\n')
    except Exception as exc:
        sys.stderr.write(f'❌ 天气对齐失败：{exc}\n')
        sys.exit(1)


if __name__ == '__main__':
    main()
