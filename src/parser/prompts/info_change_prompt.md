# Information Change Extraction Prompt

## Task
Identify information changes (revelations, discoveries, decisions) in a screenplay scene. Information changes track how character knowledge and understanding evolves.

## Input
You will receive:
- **Scene ID**: The scene identifier (e.g., "S01")
- **Scene Text**: Full text of the scene
- **Characters**: List of characters in the scene

## Output Format
Return ONLY a JSON array with this structure:
```json
{
  "info_changes": [
    {
      "character": "角色名",
      "learned": "What information this character learned (minimum 5 characters)"
    }
  ]
}
```

## Guidelines

### What is an Information Change?

Information change occurs when a character's knowledge, understanding, or decision state shifts:

**Four Categories:**

1. **revelation** (揭示): New information is revealed TO a character by another character
   - Example: "哪吒告诉悟空仓库有问题"
   - Key: Information comes FROM another character

2. **discovery** (发现): Character discovers information through observation or investigation
   - Example: "悟空发现箱子里是假货"
   - Key: Character finds out themselves through action

3. **decision** (决策): Character makes a choice or commitment
   - Example: "悟空决定去仓库调查"
   - Key: Character commits to a course of action

4. **realization** (领悟): Character understands something that was implicit before
   - Example: "悟空意识到玉鼠精可能在欺骗投资人"
   - Key: Character connects dots, has an "aha" moment

### When to Record an Info Change:

**YES - Record these:**
- Character learns new factual information
- Character makes a significant decision
- Character realizes something important
- Character's understanding of a situation shifts

**NO - Don't record these:**
- Small talk or trivial information
- Information the character already knew
- Emotional reactions without new knowledge
- Setting or atmosphere descriptions

### How to Fill Each Field:

1. **character**: The character whose information state changes
   - Use exact name as it appears in the scene
   - One character per info change

2. **learned**: Brief description of what the character learned
   - Minimum 5 characters, typically 10-30 words
   - Be specific about WHAT information
   - Use Chinese for Chinese scripts
   - Include the type implicitly: what they discovered, were told, decided, or realized
   - Examples:
     - "玉鼠精的仓库可能有问题" (revelation)
     - "箱子里全是假货" (discovery)
     - "决定去仓库调查" (decision)
     - "意识到玉鼠精可能在欺骗投资人" (realization)

## Examples

### Example 1: Multiple Info Changes

**Input:**
```
Scene: S02
Characters: ["悟空", "哪吒"]
Text:
悟空坐在办公桌前，仔细翻阅着玉鼠精的商业计划书。

哪吒推门进来，手里拿着咖啡。

哪吒：你在看什么这么认真？
悟空：一个朋友的项目，电商平台。
哪吒：（好奇）哪个朋友？
悟空：玉鼠精。你记得她吗？
哪吒：（皱眉）当然记得。她靠谱吗？

悟空没有回答，继续翻看计划书。

哪吒：我听说她的公司有些问题。仓库那边好像有点猫腻。
悟空：（抬起头）什么猫腻？
哪吒：不太清楚，只是听说。你要不要去查查？
```

**Output:**
```json
{
  "info_changes": [
    {
      "character": "悟空",
      "learned": "哪吒告知玉鼠精公司的仓库可能有问题"
    },
    {
      "character": "悟空",
      "learned": "决定去仓库调查"
    }
  ]
}
```

### Example 2: Discovery

**Input:**
```
Scene: S03
Characters: ["悟空", "哪吒"]
Text:
悟空和哪吒来到一个偏僻的仓库。大门紧锁，周围很安静。

悟空：这就是玉鼠精的仓库？
哪吒：应该是。地址在计划书上写着。
悟空：（试图推门）锁着。

哪吒掏出工具，几下就把锁撬开了。

哪吒：进去看看。

两人走进仓库，里面堆满了箱子。悟空打开其中一个箱子。

悟空：（震惊）这些都是假货！
哪吒：我就说有问题吧。玉鼠精在骗投资人。
悟空：（沉默）我得找她问清楚。
```

**Output:**
```json
{
  "info_changes": [
    {
      "character": "悟空",
      "learned": "发现仓库里存放的是假货而非真实商品"
    },
    {
      "character": "悟空",
      "learned": "意识到玉鼠精可能在欺骗投资人"
    },
    {
      "character": "悟空",
      "learned": "决定直接找玉鼠精对质"
    }
  ]
}
```

### Example 3: No Info Changes

**Input:**
```
Scene: S05
Characters: ["悟空", "哪吒"]
Text:
悟空：今天天气真好。
哪吒：是啊，阳光明媚。
悟空：要不要出去走走？
哪吒：好主意。
```

**Output:**
```json
{
  "info_changes": []
}
```

## Category Decision Tree:

Use this to choose the correct category:

```
Is information changing for a character?
├─ YES → Continue
└─ NO → Don't record

How did the character get the information?
├─ Another character told them → revelation
├─ They discovered it through action → discovery
├─ They made a choice → decision
└─ They connected dots/understood → realization
```

## Important Rules:

1. **One info change per character per piece of information**
   - If multiple characters learn the same thing, create separate entries
   - If one character learns multiple things, create separate entries

2. **Be specific in descriptions**
   - ❌ "角色获得新信息" (too vague)
   - ✅ "悟空得知仓库有假货" (specific)

3. **Match category to source**
   - Told by someone → revelation
   - Found themselves → discovery
   - Made a choice → decision
   - Understood implicitly → realization

4. **Use evidence from the scene**
   - Always include a direct quote or specific action
   - Evidence should prove the info change happened

5. **Empty array is valid**
   - If no information changes, return `[]`

## Common Mistakes to Avoid:

❌ **Confusing revelation and discovery**
- revelation: "哪吒告诉悟空有问题"
- discovery: "悟空自己发现有问题"

❌ **Recording emotions instead of information**
- ❌ "悟空感到震惊"
- ✅ "悟空发现假货"

❌ **Too vague**
- ❌ "角色获得信息"
- ✅ "悟空得知玉鼠精的仓库存在造假行为"

❌ **Missing evidence**
- ❌ No quote provided
- ✅ "悟空：（震惊）这些都是假货！"

## Important Notes:
- **Only return JSON** - No explanatory text
- **Empty array is valid** - Use `[]` when no info changes
- **Use Chinese** - All descriptions in Chinese for Chinese scripts
- **Be precise** - Each info change should be distinct and meaningful
- **Focus on knowledge** - What does the character know now that they didn't before?

---

Now extract information changes from the provided scene.
