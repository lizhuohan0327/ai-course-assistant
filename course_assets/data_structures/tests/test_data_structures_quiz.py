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
