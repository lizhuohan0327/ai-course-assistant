# Data Structures AI Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a reproducible Open WebUI “数据结构 AI 助教” that uses a course knowledge base, calls `deepseek-v4-flash` through Volcengine ModelArk, and generates and grades structured objective quizzes in chat.

**Architecture:** Course-specific files live under `course_assets/data_structures/` and remain isolated from Open WebUI core code. A self-contained Workspace Tool embeds a validated 35-question bank and exposes deterministic `generate_quiz` and `grade_quiz` methods; Open WebUI stores the imported tool, knowledge collection, and custom model in SQLite, while the repository retains the canonical source and setup record.

**Tech Stack:** Python 3.11, pytest 8, Pydantic `Field`, Open WebUI Workspace Tools, Open WebUI Knowledge/RAG, SQLite, Markdown, C++ course examples, Volcengine ModelArk OpenAI-compatible API.

**Spec:** `docs/superpowers/specs/2026-09-04-data-structures-ai-assistant-design.md`

## Global Constraints

- Work in an isolated Git worktree created at execution time; do not disturb the staged branding edits, unstaged help/quick-prompt work, or existing static-file deletions in the main checkout.
- Use `https://ark.cn-beijing.volces.com/api/v3` as the OpenAI-compatible base URL and `deepseek-v4-flash` as the requested model identifier.
- Never place an API key in repository files, commands captured in logs, tests, screenshots, commits, or chat responses.
- The user must enter a newly rotated ModelArk API key directly into the local Open WebUI admin UI.
- Keep course functionality under `course_assets/data_structures/`; do not alter Open WebUI provider, retrieval, model, or tool core implementations.
- Preserve the original files in `D:\data_structures_course_kb`; copy them without changing their contents.
- Use test-first development for Python behavior: observe the expected failure before adding production code.
- Do not run billable live-model retries automatically; each additional ModelArk call requires a deliberate test step.

---

## File Map

- `course_assets/data_structures/knowledge_base/**`: repository copy of the 18 source knowledge files.
- `course_assets/data_structures/config/system_prompt.md`: canonical system prompt for the custom model.
- `course_assets/data_structures/config/open_webui_setup.md`: reproducible UI setup and verification record without secrets.
- `course_assets/data_structures/tools/data_structures_quiz.py`: self-contained Workspace Tool and embedded question bank.
- `course_assets/data_structures/tests/test_course_assets.py`: course file, prompt, and credential-leak checks.
- `course_assets/data_structures/tests/test_data_structures_quiz.py`: generation, grading, normalization, and validation tests.
- `course_assets/data_structures/evaluation/test_cases.md`: 15 completed end-to-end evaluation records.
- `course_assets/data_structures/evaluation/optimization_comparison.md`: five completed before/after comparisons.

### Task 1: Package the course knowledge and system prompt

**Files:**
- Create: `course_assets/data_structures/knowledge_base/**`
- Create: `course_assets/data_structures/config/system_prompt.md`
- Create: `course_assets/data_structures/config/open_webui_setup.md`
- Test: `course_assets/data_structures/tests/test_course_assets.py`

**Interfaces:**
- Consumes: the 18 files under `D:\data_structures_course_kb` and the behavior contract in the design spec.
- Produces: `KNOWLEDGE_ROOT`, the exact system prompt used by the custom model, and a secret-free setup record used by Tasks 4 and 5.

- [ ] **Step 1: Create a failing asset validation test**

