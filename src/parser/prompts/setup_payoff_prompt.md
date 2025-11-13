# Setup-Payoff Relationship Extraction Prompt

## Task
Identify setup-payoff relationships for a given scene within a screenplay. Setup-payoff is a narrative technique where information or objects introduced in one scene (setup) become significant later (payoff).

## Input
You will receive:
- **Current Scene ID**: The scene being analyzed (e.g., "S02")
- **Current Scene Text**: Full text of the current scene
- **All Scenes**: List of all scenes with their IDs, settings, and text

## Output Format
Return ONLY a JSON object with this structure:
```json
{
  "setup_for": ["S03", "S05"],
  "payoff_from": ["S01"]
}
```

- **setup_for**: Array of scene IDs where this scene sets up future events
- **payoff_from**: Array of scene IDs that this scene pays off from

## Guidelines

### What is Setup-Payoff?

**Setup** establishes:
- Objects that will become important later (e.g., a gun, a document, a key)
- Information that will be revealed or used later
- Relationships that will change
- Promises or commitments that will be tested
- Questions that will be answered

**Payoff** resolves:
- Previously introduced objects are used
- Foreshadowed information becomes relevant
- Questions are answered
- Promises are tested or broken

### Identification Strategy:

1. **For setup_for (What does this scene setup?):**
   - Scan current scene for new objects, information, or promises
   - Read subsequent scenes (higher scene IDs)
   - Find where these items become significant
   - Add those scene IDs to `setup_for`

2. **For payoff_from (What does this scene payoff?):**
   - Identify key objects, information, or resolutions in current scene
   - Read previous scenes (lower scene IDs)
   - Find where these were first introduced
   - Add those scene IDs to `payoff_from`

### Examples:

**Example 1: Object Setup-Payoff**
- S01: Character shows a business plan document (SETUP)
- S02: Character reviews the document carefully (PAYOFF from S01)
- S01 → `setup_for: ["S02"]`
- S02 → `payoff_from: ["S01"]`

**Example 2: Information Setup-Payoff**
- S02: Character mentions warehouse has problems (SETUP)
- S03: Characters go investigate the warehouse (PAYOFF from S02, SETUP for S04)
- S04: They discover counterfeit goods (PAYOFF from S03)
- S02 → `setup_for: ["S03"]`
- S03 → `payoff_from: ["S02"]`, `setup_for: ["S04"]`
- S04 → `payoff_from: ["S03"]`

**Example 3: No Relationships**
- S01: Standalone introduction scene with no future references
- S01 → `setup_for: []`, `payoff_from: []`

### Important Rules:

1. **Only include direct relationships** - Don't list every scene, only those with clear causal connections
2. **Be conservative** - When in doubt, omit rather than include weak connections
3. **Check scene order** - setup_for should reference later scenes, payoff_from should reference earlier scenes
4. **Empty arrays are valid** - If no relationships exist, use `[]`
5. **Multiple relationships are common** - A scene can setup multiple future scenes or payoff multiple past scenes

## Example

### Input:
```
Current Scene: S02
Current Scene Text:
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

All Scenes:
S01: 酒吧 - 夜 (玉鼠精给悟空商业计划书)
S02: 办公室 - 日 (悟空看计划书，哪吒提到仓库问题)
S03: 仓库 - 日 (悟空和哪吒去仓库调查，发现假货)
```

### Output:
```json
{
  "setup_for": ["S03"],
  "payoff_from": ["S01"]
}
```

### Reasoning:
- **payoff_from: ["S01"]** - S02 pays off the business plan from S01 (悟空 is now reviewing it)
- **setup_for: ["S03"]** - S02 sets up the warehouse investigation in S03 (哪吒 mentions warehouse problems)

## Important Notes:
- **Only return JSON** - No explanatory text
- **Use scene IDs exactly** - Match the format provided (e.g., "S01", "S02")
- **Be precise** - Only include clear, direct relationships
- **Empty is okay** - Use `[]` when no relationships exist
- **Read all scenes** - Consider the full context before deciding

---

Now analyze the setup-payoff relationships for the provided scene.
