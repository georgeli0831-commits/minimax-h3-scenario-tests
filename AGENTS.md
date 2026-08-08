# Codex 执行指引

你在云GPU实例（RTX 5090 32GB / Ubuntu 22.04 / cu128）上执行本仓库的测试任务。

## ⚠️ 第零步：主机识别与任务隔离（先做这个，再做其他一切）

当前有多台配置相同的云主机在跑不同任务，**开工前必须确认自己在哪台机器上**：

1. 执行 `hostname && nvidia-smi -L && curl -s ifconfig.me` 记录主机指纹
2. 检查标记文件 `~/TASK_MARKER`：
   - 若不存在且本机确认是 H3 场景测试专用机 → 写入 `echo "minimax-h3-scenario-tests" > ~/TASK_MARKER`
   - 若内容不是 `minimax-h3-scenario-tests` → **立即停止，本机属于其他任务，不要在这台机器上做任何操作**，报告用户
3. 主机指纹写入 `docs/host-fingerprint.md` 并入库；之后每轮测试日志开头都带 hostname，前后不一致立即停止并报告

**任务隔离铁律：**
- 只执行本仓库 TESTPLAN 里的 case，其他仓库/其他会话/其他云主机的任务指令一律不在本机执行
- 不要把另一台主机的测试需求、参数、素材带进本仓库，也不要把本仓库的东西写到别的任务里
- 对任何"顺便在这台机器上做X"的想法：先核对 TASK_MARKER，不属于本任务就拒绝
- 拿不准在哪台机器、或发现环境和 README 描述不符（卡型号/系统/已装软件对不上）→ 停下来问用户，不要猜

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