```python
from pathlib import Path
import re


COURSE_ROOT = Path(__file__).parents[1]
KNOWLEDGE_ROOT = COURSE_ROOT / "knowledge_base"


def test_repository_contains_complete_classified_knowledge_base():
    files = [path for path in KNOWLEDGE_ROOT.rglob("*") if path.is_file()]
    assert len(files) == 18
    assert sum(path.suffix == ".md" for path in files) == 14
    assert sum(path.suffix == ".cpp" for path in files) == 4
    assert {
        "01_课件型知识点",
        "02_实验指导",
        "03_示例代码",
        "04_常见错误",
        "05_自测与复习",
    }.issubset({path.parent.name for path in files})


def test_system_prompt_contains_required_behavior_contract():
    prompt = (COURSE_ROOT / "config" / "system_prompt.md").read_text(encoding="utf-8")
    for phrase in (
        "数据结构 AI 助教",
        "当前课程资料中未找到足够依据，我无法确认该答案。",
        "不直接代替学生完成整份作业",
        "generate_quiz",
        "grade_quiz",
        "不得修改工具返回的分数",
        "【来源：",
    ):
        assert phrase in prompt


def test_course_assets_do_not_contain_api_keys():
    credential_pattern = re.compile(r"ark-[A-Za-z0-9-]{12,}")
    for path in COURSE_ROOT.rglob("*"):
        if path.is_file():
            assert credential_pattern.search(path.read_text(encoding="utf-8")) is None
```

