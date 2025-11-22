#!/usr/bin/env python3
"""
Test Gemini API connectivity before running business logic.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API with a simple request."""

    print("=" * 60)
    print("Gemini API 连通性测试")
    print("=" * 60)

    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 错误: GOOGLE_API_KEY 环境变量未设置")
        return False

    print(f"✅ API Key 已找到: {api_key[:20]}...{api_key[-4:]}")

    # Test model
    model_name = "gemini-2.5-flash"
    print(f"\n📡 测试模型: {model_name}")

    try:
        # Create LLM instance
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.0,
            max_output_tokens=100,
        )

        print("✅ LLM 实例创建成功")

        # Send test request
        print("\n📤 发送测试请求...")
        test_prompt = "请用一句话介绍你自己。"

        response = llm.invoke(test_prompt)

        print("✅ API 调用成功!")
        print(f"\n💬 响应内容:\n{response.content}\n")

        # Check response metadata
        if hasattr(response, 'response_metadata'):
            metadata = response.response_metadata
            print(f"📊 响应元数据:")
            if 'model_name' in metadata:
                print(f"  - 模型: {metadata['model_name']}")
            if 'finish_reason' in metadata:
                print(f"  - 完成原因: {metadata['finish_reason']}")

        print("\n" + "=" * 60)
        print("✅ 测试通过! Gemini API 工作正常")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 测试失败!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")

        # Parse error details
        error_str = str(e)
        if "quota" in error_str.lower() or "429" in error_str:
            print("\n💡 提示: 这是配额限制错误")
            print("   - 可能是免费配额已用完")
            print("   - 或者请求频率过高")
        elif "401" in error_str or "403" in error_str:
            print("\n💡 提示: 这是认证错误")
            print("   - 请检查 API Key 是否正确")
            print("   - 请确认 API Key 已启用 Gemini API")

        print("\n" + "=" * 60)
        print("❌ 测试失败! 请解决上述问题后重试")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    exit(0 if success else 1)
