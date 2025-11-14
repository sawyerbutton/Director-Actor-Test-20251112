"""
LLM Enhanced Parser

Enhances basic TXT parser output with semantic information extracted via LLM.

This parser builds on TXTScriptParser and uses LLM to extract:
- Scene missions (场景目标)
- Setup-payoff relationships
- Relation changes
- Info changes
- Key events
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from prompts.schemas import Script, Scene, SetupPayoff, RelationChange, InfoChange
from .txt_parser import TXTScriptParser

logger = logging.getLogger(__name__)


class LLMEnhancedParser(TXTScriptParser):
    """
    Enhanced TXT parser that uses LLM to extract semantic information.

    Process:
    1. Use TXTScriptParser to get basic structure (scenes, characters, setting)
    2. Use LLM to enhance each scene with:
       - scene_mission
       - setup_payoff
       - relation_change
       - info_change
       - key_events
    """

    def __init__(self, llm: BaseChatModel, batch_size: int = 5, progress_callback=None):
        """
        Initialize LLM Enhanced Parser.

        Args:
            llm: Language model for semantic extraction
            batch_size: Number of scenes to process in parallel (for optimization)
            progress_callback: Optional async callback for progress updates
                              Signature: async callback(current: int, total: int, message: str)
        """
        super().__init__()
        self.llm = llm
        self.batch_size = batch_size
        self.progress_callback = progress_callback

        # Load prompts
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, str]:
        """Load all LLM prompts from files."""
        prompt_dir = Path(__file__).parent / "prompts"

        prompts = {}
        prompt_files = {
            "scene_mission": "scene_mission_prompt.md",
            "setup_payoff": "setup_payoff_prompt.md",
            "relation_change": "relation_change_prompt.md",
            "info_change": "info_change_prompt.md",
            "key_events": "key_events_prompt.md"
        }

        for key, filename in prompt_files.items():
            file_path = prompt_dir / filename
            if file_path.exists():
                prompts[key] = file_path.read_text(encoding='utf-8')
            else:
                logger.warning(f"Prompt file not found: {file_path}")
                prompts[key] = ""

        return prompts

    def parse(self, file_path: str) -> Script:
        """
        Parse TXT script with LLM enhancement.

        Args:
            file_path: Path to TXT file

        Returns:
            Script object with full semantic information
        """
        # Step 1: Get basic structure using parent parser
        logger.info("Step 1: Extracting basic structure...")
        script = super().parse(file_path)

        # Read original file for scene text extraction
        content = self._read_file(file_path)
        scene_texts = self._split_scenes(content)

        # Step 2: Enhance each scene with LLM
        logger.info(f"Step 2: Enhancing {len(script.scenes)} scenes with LLM...")
        enhanced_scenes = []
        total_scenes = len(script.scenes)

        for idx, scene in enumerate(script.scenes):
            # Get original scene text
            scene_text = scene_texts[idx] if idx < len(scene_texts) else ""

            logger.info(f"Enhancing scene {scene.scene_id}...")
            enhanced_scene = self._enhance_scene(scene, scene_text, script.scenes)
            enhanced_scenes.append(enhanced_scene)

            # Report progress if callback provided
            if self.progress_callback:
                import asyncio
                asyncio.create_task(
                    self.progress_callback(
                        current=idx + 1,
                        total=total_scenes,
                        message=f"Enhanced scene {scene.scene_id} ({idx + 1}/{total_scenes})"
                    )
                )

        # Create enhanced script
        enhanced_script = Script(scenes=enhanced_scenes)

        logger.info(f"✅ Enhanced {len(enhanced_scenes)} scenes successfully")
        return enhanced_script

    def _enhance_scene(
        self,
        scene: Scene,
        scene_text: str,
        all_scenes: List[Scene]
    ) -> Scene:
        """
        Enhance a single scene with LLM-extracted information.

        Args:
            scene: Basic scene from TXT parser
            scene_text: Original scene text
            all_scenes: All scenes in script (for setup-payoff)

        Returns:
            Enhanced scene with semantic information
        """
        # Extract scene mission
        scene_mission = self._extract_scene_mission(scene.scene_id, scene.setting, scene_text)

        # Extract setup-payoff
        setup_payoff = self._extract_setup_payoff(scene.scene_id, scene_text, all_scenes)

        # Extract relation changes
        relation_changes = self._extract_relation_changes(scene.scene_id, scene_text, scene.characters)

        # Extract info changes
        info_changes = self._extract_info_changes(scene.scene_id, scene_text, scene.characters)

        # Extract key events
        key_events = self._extract_key_events(scene.scene_id, scene_text, scene.characters)

        # Create enhanced scene
        enhanced_scene = Scene(
            scene_id=scene.scene_id,
            setting=scene.setting,
            characters=scene.characters,
            scene_mission=scene_mission,
            key_events=key_events,
            setup_payoff=setup_payoff,
            relation_change=relation_changes,
            info_change=info_changes,
            key_object=scene.key_object  # Keep from basic parser (empty for now)
        )

        return enhanced_scene

    def _extract_scene_mission(self, scene_id: str, setting: str, scene_text: str) -> str:
        """
        Extract scene mission using LLM.

        Args:
            scene_id: Scene identifier
            setting: Scene setting
            scene_text: Full scene text

        Returns:
            Scene mission description
        """
        try:
            # Build prompt
            user_message = f"""Scene ID: {scene_id}