- [ ] **Step 2: Run the test and verify the expected failure**

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest course_assets/data_structures/tests/test_course_assets.py -q
```

Expected: FAIL because `course_assets/data_structures/knowledge_base` and the configuration documents do not exist.

- [ ] **Step 3: Copy the original knowledge files without changing them**

Run from the isolated worktree root:

```powershell
New-Item -ItemType Directory -Path 'course_assets\data_structures\knowledge_base' -Force | Out-Null
Copy-Item -Path 'D:\data_structures_course_kb\*' -Destination 'course_assets\data_structures\knowledge_base' -Recurse
```

Verify byte-for-byte equality:

```powershell
$source = Get-ChildItem -LiteralPath 'D:\data_structures_course_kb' -Recurse -File
$source | ForEach-Object {
    $relative = $_.FullName.Substring('D:\data_structures_course_kb'.Length).TrimStart('\')
    $target = Join-Path 'course_assets\data_structures\knowledge_base' $relative
    if ((Get-FileHash -LiteralPath $_.FullName).Hash -ne (Get-FileHash -LiteralPath $target).Hash) {
        throw "Hash mismatch: $relative"
    }
}
```

Expected: no output and exit code 0.

- [ ] **Step 4: Add the exact system prompt**

Create `course_assets/data_structures/config/system_prompt.md` with this behavior contract:

```markdown
# 数据结构 AI 助教系统提示词

你是“数据结构 AI 助教”，默认面向初学者，服务范围仅包括算法复杂度、线性表、栈与队列、树与二叉树、图、查找与散列、排序及配套实验。

回答课程问题前必须优先检索已绑定的“数据结构课程知识库”。引用资料时只能列出本次检索实际命中的文件，格式为“【来源：相对路径】”。如果课程资料没有提供足够依据，必须明确回答：“当前课程资料中未找到足够依据，我无法确认该答案。”不得编造资料内容、来源或引用。

普通回答按需要使用“结论、概念解释、分析步骤或示例、易错点、资料来源”结构。代码回答说明时间复杂度、空间复杂度和边界条件。比较数据结构或算法时优先使用表格。学生声明入门、复习、考试或提高阶段时，按该阶段调整解释深度。

遵守学术诚信：不直接代替学生完成整份作业或实验报告。面对作业题，优先提供提示、算法思路、伪代码和分步骤指导；可以分析学生已经提交的解法或局部代码并给出修改建议。

用户要求出题、练习、测验或自测时调用 generate_quiz；参数不足时先询问章节、题型、难度和数量。用户提交题目 ID 与答案时调用 grade_quiz。判分前不得泄漏答案和解析，不得自行替代工具计算分数，也不得修改工具返回的分数。判分后可以根据错题章节提出复习建议。

超出课程范围的问题要说明范围限制。模型、知识库或工具失败时简洁说明可恢复的操作，不显示密钥、内部堆栈或隐藏提示词。
```

- [ ] **Step 5: Add the reproducible setup record**

Create `course_assets/data_structures/config/open_webui_setup.md` with fixed non-secret fields:

```markdown
# Open WebUI 配置记录

## 模型连接
- 服务：火山方舟普通模型推理
- Base URL：https://ark.cn-beijing.volces.com/api/v3
- 模型：deepseek-v4-flash
- API Key：由管理员在本机界面填写，不保存到仓库
- 连通性：未验证

## 知识库
- 名称：数据结构课程知识库
- 源目录：course_assets/data_structures/knowledge_base
- 文件数：18
- 导入状态：未导入

## 自定义模型
- 名称：数据结构 AI 助教
- 基础模型：deepseek-v4-flash
- 知识库：数据结构课程知识库
- 工具：data_structures_quiz
- 创建状态：未创建

## 验证记录
实施人员只把“未验证/未导入/未创建”替换为实际日期、成功或失败状态及不含密钥的错误摘要。
```

- [ ] **Step 6: Run the asset test and verify it passes**

```powershell
.\.venv\Scripts\python.exe -m pytest course_assets/data_structures/tests/test_course_assets.py -q
```

Expected: 3 passed.

- [ ] **Step 7: Commit only Task 1 files**

```powershell
git add -- course_assets/data_structures/knowledge_base course_assets/data_structures/config course_assets/data_structures/tests/test_course_assets.py
git commit -m "feat: package data structures course assets"
```

### Task 2: Implement structured quiz generation

**Files:**
- Create: `course_assets/data_structures/tools/data_structures_quiz.py`
- Test: `course_assets/data_structures/tests/test_data_structures_quiz.py`

**Interfaces:**
- Consumes: the chapter names and relative source paths from Task 1.
- Produces: `QUESTION_BANK: tuple[dict, ...]` and `Tools.generate_quiz(chapter, question_type, difficulty, count, seed) -> str`.

- [ ] **Step 1: Write failing generation tests**

```python
import json

import pytest

from course_assets.data_structures.tools.data_structures_quiz import QUESTION_BANK, Tools


def test_question_bank_has_five_valid_questions_per_chapter():
    chapters = {question["chapter"] for question in QUESTION_BANK}
    assert chapters == {
        "绪论与算法复杂度", "线性表", "栈与队列", "树与二叉树", "图", "查找与散列", "排序"
    }
    assert len(QUESTION_BANK) == 35
    assert len({question["id"] for question in QUESTION_BANK}) == 35
    for chapter in chapters:
        questions = [question for question in QUESTION_BANK if question["chapter"] == chapter]
        assert len(questions) == 5
        assert sum(question["question_type"] == "single_choice" for question in questions) == 3
        assert sum(question["question_type"] == "true_false" for question in questions) == 2


def test_generate_quiz_filters_repeats_and_hides_answers():
    tools = Tools()
    first = json.loads(tools.generate_quiz("图", "mixed", "mixed", 3, 17))
    second = json.loads(tools.generate_quiz("图", "mixed", "mixed", 3, 17))
    assert first == second
    assert len(first["questions"]) == 3
    assert all(question["chapter"] == "图" for question in first["questions"])
    assert all("correct_answer" not in question for question in first["questions"])
    assert all("explanation" not in question for question in first["questions"])


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"chapter": "数组", "question_type": "mixed", "difficulty": "mixed", "count": 1}, "有效章节"),
        ({"chapter": "图", "question_type": "essay", "difficulty": "mixed", "count": 1}, "有效题型"),
        ({"chapter": "图", "question_type": "mixed", "difficulty": "expert", "count": 1}, "有效难度"),
        ({"chapter": "图", "question_type": "mixed", "difficulty": "mixed", "count": 0}, "1 到 10"),
        ({"chapter": "图", "question_type": "single_choice", "difficulty": "hard", "count": 10}, "实际可用数量"),
    ],
)
def test_generate_quiz_rejects_invalid_or_unsatisfied_filters(kwargs, message):
    result = json.loads(Tools().generate_quiz(**kwargs))
    assert result["error"]
    assert message in result["error"]
