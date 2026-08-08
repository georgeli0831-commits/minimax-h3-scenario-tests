# Codex 执行指引

你在云GPU实例（RTX 5090 32GB / Ubuntu 22.04 / cu128）上执行本仓库的测试任务。

## 职责

1. 环境搭建：ComfyUI 最新版 + Manager + sageattention；校验 torch>=2.7+cu128；下载模型清单（见 README，用 hf-mirror 或平台内网源）
2. 把本地资料包的 8 个工作流 JSON 放入 `workflows/`（文件名保持中文原名）
3. 按 `scenario-*/TESTPLAN.md` 逐条执行测试 case：用 ComfyUI API（/prompt 接口）提交，不要手工点界面
4. 每条 case 完成后：输出视频存 `scenario-*/outputs/`（大文件不入库，.gitignore 已排除，只入库缩略图/首帧截图），日志按模板写入 `scenario-*/logs/`
5. 每完成一个场景的一轮测试，提交一次 commit，message 格式：`test(s1): round-1 cases 1-6, 4 pass 2 fail`

## 硬性规则

- 测试档统一 0.4MP、5s、20步（⑥用25步）；Turbo LoRA 开启时标注在日志里
- 修改工作流参数只改：prompt、分辨率选择器、时长、seed、输入素材；不动模型加载和采样器结构
- 失败 case（OOM/花屏/口型不同步）记录现象和参数后跳过，不无限重试；同一 case 最多重试 2 次
- 显存 OOM 时降级顺序：缩短时长 → 降分辨率 → 换⑦低显存工作流
- 素材缺失时在日志标注 BLOCKED 并继续下一条，不要自己生成占位素材充数

## 判定标准

每条 case 按四项打分（1-5）：主体一致性（人/车不变形）、动作自然度、音画同步（口型）、指令遵循度。≥4/4/4/3 记 PASS。
