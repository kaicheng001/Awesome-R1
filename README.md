# Awesome R1 [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of research papers, models, and resources related to R1-style reasoning models following DeepSeek-R1's breakthrough in January 2025.

DeepSeek-R1 introduced a new paradigm of reasoning in large language models. This repository collects all subsequent research papers, implementations, and resources that build upon or relate to the R1 approach across various domains.

## Table of Contents

- [Papers](#papers)
- [Tools and Resources](#tools-and-resources)
- [Related Awesome Lists](#related-awesome-lists)
- [Contributing](#contributing)

## Papers

| Paper                                                | Code                                   | Models                                      | Dataset | Project Page                        | Date    |
| ---------------------------------------------------- | -------------------------------------- | ------------------------------------------- | ------- | ----------------------------------- | ------- |
| [R1-Searcher++: Incentivizing the Dynamic Knowledge Acquisition of LLMs  via Reinforcement Learning](https://arxiv.org/abs/2505.17005) | [R1-Searcher-plus](https://github.com/RUCAIBox/R1-Searcher-plus) | - | - | - | 2025.05.22 |
| [UniVG-R1: Reasoning Guided Universal Visual Grounding with Reinforcement Learning](https://arxiv.org/abs/2505.14231) | [AMAP-ML/UniVG-R1](https://github.com/AMAP-ML/UniVG-R1) | - | - | [UniVG-R1-page](https://amap-ml.github.io/UniVG-R1-page/) | 2025.05.20 |
| [Table-R1: Region-based Reinforcement Learning for Table Understanding](https://arxiv.org/abs/2505.12415) | - | - | TableInstruct, TableBench, WikiTQ | - | 2025.05.18 |  
| [Learning When to Think: Shaping Adaptive Reasoning in R1-Style Models via Multi-Stage RL](https://arxiv.org/abs/2505.10832) | [TU2021/AutoThink](https://github.com/TU2021/AutoThink) | [AutoThink](https://huggingface.co/collections/SONGJUNTU/autothink-682624e1466651b08055b479) | MATH, Minerva, Olympiad, AIME24, AMC23 | - | 2025.05.16 |
| [EchoInk-R1: Exploring Audio-Visual Reasoning in Multimodal LLMs via Reinforcement Learning](https://arxiv.org/abs/2505.04623) | [HarryHsing/EchoInk](https://github.com/HarryHsing/EchoInk) | [harryhsing/EchoInk-R1-7B](https://huggingface.co/harryhsing/EchoInk-R1-7B) | [harryhsing/AVQA-R1-6K](https://huggingface.co/datasets/harryhsing/AVQA-R1-6K) | -  | 2025.05.07 |
| [RM-R1: Reward Modeling as Reasoning](https://arxiv.org/abs/2505.02387) | [RM-R1-UIUC/RM-R1](https://github.com/RM-R1-UIUC/RM-R1) | [RM-R1](https://huggingface.co/collections/gaotang/rm-r1-681128cdab932701cad844c8) | [RM-R1](https://huggingface.co/collections/gaotang/rm-r1-681128cdab932701cad844c8) | - | 2025.05.05 |
| [Skywork R1V2: Multimodal Hybrid Reinforcement Learning for Reasoning](https://arxiv.org/abs/2504.16656) | [SkyworkAI/Skywork-R1V](https://github.com/SkyworkAI/Skywork-R1V) | [Skywork/Skywork-R1V2-38B](https://huggingface.co/Skywork/Skywork-R1V2-38B) | - | - | 2025.04.23 |
| [Open-Medical-R1: How to Choose Data for RLVR Training at Medicine Domain](https://arxiv.org/abs/2504.13950) | [Qsingle/open-medical-r1](https://github.com/Qsingle/open-medical-r1) | [qiuxi337/gemma-3-12b-bnb-grpo](https://github.com/Qsingle/open-medical-r1)[qiuxi337/gemma-3-12b-it-grpo](https://huggingface.co/qiuxi337/gemma-3-12b-it-grpo) | - | - | 2025.04.16 |
| [GUI-R1: A Generalist R1-Style Vision-Language Action Model For GUI Agents](https://arxiv.org/abs/2504.10458) | [ritzz-ai/GUI-R1](https://github.com/ritzz-ai/GUI-R1) | [ritzzai/GUI-R1](https://huggingface.co/ritzzai/GUI-R1) | [ritzzai/GUI-R1](https://huggingface.co/datasets/ritzzai/GUI-R1) | - | 2025.04.14 |
| [MT-R1-Zero: Advancing LLM-based Machine Translation via R1-Zero-like Reinforcement Learning](https://arxiv.org/abs/2504.10160) | [fzp0424/MT-R1-Zero](https://github.com/fzp0424/MT-R1-Zero) |  - | [data](https://github.com/fzp0424/MT-R1-Zero/tree/main/data) | - | 2025.04.10 |
| [Skywork R1V: Pioneering Multimodal Reasoning with Chain-of-Thought](https://arxiv.org/abs/2504.05599) | [SkyworkAI/Skywork-R1V](https://github.com/SkyworkAI/Skywork-R1V) | [Skywork/Skywork-R1V-38B](https://huggingface.co/Skywork/Skywork-R1V-38B) | - | - | 2025.04.08 |
| [VLM-R1: A Stable and Generalizable R1-style Large Vision-Language Model](https://arxiv.org/abs/2504.07615) | [om-ai-lab/VLM-R1](https://github.com/om-ai-lab/VLM-R1) | [VLM-R1 Models](https://huggingface.co/collections/omlab/vlm-r1-models-67b7352db15c19d57157c348) | [omlab/VLM-R1](https://huggingface.co/datasets/omlab/VLM-R1) | [VLM-R1 Blog](https://om-ai-lab.github.io/index.html) | 2025.04.07 |
| [UI-R1: Enhancing Efficient Action Prediction of GUI Agents by Reinforcement Learning](https://arxiv.org/abs/2503.21620) | [lll6gg/UI-R1](https://github.com/lll6gg/UI-R1) | [LZXzju/Qwen2.5-VL-3B-UI-R1](https://huggingface.co/LZXzju/Qwen2.5-VL-3B-UI-R1)[LZXzju/Qwen2.5-VL-3B-UI-R1-E](https://huggingface.co/LZXzju/Qwen2.5-VL-3B-UI-R1-E) | [LZXzju/UI-R1-3B-Train](https://huggingface.co/datasets/LZXzju/UI-R1-3B-Train) | - | 2025.03.27 |
| [Vision-R1: Evolving Human-Free Alignment in Large Vision-Language Models via Vision-Guided Reinforcement Learning](https://arxiv.org/abs/2503.18013) | [Vision-R1](https://github.com/jefferyZhan/Griffon/tree/master/Vision-R1) | [Vision-R1 Models](https://huggingface.co/collections/JefferyZhan/vision-r1-67e166f8b6a9ec3f6a664262) | [JefferyZhan/Vision-R1-Data](https://huggingface.co/datasets/JefferyZhan/Vision-R1-Data) | - | 2025.03.18 |
| [Med-R1: Reinforcement Learning for Generalizable Medical Reasoning in Vision-Language Models](https://arxiv.org/abs/2503.13939) | - | - | - | - | 2025.03.18 |
| [Search-R1: Training LLMs to Reason and Leverage Search Engines with Reinforcement Learning](https://arxiv.org/abs/2503.09516) | [PeterGriffinJin/Search-R1](https://github.com/PeterGriffinJin/Search-R1) | [Search-R1](https://huggingface.co/collections/PeterJinGo/search-r1-67d1a021202731cb065740f5) | [Search-R1](https://huggingface.co/collections/PeterJinGo/search-r1-67d1a021202731cb065740f5) | - | 2025.03.12 |
| [Vision-R1: Incentivizing Reasoning Capability in Multimodal Large Language Models](https://arxiv.org/abs/2503.06749) | [Osilly/Vision-R1](https://github.com/Osilly/Vision-R1) | [Osilly/Vision-R1-7B](https://huggingface.co/Osilly/Vision-R1-7B) | [Osilly/Vision-R1-cold](https://huggingface.co/datasets/Osilly/Vision-R1-cold) | - | 2025.03.09 |
| [LMM-R1: Empowering 3B LMMs with Strong Reasoning Abilities Through Two-Stage Rule-Based RL](https://arxiv.org/abs/2503.07536) | [lmm-r1](https://github.com/TideDra/lmm-r1) | [VLM-Reasoner/LMM-R1-MGT-PerceReason](https://huggingface.co/VLM-Reasoner/LMM-R1-MGT-PerceReason) | [VLM-Reasoner/VerMulti](https://huggingface.co/datasets/VLM-Reasoner/VerMulti) | [LMM-R1-ProjectPage](https://forjadeforest.github.io/LMM-R1-ProjectPage/) | 2025.03.07 |
| [R1-Searcher: Incentivizing the Search Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2503.05592) | [RUCAIBox/R1-Searcher](https://github.com/RUCAIBox/R1-Searcher) | [XXsongLALA/Qwen-2.5-7B-base-RAG-RL](https://huggingface.co/XXsongLALA/Qwen-2.5-7B-base-RAG-RL)[XXsongLALA/Llama-3.1-8B-instruct-RAG-RL](https://huggingface.co/XXsongLALA/Llama-3.1-8B-instruct-RAG-RL) | [XXsongLALA/Llama-3.1-8B-instruct-RAG-RL](https://huggingface.co/datasets/XXsongLALA/RAG-RL-Hotpotqa-with-2wiki) | - | 2025.03.07 |
| [Rank-R1: Enhancing Reasoning in LLM-based Document Rerankers via Reinforcement Learning](https://arxiv.org/abs/2503.06034) | [Rank-R1](https://github.com/ielab/llm-rankers/tree/main/Rank-R1) | - | [Rank-R1](https://github.com/ielab/llm-rankers/tree/main/Rank-R1) | - | 2025.03.06 |
| [R1-Omni: Explainable Omni-Multimodal Emotion Recognition with Reinforcement Learning](https://arxiv.org/abs/2503.05379) | [HumanMLLM/R1-Omni](https://github.com/HumanMLLM/R1-Omni) | [StarJiaxing/R1-Omni-0.5B](https://huggingface.co/StarJiaxing/R1-Omni-0.5B) | - | - | 2025.03.05 |
| [TinyR1-32B-Preview: Boosting Accuracy with Branch-Merge Distillation](https://arxiv.org/abs/2503.04872) | - | - | - | - | 2025.03.04 |
| [R1-T1: Fully Incentivizing Translation Capability in LLMs via Reasoning Learning](https://arxiv.org/abs/2502.19735) | [superboom/R1-T1](https://github.com/superboom/R1-T1) | - | - | - | 2025.02.27 |
| [MedVLM-R1: Incentivizing Medical Reasoning Capability of Vision-Language Models (VLMs) via Reinforcement Learning](https://arxiv.org/abs/2502.19634) | - | [JZPeterPan/MedVLM-R1](https://huggingface.co/JZPeterPan/MedVLM-R1) | [VQA-RAD, SLAKE, PMC-VQA](https://huggingface.co/JZPeterPan/MedVLM-R1) | - | 2025.02.26 |
| [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning](https://arxiv.org/abs/2501.12948) | [deepseek-ai/DeepSeek-R1](https://github.com/deepseek-ai/DeepSeek-R1) | [deepseek-ai/DeepSeek-R1](https://huggingface.co/deepseek-ai/DeepSeek-R1) | [MATH, GSM8K, AIME 2024, MMLU, HumanEval, LiveCodeBench](https://github.com/deepseek-ai/DeepSeek-R1) | - | 2025.01.22 |

_Sort by release date, latest first, `-` indicate that there is no relevant code or model link_

## Tools and Resources

- [ ] TODO

## Related Awesome Lists

- [Awesome-LLM](https://github.com/Hannibal046/Awesome-LLM)
- [Awesome-Multimodal-Large-Language-Models](https://github.com/BradyFU/Awesome-Multimodal-Large-Language-Models)
- [Awesome-Reasoning-Foundation-Models](https://github.com/reasoning-survey/Awesome-Reasoning-Foundation-Models)
- [Awesome-LLM-Post-training](https://github.com/mbzuai-oryx/Awesome-LLM-Post-training)
- [Awesome-Unified-Multimodal-Models](https://github.com/showlab/Awesome-Unified-Multimodal-Models)
- [Awesome-RL-based-LLM-Reasoning](https://github.com/bruno686/Awesome-RL-based-LLM-Reasoning) -
- [Awesome-Long-Chain-of-Thought-Reasoning](https://github.com/LightChen233/Awesome-Long-Chain-of-Thought-Reasoning)
- [Awesome_Efficient_LRM_Reasoning](https://github.com/XiaoYee/Awesome_Efficient_LRM_Reasoning) -
- [Awesome-Multimodal-Reasoning](https://github.com/Video-R1/Awesome-Multimodal-Reasoning)
- [Awesome-RL-based-Reasoning-MLLMs](https://github.com/Sun-Haoyuan23/Awesome-RL-based-Reasoning-MLLMs)
- [Awesome-Large-Multimodal-Reasoning-Models](https://github.com/HITsz-TMG/Awesome-Large-Multimodal-Reasoning-Models)
- [Multimodal-AND-Large-Language-Models](https://github.com/Yangyi-Chen/Multimodal-AND-Large-Language-Models)

## Contributing

Contributions are welcome! This list is continuously updated. If you have any suggestions or find any missing papers, please feel free to open an issue or submit a pull request.

### What to Include

- ✅ Research papers with "R1"/"r1" in title
- ✅ Tools and resources that implement or utilize R1
- ✅ Related awesome lists

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=kaicheng001/awesome-r1&type=Date)](https://star-history.com/#kaicheng001/awesome-r1&Date)