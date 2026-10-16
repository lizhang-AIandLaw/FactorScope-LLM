# FactorScope-LLM

[中文说明](README-zh.md)

This repository provides the controlled corpus and analysis code for **“Where
Do Legal Factors Live in LLMs?”** (Li Zhang and Kevin D. Ashley), accepted at
JURIX 2026.

## Paper overview

HYPO dimensions and CATO factors represent legally significant fact patterns
that legal experts abstract from case narratives. FactorScope-LLM examines
whether information corresponding to the 26 CATO trade-secret factors can be
read from the internal activations of pretrained large language models. The
paper addresses two research questions:

- **RQ1, decodability:** can the presence of each factor be read from
  residual-stream activations by a linear classifier?
- **RQ2, sparse localization:** can this information be read from one or five
  selected sparse-autoencoder (SAE) features?

The analysis covers Qwen3-1.7B, Qwen3-8B, and Gemma-2 2B with publicly
released SAEs (Qwen-Scope and Gemma Scope). A TF-IDF classifier on the same
split provides a lexical reference.

## Dataset

The controlled corpus is included in `data/`. See `data/README.md` for the
record schema.

| Partition | Factor-present | Factor-free | Total |
| --- | ---: | ---: | ---: |
| train | 3,485 | 447 | 3,932 |
| test | 3,507 | 454 | 3,961 |
| corpus | 6,992 | 901 | 7,893 |

## Repository structure

```text
FactorScope-LLM/
├── data/
│   ├── classification/       # Factor-present and factor-free passages
│   ├── manifest.json         # Counts and corpus digest
│   └── README.md             # Schema and data notes
├── src/
│   ├── factors.py            # Factor definitions, entailment relations, catalog utilities
│   ├── inspect_dataset.py    # Dataset audit
│   ├── extract_activations.py  # Qwen residual and SAE activations
│   ├── probe.py              # RQ1 residual readouts and RQ2 sparse readouts (Qwen)
│   ├── gemma_probe.py        # RQ1/RQ2 for Gemma-2 2B
│   ├── tfidf_baseline.py     # Lexical baseline
│   └── stability_recheck.py  # Bootstrap stability of the top-five features
├── tests/
└── requirements.txt
```

## Quick start

### 1. Install dependencies and inspect the corpus

```bash
git clone https://github.com/lizhang-AIandLaw/FactorScope-LLM.git
cd FactorScope-LLM
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/inspect_dataset.py --verify-manifest
```

The audit checks the factor catalog, record counts by split, record fields,
passage uniqueness, and the corpus digest.

### 2. Run the CPU lexical baseline

```bash
python src/tfidf_baseline.py
```

### 3. Run RQ1 and RQ2 on a GPU

The following example extracts Qwen3-8B activations for F16 at the three
sampled layers and fits the residual and sparse readouts:

```bash
python src/extract_activations.py \
  --data-dir data/classification \
  --factors F16 \
  --model Qwen/Qwen3-8B-Base \
  --sae Qwen/SAE-Res-Qwen3-8B-Base-W64K-L0_100 \
  --layers 9,18,27 \
  --out artifacts/activations/qwen3-8b-f16

python src/probe.py \
  --acts artifacts/activations/qwen3-8b-f16 \
  --factors F16 \
  --factor-set 27 \
  --report artifacts/probes/qwen3-8b-f16.md
```

For Qwen3-1.7B use `Qwen/Qwen3-1.7B-Base`,
`Qwen/SAE-Res-Qwen3-1.7B-Base-W32K-L0_100`, and layers `7,14,21`. For Gemma-2
2B run `python src/gemma_probe.py --factors F16`, which extracts activations at
layers 6, 13, and 20 and fits the readouts in one step.

### 4. Check feature stability

```bash
python src/stability_recheck.py \
  --acts artifacts/activations/qwen3-8b \
  --probe artifacts/probes/qwen3-8b.json \
  --factors F2,F8,F11,F24
```

Activation extraction requires a CUDA-capable environment and downloads the
specified model and SAE weights from Hugging Face. Recomputed artifacts are
written under `artifacts/`.

## Reading the results

For each factor and sampled layer, `probe.py` reports the test AUC of the
full-vector readout (`raw_auc`), the single-feature and five-feature readouts
(`top1_auc`, `top5_auc`) with the selected feature IDs, and the mean AUC of
20 random five-feature draws. The paper reports each factor's best layer and
the feature selected there.
