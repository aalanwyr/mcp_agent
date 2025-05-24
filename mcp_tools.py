from typing import Optional
from mcp.server.fastmcp import FastMCP
import importlib
import os
from pathlib import Path

class MCPTools:
    def __init__(self, tool_name: str):
        """Initialize MCP Tools wrapper
        
        Args:
            tool_name: Name of the specific tool to load (e.g. 'web_search', 'local_search')
        """
        self.tool_name = tool_name
        
        # Import the specific tool module
        try:
            self.tool_module = importlib.import_module(tool_name)
        except ImportError as e:
            raise ImportError(f"Could not load tool module '{tool_name}': {str(e)}")
            
        # Get the MCP instance from the module
        self.mcp = getattr(self.tool_module, 'mcp', None)
        if not self.mcp:
            raise AttributeError(f"Tool module '{tool_name}' does not expose an MCP instance")

    def run(self):
        """Run the MCP server with the loaded tool"""
        self.mcp.run(transport='stdio')

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mcp_tools.py <tool_name>")
        sys.exit(1)
        
    tool_name = sys.argv[1]
    tools = MCPTools(tool_name)
    tools.run() 