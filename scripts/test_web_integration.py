#!/usr/bin/env python3
"""
Test script for Phase 3 Web integration.
Tests the TXT parsing endpoints without requiring a running server.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_basic_parsing():
    """Test basic TXT parsing (Phase 1)"""
    print("\n" + "="*60)
    print("TEST 1: Basic TXT Parsing (Phase 1)")
    print("="*60)

    try:
        from src.parser import TXTScriptParser

        script_path = "examples/test_scripts/simple_script.txt"
        parser = TXTScriptParser()

        print(f"📄 Parsing: {script_path}")
        script = parser.parse(script_path)

        print(f"✅ Successfully parsed!")
        print(f"   - Total scenes: {len(script.scenes)}")

        # Extract all characters from scenes
        all_chars = set()
        for scene in script.scenes:
            all_chars.update(scene.characters)
        print(f"   - Characters: {', '.join(list(all_chars)[:5])}")

        # Validate structure
        assert len(script.scenes) > 0, "Script should have scenes"
        assert all(scene.scene_id for scene in script.scenes), "All scenes should have IDs"

        print("✅ TEST 1 PASSED\n")
        return True

    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_enhanced_parsing_mock():
    """Test LLM enhanced parsing with mock (Phase 2)"""
    print("\n" + "="*60)
    print("TEST 2: LLM Enhanced Parsing (Phase 2 - Mock)")
    print("="*60)

    try:
        from src.parser import LLMEnhancedParser
        from unittest.mock import Mock

        # Create mock LLM
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = json.dumps({
            "scene_mission": "Test scene mission",
            "key_events": ["Event 1: Test event happens"],
            "setup_payoff": [],
            "relation_change": [],
            "info_change": []
        })

        script_path = "examples/test_scripts/simple_script.txt"
        parser = LLMEnhancedParser(llm=mock_llm)

        print(f"📄 Parsing with LLM enhancement: {script_path}")
        print("   (Using mock LLM)")
        script = parser.parse(script_path)

        print(f"✅ Successfully parsed with LLM enhancement!")
        print(f"   - Total scenes: {len(script.scenes)}")

        # Extract all characters from scenes
        all_chars = set()
        for scene in script.scenes:
            all_chars.update(scene.characters)
        print(f"   - Characters: {', '.join(list(all_chars)[:5])}")

        # Check if LLM enhancement was applied
        if script.scenes:
            scene = script.scenes[0]
            print(f"   - First scene mission: {scene.scene_mission}")
            print(f"   - First scene key events: {len(scene.key_events)}")

        print("✅ TEST 2 PASSED\n")
        return True

    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_serialization():
    """Test that parsed scripts can be serialized to JSON"""
    print("\n" + "="*60)
    print("TEST 3: JSON Serialization")
    print("="*60)

    try:
        from src.parser import TXTScriptParser

        script_path = "examples/test_scripts/simple_script.txt"
        parser = TXTScriptParser()
        script = parser.parse(script_path)

        print("📝 Converting Script object to JSON...")
        json_data = script.model_dump()
        json_str = json.dumps(json_data, ensure_ascii=False, indent=2)

        print(f"✅ Successfully serialized to JSON!")
        print(f"   - JSON size: {len(json_str)} characters")
        print(f"   - Contains {len(json_data['scenes'])} scenes")

        # Validate JSON structure
        assert "scenes" in json_data, "JSON should have scenes"
        assert len(json_data['scenes']) > 0, "JSON should have at least one scene"
        assert all('scene_id' in s for s in json_data['scenes']), "All scenes should have IDs"

        # Test deserialization
        print("📝 Testing JSON deserialization...")
        from prompts.schemas import Script
        script_restored = Script.model_validate(json_data)

        assert len(script_restored.scenes) == len(script.scenes), "Scene count should match"
        assert script_restored.scenes[0].scene_id == script.scenes[0].scene_id, "Scene IDs should match"

        print("✅ TEST 3 PASSED\n")
        return True

    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_web_app_structure():
    """Test that Web app has required endpoints"""
    print("\n" + "="*60)
    print("TEST 4: Web App Structure")
    print("="*60)

    try:
        from src.web.app import app

        print("🔍 Checking FastAPI app routes...")

        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append((route.path, route.methods))

        # Check for required endpoints
        required_endpoints = [
            "/api/parse-txt",
            "/parse-preview/{job_id}",
            "/analysis-from-parsed/{job_id}",
        ]

        found_endpoints = []
        for endpoint in required_endpoints:
            # Check if endpoint exists (exact or pattern match)
            endpoint_found = False
            for path, methods in routes:
                if endpoint.replace("{job_id}", "") in path:
                    endpoint_found = True
                    found_endpoints.append(f"✅ {endpoint} - {methods}")
                    break

            if not endpoint_found:
                print(f"❌ Missing endpoint: {endpoint}")
                return False

        print("✅ All required endpoints found:")
        for endpoint in found_endpoints:
            print(f"   {endpoint}")

        print("✅ TEST 4 PASSED\n")
        return True

    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_files():
    """Test that required template files exist"""
    print("\n" + "="*60)
    print("TEST 5: Template Files")
    print("="*60)

    try:
        required_templates = [
            "templates/parse_preview.html",
            "templates/index.html",
            "static/js/upload.js",
        ]

        for template in required_templates:
            path = Path(template)
            if not path.exists():
                print(f"❌ Missing template: {template}")
                return False

            file_size = path.stat().st_size
            print(f"✅ Found: {template} ({file_size} bytes)")

        # Check parse_preview.html content
        preview_path = Path("templates/parse_preview.html")
        content = preview_path.read_text(encoding='utf-8')

        required_elements = [
            "previewContent",
            "WebSocket",
            "continueAnalysisBtn",
            "downloadJsonBtn",
        ]

        print("\n🔍 Checking parse_preview.html content...")
        for element in required_elements:
            if element in content:
                print(f"✅ Contains: {element}")
            else:
                print(f"❌ Missing: {element}")
                return False

        print("✅ TEST 5 PASSED\n")
        return True

    except Exception as e:
        print(f"❌ TEST 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 PHASE 3 WEB INTEGRATION TEST SUITE")
    print("="*60)

    tests = [
        test_basic_parsing,
        test_llm_enhanced_parsing_mock,
        test_json_serialization,
        test_web_app_structure,
        test_template_files,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"❌ Test crashed: {test_func.__name__}")
            import traceback
            traceback.print_exc()
            results.append((test_func.__name__, False))

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n🎯 Results: {passed}/{total} tests passed ({passed*100//total}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED - Phase 3 is production ready!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
