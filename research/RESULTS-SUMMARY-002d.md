# Study 002d — 0.8B Coding Gap Analysis

*2026-03-12 03:55*


## Key Question: Which scaffold closes the 0.8B→1.5B coding gap?


| Task | Model | S0_raw | S1_qt | S3_fewshot | S6_prefix | S1+S6 |

|------|-------|--------|-------|------------|-----------|-------|

| CD1_word_count | 0.8b | ✓(3/3) | ✗(0/3) | ✗(0/3) | ✓(3/3) | ✗(0/3) |
| CD1_word_count | 1.5b | ✓(3/3) | ✗(1/3) | ✗(0/3) | ✓(3/3) | ✓(3/3) |
| CD2_list_flatte | 0.8b | ✓(2/3) | ✓(3/3) | ✗(0/3) | ✓(2/3) | ✓(3/3) |
| CD2_list_flatte | 1.5b | ✓(3/3) | ✓(3/3) | ✗(0/3) | ✓(2/3) | ✓(3/3) |
| CD3_string_tran | 0.8b | ✗(0/3) | ✗(0/3) | ✗(0/3) | ✗(0/3) | ✗(0/3) |
| CD3_string_tran | 1.5b | ✓(3/3) | ✓(3/3) | ✗(0/3) | ✓(3/3) | ✓(3/3) |
| CD4_dict_invert | 0.8b | ✗(1/3) | ✗(0/3) | ✗(0/3) | ✗(0/3) | ✗(0/3) |
| CD4_dict_invert | 1.5b | ✓(3/3) | ✓(3/3) | ✓(3/3) | ✓(3/3) | ✓(3/3) |
| CD5_simple_clas | 0.8b | ✗(0/3) | ✓(3/3) | ✗(0/3) | ✓(2/3) | ✓(3/3) |
| CD5_simple_clas | 1.5b | ✗(0/3) | ✓(3/3) | ✗(0/3) | ✓(2/3) | ✓(3/3) |

## Tier Jump Analysis

Tasks where 0.8B with scaffold ≥ 1.5B raw:

- **TIER JUMP**: CD1_word_count — 0.8B + S6_prefix matches 1.5B raw ✅
- **TIER JUMP**: CD2_list_flatten — 0.8B + S1_quickthink matches 1.5B raw ✅
- **TIER JUMP**: CD2_list_flatten — 0.8B + S6_prefix matches 1.5B raw ✅
- **TIER JUMP**: CD2_list_flatten — 0.8B + S1+S6_combo matches 1.5B raw ✅
- CD5_simple_class: 1.5B itself fails raw — skip