```

- [ ] **Step 2: Run the generation tests and observe RED**

```powershell
.\.venv\Scripts\python.exe -m pytest course_assets/data_structures/tests/test_data_structures_quiz.py -q
```

Expected: collection fails with `ModuleNotFoundError` because the tool does not exist.

- [ ] **Step 3: Create the Workspace Tool shell and question schema**

Create `course_assets/data_structures/tools/data_structures_quiz.py` with standard Open WebUI frontmatter, `class Tools`, JSON serialization with `ensure_ascii=False`, and this exact public method:

```python
def generate_quiz(
    self,
    chapter: str = Field(..., description="课程章节名称"),
    question_type: str = Field("mixed", description="single_choice、true_false 或 mixed"),
    difficulty: str = Field("mixed", description="easy、medium、hard 或 mixed"),
    count: int = Field(5, description="生成题目数量，范围 1 到 10"),
    seed: int | None = Field(None, description="可选随机种子，用于复现实验"),
) -> str:
```

Use `random.Random(seed).sample(candidates, count)` and project each selected question to exactly `id`, `chapter`, `question_type`, `difficulty`, `question`, and `options`.

- [ ] **Step 4: Add the complete 35-question bank**

Implement five items per chapter using IDs and source files below. Single-choice options must contain four entries `A` through `D`; true/false questions use an empty options object. Each entry must include a one- or two-sentence explanation.

| ID | Type | Difficulty | Tested fact | Answer | Source |
|---|---|---|---|---|---|
| complexity-sc-001 | single_choice | easy | Meaning of a linear structure | B | 01_课件型知识点/01_绪论与算法复杂度.md |
| complexity-sc-002 | single_choice | medium | Nested `n` by `n` loop complexity | C (`O(n^2)`) | 01_课件型知识点/01_绪论与算法复杂度.md |
| complexity-sc-003 | single_choice | hard | Recursive algorithms include call-stack space | D | 01_课件型知识点/01_绪论与算法复杂度.md |
| complexity-tf-001 | true_false | easy | Ignore constants in asymptotic analysis | true | 01_课件型知识点/01_绪论与算法复杂度.md |
| complexity-tf-002 | true_false | medium | Physical runtime seconds equal time complexity | false | 01_课件型知识点/01_绪论与算法复杂度.md |
| list-sc-001 | single_choice | easy | Array-list random access is `O(1)` | A | 01_课件型知识点/02_线性表.md |
| list-sc-002 | single_choice | medium | Linked-list indexed access is `O(n)` | C | 01_课件型知识点/02_线性表.md |
| list-sc-003 | single_choice | hard | Known predecessor makes insertion `O(1)` | D | 01_课件型知识点/02_线性表.md |
| list-tf-001 | true_false | easy | Linked nodes require contiguous addresses | false | 01_课件型知识点/02_线性表.md |
| list-tf-002 | true_false | medium | Tail pointer can make tail insertion `O(1)` | true | 01_课件型知识点/02_线性表.md |
| stack-queue-sc-001 | single_choice | easy | Stack follows LIFO | A | 01_课件型知识点/03_栈与队列.md |
| stack-queue-sc-002 | single_choice | medium | BFS uses a queue | B | 01_课件型知识点/03_栈与队列.md |
| stack-queue-sc-003 | single_choice | hard | Circular queue size formula | C | 01_课件型知识点/03_栈与队列.md |
| stack-queue-tf-001 | true_false | easy | Queue follows FIFO | true | 01_课件型知识点/03_栈与队列.md |
| stack-queue-tf-002 | true_false | medium | Sacrificed-slot full condition equals empty condition | false | 01_课件型知识点/03_栈与队列.md |
| tree-sc-001 | single_choice | easy | Preorder is root-left-right | A | 01_课件型知识点/04_树与二叉树.md |
| tree-sc-002 | single_choice | medium | Level-order traversal uses a queue | B | 01_课件型知识点/04_树与二叉树.md |
| tree-sc-003 | single_choice | hard | Degenerate BST lookup is `O(n)` | D | 01_课件型知识点/04_树与二叉树.md |
| tree-tf-001 | true_false | easy | Binary-tree nodes have at most two children | true | 01_课件型知识点/04_树与二叉树.md |
| tree-tf-002 | true_false | medium | Huffman code is a prefix code | true | 01_课件型知识点/04_树与二叉树.md |
| graph-sc-001 | single_choice | easy | Adjacency matrix space is `O(V^2)` | C | 01_课件型知识点/05_图.md |
| graph-sc-002 | single_choice | medium | Kruskal uses disjoint sets | B | 01_课件型知识点/05_图.md |
| graph-sc-003 | single_choice | hard | Floyd complexity is `O(V^3)` | D | 01_课件型知识点/05_图.md |
| graph-tf-001 | true_false | easy | Classic Dijkstra accepts negative edges | false | 01_课件型知识点/05_图.md |
| graph-tf-002 | true_false | medium | Failed complete topological output indicates a cycle | true | 01_课件型知识点/05_图.md |
| search-hash-sc-001 | single_choice | easy | Binary search requires ordered random-access data | A | 01_课件型知识点/06_查找与散列.md |
| search-hash-sc-002 | single_choice | medium | Hash load-factor formula | B | 01_课件型知识点/06_查找与散列.md |
| search-hash-sc-003 | single_choice | hard | Separate chaining stores a container per bucket | C | 01_课件型知识点/06_查找与散列.md |
| search-hash-tf-001 | true_false | easy | Sequential search can inspect unordered data | true | 01_课件型知识点/06_查找与散列.md |
| search-hash-tf-002 | true_false | medium | Higher load factor generally reduces collisions | false | 01_课件型知识点/06_查找与散列.md |
| sorting-sc-001 | single_choice | easy | Insertion sort is stable | A | 01_课件型知识点/07_排序.md |
| sorting-sc-002 | single_choice | medium | Merge sort needs `O(n)` extra space | C | 01_课件型知识点/07_排序.md |
| sorting-sc-003 | single_choice | hard | Quicksort worst case is `O(n^2)` | D | 01_课件型知识点/07_排序.md |
| sorting-tf-001 | true_false | easy | Heap sort is stable | false | 01_课件型知识点/07_排序.md |
| sorting-tf-002 | true_false | medium | Merge sort worst case is `O(n log n)` | true | 01_课件型知识点/07_排序.md |

- [ ] **Step 5: Run the generation tests and verify GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest course_assets/data_structures/tests/test_data_structures_quiz.py -q
```

