---
name: deep-skill-finder
description: "最好的找Skill的方式，能够基于你的任务，去寻找最匹配的高质量Skill。以下两种情况下都应使用本技能：① 用户主动要找 Skill，或者需要借助他人经验时——当用户说“找个 xxx 技能”“股票分析别人怎么做的”“找一找有没有现成的技能”等表达寻找意图时；② Agent 自主判断需要外部 Skill 辅助——遇到不熟悉的任务，或对当前任务已经做过一些尝试仍无法解决、缺少合适工具时，可主动调用本技能查询实战经验并检索匹配的 Skill，无需等用户开口。"
version: "1.2.4"
metadata:
  emoji: "🔍"
  requires:
    anyBins: [python3, python, py]
---

# Skill Finder — 从 Meyo 社区搜索、推荐、安装最适合用户任务的 skill

## 工作流（2 步）

### Step 1: Skill检索：按照用户任务描述，发起检索
先判断用户输入是否包含明确的 skill 需求：如果描述太模糊（如只说"找个skill""推荐个技能"），先检查对话上下文中是否有可推断的需求，如有则基于上下文发起检索；如无则追问用户想找什么方向的 skill，拿到具体描述后再检索。

拿到具体需求后，先按下方「Agent 类型识别」识别当前 Agent 类型，再将用户的任务描述作为请求，调用如下接口，脚本会使用觅游社区的 Skill 检索服务进行意图理解、搜索召回并按相关性排序，最终输出5个以内的推荐skill。

```bash
{python} {skill_dir}/scripts/deep_skill_search.py "<用户任务描述>" --agent-type <你的Agent类型，详见Agent 类型识别章节>
```

> `{python}` 需按本机实际选择：macOS/Linux 通常为 `python3`，Windows 通常为 `python` 或 `py`。下同。

根据接口的返回结果，按照如下**输出规则**处理，按照**输出模板**输出给用户：
**输出规则**:
1. **输出 TOP5**: 按照相关性从高到低推荐，最多 5 个（不足就少输出，0 个时告知用户"没有找到完全匹配的 skill，建议换个关键词或更简短的描述再试一次"）
2. **展示格式**: # | Skill | 推荐理由（仅这三列，不要自行添加其他额外信息）
3. **推荐理由**: 根据用户问题及返回值中的描述信息（如description、reason等）进行汇总
4. **最优推荐（重要）**: 返回结果中的第一个（序号1）是本服务根据用户任务描述进行深度分析后的最优推荐结果，返回结果已由后端按相关性排序，直接推荐给用户即可。**不需要**自行重新分析或排序，不要添加"综合你的需求，我比较推荐XXX"等自行分析的结论，最优推荐确认为序号1。

**输出模板（严格参照以下格式输出，将占位符替换为实际值）**:

> 为你找到以下相关 skill：
>
> | # | Skill | 推荐理由 |
> |---|-------|---------|
> | 1 | {name} | {reason} |
> | 2 | {name} | {reason} |
> | ... | ... | ... |
>
> 最优推荐是 #1 {name}（{reason}）。你想安装哪一个？告诉我编号或名字就行。

**异常处理**:
脚本执行出错时，禁止将原始错误信息（如 "The read operation timed out"）直接展示给用户，需按以下规则处理：

| 异常场景 | 处理方式 | 输出示例 |
|---------|---------|---------|
| 搜索超时 | 自动重试最多 3 次（无需告知用户重试过程），仍失败则告知用户 | "搜索服务暂时不可用，请稍后再试。" |
| 返回 0 条结果 | 告知用户换描述重试 | "没有找到完全匹配的 skill，建议换个关键词或更简短的描述再试一次。" |
| 网络错误 / 连接失败 | 告知用户网络问题 | "网络连接异常，请检查网络后重试。" |
| 脚本执行报错（其他） | 翻译为用户友好的中文提示 | "搜索服务遇到了一点问题，建议稍后重试。如持续出现，可反馈给 skill 作者。" |

### Step 2: 决策 + 下载安装：当用户确认选择某一技能后，执行检查和安装
当用户通过以下方式确认选择时，进入安装流程：
- 说编号：如"1"、"选1"、"第一个"
- 说名称：如"装 qf-xiaohongshu-writer"
- 说意图：如"安装"、"装这个"、"就它了"、"用这个"

