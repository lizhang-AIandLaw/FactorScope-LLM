# FactorScope-LLM

[English README](README.md)

本仓库提供论文 **“Where Do Legal Factors Live in LLMs?”**（Li Zhang、Kevin D. Ashley）
使用的受控语料库和分析代码。论文已被 JURIX 2026 录用。

## 论文简介

HYPO 维度和 CATO 因子表示法律专家从案件叙述中抽象出的、具有法律意义的事实模式。
FactorScope-LLM 考察能否从预训练大语言模型的内部激活中，读出与 26 个 CATO 商业秘密
因子相对应的信息。论文包含两个研究问题：

- **RQ1，可解码性：** 能否用线性分类器从残差流激活中读出每个因子是否存在？
- **RQ2，稀疏定位：** 能否从一个或五个选中的稀疏自编码器（SAE）特征中读出这一信息？

分析覆盖 Qwen3-1.7B、Qwen3-8B 和 Gemma-2 2B，使用公开发布的 SAE（Qwen-Scope 和
Gemma Scope）。在相同划分上训练的 TF-IDF 分类器作为词汇参照。

## 数据集

受控语料库位于 `data/`，字段说明见 `data/README.md`。

| 划分 | 含因子 | 无因子 | 总计 |
| --- | ---: | ---: | ---: |
| train | 3,485 | 447 | 3,932 |
| test | 3,507 | 454 | 3,961 |
| 全部 | 6,992 | 901 | 7,893 |

## 仓库结构

```text
FactorScope-LLM/
├── data/
│   ├── classification/       # 含因子段落与无因子段落
│   ├── manifest.json         # 数量统计与语料摘要值
│   └── README.md             # 字段和数据说明
├── src/
│   ├── factors.py            # 因子定义、蕴含关系和目录工具
│   ├── inspect_dataset.py    # 数据集核验
│   ├── extract_activations.py  # Qwen 残差与 SAE 激活提取
│   ├── probe.py              # RQ1 残差读出与 RQ2 稀疏读出（Qwen）
│   ├── gemma_probe.py        # Gemma-2 2B 的 RQ1/RQ2
│   ├── tfidf_baseline.py     # 词汇基线
│   └── stability_recheck.py  # top-5 特征的 bootstrap 稳定性
├── tests/
└── requirements.txt
```

## Quick Start

### 1. 安装依赖并核验语料库

```bash
git clone https://github.com/lizhang-AIandLaw/FactorScope-LLM.git
cd FactorScope-LLM
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/inspect_dataset.py --verify-manifest
```

核验程序会检查因子目录、各划分的记录数量、记录字段、段落唯一性以及语料摘要值。

### 2. 运行 CPU 词汇基线

```bash
python src/tfidf_baseline.py
```

### 3. 在 GPU 上运行 RQ1 和 RQ2

下面的示例在三个采样层为 F16 提取 Qwen3-8B 激活，并拟合残差读出和稀疏读出：

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

Qwen3-1.7B 使用 `Qwen/Qwen3-1.7B-Base`、`Qwen/SAE-Res-Qwen3-1.7B-Base-W32K-L0_100`
和层 `7,14,21`。Gemma-2 2B 运行 `python src/gemma_probe.py --factors F16`，它会在
第 6、13、20 层提取激活并一次完成读出拟合。

### 4. 检查特征稳定性

```bash
python src/stability_recheck.py \
  --acts artifacts/activations/qwen3-8b \
  --probe artifacts/probes/qwen3-8b.json \
  --factors F2,F8,F11,F24
```

激活提取需要支持 CUDA 的环境，并会从 Hugging Face 下载指定的模型和 SAE 权重。重新
计算的文件会写入 `artifacts/`。

## 结果解读

对每个因子和每个采样层，`probe.py` 报告完整向量读出的测试集 AUC（`raw_auc`）、单特征
和五特征读出的 AUC（`top1_auc`、`top5_auc`）及选中的特征编号，以及 20 次随机五特征
抽样的平均 AUC。论文报告每个因子的最佳层及在该层选中的特征。