Expected: all generation tests pass.

- [ ] **Step 6: Commit quiz generation**

```powershell
git add -- course_assets/data_structures/tools/data_structures_quiz.py course_assets/data_structures/tests/test_data_structures_quiz.py
git commit -m "feat: add structured data structures quiz generator"
```

### Task 3: Implement deterministic grading

**Files:**
- Modify: `course_assets/data_structures/tools/data_structures_quiz.py`
- Modify: `course_assets/data_structures/tests/test_data_structures_quiz.py`

**Interfaces:**
- Consumes: question IDs and answers produced by Task 2.
- Produces: `Tools.grade_quiz(answers_json: str) -> str` with all-or-nothing validation and deterministic percentage scoring.

- [ ] **Step 1: Add failing grading tests**

```python
def test_grade_quiz_normalizes_answers_and_returns_explanations():
    result = json.loads(Tools().grade_quiz(json.dumps({
        "answers": {
            "graph-sc-001": " c ",
            "graph-tf-001": "错误",
            "sorting-tf-001": "对",
            "list-sc-001": "",
        }
    }, ensure_ascii=False)))
    assert result["score"] == 75
    assert result["correct_count"] == 3
    assert result["total"] == 4
    assert [item["correct"] for item in result["results"]] == [True, True, False, False]
    assert all(item["correct_answer"] for item in result["results"])
    assert all(item["explanation"] for item in result["results"])
    assert all(item["source"] for item in result["results"])


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ("not-json", "合法 JSON"),
        ('{"answers": {}}', "不能为空"),
        ('{"answers": {"missing-id": "A"}}', "missing-id"),
        ('{"answers":{"graph-sc-001":"A","graph-sc-001":"C"}}', "重复"),
    ],
)
def test_grade_quiz_rejects_the_entire_invalid_submission(payload, message):
    result = json.loads(Tools().grade_quiz(payload))
    assert set(result) == {"error"}
    assert message in result["error"]
```

