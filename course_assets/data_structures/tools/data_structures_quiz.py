"""
title: Data Structures Quiz Generator
author: Open WebUI
description: Generate structured practice questions from the packaged data structures course.
version: 1.0.0
license: MIT
"""

import json
import random

from pydantic import Field


_CHAPTERS = (
    "绪论与算法复杂度",
    "线性表",
    "栈与队列",
    "树与二叉树",
    "图",
    "查找与散列",
    "排序",
)
_QUESTION_TYPES = ("single_choice", "true_false", "mixed")
_DIFFICULTIES = ("easy", "medium", "hard", "mixed")
_PUBLIC_FIELDS = ("id", "chapter", "question_type", "difficulty", "question", "options")
TRUE_FALSE_ANSWERS = {
    "true": "true",
    "正确": "true",
    "对": "true",
    "false": "false",
    "错误": "false",
    "错": "false",
}


class _QuizValidationError(ValueError):
    pass


def _question(
    identifier: str,
    chapter: str,
    question_type: str,
    difficulty: str,
    question: str,
    options: dict[str, str],
    correct_answer: str | bool,
    explanation: str,
    source: str,
) -> dict:
    return {
        "id": identifier,
        "chapter": chapter,
        "question_type": question_type,
        "difficulty": difficulty,
        "question": question,
        "options": options,
        "correct_answer": correct_answer,
        "explanation": explanation,
        "source": source,
    }


