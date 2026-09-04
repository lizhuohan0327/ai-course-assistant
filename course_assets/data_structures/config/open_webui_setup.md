# Open WebUI 配置记录

## 模型连接
- 服务：火山方舟普通模型推理
- Base URL：https://ark.cn-beijing.volces.com/api/v3
- 模型：deepseek-v4-flash
- API Key：由管理员在本机界面填写，不保存到仓库
- 连通性：2026-09-05 已验证；模型列表包含 deepseek-v4-flash，单次连接测试成功

## 知识库
- 名称：数据结构课程知识库
- 源目录：course_assets/data_structures/knowledge_base
- 文件数：18
- 导入状态：2026-09-05 已导入，18 个文件均完成处理

## 自定义模型
- 名称：数据结构 AI 助教
- 基础模型：deepseek-v4-flash
- 知识库：数据结构课程知识库
- 工具：data_structures_quiz
- 创建状态：2026-09-05 已创建并绑定知识库与 data_structures_quiz 工具

## 验证记录
- 2026-09-05：RAG 回答命中 `05_图.md`，正确说明 Dijkstra 不适用于负权边。
- 2026-09-05：工具被识别为 2 个可调用函数；成功生成 2 道“图”章节题目，未提前泄漏答案。
- 2026-09-05：判分工具按返回的题目 ID 完成批改，示例答案得分为 100%（2/2）。
- 2026-09-05：首次生成练习时，省略的可选参数被旧版工具当作 Pydantic `FieldInfo`，导致随机种子类型错误；改用原生 Python 默认值、将 `chapter` 设为真正必填后复测通过。
