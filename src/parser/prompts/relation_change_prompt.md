# Relation Change Extraction Prompt

## Task
Identify relationship changes between characters in a screenplay scene. Relation changes track how character dynamics evolve throughout the story.

## Input
You will receive:
- **Scene ID**: The scene identifier (e.g., "S01")
- **Scene Text**: Full text of the scene
- **Characters**: List of characters in the scene

## Output Format
Return ONLY a JSON array with this structure:
```json
{
  "relation_changes": [
    {
      "chars": ["角色A", "角色B"],
      "from": "Initial relationship state",
      "to": "Changed relationship state"
    }
  ]
}
```

## Guidelines

### What is a Relation Change?

A relation change occurs when the dynamic between two (or more) characters shifts in a meaningful way:

**Types of Changes:**
1. **Trust**: Building or losing trust
2. **Conflict**: Escalation or de-escalation of tension
3. **Alliance**: Forming or breaking partnerships
4. **Intimacy**: Emotional closeness or distance
5. **Power**: Shifting dominance or equality
6. **Knowledge**: One character learns something about another

### When to Record a Change:

**YES - Record these:**
- A character reveals new information that changes another's perception
- Conflict escalates from calm to tense
- Trust is broken or established
- Characters form an alliance or partnership
- Power dynamic shifts (e.g., from equal to dominant/submissive)

**NO - Don't record these:**
- Small talk or casual conversation without emotional impact
- Relationship state that doesn't change during the scene
- Background information that doesn't affect current dynamics

### How to Fill Each Field:

1. **chars**: Array of character names (must be exactly 2 characters)
   - Use exact names as they appear in the scene
   - Order doesn't matter

2. **from**: Brief description of relationship state at scene start
   - Examples: "陌生人", "老朋友但疏远", "信任的伙伴", "敌对关系"
   - Keep it 3-15 words (minimum 2 characters)

3. **to**: Brief description of relationship state at scene end
   - Examples: "产生怀疑", "建立初步信任", "关系紧张", "达成合作"
   - Keep it 3-15 words (minimum 2 characters)

## Examples

### Example 1: Trust Building

**Input:**
```
Scene: S01
Characters: ["悟空", "玉鼠精"]
Text:
玉鼠精：悟空，好久不见！
悟空：（冷淡）你来干什么？
玉鼠精：我有个生意要和你谈。听说你现在在做尽职调查？
悟空：我不接私活。

玉鼠精坐在悟空旁边，拿出一份商业计划书。

玉鼠精：这次不一样，这是个大项目。电商平台，融资一个亿。
悟空：（看了一眼）你的平台？
玉鼠精：对，我花了三年时间做起来的。现在需要资金扩张。
```

**Output:**
```json
{
  "relation_changes": [
    {
      "chars": ["悟空", "玉鼠精"],
      "from": "老朋友但疏远冷淡",
      "to": "悟空开始对项目产生兴趣"
    }
  ]
}
```

### Example 2: Trust Broken

**Input:**
```
Scene: S03
Characters: ["悟空", "哪吒"]
Text:
悟空打开其中一个箱子。

悟空：（震惊）这些都是假货！
哪吒：我就说有问题吧。玉鼠精在骗投资人。
悟空：（沉默）我得找她问清楚。
```

**Output:**
```json
{
  "relation_changes": [
    {
      "chars": ["悟空", "玉鼠精"],
      "from": "潜在的合作关系",
      "to": "悟空对玉鼠精产生怀疑"
    }
  ]
}
```

### Example 3: No Change

**Input:**
```
Scene: S04
Characters: ["悟空", "哪吒"]
Text:
悟空：今天天气不错。
哪吒：是啊，要不要去喝咖啡？
悟空：好啊。
```

**Output:**
```json
{
  "relation_changes": []
}
```

## Important Rules:

1. **Only record actual changes** - If the relationship is static, return empty array `[]`
2. **One change per character pair** - Don't duplicate the same relationship change
3. **Be specific in evidence** - Use quotes or specific actions, not vague descriptions
4. **Before/after must differ** - If they're the same, there's no change
5. **Consider subtext** - Sometimes the change is in what's NOT said
6. **Multiple pairs possible** - A scene with 3 characters can have multiple relationship changes

## Common Mistakes to Avoid:

❌ **Too vague**: "关系变化" → ✅ **Be specific**: "从信任到怀疑"
❌ **No evidence**: Using generic descriptions → ✅ **Use quotes**: Direct dialogue or action
❌ **Recording static states**: Describing existing relationships without change → ✅ **Only record changes**
❌ **Before = After**: "朋友" → "朋友" → ✅ **Must be different**: "朋友" → "产生分歧的朋友"

## Important Notes:
- **Only return JSON** - No explanatory text before or after
- **Empty array is valid** - Use `[]` when no changes occur
- **Use Chinese** - All descriptions should be in Chinese for Chinese scripts
- **Be concise** - Each field should be brief and specific
- **Focus on drama** - Only record meaningful changes, not trivial interactions

---

Now extract relation changes from the provided scene.