QUESTION_BANK: tuple[dict, ...] = (
    _question("complexity-sc-001", "绪论与算法复杂度", "single_choice", "easy", "在线性结构中，除首尾元素外，每个元素通常具有什么关系？", {"A": "有多个直接前驱和后继", "B": "有且仅有一个直接前驱和一个直接后继", "C": "只存在一对多关系", "D": "元素之间没有关系"}, "B", "线性结构中，除首尾元素外，每个元素有且仅有一个直接前驱和一个直接后继。", "01_课件型知识点/01_绪论与算法复杂度.md"),
    _question("complexity-sc-002", "绪论与算法复杂度", "single_choice", "medium", "两层循环都从 1 执行到 n，循环体为常数时间操作，其时间复杂度是？", {"A": "O(1)", "B": "O(n)", "C": "O(n^2)", "D": "O(n log n)"}, "C", "两层各执行 n 次的嵌套循环共有约 n² 次常数操作。", "01_课件型知识点/01_绪论与算法复杂度.md"),
    _question("complexity-sc-003", "绪论与算法复杂度", "single_choice", "hard", "分析递归算法的空间复杂度时，除局部变量外还必须考虑什么？", {"A": "输入数据的物理地址", "B": "CPU 的主频", "C": "代码文件大小", "D": "递归调用栈空间"}, "D", "递归调用会占用调用栈，因此递归栈空间也属于额外空间。", "01_课件型知识点/01_绪论与算法复杂度.md"),
    _question("complexity-tf-001", "绪论与算法复杂度", "true_false", "easy", "渐进时间复杂度分析中通常保留最高阶项并忽略常数系数。", {}, True, "时间复杂度描述随问题规模增长的数量级，常数系数不影响渐进阶。", "01_课件型知识点/01_绪论与算法复杂度.md"),
    _question("complexity-tf-002", "绪论与算法复杂度", "true_false", "medium", "算法在某台机器上实际运行的秒数与它的时间复杂度完全等同。", {}, False, "实际秒数受机器和实现影响；时间复杂度描述规模增长时的数量级。", "01_课件型知识点/01_绪论与算法复杂度.md"),
    _question("list-sc-001", "线性表", "single_choice", "easy", "顺序表按下标随机访问元素的时间复杂度通常是？", {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n^2)"}, "A", "顺序表使用连续空间，按下标可直接定位元素。", "01_课件型知识点/02_线性表.md"),
    _question("list-sc-002", "线性表", "single_choice", "medium", "单链表按序号查找第 i 个元素的时间复杂度通常是？", {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n log n)"}, "C", "单链表需要从头结点沿指针逐个访问，按序号查找为 O(n)。", "01_课件型知识点/02_线性表.md"),
    _question("list-sc-003", "线性表", "single_choice", "hard", "在单链表中已知待插入位置的前驱节点时，插入操作的时间复杂度是？", {"A": "O(n^2)", "B": "O(n log n)", "C": "O(n)", "D": "O(1)"}, "D", "已知前驱后只需调整常数个指针。", "01_课件型知识点/02_线性表.md"),
    _question("list-tf-001", "线性表", "true_false", "easy", "链表节点在内存中的物理地址必须连续。", {}, False, "链式存储不要求节点的物理地址连续。", "01_课件型知识点/02_线性表.md"),
    _question("list-tf-002", "线性表", "true_false", "medium", "单链表维护尾指针时，表尾插入可达到 O(1)。", {}, True, "尾指针直接指向最后一个节点，避免了遍历查找表尾。", "01_课件型知识点/02_线性表.md"),
    _question("stack-queue-sc-001", "栈与队列", "single_choice", "easy", "栈遵循哪种访问原则？", {"A": "LIFO（后进先出）", "B": "FIFO（先进先出）", "C": "随机访问", "D": "按优先级访问"}, "A", "栈只在一端插入和删除，遵循后进先出。", "01_课件型知识点/03_栈与队列.md"),
    _question("stack-queue-sc-002", "栈与队列", "single_choice", "medium", "广度优先搜索（BFS）通常使用哪种数据结构？", {"A": "栈", "B": "队列", "C": "散列表", "D": "二叉搜索树"}, "B", "BFS 按发现先后扩展结点，因此使用队列。", "01_课件型知识点/05_图.md"),
    _question("stack-queue-sc-003", "栈与队列", "single_choice", "hard", "容量为 capacity 的牺牲一个存储单元的循环队列，其元素个数公式是？", {"A": "rear - front", "B": "(front - rear) % capacity", "C": "(rear - front + capacity) % capacity", "D": "(rear + front) % capacity"}, "C", "循环队列需加上 capacity 后取模以得到非负的队列长度。", "01_课件型知识点/03_栈与队列.md"),
    _question("stack-queue-tf-001", "栈与队列", "true_false", "easy", "队列遵循 FIFO（先进先出）原则。", {}, True, "队列从一端入队、另一端出队，最先进入的元素最先离开。", "01_课件型知识点/03_栈与队列.md"),
    _question("stack-queue-tf-002", "栈与队列", "true_false", "medium", "牺牲一个存储单元的循环队列中，队满条件与队空条件相同。", {}, False, "牺牲一个单元正是为了区分 front == rear 的队空状态和队满状态。", "01_课件型知识点/03_栈与队列.md"),
    _question("tree-sc-001", "树与二叉树", "single_choice", "easy", "二叉树前序遍历的访问顺序是？", {"A": "根、左、右", "B": "左、根、右", "C": "左、右、根", "D": "右、根、左"}, "A", "前序遍历先访问根节点，再访问左子树和右子树。", "01_课件型知识点/04_树与二叉树.md"),
    _question("tree-sc-002", "树与二叉树", "single_choice", "medium", "二叉树层序遍历通常使用哪种数据结构？", {"A": "栈", "B": "队列", "C": "并查集", "D": "散列表"}, "B", "层序遍历按从上到下、从左到右处理节点，通常使用队列。", "01_课件型知识点/04_树与二叉树.md"),
    _question("tree-sc-003", "树与二叉树", "single_choice", "hard", "二叉搜索树退化为链表时，查找的最坏时间复杂度是？", {"A": "O(1)", "B": "O(log n)", "C": "O(n log n)", "D": "O(n)"}, "D", "退化后的 BST 高度为 n，查找需要沿链逐个比较。", "01_课件型知识点/04_树与二叉树.md"),
    _question("tree-tf-001", "树与二叉树", "true_false", "easy", "二叉树的每个节点最多有两个孩子。", {}, True, "二叉树的孩子最多为左孩子和右孩子两个。", "01_课件型知识点/04_树与二叉树.md"),
    _question("tree-tf-002", "树与二叉树", "true_false", "medium", "哈夫曼编码是一种前缀编码。", {}, True, "任意哈夫曼编码都不会是另一个字符编码的前缀。", "01_课件型知识点/04_树与二叉树.md"),
    _question("graph-sc-001", "图", "single_choice", "easy", "使用邻接矩阵存储含 V 个顶点的图，空间复杂度是？", {"A": "O(V)", "B": "O(E)", "C": "O(V^2)", "D": "O(V+E)"}, "C", "邻接矩阵需要为每一对顶点保留一个矩阵位置。", "01_课件型知识点/05_图.md"),
    _question("graph-sc-002", "图", "single_choice", "medium", "Kruskal 算法通常用什么结构判断加入一条边后是否成环？", {"A": "队列", "B": "并查集", "C": "栈", "D": "哈夫曼树"}, "B", "Kruskal 按边权选边，并使用并查集判断端点是否已经连通。", "01_课件型知识点/05_图.md"),
    _question("graph-sc-003", "图", "single_choice", "hard", "Floyd 算法的时间复杂度是？", {"A": "O(V)", "B": "O(V log V)", "C": "O(V^2)", "D": "O(V^3)"}, "D", "Floyd 通过三重顶点循环更新所有顶点对的最短路径。", "01_课件型知识点/05_图.md"),
    _question("graph-tf-001", "图", "true_false", "easy", "经典 Dijkstra 算法可以直接处理带负权边的图。", {}, False, "Dijkstra 适用于边权非负的单源最短路径问题。", "01_课件型知识点/05_图.md"),
    _question("graph-tf-002", "图", "true_false", "medium", "拓扑排序无法输出全部顶点时，图中存在环。", {}, True, "拓扑排序适用于 DAG；不能输出全部顶点说明存在环。", "01_课件型知识点/05_图.md"),
    _question("search-hash-sc-001", "查找与散列", "single_choice", "easy", "使用折半查找的前提之一是数据必须？", {"A": "有序且适合随机访问", "B": "存储在链表中", "C": "元素互不相同", "D": "使用散列表存储"}, "A", "折半查找要求数据有序，并适合按中间位置随机访问。", "01_课件型知识点/06_查找与散列.md"),
    _question("search-hash-sc-002", "查找与散列", "single_choice", "medium", "散列表的装填因子 α 的正确表达式是？", {"A": "散列表容量 / 表中元素个数", "B": "表中元素个数 / 散列表容量", "C": "冲突次数 / 表中元素个数", "D": "桶数量 / 冲突次数"}, "B", "装填因子定义为表中元素个数除以散列表容量。", "01_课件型知识点/06_查找与散列.md"),
    _question("search-hash-sc-003", "查找与散列", "single_choice", "hard", "采用链地址法解决散列冲突时，每个桶通常维护什么？", {"A": "一个固定长度数组", "B": "一个递归调用栈", "C": "一个链表或其他容器", "D": "一个有序矩阵"}, "C", "链地址法让每个桶维护一个链表或其他容器以保存冲突元素。", "01_课件型知识点/06_查找与散列.md"),
    _question("search-hash-tf-001", "查找与散列", "true_false", "easy", "顺序查找可以用于无序表。", {}, True, "顺序查找逐项检查元素，适用于无序表。", "01_课件型知识点/06_查找与散列.md"),
    _question("search-hash-tf-002", "查找与散列", "true_false", "medium", "散列表装填因子越高，一般冲突概率越低。", {}, False, "装填因子越高，通常冲突概率越高。", "01_课件型知识点/06_查找与散列.md"),
    _question("sorting-sc-001", "排序", "single_choice", "easy", "下列关于插入排序的说法正确的是？", {"A": "插入排序是稳定的", "B": "插入排序最坏为 O(log n)", "C": "插入排序一定需要 O(n) 额外空间", "D": "插入排序通常不稳定"}, "A", "课程资料指出插入排序平均 O(n²) 且稳定。", "01_课件型知识点/07_排序.md"),
    _question("sorting-sc-002", "排序", "single_choice", "medium", "归并排序通常需要多少额外空间？", {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n^2)"}, "C", "归并排序需要额外 O(n) 空间来完成合并。", "01_课件型知识点/07_排序.md"),
    _question("sorting-sc-003", "排序", "single_choice", "hard", "快速排序的最坏时间复杂度是？", {"A": "O(1)", "B": "O(log n)", "C": "O(n log n)", "D": "O(n^2)"}, "D", "快速排序平均为 O(n log n)，最坏情况为 O(n²)。", "01_课件型知识点/07_排序.md"),
    _question("sorting-tf-001", "排序", "true_false", "easy", "堆排序是稳定排序。", {}, False, "堆排序会交换相同关键字元素的相对顺序，因此不稳定。", "01_课件型知识点/07_排序.md"),
    _question("sorting-tf-002", "排序", "true_false", "medium", "归并排序的最坏时间复杂度是 O(n log n)。", {}, True, "归并排序的平均和最坏时间复杂度均为 O(n log n)。", "01_课件型知识点/07_排序.md"),
)


def _error(message: str) -> str:
    return json.dumps({"error": message}, ensure_ascii=False)


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise _QuizValidationError(f"JSON 对象包含重复键：{key}。")
        result[key] = value
    return result


def _parse_answers(answers_json: str) -> dict[str, object]:
    try:
        submission = json.loads(answers_json, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, TypeError) as error:
        raise _QuizValidationError("提交内容必须是合法 JSON。") from error

    if not isinstance(submission, dict):
        raise _QuizValidationError("提交内容必须是 JSON 对象。")

    answers = submission.get("answers")
    if not isinstance(answers, dict) or not answers:
        raise _QuizValidationError("answers 不能为空，且必须是 JSON 对象。")
    return answers


def _normalize_answer(question: dict, answer: object) -> str:
    if not isinstance(answer, str):
        raise _QuizValidationError(f"题目 {question['id']} 的答案必须是字符串。")
    if question["question_type"] == "single_choice":
        return answer.strip().upper()
    return TRUE_FALSE_ANSWERS.get(answer.strip().lower(), answer.strip().lower())


def _display_correct_answer(question: dict) -> str:
    correct_answer = question["correct_answer"]
    if question["question_type"] == "true_false":
        return "true" if correct_answer else "false"
    return correct_answer


class Tools:
    def generate_quiz(
        self,
        chapter: str = Field(..., description="课程章节名称"),
        question_type: str = Field("mixed", description="single_choice、true_false 或 mixed"),
        difficulty: str = Field("mixed", description="easy、medium、hard 或 mixed"),
        count: int = Field(5, description="生成题目数量，范围 1 到 10"),
        seed: int | None = Field(None, description="可选随机种子，用于复现实验"),
    ) -> str:
        if chapter not in _CHAPTERS:
            return _error("请输入有效章节。")
        if question_type not in _QUESTION_TYPES:
            return _error("请输入有效题型。")
        if difficulty not in _DIFFICULTIES:
            return _error("请输入有效难度。")
        if not 1 <= count <= 10:
            return _error("题目数量必须在 1 到 10 之间。")

        candidates = [
            item
            for item in QUESTION_BANK
            if item["chapter"] == chapter
            and (question_type == "mixed" or item["question_type"] == question_type)
            and (difficulty == "mixed" or item["difficulty"] == difficulty)
        ]
        if count > len(candidates):
            return _error(f"请求数量超过实际可用数量（{len(candidates)}）。")

        questions = [
            {field: item[field] for field in _PUBLIC_FIELDS}
            for item in random.Random(seed).sample(candidates, count)
        ]
        return json.dumps({"questions": questions}, ensure_ascii=False)

    def grade_quiz(
        self,
        answers_json: str = Field(
            ...,
            description='JSON 对象字符串，例如 {"answers":{"graph-sc-001":"A"}}',
        ),
    ) -> str:
        try:
            answers = _parse_answers(answers_json)
            questions_by_id = {question["id"]: question for question in QUESTION_BANK}
            unknown_ids = [question_id for question_id in answers if question_id not in questions_by_id]
            if unknown_ids:
                raise _QuizValidationError(f"题目 ID 不存在：{unknown_ids[0]}。")

            results = []
            correct_count = 0
            for question_id, answer in answers.items():
                question = questions_by_id[question_id]
                student_answer = _normalize_answer(question, answer)
                correct_answer = _display_correct_answer(question)
                correct = student_answer == correct_answer
                correct_count += correct
                results.append(
                    {
                        "question_id": question_id,
                        "correct": correct,
                        "student_answer": student_answer,
                        "correct_answer": correct_answer,
                        "explanation": question["explanation"],
                        "source": question["source"],
                    }
                )
        except _QuizValidationError as error:
            return _error(str(error))

        total = len(results)
        return json.dumps(
            {
                "score": round(correct_count / total * 100),
                "correct_count": correct_count,
                "total": total,
                "results": results,
            },
            ensure_ascii=False,
        )
