# Key Events Extraction Prompt

## Task
Extract key events from a screenplay scene. Key events are the 3-5 most important dramatic moments that advance the plot or reveal character.

## Input
You will receive:
- **Scene ID**: The scene identifier (e.g., "S01")
- **Scene Text**: Full text of the scene
- **Characters**: List of characters in the scene

## Output Format
Return ONLY a JSON array with this structure:
```json
{
  "key_events": [
    "First key event description",
    "Second key event description",
    "Third key event description"
  ]
}
```

## Guidelines

### What is a Key Event?

A key event is a significant plot point or character moment that:
1. **Advances the story** - Something happens that changes the situation
2. **Reveals character** - Shows who characters are through action or decision
3. **Creates conflict** - Introduces or escalates tension
4. **Provides information** - Delivers crucial story information
5. **Turns the scene** - Changes the direction of the scene

### Selection Criteria:

**YES - Include these:**
- Major decisions or commitments
- Revelations or discoveries
- Confrontations or conflicts
- Turning points in relationships
- Introduction of key objects or information

**NO - Exclude these:**
- Minor dialogue exchanges
- Setting descriptions
- Transitional moments
- Repeated information
- Trivial actions

### How Many Events?

- **Minimum**: 1 (even simple scenes have at least one key moment)
- **Typical**: 3-5 events
- **Maximum**: 7 (if scene is very complex)

**Quality over quantity** - Better to have 3 important events than 7 trivial ones.

### How to Write Each Event:

1. **Be specific**: Include WHO does WHAT
   - ✅ "玉鼠精向悟空提出尽职调查委托"
   - ❌ "角色提出请求"

2. **Be concise**: 10-20 words per event
   - ✅ "悟空发现仓库里全是假货，怀疑玉鼠精欺诈"
   - ❌ "悟空走进仓库，看到很多箱子，打开其中一个，发现里面的商品都是假的，他感到很震惊，开始怀疑玉鼠精的诚信"

3. **Use action verbs**: Focus on what happens
   - ✅ "哪吒撬开仓库门锁"
   - ❌ "仓库的门被打开了"

4. **Chronological order**: List events in the order they occur

5. **Use Chinese**: Write in Chinese for Chinese scripts

## Examples

### Example 1: Business Proposal Scene

**Input:**
```
Scene: S01 - 酒吧 - 夜
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

**Output:**
```json
{
  "key_events": [
    "玉鼠精突然出现，主动找悟空",
    "玉鼠精向悟空提出尽职调查业务委托",
    "悟空最初拒绝，声称不接私活",
    "玉鼠精展示商业计划书，提到一亿融资规模",
    "悟空开始对项目产生兴趣，询问更多细节"
  ]
}
```

### Example 2: Investigation Scene

**Input:**
```
Scene: S03 - 仓库 - 日
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
  "key_events": [
    "悟空和哪吒找到玉鼠精的仓库",
    "哪吒撬开锁，两人进入仓库",
    "悟空打开箱子，发现里面全是假货",
    "悟空意识到玉鼠精可能在欺骗投资人",
    "悟空决定直接找玉鼠精对质"
  ]
}
```

### Example 3: Simple Dialogue Scene

**Input:**
```
Scene: S02 - 办公室 - 日
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
  "key_events": [
    "悟空研究玉鼠精的商业计划书",
    "哪吒得知悟空在评估玉鼠精的项目",
    "哪吒透露玉鼠精公司仓库可能有问题",
    "悟空决定去仓库实地调查"
  ]
}
```

## Extraction Strategy:

Follow this process to identify key events:

1. **Read the entire scene** - Don't miss late-scene turning points
2. **Identify the scene arc**:
   - Where does it start? (situation)
   - What changes? (events)
   - Where does it end? (new situation)
3. **Mark dramatic moments**:
   - New information revealed
   - Decisions made
   - Conflicts escalating
   - Objects introduced
   - Relationship shifts
4. **Select 3-5 most important** - Not everything is key
5. **Write in chronological order** - As they appear in the scene

## Important Rules:

1. **Minimum 1, typically 3-5, maximum 7** events
2. **Chronological order** - List as they occur in the scene
3. **Specific and concise** - 10-20 words each
4. **Use Chinese** - Write in Chinese for Chinese scripts
5. **Focus on action** - What happens, not how it feels
6. **No duplication** - Each event should be distinct

## Common Mistakes to Avoid:

❌ **Too vague**: "角色对话" → ✅ **Be specific**: "哪吒透露仓库有假货"

❌ **Too detailed**: "悟空走进房间，坐下来，拿起文件，慢慢翻阅，发现了一个细节" → ✅ **Be concise**: "悟空发现商业计划书中的疑点"

❌ **Including trivial actions**: "角色喝咖啡", "角色走进房间" → ✅ **Focus on plot**: "角色做出重要决定"

❌ **Describing emotions**: "角色感到惊讶" → ✅ **Describe events**: "角色发现秘密"

❌ **Wrong order**: Listing events out of sequence → ✅ **Chronological**: As they appear in scene

## Important Notes:
- **Only return JSON** - No explanatory text before or after
- **Array must not be empty** - Every scene has at least one key event
- **Be selective** - Not every action is a key event
- **Quality matters** - Choose the most dramatic and plot-relevant moments
- **Use active voice** - "角色做X" not "X被做"

---

Now extract the key events from the provided scene.
