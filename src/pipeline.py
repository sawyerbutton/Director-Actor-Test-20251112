"""
LangGraph-based pipeline for the three-stage script analysis system.

This module implements the Director-Actor architecture:
- Director: Orchestrates the workflow
- Actors: Three specialized agents (Discoverer, Auditor, Modifier)

Supports multiple LLM providers:
- DeepSeek (default, via OpenAI-compatible API)
- Anthropic Claude
- OpenAI
"""

from typing import TypedDict, Annotated, Sequence, Optional, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, END
from prompts.schemas import (
    Script, DiscovererOutput, AuditorOutput, ModifierOutput,
    calculate_setup_payoff_density, validate_tcc_independence
)
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# State Definition
# ============================================================================

class PipelineState(TypedDict):
    """
    State for the script analysis pipeline.

    This state is passed between nodes in the LangGraph workflow.
    """
    # Input
    script: Script

    # Stage outputs
    discoverer_output: Optional[DiscovererOutput]
    auditor_output: Optional[AuditorOutput]
    modifier_output: Optional[ModifierOutput]

    # Metadata & control
    current_stage: str
    errors: list[str]
    retry_count: int

    # Messages (for LLM communication)
    messages: Annotated[Sequence[BaseMessage], "append"]


# ============================================================================
# LLM Configuration
# ============================================================================