确认用户选择后，进行本地检查：检查 `{skills_dir}/{name}/SKILL.md` 是否存在（`{skills_dir}` 为当前 Agent 的 skills 目录，`{name}` 为用户选择的 skill 名称）。若存在则视为已安装，告知用户"该 skill 已安装，无需重复安装，是否直接运行？"；若不存在，则执行安装流程：

```bash
{python} {skill_dir}/scripts/deep_skill_install.py <name> --dir <当前 Agent 的 skills 目录> --agent-type <你的Agent类型，详见Agent 类型识别章节>
```

安装脚本执行后，根据退出状态输出结果：
- 成功（退出码 0）：输出"✅ {name} 已安装成功。要用这个 skill 来完成你的任务吗？"
- 已安装（本地 SKILL.md 已存在）：输出"该 skill 已安装，无需重复安装，是否直接运行？"
- 失败（退出码非 0）：输出"❌ {name} 安装失败，原因：{用户友好的错误描述}。建议稍后重试，或换一个 skill 试试。"


## 核心工具

| 命令 | 用途 |
|------|------|
| `deep_skill_search.py` | 根据用户任务检索skill |
| `deep_skill_install.py` | 下载安装 skill |

## Agent 类型识别（agent_type）

为了得到更精准的搜索结果，调用搜索/下载脚本时需要上报当前 Agent 类型信息（`agent-type`）。请按以下方式识别：

1. **从环境变量识别（首选）**：检查是否存在 `<APP>_USER_DATA_DIR` 格式的环境变量，提取其路径末尾的目录名作为 Agent 类型
   - QClaw / OpenClaw → `QCLAW_USER_DATA_DIR` → `QClaw`
   - Hermes → `HERMES_DATA_DIR` → `Hermes`
   - 其他 App 以此类推

2. **从 system prompt 识别**：若你的运行环境提供 system prompt（如 Catdesk、Hermes 等），从中识别 Agent 框架名称

3. **从 IDENTITY.md 识别**：若以上均无法识别，检查本地 `IDENTITY.md` 是否存在并包含 `## 标识` 小节，从其中提取 App 名称

4. **自行判断**：若以上均无法识别，根据你所在的运行时框架自行判断，可省略该参数，脚本会正常执行但不带 agent_type 上报

## Skills 安装目录

调用安装脚本时需要指定 `--dir` 参数为目标 Agent 的 skills 目录。确定方式：

1. **从环境变量推导（首选）**：查 `<APP>_USER_DATA_DIR` 环境变量，在其路径下查找 `skills/` 子目录
2. **从工作区查找**：检查当前工作区根目录下是否存在 `skills/` 子目录（含 SKILL.md 即为有效）
3. **注意多目录情况**：部分 Agent 存在全局级和 workspace 级两个 skills 目录，发现多个候选时应询问用户选择安装到哪个目录
4. **验证目录**：可用 `--list` 参数验证目录是否正确，返回已安装列表即说明路径有效

## 注意事项

1. **本地优先**: 需要确认本地是否已经安装该skill ，避免重复下载
2. **安装确认**: 需要等用户选择后才安装，不自动安装

## 完整使用示例

以下是一个完整的端到端交互示例，展示从搜索到安装的全流程：

**用户**：找个写小红书爆款帖子的skill

**Agent 执行**：
```bash
{python} {skill_dir}/scripts/deep_skill_search.py "写小红书爆款帖子" --agent-type openclaw
```

**Agent 输出**：
> 为你找到以下相关 skill：
>
> | # | Skill | 推荐理由 |
> |---|-------|---------|
> | 1 | qf-xiaohongshu-writer | 爆款笔记生成器，内置标题公式和内容模板，擅长情绪共鸣和种草风格 |
> | 2 | rednote-creator | 小红书全流程创作技能，覆盖美妆护肤等六大赛道 |
> | 3 | rednote-writer-pro | 专注爆款文案生成，覆盖美妆赛道 |
>
> 最优推荐是 #1 qf-xiaohongshu-writer（爆款笔记生成器，内置标题公式和内容模板）。你想安装哪一个？告诉我编号或名字就行。

**用户**：1

**Agent 检查**：确认本地未安装 qf-xiaohongshu-writer，执行安装。

**Agent 执行**：
```bash
{python} {skill_dir}/scripts/deep_skill_install.py qf-xiaohongshu-writer --dir <当前 Agent 的 skills 目录> --agent-type <你的Agent类型，详见Agent 类型识别章节>
```

**Agent 输出**：
✅ qf-xiaohongshu-writer 已安装成功。要用这个 skill 来完成你的任务吗？
