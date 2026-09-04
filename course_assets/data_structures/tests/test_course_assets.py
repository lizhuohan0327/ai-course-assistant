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


def test_system_prompt_makes_knowledge_abstention_exclusive():
    prompt = (COURSE_ROOT / "config" / "system_prompt.md").read_text(encoding="utf-8")
    assert "未找到足够依据时只能输出固定拒答语" in prompt
    assert "不得补充课程外的通用知识" in prompt


def test_system_prompt_rejects_complete_assignment_deliverables():
    prompt = (COURSE_ROOT / "config" / "system_prompt.md").read_text(encoding="utf-8")
    assert "拒绝一次性输出可直接提交的完整作业或实验报告" in prompt
    assert "只能提供提纲、提示、伪代码和分步指导" in prompt


def test_course_assets_do_not_contain_api_keys():
    credential_pattern = re.compile(r"ark-[A-Za-z0-9-]{12,}")
    text_extensions = {".md", ".cpp", ".py"}
    for path in COURSE_ROOT.rglob("*"):
        if path.is_file() and path.suffix in text_extensions:
            assert credential_pattern.search(path.read_text(encoding="utf-8")) is None
