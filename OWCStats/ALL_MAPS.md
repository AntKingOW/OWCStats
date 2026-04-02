# Overwatch Map Catalog

## Purpose

This file stores the broader Overwatch map catalog separately from the current OWCS tournament map pool.

This lets OWCStats track:

- all known maps
- each map's mode category
- English name
- Korean name
- whether the map is active in the current OWCS Korea 2026 Stage 1 map pool

## Source Rule

- The overall map list is based on the screenshots provided during review.
- The tournament-active map pool is based on the Liquipedia map pool screenshot already reviewed.
- Korean names are recorded when provided in the supplied screenshots.

## Structured Catalog

```json
[
  {
    "map_name_en": "Antarctic Peninsula",
    "map_name_ko": "남극 반도",
    "map_mode_en": "Control",
    "map_mode_ko": "쟁탈",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Busan",
    "map_name_ko": "부산",
    "map_mode_en": "Control",
    "map_mode_ko": "쟁탈",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Ilios",
    "map_name_ko": "일리오스",
    "map_mode_en": "Control",
    "map_mode_ko": "쟁탈",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Lijiang Tower",
    "map_name_ko": "리장 타워",
    "map_mode_en": "Control",
    "map_mode_ko": "쟁탈",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Nepal",
    "map_name_ko": "네팔",
    "map_mode_en": "Control",
    "map_mode_ko": "쟁탈",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Oasis",
    "map_name_ko": "오아시스",
    "map_mode_en": "Control",
    "map_mode_ko": "쟁탈",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Samoa",
    "map_name_ko": "사모아",
    "map_mode_en": "Control",
    "map_mode_ko": "쟁탈",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Blizzard World",
    "map_name_ko": "블리자드 월드",
    "map_mode_en": "Hybrid",
    "map_mode_ko": "혼합",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Eichenwalde",
    "map_name_ko": "아이헨발데",
    "map_mode_en": "Hybrid",
    "map_mode_ko": "혼합",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Hollywood",
    "map_name_ko": "할리우드",
    "map_mode_en": "Hybrid",
    "map_mode_ko": "혼합",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "King's Row",
    "map_name_ko": "왕의 길",
    "map_mode_en": "Hybrid",
    "map_mode_ko": "혼합",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Midtown",
    "map_name_ko": "미드타운",
    "map_mode_en": "Hybrid",
    "map_mode_ko": "혼합",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Numbani",
    "map_name_ko": "눔바니",
    "map_mode_en": "Hybrid",
    "map_mode_ko": "혼합",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Paraíso",
    "map_name_ko": "파라이수",
    "map_mode_en": "Hybrid",
    "map_mode_ko": "혼합",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Aatlis",
    "map_name_ko": "아틀리스",
    "map_mode_en": "Flashpoint",
    "map_mode_ko": "플래시포인트",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "New Junk City",
    "map_name_ko": "뉴 정크 시티",
    "map_mode_en": "Flashpoint",
    "map_mode_ko": "플래시포인트",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Suravasa",
    "map_name_ko": "수라바사",
    "map_mode_en": "Flashpoint",
    "map_mode_ko": "플래시포인트",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Colosseo",
    "map_name_ko": "콜로세오",
    "map_mode_en": "Push",
    "map_mode_ko": "밀기",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Esperanca",
    "map_name_ko": "이스페란사",
    "map_mode_en": "Push",
    "map_mode_ko": "밀기",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "New Queen Street",
    "map_name_ko": "뉴 퀸 스트리트",
    "map_mode_en": "Push",
    "map_mode_ko": "밀기",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Runasapi",
    "map_name_ko": "루나사피",
    "map_mode_en": "Push",
    "map_mode_ko": "밀기",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Circuit Royal",
    "map_name_ko": "서킷 로얄",
    "map_mode_en": "Escort",
    "map_mode_ko": "호위",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Dorado",
    "map_name_ko": "도라도",
    "map_mode_en": "Escort",
    "map_mode_ko": "호위",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Havana",
    "map_name_ko": "하바나",
    "map_mode_en": "Escort",
    "map_mode_ko": "호위",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Junkertown",
    "map_name_ko": "66번 국도",
    "map_mode_en": "Escort",
    "map_mode_ko": "호위",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Rialto",
    "map_name_ko": "리알토",
    "map_mode_en": "Escort",
    "map_mode_ko": "호위",
    "in_owcs_korea_2026_stage1_pool": true
  },
  {
    "map_name_en": "Route 66",
    "map_name_ko": "66번 국도",
    "map_mode_en": "Escort",
    "map_mode_ko": "호위",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Shambali Monastery",
    "map_name_ko": "샴발리 수도원",
    "map_mode_en": "Escort",
    "map_mode_ko": "호위",
    "in_owcs_korea_2026_stage1_pool": false
  },
  {
    "map_name_en": "Watchpoint: Gibraltar",
    "map_name_ko": "감시 기지: 지브롤터",
    "map_mode_en": "Escort",
    "map_mode_ko": "호위",
    "in_owcs_korea_2026_stage1_pool": true
  }
]
```

## Notes

- English and Korean map names are stored together for later bilingual use.
- The `in_owcs_korea_2026_stage1_pool` field separates the current tournament pool from the wider game map catalog.
- Korean names are stored from the provided screenshot set; if you want, we can later review and normalize spellings one more time.