def create_llm(
    provider: str = "deepseek",
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 4096
) -> BaseChatModel:
    """
    Create LLM instance based on provider.

    Args:
        provider: LLM provider ("deepseek", "anthropic", "openai")
        model: Model name (optional, uses default if not provided)
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate

    Returns:
        Configured LLM instance

    Environment Variables:
        - DEEPSEEK_API_KEY: DeepSeek API key
        - DEEPSEEK_BASE_URL: DeepSeek API base URL (optional, default: https://api.deepseek.com/v1)
        - ANTHROPIC_API_KEY: Anthropic API key (if using Claude)
        - OPENAI_API_KEY: OpenAI API key (if using OpenAI)
    """
    provider = provider.lower()

    if provider == "deepseek":
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")

        base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        model = model or "deepseek-chat"

        logger.info(f"Creating DeepSeek LLM: {model} (base_url: {base_url})")

        return ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=temperature,
            max_tokens=max_tokens
        )

    elif provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError:
            raise ImportError("langchain-anthropic not installed. Install with: pip install langchain-anthropic")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        model = model or "claude-sonnet-4-5"

        logger.info(f"Creating Anthropic LLM: {model}")

        return ChatAnthropic(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        model = model or "gpt-4-turbo-preview"

        logger.info(f"Creating OpenAI LLM: {model}")

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    else:
        raise ValueError(f"Unknown provider: {provider}. Choose from: deepseek, anthropic, openai")


# ============================================================================
# Prompt Loading
# ============================================================================

def load_prompt(stage: str) -> str:
    """Load prompt template for a given stage."""
    prompt_dir = Path(__file__).parent.parent / "prompts"
    prompt_file = prompt_dir / f"stage{stage}.md"

    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


# ============================================================================
# Actor Nodes
# ============================================================================

class DiscovererActor:
    """Stage 1: TCC Identification Actor."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt_template = load_prompt("1_discoverer")

    def __call__(self, state: PipelineState) -> PipelineState:
        """Execute Stage 1: Discover TCCs."""
        logger.info("=== Stage 1: Discoverer Actor ===")

        try:
            # Prepare input
            script_json = state["script"].model_dump_json(indent=2)

            # Create messages
            messages = [
                SystemMessage(content=self.prompt_template),
                HumanMessage(content=f"Analyze this script:\n\n{script_json}")
            ]

            # Call LLM
            logger.info("Calling LLM for TCC identification...")
            response = self.llm.invoke(messages)

            # Parse and validate output
            discoverer_output = DiscovererOutput.model_validate_json(response.content)

            # Validate TCC independence
            warnings = validate_tcc_independence(discoverer_output.tccs)
            if warnings:
                logger.warning(f"TCC independence warnings: {warnings}")
                state["errors"].extend(warnings)

            # Update state
            state["discoverer_output"] = discoverer_output
            state["current_stage"] = "discoverer_completed"
            state["messages"] = messages + [response]

            logger.info(f"✅ Identified {len(discoverer_output.tccs)} TCCs")
            for tcc in discoverer_output.tccs:
                logger.info(f"  - {tcc.tcc_id}: {tcc.super_objective} (conf: {tcc.confidence:.2f})")

        except Exception as e:
            logger.error(f"❌ Discoverer failed: {e}")
            state["errors"].append(f"Discoverer error: {str(e)}")
            state["current_stage"] = "discoverer_failed"
            state["retry_count"] += 1

        return state


class AuditorActor:
    """Stage 2: TCC Ranking & Analysis Actor."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt_template = load_prompt("2_auditor")

    def __call__(self, state: PipelineState) -> PipelineState:
        """Execute Stage 2: Rank TCCs."""
        logger.info("=== Stage 2: Auditor Actor ===")

        try:
            # Prepare input
            script = state["script"]
            discoverer_output = state["discoverer_output"]

            input_data = {
                "script": script.model_dump(),
                "tccs": [tcc.model_dump() for tcc in discoverer_output.tccs]
            }

            # Create messages
            messages = [
                SystemMessage(content=self.prompt_template),
                HumanMessage(content=f"Rank these TCCs:\n\n{json.dumps(input_data, indent=2, ensure_ascii=False)}")
            ]

            # Call LLM
            logger.info("Calling LLM for TCC ranking...")
            response = self.llm.invoke(messages)

            # Parse and validate output
            auditor_output = AuditorOutput.model_validate_json(response.content)

            # Update state
            state["auditor_output"] = auditor_output
            state["current_stage"] = "auditor_completed"
            state["messages"].extend([messages[0], messages[1], response])

            # Log results
            logger.info(f"✅ Ranking complete:")
            logger.info(f"  A-line: {auditor_output.rankings.a_line.tcc_id} (spine: {auditor_output.rankings.a_line.spine_score:.1f})")
            logger.info(f"  B-lines: {len(auditor_output.rankings.b_lines)}")
            logger.info(f"  C-lines: {len(auditor_output.rankings.c_lines)}")

        except Exception as e:
            logger.error(f"❌ Auditor failed: {e}")
            state["errors"].append(f"Auditor error: {str(e)}")
            state["current_stage"] = "auditor_failed"
            state["retry_count"] += 1

        return state


class ModifierActor:
    """Stage 3: Structural Correction Actor."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm
        self.prompt_template = load_prompt("3_modifier")

    def __call__(self, state: PipelineState) -> PipelineState:
        """Execute Stage 3: Apply structural corrections."""
        logger.info("=== Stage 3: Modifier Actor ===")

        try:
            # Generate audit report (simple version - real implementation would be more sophisticated)
            from prompts.schemas import validate_setup_payoff_integrity, AuditReport, Issue, SuggestedFix

            script = state["script"]
            errors = validate_setup_payoff_integrity(script)

            # Create issues from validation errors
            issues = []
            for i, error in enumerate(errors[:10], 1):  # Limit to 10 issues
                # Parse error message to create fix
                # This is simplified - real implementation would be more sophisticated
                issue = Issue(
                    issue_id=f"ISS_{i:03d}",
                    severity="high",
                    category="broken_setup_payoff",
                    description=error,
                    affected_scenes=["S01"],  # Simplified
                    suggested_fix=SuggestedFix(
                        action="add_payoff_reference",
                        target_scene="S01",
                        field="setup_payoff.payoff_from",
                        value=[]
                    )
                )
                issues.append(issue)

            audit_report = AuditReport(issues=issues)

            if not issues:
                logger.info("✅ No structural issues found, skipping Modifier")
                state["modifier_output"] = ModifierOutput(
                    modified_script=script,
                    modification_log=[],
                    validation=ModificationValidation(
                        total_issues=0,
                        fixed=0,
                        skipped=0,
                        new_issues_introduced=0
                    )
                )
                state["current_stage"] = "modifier_completed"
                return state

            # Prepare input
            input_data = {
                "script": script.model_dump(),
                "audit_report": audit_report.model_dump()
            }

            # Create messages
            messages = [
                SystemMessage(content=self.prompt_template),
                HumanMessage(content=f"Fix these issues:\n\n{json.dumps(input_data, indent=2, ensure_ascii=False)}")
            ]

            # Call LLM
            logger.info(f"Calling LLM to fix {len(issues)} issues...")
            response = self.llm.invoke(messages)

            # Parse and validate output
            modifier_output = ModifierOutput.model_validate_json(response.content)

            # Update state
            state["modifier_output"] = modifier_output
            state["current_stage"] = "modifier_completed"
            state["messages"].extend([messages[0], messages[1], response])

            # Log results
            logger.info(f"✅ Modifications complete:")
            logger.info(f"  Total issues: {modifier_output.validation.total_issues}")
            logger.info(f"  Fixed: {modifier_output.validation.fixed}")
            logger.info(f"  Skipped: {modifier_output.validation.skipped}")

        except Exception as e:
            logger.error(f"❌ Modifier failed: {e}")
            state["errors"].append(f"Modifier error: {str(e)}")
            state["current_stage"] = "modifier_failed"
            state["retry_count"] += 1

        return state


# ============================================================================
# Conditional Logic
# ============================================================================

def should_continue_to_auditor(state: PipelineState) -> str:
    """Decide whether to continue to Auditor or retry/fail."""
    if state["current_stage"] == "discoverer_completed":
        return "auditor"
    elif state["retry_count"] < 3:
        return "discoverer"  # Retry
    else:
        return END  # Give up


def should_continue_to_modifier(state: PipelineState) -> str:
    """Decide whether to continue to Modifier or retry/fail."""
    if state["current_stage"] == "auditor_completed":
        return "modifier"
    elif state["retry_count"] < 3:
        return "auditor"  # Retry
    else:
        return END  # Give up


def should_end(state: PipelineState) -> str:
    """Decide whether to end the pipeline."""
    if state["current_stage"] == "modifier_completed":
        return END
    elif state["retry_count"] < 3:
        return "modifier"  # Retry
    else:
        return END  # Give up


# ============================================================================
# Pipeline Builder
# ============================================================================

def create_pipeline(
    llm: Optional[BaseChatModel] = None,
    provider: str = "deepseek",
    model: Optional[str] = None
) -> StateGraph:
    """
    Create the LangGraph pipeline for script analysis.

    Args:
        llm: Optional LLM instance. If provided, provider and model are ignored.
        provider: LLM provider ("deepseek", "anthropic", "openai"). Default: "deepseek"
        model: Model name (optional, uses default for provider)

    Returns:
        Compiled StateGraph ready to execute.

    Examples:
        # Use default (DeepSeek)
        pipeline = create_pipeline()

        # Use specific provider
        pipeline = create_pipeline(provider="anthropic", model="claude-sonnet-4-5")

        # Use custom LLM instance
        custom_llm = ChatOpenAI(...)
        pipeline = create_pipeline(llm=custom_llm)
    """
    # Create LLM if not provided
    if llm is None:
        llm = create_llm(provider=provider, model=model)

    # Create actors
    discoverer = DiscovererActor(llm)
    auditor = AuditorActor(llm)
    modifier = ModifierActor(llm)

    # Build graph
    workflow = StateGraph(PipelineState)

    # Add nodes
    workflow.add_node("discoverer", discoverer)
    workflow.add_node("auditor", auditor)
    workflow.add_node("modifier", modifier)

    # Add edges
    workflow.add_edge("START", "discoverer")
    workflow.add_conditional_edges(
        "discoverer",
        should_continue_to_auditor,
        {
            "auditor": "auditor",
            "discoverer": "discoverer",
            END: END
        }
    )
    workflow.add_conditional_edges(
        "auditor",
        should_continue_to_modifier,
        {
            "modifier": "modifier",
            "auditor": "auditor",
            END: END
        }
    )
    workflow.add_conditional_edges(
        "modifier",
        should_end,
        {
            "modifier": "modifier",
            END: END
        }
    )

    # Compile
    app = workflow.compile()

    logger.info("✅ Pipeline created successfully")
    return app


# ============================================================================
# Convenience Functions
# ============================================================================

def run_pipeline(
    script: Script,
    llm: Optional[BaseChatModel] = None,
    provider: str = "deepseek",
    model: Optional[str] = None
) -> PipelineState:
    """
    Run the complete pipeline on a script.

    Args:
        script: Input script to analyze
        llm: Optional LLM instance. If provided, provider and model are ignored.
        provider: LLM provider ("deepseek", "anthropic", "openai"). Default: "deepseek"
        model: Model name (optional, uses default for provider)

    Returns:
        Final pipeline state with all outputs

    Examples:
        # Use default (DeepSeek)
        result = run_pipeline(script)

        # Use specific provider
        result = run_pipeline(script, provider="anthropic")

        # Use custom LLM
        result = run_pipeline(script, llm=custom_llm)
    """
    pipeline = create_pipeline(llm=llm, provider=provider, model=model)

    # Initialize state
    initial_state: PipelineState = {
        "script": script,
        "discoverer_output": None,
        "auditor_output": None,
        "modifier_output": None,
        "current_stage": "initialized",
        "errors": [],
        "retry_count": 0,
        "messages": []
    }

    # Run pipeline
    logger.info("🚀 Starting pipeline execution...")
    final_state = pipeline.invoke(initial_state)

    # Log summary
    logger.info("=" * 60)
    logger.info("Pipeline Execution Complete")
    logger.info("=" * 60)
    if final_state["errors"]:
        logger.warning(f"Errors encountered: {len(final_state['errors'])}")
        for error in final_state["errors"]:
            logger.warning(f"  - {error}")
    else:
        logger.info("✅ No errors")

    return final_state


if __name__ == "__main__":
    # Example usage
    from prompts.schemas import Scene, SetupPayoff

    # Create a simple test script
    test_script = Script(scenes=[
        Scene(
            scene_id="S01",
            setting="测试场景",
            characters=["角色A", "角色B"],
            scene_mission="建立角色关系和冲突",
            key_events=["事件1", "事件2"],
            setup_payoff=SetupPayoff(setup_for=["S02"], payoff_from=[])
        ),
        Scene(
            scene_id="S02",
            setting="测试场景2",
            characters=["角色A", "角色C"],
            scene_mission="推进冲突发展",
            key_events=["事件3"],
            setup_payoff=SetupPayoff(setup_for=[], payoff_from=["S01"])
        )
    ])

    print("This is a demonstration script. To run with real LLM:")
    print("  1. Set ANTHROPIC_API_KEY environment variable")
    print("  2. Import and call: run_pipeline(your_script)")