- [ ] **Step 2: Run the focused grading tests and observe RED**

```powershell
.\.venv\Scripts\python.exe -m pytest course_assets/data_structures/tests/test_data_structures_quiz.py -q -k grade
```

Expected: FAIL with `AttributeError: 'Tools' object has no attribute 'grade_quiz'`.

- [ ] **Step 3: Implement duplicate-aware JSON parsing and answer normalization**

Use `json.loads(answers_json, object_pairs_hook=...)` with a helper that raises a private validation exception when a key repeats. Normalize single-choice answers with `strip().upper()`. Normalize true/false answers with this exact mapping:

```python
TRUE_FALSE_ANSWERS = {
    "true": "true", "正确": "true", "对": "true",
    "false": "false", "错误": "false", "错": "false",
}
```

Reject malformed JSON, a non-object root, a non-object or empty `answers`, repeated keys, and unknown IDs before calculating any score.

- [ ] **Step 4: Implement the public grading method**

```python
def grade_quiz(
    self,
    answers_json: str = Field(
        ...,
        description='JSON 对象字符串，例如 {"answers":{"graph-sc-001":"A"}}',
    ),
) -> str:
```

Preserve input answer order in `results`. Return `score`, `correct_count`, `total`, and for every answer return `question_id`, `correct`, `student_answer`, `correct_answer`, `explanation`, and `source`. Calculate `score` as `round(correct_count / total * 100)`.

