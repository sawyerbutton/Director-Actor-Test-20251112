"""
TXT Script Parser

Parses plain text screenplay files and converts them to Script JSON format.

Supported formats:
- Standard format: "场景 1: 酒吧 - 夜"
- Numbered format: "第一场 酒吧 - 夜"
- Final Draft style: "INT. 酒吧 - 夜"
"""

import re
from typing import List, Dict, Tuple
from prompts.schemas import Script, Scene, PerformanceNote
from .base import ScriptParser
import logging

logger = logging.getLogger(__name__)


class TXTScriptParser(ScriptParser):
    """
    Parser for plain text screenplay files.

    This parser uses regular expressions to identify scenes, characters,
    and dialogue, then constructs a basic Script object.
    """

    # Scene heading patterns
    SCENE_PATTERNS = [
        r'^场景\s*(\d+)[：:]\s*(.+)',              # 场景 1: 酒吧 - 夜
        r'^第([一二三四五六七八九十百]+)场\s+(.+)',   # 第一场 酒吧 - 夜
        r'^(INT\.|EXT\.)\s+(.+)',                  # INT. 酒吧 - 夜
        r'^S(\d+)\s*[：:]\s*(.+)',                # S1: 酒吧 - 夜
        r'^(\d+)[、，,]\s*(.+)',                   # 1、酒吧 - 夜 (中文顿号格式)
    ]

    # Scene separator patterns
    SEPARATOR_PATTERNS = [
        r'^-{3,}$',      # ---
        r'^={3,}$',      # ===
        r'^#{3,}$',      # ###
    ]

    # Dialogue pattern: "角色名：台词" or "角色名\n台词"
    DIALOGUE_PATTERNS = [
        r'^([^：:\n]+)[：:]\s*(.+)',              # 角色：台词
        r'^([A-Z\u4e00-\u9fa5]{2,})\n\s+(.+)',   # 角色名(独立行)\n  台词
    ]

    # 表演提示模式：角色名后的括号内容
    # 例: 庄见青（呢喃）：, 李明(颤抖地):
    PERFORMANCE_NOTE_PATTERNS = [
        r'^([^（(：:]+)[（(]([^）)]+)[）)][：:]?\s*(.*)$',  # 角色名（提示）：台词
    ]

    # 视觉动作模式：特殊符号开头的行
    VISUAL_ACTION_PATTERNS = [
        r'^△\s*(.+)$',           # △ 开头 (三角形)
        r'^▲\s*(.+)$',           # ▲ 开头 (实心三角)
        r'^■\s*(.+)$',           # ■ 开头 (黑方块)
        r'^【(.+)】$',            # 【】 包裹
        r'^\[(.+)\]$',           # [] 包裹 (英文方括号)
        r'^〔(.+)〕$',            # 〔〕 包裹
    ]

    def __init__(self):
        """Initialize TXT parser."""
        self.chinese_numbers = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        }

    def parse(self, file_path: str) -> Script:
        """
        Parse a TXT script file.

        Args:
            file_path: Path to the TXT file

        Returns:
            Script object with basic structure (scenes, characters)

        Raises:
            FileNotFoundError: If file not found
            ValueError: If file is not a .txt file
        """
        # Validate file type
        self._validate_file_type(file_path, '.txt')

        # Read file content
        content = self._read_file(file_path)

        # Split into scenes
        scene_blocks = self._split_scenes(content)
        logger.info(f"Split script into {len(scene_blocks)} scenes")

        # Parse each scene
        scenes = []
        scene_id_counts = {}  # Track scene ID usage for deduplication
        valid_scene_idx = 1

        for block in scene_blocks:
            # Skip empty or separator-only blocks
            if not block.strip() or len(block.strip()) < 5:
                continue

            scene = self._parse_scene(block, valid_scene_idx)
            if scene:
                # Handle duplicate scene IDs
                original_id = scene.scene_id
                if original_id in scene_id_counts:
                    # Add suffix for duplicate IDs
                    scene_id_counts[original_id] += 1
                    suffix = chr(ord('a') + scene_id_counts[original_id] - 1)  # a, b, c...
                    scene.scene_id = f"{original_id}{suffix}"
                    logger.warning(f"Duplicate scene ID '{original_id}' found, renamed to '{scene.scene_id}'")
                else:
                    scene_id_counts[original_id] = 1

                scenes.append(scene)
                valid_scene_idx += 1

        # Create Script object
        script = Script(scenes=scenes)

        logger.info(f"Parsed {len(scenes)} scenes successfully")
        return script

    def validate(self, script: Script) -> List[str]:
        """
        Validate the parsed script.

        Args:
            script: Parsed Script object

        Returns:
            List of validation warnings/errors
        """
        warnings = []

        if not script.scenes:
            warnings.append("No scenes found in script")

        for scene in script.scenes:
            # Check if scene has characters
            if not scene.characters:
                warnings.append(f"{scene.scene_id}: No characters found")

            # Check if scene has any content
            if not scene.scene_mission and not scene.key_events:
                warnings.append(f"{scene.scene_id}: Scene appears to be empty")

        return warnings

    def _split_scenes(self, content: str) -> List[str]:
        """
        Split script content into individual scene blocks.

        Args:
            content: Full script text

        Returns:
            List of scene text blocks
        """
        scenes = []
        current_scene = []
        lines = content.split('\n')

        for line in lines:
            # Check if this is a scene heading
            is_scene_heading = False
            for pattern in self.SCENE_PATTERNS:
                if re.match(pattern, line.strip(), re.IGNORECASE):
                    # Save previous scene if exists
                    if current_scene:
                        scenes.append('\n'.join(current_scene))
                        current_scene = []

                    current_scene.append(line)
                    is_scene_heading = True
                    break

            # Check if this is a separator
            if not is_scene_heading:
                for pattern in self.SEPARATOR_PATTERNS:
                    if re.match(pattern, line.strip()):
                        # Save previous scene if exists
                        if current_scene:
                            scenes.append('\n'.join(current_scene))
                            current_scene = []
                        is_scene_heading = True
                        break

            # Add line to current scene
            if not is_scene_heading:
                current_scene.append(line)

        # Add last scene
        if current_scene:
            scenes.append('\n'.join(current_scene))

        return scenes

    def _parse_scene(self, scene_text: str, scene_number: int) -> Scene:
        """
        Parse a single scene block.

        Args:
            scene_text: Text of one scene
            scene_number: Scene number

        Returns:
            Scene object or None if parsing fails
        """
        lines = scene_text.strip().split('\n')
        if not lines:
            return None

        # Extract scene ID and setting
        scene_id, scene_setting = self._extract_scene_info(lines[0], scene_number)

        # Extract characters from dialogue
        characters = self._extract_characters(scene_text)

        # Extract basic description (first non-dialogue, non-heading text)
        description = self._extract_description(lines[1:] if len(lines) > 1 else [])

        # 新增：提取表演提示 (v2.6.0)
        performance_notes = self._extract_performance_notes(scene_text)

        # 新增：提取视觉动作 (v2.6.0)
        visual_actions = self._extract_visual_actions(scene_text)

        # If no characters found, add placeholder
        if not characters:
            characters = ["待识别"]

        # Create Scene object with minimal information
        # LLM enhancement will add scene_mission, setup_payoff, etc.
        from prompts.schemas import SetupPayoff

        # Ensure scene_mission has at least 10 characters for validation
        scene_mission = description if description and len(description) >= 10 else "待LLM提取场景任务目标"

        scene = Scene(
            scene_id=scene_id,
            setting=scene_setting or "待识别",          # Required field
            characters=list(set(characters)),          # Remove duplicates
            scene_mission=scene_mission,               # Placeholder with minimum length
            key_events=[],                             # Will be filled by LLM
            setup_payoff=SetupPayoff(),                # Empty SetupPayoff object
            relation_change=[],                        # Will be filled by LLM
            info_change=[],                            # Will be filled by LLM
            key_object=[],                             # Will be filled by LLM
            performance_notes=performance_notes,       # 新增：表演提示
            visual_actions=visual_actions              # 新增：视觉动作
        )

        return scene

    def _extract_scene_info(self, heading: str, scene_number: int) -> Tuple[str, str]:
        """
        Extract scene ID and setting from scene heading.

        Args:
            heading: Scene heading line
            scene_number: Fallback scene number

        Returns:
            Tuple of (scene_id, scene_setting)
        """
        # Try each pattern
        for pattern in self.SCENE_PATTERNS:
            match = re.match(pattern, heading.strip(), re.IGNORECASE)
            if match:
                groups = match.groups()

                # Handle different pattern types
                if '场景' in pattern or 'S' in pattern:
                    # Numeric ID
                    scene_id = f"S{str(groups[0]).zfill(2)}"
                    scene_setting = groups[1].strip()
                elif '第' in pattern and '场' in pattern:
                    # Chinese number
                    chinese_num = groups[0]
                    numeric = self._chinese_to_number(chinese_num)
                    scene_id = f"S{str(numeric).zfill(2)}"
                    scene_setting = groups[1].strip()
                elif 'INT.' in pattern or 'EXT.' in pattern:
                    # Final Draft style
                    scene_id = f"S{str(scene_number).zfill(2)}"
                    scene_setting = f"{groups[0]} {groups[1]}".strip()
                else:
                    scene_id = f"S{str(scene_number).zfill(2)}"
                    scene_setting = groups[1].strip()

                return scene_id, scene_setting

        # Fallback
        return f"S{str(scene_number).zfill(2)}", heading.strip()

    def _chinese_to_number(self, chinese: str) -> int:
        """
        Convert Chinese number to Arabic number.

        Args:
            chinese: Chinese number string (e.g., "一", "十", "二十")

        Returns:
            Arabic number
        """
        # Simple conversion (supports 一 through 十)
        if chinese in self.chinese_numbers:
            return self.chinese_numbers[chinese]

        # Handle 十几, 二十几, etc.
        if '十' in chinese:
            parts = chinese.split('十')
            if len(parts) == 2:
                tens = self.chinese_numbers.get(parts[0], 1) if parts[0] else 1
                ones = self.chinese_numbers.get(parts[1], 0) if parts[1] else 0
                return tens * 10 + ones

        # Fallback to 1
        return 1

    def _extract_characters(self, scene_text: str) -> List[str]:
        """
        Extract character names from dialogue.

        Args:
            scene_text: Full scene text

        Returns:
            List of character names
        """
        characters = []
        lines = scene_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try dialogue patterns
            for pattern in self.DIALOGUE_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    character = match.group(1).strip()
                    # Clean up character name
                    character = character.replace('：', '').replace(':', '').strip()
                    # Filter out obvious non-characters
                    if len(character) >= 2 and len(character) <= 10:
                        if not any(sep in character for sep in ['。', '，', '、']):
                            characters.append(character)
                    break

        return characters

    def _extract_description(self, lines: List[str]) -> str:
        """
        Extract scene description from non-dialogue lines.

        Args:
            lines: Scene lines (excluding heading)

        Returns:
            Scene description text
        """
        description_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip if it looks like dialogue
            is_dialogue = False
            for pattern in self.DIALOGUE_PATTERNS:
                if re.match(pattern, line):
                    is_dialogue = True
                    break

            if not is_dialogue and len(line) > 5:
                description_lines.append(line)

            # Take only first few description lines
            if len(description_lines) >= 3:
                break

        return ' '.join(description_lines) if description_lines else ""

    def _extract_performance_notes(self, scene_text: str) -> List[PerformanceNote]:
        """
        Extract performance notes from scene text.

        Performance notes are hints in parentheses after character names,
        e.g., "庄见青（呢喃）：" or "李明(颤抖地):"

        Args:
            scene_text: Full scene text

        Returns:
            List of PerformanceNote objects
        """
        performance_notes = []
        lines = scene_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try performance note patterns
            for pattern in self.PERFORMANCE_NOTE_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    groups = match.groups()
                    character = groups[0].strip()
                    note = groups[1].strip()
                    dialogue = groups[2].strip() if len(groups) > 2 and groups[2] else None

                    # Filter out invalid character names
                    if len(character) >= 1 and len(character) <= 10:
                        if not any(sep in character for sep in ['。', '，', '、', '：', ':']):
                            performance_notes.append(PerformanceNote(
                                character=character,
                                note=note,
                                line_context=dialogue if dialogue else None
                            ))
                    break

        return performance_notes

    def _extract_visual_actions(self, scene_text: str) -> List[str]:
        """
        Extract visual action descriptions from scene text.

        Visual actions are lines starting with special symbols like △, ■, 【】, etc.
        These describe physical actions or stage directions.

        Args:
            scene_text: Full scene text

        Returns:
            List of visual action strings
        """
        visual_actions = []
        lines = scene_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try visual action patterns
            for pattern in self.VISUAL_ACTION_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    action = match.group(1).strip()
                    if action and len(action) >= 2:
                        visual_actions.append(action)
                    break

        return visual_actions
