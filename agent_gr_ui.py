import os
import asyncio
from dotenv import load_dotenv
from mcp import StdioServerParameters
from mcp_llm_bridge.config import BridgeConfig, LLMConfig
from mcp_llm_bridge.bridge import BridgeManager
import colorlog
import logging

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain_core.runnables import RunnableBranch
from langchain_core.runnables import RunnablePassthrough

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

import os
import base64
import matplotlib.pyplot as plt
import numpy as np

os.environ["NVIDIA_API_KEY"] = "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"


def clean_llm_response(response: str) -> str:
    """
    Clean the LLM response to extract just the final answer.
    Removes thinking process and any XML-like tags.
    """
    # First try to get the last line that's not empty
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    if lines:
        final_answer = lines[-1]  # Get the last non-empty line
        
        # Remove any XML-like tags
        final_answer = final_answer.replace('<think>', '').replace('</think>', '')
        
        # Clean up any remaining whitespace
        final_answer = final_answer.strip()
        
        return final_answer
    return response.strip()

async def process_single_message(user_input: str):

    load_dotenv()
    api_key_nim="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"
    
    tool_selector = ChatNVIDIA(
        model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
        api_key=api_key_nim,
        base_url="https://integrate.api.nvidia.com/v1"
    )
    
    tool_prompt = f"""Given the user query: "{user_input}"
    Choose between 'web_search' or 'local_search' based on these criteria:
    - Use web_search for current events, online information, or general knowledge
    - Use local_search for finding files or information in the local system
    Respond with only one word: either 'web_search' or 'local_search'"""

    tool_response = tool_selector.invoke(tool_prompt)
    selected_tool = clean_llm_response(tool_response.content.strip().lower())

    web_search_config = BridgeConfig(
        mcp_server_params=StdioServerParameters(
            command="python",
            args=["mcp_tools.py", "web_search", user_input],
            env=None
        ),
        llm_config=LLMConfig(
            api_key=api_key_nim,
            model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
            base_url="https://integrate.api.nvidia.com/v1"
        ),
        system_prompt="You are a helpful assistant that can use tools to help answer questions."
    )
    
    local_search_config = BridgeConfig(
        mcp_server_params=StdioServerParameters(
            command="python",
            args=["mcp_tools.py", "local_search", user_input],
            env=None
        ),
        llm_config=LLMConfig(
            api_key=api_key_nim,
            model="nvidia/llama-3.1-nemotron-ultra-253b-v1",
            base_url="https://integrate.api.nvidia.com/v1"
        ),
        system_prompt="""
        You are a helpful assistant that can use tools to find files in the local system.
        Rules:
        - If find the file, return the file name and path.
        - If not find the file, return 'Not found'.
        - Do not think out loud or provide analysis."""
    )

    config = web_search_config if selected_tool == "web_search" else local_search_config
    print(f"\nSelected tool: {selected_tool}")
    print(f"\nSelected config: {config}")

    async with BridgeManager(config) as bridge:
        try:
          # Add logging for tool selection and execution
            print(f"\n=== Debug Information ===")
            print(f"Tool selected: {selected_tool}")
            print(f"Input query: {user_input}")
            print("\nSending request to tool...")
            response = await bridge.process_message(user_input)
            
            # Parse and display the response more clearly
            print("\n=== Tool Execution Results ===")
            print(f"\nResponse in TERMINAL: {response}")
            if isinstance(response, dict):
                formatted_response = "\n".join([f"{key}: {value}" for key, value in response.items()])
                return formatted_response
            return str(response)
            
        except Exception as e:
            return f"Error occurred: {str(e)}"


def chat_with_agent(message, history):
    response = asyncio.run(process_single_message(message))
    print(f"\n Response in chat_with_agent: {response}")
    # Remove the thinking process enclosed in <think> tags
    if isinstance(response, str):
        # Find the last occurrence of </think>
        think_end = response.rfind('</think>')
        if think_end != -1:
            # Get everything after the last </think> tag
            final_response = response[think_end + 8:].strip()
        else:
            final_response = response.strip()
    else:
        final_response = str(response)
    
    return final_response

# Create and launch the Gradio interface
import gradio as gr

css = """
body, .gradio-container {
    font-family: 'Noto Sans SC', 'Microsoft YaHei', 'Arial Unicode MS', sans-serif;
}
"""

demo = gr.ChatInterface(
    fn=chat_with_agent,
    title="MCP Agent Chat",
    description="Chat with the MCP Agent - It can perform web searches and local file searches.",
    examples=["What's the weather like today?", "Find files in my system"],
    theme="default",
    css=css
)

if __name__ == "__main__":
    demo.launch(server_port=8000, server_name="0.0.0.0", share=False)