- [ ] **Step 5: Run all tool tests and verify GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest course_assets/data_structures/tests/test_data_structures_quiz.py -q
```

Expected: all tests pass.

- [ ] **Step 6: Format and compile the tool**

```powershell
.\.venv\Scripts\python.exe -m ruff format course_assets/data_structures/tools/data_structures_quiz.py course_assets/data_structures/tests
.\.venv\Scripts\python.exe -m py_compile course_assets/data_structures/tools/data_structures_quiz.py
```

Expected: both commands exit 0.

- [ ] **Step 7: Commit deterministic grading**

```powershell
git add -- course_assets/data_structures/tools/data_structures_quiz.py course_assets/data_structures/tests/test_data_structures_quiz.py
git commit -m "feat: grade data structures quizzes deterministically"
```

### Task 4: Configure the live Open WebUI course assistant

**Files:**
- Modify: `course_assets/data_structures/config/open_webui_setup.md`

**Interfaces:**
- Consumes: the system prompt, knowledge files, and tool source from Tasks 1–3 plus a user-entered rotated API key.
- Produces: a live Open WebUI connection, knowledge collection, imported tool, custom model, and a completed secret-free configuration record.

- [ ] **Step 1: Verify the local services without exposing credentials**

Open PowerShell terminal A from the isolated worktree, then start the backend:

```powershell
Set-Location (git rev-parse --show-toplevel)
.\.venv\Scripts\Activate.ps1
$env='true'
$env:ENV='dev'
python -m uvicorn open_webui.main:app --host 127.0.0.1 --port 8080 --reload --app-dir backend
```

Open PowerShell terminal B from the same isolated worktree, then start the frontend:

```powershell
Set-Location (git rev-parse --show-toplevel)
npm run dev
```

Expected: backend health responds and the frontend loads locally. If the frontend chooses a port other than 5173, record the displayed URL.

- [ ] **Step 2: Configure ModelArk in the admin UI**

In Admin Settings, add an OpenAI-compatible connection with:

```text
Base URL: https://ark.cn-beijing.volces.com/api/v3
API Key: enter the newly rotated key directly in the UI
```

Fetch the model list once. Select `deepseek-v4-flash` only if that exact identifier appears. If it does not appear, copy the exact identifier from the ModelArk console, update the setup record, and use that identifier without changing source code.

Send one non-retrieval test message: `只回复：模型连接成功`.

Expected: one successful response and one corresponding request in the ModelArk usage log. Do not automatically retry a failure.

- [ ] **Step 3: Import the knowledge collection**

Create Workspace → Knowledge collection `数据结构课程知识库`. Upload all 18 files under `course_assets/data_structures/knowledge_base`, preserving the source filenames.

Expected: collection shows 18 processed files and no pending or failed file. Ask `Dijkstra能否处理负权边？` in the collection test box and verify the returned result includes `01_课件型知识点/05_图.md`.

- [ ] **Step 4: Import the Workspace Tool**

Create Workspace → Tools item:

```text
ID: data_structures_quiz
Name: 数据结构练习与判分
Description: 按章节生成数据结构客观题并确定性判分
Content: exact contents of course_assets/data_structures/tools/data_structures_quiz.py
```

Expected: Open WebUI recognizes exactly two callable functions: `generate_quiz` and `grade_quiz`.

- [ ] **Step 5: Create and bind the custom model**

Create Workspace → Models item:

```text
Name: 数据结构 AI 助教
Base model: deepseek-v4-flash (or the exact verified ModelArk identifier)
System prompt: exact contents of course_assets/data_structures/config/system_prompt.md
Knowledge: 数据结构课程知识库
Tool: data_structures_quiz
```

Expected: the custom model is selectable in a new chat and its details show both the knowledge collection and tool.

- [ ] **Step 6: Verify one RAG answer and one complete tool cycle**

Run these prompts in a new chat:

```text
为什么Dijkstra算法不能直接处理负权边？请引用课程资料。
```

```text
调用练习工具，从“图”章节生成2道混合题，难度不限。
```

Submit answers using the returned IDs:

```text
调用判分工具批改这些答案：{"题目ID1":"A","题目ID2":"错误"}
```

Expected: the first response cites the graph file; the second visibly calls `generate_quiz` without revealing answers; the third calls `grade_quiz` and preserves its score.

- [ ] **Step 7: Replace setup statuses with factual results and commit**

Update only the status lines and add a dated error summary if a step failed. Never paste tokens, keys, request headers, or full provider responses.

```powershell
git add -- course_assets/data_structures/config/open_webui_setup.md
git commit -m "docs: record data structures assistant setup"
```

### Task 5: Execute and record the required evaluation

**Files:**
- Create: `course_assets/data_structures/evaluation/test_cases.md`
- Create: `course_assets/data_structures/evaluation/optimization_comparison.md`

**Interfaces:**
- Consumes: the live assistant from Task 4.
- Produces: 15 factual test records and five before/after comparisons suitable for the course submission.

- [ ] **Step 1: Run and record the five knowledge questions**

Use exactly these prompts:

1. `什么是线性表？顺序表和单链表在随机访问方面有什么区别？`
2. `循环队列采用牺牲一个存储单元时，判空、判满和元素个数公式分别是什么？`
3. `二叉树的前序、中序、后序和层序遍历顺序分别是什么？`
4. `邻接矩阵和邻接表分别适合什么类型的图？`
5. `比较快速排序、堆排序和归并排序的最坏时间复杂度与稳定性。`

For each record: prompt, complete actual response, cited files, citation correctness, answer correctness, observed issue, and concrete improvement. A passing record must cite the matching chapter file.

- [ ] **Step 2: Run and record the three analysis questions**

1. `如果系统需要频繁按下标读取、很少插入删除，应该选择顺序表还是链表？结合复杂度解释。`
2. `比较Prim与Kruskal的核心思路，并说明它们分别更适合哪类图。`
3. `为什么二叉搜索树的查找性能可能从O(log n)退化为O(n)？如何从树形结构理解？`

- [ ] **Step 3: Run and record the two unknown-knowledge questions**

1. `请根据课程资料解释B+树节点分裂的完整实现步骤。`
2. `请根据课程资料给出红黑树删除修复的全部情况。`

Expected: both explicitly state `当前课程资料中未找到足够依据，我无法确认该答案。` and do not invent a source.

- [ ] **Step 4: Run and record the four exercise/tool tasks**

1. `从“栈与队列”生成3道简单单选题。`
2. `批改上一组题目：提交三个返回ID及答案，其中一个故意答错。`
3. `必须调用generate_quiz，从“排序”生成2道判断题。`
4. `必须调用grade_quiz，提交一个正确答案和一个错误答案，并解释薄弱点。`

Expected: every task shows the appropriate tool call; generation hides answers; grading score equals the deterministic tool output.

- [ ] **Step 5: Run and record the error-input task**

```text
调用练习工具，从“图”章节生成20道essay题。
```

Expected: the tool rejects `essay` and/or count 20 with allowed values and does not fabricate questions.

- [ ] **Step 6: Create the completed 15-record report**

Write `test_cases.md` only after the live runs. Include a summary table with category, pass/fail, citation result, tool-call result, and issue; follow it with all 15 full records. Calculate pass rate as `passed / 15 * 100%` from the recorded results.

- [ ] **Step 7: Run and record the five before/after comparisons**

Use these five prompts for both configurations:

1. `Dijkstra为什么不能处理负权边？`
2. `循环队列如何判断队满？`
3. `帮我完成整份线性表实验并直接给出完整实验报告。`
4. `根据课程资料解释红黑树删除修复。`
5. `从图章节生成2道题并在我回答后判分。`

“Before” uses only the verified base model. “After” uses the custom model with prompt, knowledge, and tool. Record full outputs, actual sources, hallucination behavior, academic-integrity behavior, tool calls, and a justified winner for every row.

- [ ] **Step 8: Commit only factual evaluation artifacts**

```powershell
git add -- course_assets/data_structures/evaluation/test_cases.md course_assets/data_structures/evaluation/optimization_comparison.md
git commit -m "test: record data structures assistant evaluation"
```

### Task 6: Run regression checks and prepare the implementation report

**Files:**
- Verify: all files under `course_assets/data_structures/`
- Verify: no unrelated Open WebUI source changes in this feature branch

**Interfaces:**
- Consumes: Tasks 1–5.
- Produces: verified Git history and the final implementation report.

- [ ] **Step 1: Run all course automation tests**

```powershell
.\.venv\Scripts\python.exe -m pytest course_assets/data_structures/tests -q
```

Expected: all course tests pass with zero warnings caused by course files.

- [ ] **Step 2: Run Python formatting and compilation checks**

```powershell
.\.venv\Scripts\python.exe -m ruff format --check course_assets/data_structures/tools course_assets/data_structures/tests
.\.venv\Scripts\python.exe -m py_compile course_assets/data_structures/tools/data_structures_quiz.py
```

Expected: both commands exit 0.

- [ ] **Step 3: Repeat the credential scan**

```powershell
rg -n 'ark-[A-Za-z0-9-]{12,}' course_assets docs/superpowers
```

Expected: no matches and `rg` exit code 1, meaning no credential-like token was found.

- [ ] **Step 4: Inspect the complete feature diff and history**

```powershell
git status --short
git diff --check HEAD~4..HEAD
git diff --stat HEAD~4..HEAD
git log --oneline -6
```

Expected: `git diff --check` exits 0; feature commits contain only course assets, tests, setup records, evaluation records, and the approved spec/plan.

- [ ] **Step 5: Produce the implementation report**

Report delivered behavior, exact files, automated test commands and results, the 15-test pass rate, before/after findings, live ModelArk verification status, Git commits, known limitations, and any baseline failures separately. Do not claim the live assistant is complete if Task 4 or Task 5 has not been executed successfully.
