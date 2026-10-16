# Dataset

The repository contains the frozen controlled corpus used in the paper.

- `classification/`: 6,992 factor-present passages covering all 26 CATO
  factors (217 to 324 per factor), plus 901 factor-free passages. Each factor
  directory stores its passages in `pos.jsonl`; `neutral.jsonl` is stored at
  the directory root.
- `manifest.json`: factor list, passage counts by split, and the SHA-256
  digest of the corpus files.

## Partitions

Every record carries a `split` field, `train` or `test`. Jointly generated
passages stay on one side of the split, and no identical passage appears in
both partitions.

| Partition | Factor-present | Factor-free | Total |
| --- | ---: | ---: | ---: |
| train | 3,485 | 447 | 3,932 |
| test | 3,507 | 454 | 3,961 |

## Record fields

| Field | Meaning |
| --- | --- |
| `text` | The two- to four-sentence passage |
| `factor` | Target factor (`F1` to `F27`, no `F9`) or `NONE` for factor-free passages |
| `label` | 1 for factor-present, 0 for factor-free |
| `split` | `train` or `test` |
| `industry` | Business setting of the narrative (eight settings) |
| `secret_type` | Type of information at issue (eight types) |
| `style` | Narrative style (`S1` to `S4`) |

The passages are synthetic research data and should not be treated as legal
advice or records of actual disputes.

Run `python src/inspect_dataset.py --verify-manifest` from the repository root
to verify counts, fields, passage uniqueness, and the corpus digest.