Setting: {setting}
Text:
{scene_text}
"""

            # Call LLM
            response = self.llm.invoke([
                SystemMessage(content=self.prompts["scene_mission"]),
                HumanMessage(content=user_message)
            ])

            # Parse response
            result = self._parse_json_response(response.content)
            scene_mission = result.get("scene_mission", "待LLM提取场景目标")

            logger.debug(f"{scene_id} scene_mission: {scene_mission}")
            return scene_mission

        except Exception as e:
            logger.error(f"Error extracting scene mission for {scene_id}: {e}")
            return "待LLM提取场景目标"

    def _extract_setup_payoff(
        self,
        scene_id: str,
        scene_text: str,
        all_scenes: List[Scene]
    ) -> SetupPayoff:
        """
        Extract setup-payoff relationships using LLM.

        Args:
            scene_id: Current scene identifier
            scene_text: Current scene text
            all_scenes: All scenes in script

        Returns:
            SetupPayoff object
        """
        try:
            # Build context with all scenes
            all_scenes_text = "\n\n".join([
                f"{s.scene_id}: {s.setting}"
                for s in all_scenes
            ])

            user_message = f"""Current Scene: {scene_id}
Current Scene Text:
{scene_text}

All Scenes:
{all_scenes_text}
"""

            # Call LLM
            response = self.llm.invoke([
                SystemMessage(content=self.prompts["setup_payoff"]),
                HumanMessage(content=user_message)
            ])

            # Parse response
            result = self._parse_json_response(response.content)
            setup_payoff = SetupPayoff(
                setup_for=result.get("setup_for", []),
                payoff_from=result.get("payoff_from", [])
            )

            logger.debug(f"{scene_id} setup_payoff: {setup_payoff}")
            return setup_payoff

        except Exception as e:
            logger.error(f"Error extracting setup-payoff for {scene_id}: {e}")
            return SetupPayoff()

    def _extract_relation_changes(
        self,
        scene_id: str,
        scene_text: str,
        characters: List[str]
    ) -> List[RelationChange]:
        """
        Extract relation changes using LLM.

        Args:
            scene_id: Scene identifier
            scene_text: Full scene text
            characters: List of characters in scene

        Returns:
            List of RelationChange objects
        """
        try:
            user_message = f"""Scene ID: {scene_id}
Scene Text:
{scene_text}

Characters: {', '.join(characters)}
"""

            # Call LLM
            response = self.llm.invoke([
                SystemMessage(content=self.prompts["relation_change"]),
                HumanMessage(content=user_message)
            ])

            # Parse response
            result = self._parse_json_response(response.content)
            relation_changes_data = result.get("relation_changes", [])

            # Convert to RelationChange objects
            relation_changes = [
                RelationChange(**rc) for rc in relation_changes_data
            ]

            logger.debug(f"{scene_id} relation_changes: {len(relation_changes)} changes")
            return relation_changes

        except Exception as e:
            logger.error(f"Error extracting relation changes for {scene_id}: {e}")
            return []

    def _extract_info_changes(
        self,
        scene_id: str,
        scene_text: str,
        characters: List[str]
    ) -> List[InfoChange]:
        """
        Extract information changes using LLM.

        Args:
            scene_id: Scene identifier
            scene_text: Full scene text
            characters: List of characters in scene

        Returns:
            List of InfoChange objects
        """
        try:
            user_message = f"""Scene ID: {scene_id}
Scene Text:
{scene_text}

Characters: {', '.join(characters)}
"""

            # Call LLM
            response = self.llm.invoke([
                SystemMessage(content=self.prompts["info_change"]),
                HumanMessage(content=user_message)
            ])

            # Parse response
            result = self._parse_json_response(response.content)
            info_changes_data = result.get("info_changes", [])

            # Convert to InfoChange objects
            info_changes = [
                InfoChange(**ic) for ic in info_changes_data
            ]

            logger.debug(f"{scene_id} info_changes: {len(info_changes)} changes")
            return info_changes

        except Exception as e:
            logger.error(f"Error extracting info changes for {scene_id}: {e}")
            return []

    def _extract_key_events(
        self,
        scene_id: str,
        scene_text: str,
        characters: List[str]
    ) -> List[str]:
        """
        Extract key events using LLM.

        Args:
            scene_id: Scene identifier
            scene_text: Full scene text
            characters: List of characters in scene

        Returns:
            List of key event descriptions
        """
        try:
            user_message = f"""Scene ID: {scene_id}
Scene Text:
{scene_text}

Characters: {', '.join(characters)}
"""

            # Call LLM
            response = self.llm.invoke([
                SystemMessage(content=self.prompts["key_events"]),
                HumanMessage(content=user_message)
            ])

            # Parse response
            result = self._parse_json_response(response.content)
            key_events = result.get("key_events", [])

            logger.debug(f"{scene_id} key_events: {len(key_events)} events")
            return key_events

        except Exception as e:
            logger.error(f"Error extracting key events for {scene_id}: {e}")
            return []

    def _parse_json_response(self, response: str) -> Dict:
        """
        Parse JSON from LLM response.

        Handles cases where LLM includes extra text around JSON.

        Args:
            response: LLM response text

        Returns:
            Parsed JSON dictionary
        """
        # Try direct parsing first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Try finding JSON block in markdown code fence
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Try finding first { to last }
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            json_str = response[start:end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # If all fails, return empty dict
        logger.warning(f"Could not parse JSON from response: {response[:100]}...")
        return {}
