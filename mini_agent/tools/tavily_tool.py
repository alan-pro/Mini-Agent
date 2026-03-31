from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
import logging
import json
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("tavily-search")

# 获取 API Key
api_key = os.getenv("TAVILY_API_KEY")
if not api_key:
    logger.error("TAVILY_API_KEY environment variable not set")
    raise RuntimeError("TAVILY_API_KEY not set")

# 初始化客户端
try:
    client = TavilyClient(api_key=api_key)
    logger.info("Tavily client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Tavily client: {e}")
    raise

@mcp.tool()
async def search(query: str, max_results: int = 5) -> str:
    """
    Search using Tavily AI search engine.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
    """
    try:
        result = await asyncio.to_thread(
            client.search,
            query=query,
            max_results=max_results,
            include_answer=True,  # 包含 AI 生成的答案
            include_raw_content=False  # 避免返回过多内容
        )
        
        # 格式化输出，使其更易读
        formatted_result = {
            "query": query,
            "answer": result.get("answer", ""),
            "results": [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500]  # 限制内容长度
                }
                for r in result.get("results", [])
            ]
        }
        
        return json.dumps(formatted_result, ensure_ascii=False, indent=2)
    
    except asyncio.CancelledError:
        logger.warning("Search cancelled")
        return json.dumps({"error": "cancelled", "query": query})

    except Exception as e:
        logger.error(f"Search error: {e}")
        return json.dumps({"error": str(e), "query": query})

@mcp.tool()
async def search_with_context(query: str, max_results: int = 3) -> str:
    """
    Search and return results with more context for deep research.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 3)
    """
    try:
        result = await asyncio.to_thread(
            client.search,
            query=query,
            max_results=max_results,
            include_answer=True,
            include_raw_content=True,  # 包含原始内容用于深度分析
            search_depth="advanced"  # 使用高级搜索深度
        )
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    

    except asyncio.CancelledError:
        logger.warning("Search cancelled")
        return json.dumps({"error": "cancelled", "query": query})
        
    except Exception as e:
        logger.error(f"Deep search error: {e}")
        return json.dumps({"error": str(e), "query": query})

if __name__ == "__main__":
    mcp.run()