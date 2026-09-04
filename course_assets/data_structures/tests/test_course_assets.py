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
