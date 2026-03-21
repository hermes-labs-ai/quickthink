# Study 003 — Gap Task Coverage

*2026-03-12 04:17*


## Results by Category


### SUMMARIZATION

| Task | Model | S0_raw | S1_quickthink | S3_fewshot | S6_prefix |
|------|-------|--------|--------------|------------|-----------|
| G1_summarization | 1.5b | ✓(3/3) | ✗(1/3) | ✓(3/3) | ✗(1/3) |
| G1_summarization | 0.8b | ✓(3/3) | ✓(3/3) | ✓(3/3) | ✓(3/3) |
| G1b_summarization_bu | 1.5b | ✗(0/3) | ✗(0/3) | ✗(0/3) | ✗(0/3) |
| G1b_summarization_bu | 0.8b | ✗(0/3) | ✗(0/3) | ✗(0/3) | ✓(3/3) |

### NER

| Task | Model | S0_raw | S1_quickthink | S3_fewshot | S6_prefix |
|------|-------|--------|--------------|------------|-----------|
| G2_ner_simple | 1.5b | ✗(0/3) | ✗(0/3) | ✓(3/3) | ✓(3/3) |
| G2_ner_simple | 0.8b | ✗(0/3) | ✗(0/3) | ✗(0/3) | ✗(0/3) |
| G2b_ner_minimal | 1.5b | ✓(3/3) | ✓(3/3) | ✓(3/3) | ✗(0/3) |
| G2b_ner_minimal | 0.8b | ✓(3/3) | ✗(0/3) | ✓(3/3) | ✗(0/3) |

### MULTI_LABEL

| Task | Model | S0_raw | S1_quickthink | S3_fewshot | S6_prefix |
|------|-------|--------|--------------|------------|-----------|
| G3_multilabel | 1.5b | ✓(3/3) | ✓(3/3) | ✓(3/3) | ✗(1/3) |
| G3_multilabel | 0.8b | ✗(0/3) | ✗(0/3) | ✓(3/3) | ✓(3/3) |

### LONG_CONTEXT

| Task | Model | S0_raw | S1_quickthink | S3_fewshot | S6_prefix |
|------|-------|--------|--------------|------------|-----------|
| G4_context_retention | 1.5b | ✓(3/3) | ✗(0/3) | ✓(3/3) | ✓(3/3) |
| G4_context_retention | 0.8b | ✓(3/3) | ✓(3/3) | ✓(3/3) | ✓(3/3) |

## Tier Jump Analysis (0.8B + scaffold ≥ 1.5B raw)

- **TIER JUMP**: G1_summarization — 0.8B + S1_quickthink matches 1.5B raw ✅

- **TIER JUMP**: G1_summarization — 0.8B + S3_few_shot matches 1.5B raw ✅

- **TIER JUMP**: G1_summarization — 0.8B + S6_prefix matches 1.5B raw ✅

- G1b_summarization_bullets: 1.5B fails raw too — task above both models

- G2_ner_simple: 1.5B fails raw too — task above both models

- **TIER JUMP**: G2b_ner_minimal — 0.8B + S3_few_shot matches 1.5B raw ✅

- **TIER JUMP**: G3_multilabel — 0.8B + S3_few_shot matches 1.5B raw ✅

- **TIER JUMP**: G3_multilabel — 0.8B + S6_prefix matches 1.5B raw ✅

- **TIER JUMP**: G4_context_retention — 0.8B + S1_quickthink matches 1.5B raw ✅

- **TIER JUMP**: G4_context_retention — 0.8B + S3_few_shot matches 1.5B raw ✅

- **TIER JUMP**: G4_context_retention — 0.8B + S6_prefix matches 1.5B raw ✅
