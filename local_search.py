from typing import Optional, Tuple
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from langchain_nvidia_ai_endpoints import ChatNVIDIA

# Initialize FastMCP server
mcp = FastMCP("local_search")

async def parse_search_query(query: str, api_key: str) -> Tuple[str, Optional[str]]:
    """Use LLM to parse natural language query for file search parameters
    
    Args:
        query: Natural language query
        api_key: NVIDIA API key for LLM access
        
    Returns:
        Tuple[str, Optional[str]]: (filename/pattern, start_path or None)
    """
    parser = ChatNVIDIA(
        model="meta/llama-3.2-3b-instruct",
        api_key=api_key,
        base_url="https://integrate.api.nvidia.com/v1"
    )
    
    parse_prompt = f"""Given the file search query: "{query}"
    Extract the filename/pattern and search path (if specified).
    
    Rules:
    - If a specific file name is mentioned, use it as the filename as pattern
    - If a specific file extension is mentioned (pdf, txt, etc), use *.extension as pattern
    - If no specific file name and extension is mentioned, use None as the filename as pattern
    - If no path is specified, return ~/ for path
    - Return in format: FILENAME: <filename/pattern>, PATH: <path or None>
    
    Example responses:
    Query: "Find all PDF file"
    FILENAME: *.pdf, PATH: ~/
    
    Query: "Search for report.txt in ~/Documents"
    FILENAME: report.txt, PATH: ~/Documents

    Query: "Search some files in ~/Documents"
    FILENAME: None, PATH: ~/Documents
    """
    
    response = parser.invoke(parse_prompt)
    parsed = response.content.strip()
    
    # Extract filename and path from response
    try:
        filename_part = parsed.split("FILENAME:")[1].split(",")[0].strip()
        path_part = parsed.split("PATH:")[1].strip()

        print(f"filename_part: {filename_part}, path_part: {path_part}")
        
        # Convert "None" string to None
        path = None if path_part.lower() == "none" else path_part
        
        return filename_part, path
    except Exception:
        # Return defaults if parsing fails
        return "*.txt", None

@mcp.tool()
async def find_file(query: str) -> str:
    """Search for files based on natural language query
    
    Args:
        query: Natural language query describing what to search for
        
    Returns:
        str: Search results or guidance message
    """
    try:
        # Get API key from environment
        api_key_nim="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"
        if not api_key_nim:
            return "Error: NVIDIA API key not found in environment"
            
        filename, start_path = await parse_search_query(query, api_key_nim)
        print(f"filename: {filename}, start_path: {start_path}")
        
        # Default to home directory if no path specified
        if not start_path:
            start_path = str(Path.home())
        
        # Convert to absolute path
        start_path = str(Path(start_path).expanduser().resolve())
        
        # Keep track of matches
        matches = []
        
        # Walk through directory tree
        for root, dirs, files in os.walk(start_path):
            # Handle wildcard searches (*.ext)
            if filename.startswith('*'):
                ext = filename[1:]  # get the extension including the dot
                matches.extend([
                    str(Path(root) / file)
                    for file in files
                    if file.lower().endswith(ext)
                ])
            # Handle regular searches
            else:
                matches.extend([
                    str(Path(root) / file)
                    for file in files
                    if filename.lower() in file.lower()
                ])
            
            # Limit results to prevent overwhelming output
            if len(matches) >= 10:
                break
        
        if not matches:
            return f"No matching files found in {start_path}"
        
        # Format results
        result = f"Found the following files in {start_path}:\n"
        for i, match in enumerate(matches, 1):
            result += f"{i}. {match}\n"
        if len(matches) >= 10:
            result += "\n(Showing first 10 results only)"
        return result
        
    except Exception as e:
        return f"Error searching for files: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio') 