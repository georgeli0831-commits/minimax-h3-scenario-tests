# MiniMax H3 三大场景视频测试

针对电动车/摩托车营销视频的三大场景，用 MiniMax H3 开源版（2026-08-03 开放权重）+ ComfyUI 8套工作流做系统性测试。

## 三大场景

| 场景 | 目标 | 主力工作流 | 目录 |
|---|---|---|---|
| S1 单人口播 | 工厂门前单人边走边介绍车细节参数+试骑+说话 | ⑥图片音频参考（备选⑧r2v综合） | `scenario-1-solo-intro/` |
| S2 场景剧 | 模拟真实客户双人/多人使用车，带对话 | ④三图参考 / ⑦多条件低显存（双人用③双图） | `scenario-2-customer-drama/` |
| S3 TVC品牌片 | 概念版/炫酷/生活场景 AIGC 品牌短片 | ①文生 + ②图生 + ⑤首尾帧组合 | `scenario-3-tvc-brand/` |

## 云GPU环境（租用）

- GPU: RTX 5090 32GB ×1；vCPU ≥14核；内存 ≥90GB（最低64GB）；数据盘 ≥100GB
- 镜像: Ubuntu 22.04 + PyTorch ≥2.7 + CUDA 12.8 (cu128)，Python 3.11/3.12。**5090 是 Blackwell，cu124 及以下不认卡**
- ComfyUI 最新版 + Manager（H3 节点 2026-08-03 才合并）
- `pip install sageattention`；挂 Turbo LoRA（4步采样）加速迭代

## 模型清单（约40GB，下到数据盘）

| 类型 | 文件 | 目录 |
|---|---|---|
| 主模型 | minimax_h3_fl2va_pruned_int8_convrot.safetensors | models/diffusion_models/ |
| 主模型 | minimax_h3_ref2va_pruned_int8_convrot.safetensors | models/diffusion_models/ |
| 文本编码器 | qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors | models/text_encoders/ |
| 视频VAE | minimax_h3_video_vae_fp16.safetensors | models/vae/ |
| 音频VAE | minimax_h3_audio_vae_fp32.safetensors | models/vae/ |

## 工作流来源

8套工作流 JSON 在本地资料包（`/Users/lijiaming/Projects/comfyui工作流研究` 下的8个zip），入库到 `workflows/` 目录后再开始测试。

## 通用测试纪律

1. 一律 0.4MP + 5s 先测，通过后再拉分辨率/时长
2. 满意的结果立刻把 seed 改 fixed 并记录
3. 每个 case 按 `docs/test-log-template.md` 记录到对应场景的 `logs/`
4. 中文口播一律预录音频喂入（<Audio 1> exactly as it is），不让模型自己生成中文语音
