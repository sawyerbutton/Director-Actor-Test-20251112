# Scene Mission Extraction Prompt

## Task
Extract the scene mission (场景目标) from a screenplay scene. The scene mission is the primary dramatic objective that drives the scene forward.

## Input
You will receive:
- **Scene ID**: The scene identifier (e.g., "S01")
- **Scene Setting**: Location and time (e.g., "酒吧 - 夜")
- **Scene Text**: Full text of the scene including dialogue and action

## Output Format
Return ONLY a JSON object with this structure:
```json
{
  "scene_mission": "string describing the scene's dramatic objective"
}
```

## Guidelines

### What is a Scene Mission?
A scene mission is the primary dramatic question or objective that the scene is trying to achieve. It should be:
1. **Specific**: Not vague or generic
2. **Actionable**: Describes what characters are trying to accomplish
3. **Dramatic**: Focuses on conflict, decision, or revelation
4. **Concise**: One clear sentence (20-50 words)

### Good Examples:
- "悟空必须决定是否接受玉鼠精的尽职调查委托"
- "哪吒向悟空透露玉鼠精公司存在问题的线索"
- "悟空发现仓库里的假货，怀疑玉鼠精欺诈"

### Bad Examples (Avoid):
- "角色对话" (Too vague)
- "悟空和玉鼠精在酒吧见面" (Only describes action, not dramatic objective)
- "场景展示了角色的情绪变化" (Too abstract)

### Extraction Strategy:
1. **Read the entire scene** - Don't just summarize the first few lines
2. **Identify the conflict** - What tension or decision drives the scene?
3. **Focus on the protagonist** - What is the main character trying to achieve?
4. **Look for turning points** - What changes by the end of the scene?
5. **Ignore non-essential details** - Focus on dramatic core, not setting details

## Example

### Input:
```
Scene ID: S01
Setting: 酒吧 - 夜
Text:
悟空坐在吧台，手里拿着一杯酒。玉鼠精从门口走了进来。

玉鼠精：悟空，好久不见！
悟空：（冷淡）你来干什么？
玉鼠精：我有个生意要和你谈。听说你现在在做尽职调查？
悟空：我不接私活。

玉鼠精坐在悟空旁边，拿出一份商业计划书。

玉鼠精：这次不一样，这是个大项目。电商平台，融资一个亿。
悟空：（看了一眼）你的平台？
玉鼠精：对，我花了三年时间做起来的。现在需要资金扩张。
```

### Output:
```json
{
  "scene_mission": "玉鼠精试图说服悟空接受她的电商平台尽职调查委托，悟空最初拒绝但开始产生兴趣"
}
```

## Important Notes:
- **Only return JSON** - Do not include any explanatory text before or after
- **Use Chinese** - Scene missions should be in Chinese for Chinese scripts
- **Be concise** - Aim for 20-50 words
- **Focus on drama** - Not just plot summary, but dramatic objective
- **Capture the arc** - If the scene has a turning point, include it

---

Now extract the scene mission from the provided scene.
