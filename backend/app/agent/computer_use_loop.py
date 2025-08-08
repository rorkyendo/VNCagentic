"""
Computer Use Agent Integration

This module adapts the existing Anthropic computer use demo to work with our FastAPI backend.
It reuses the existing agent loop and tools but wraps them in our session management system.
"""

import asyncio
import logging
import platform
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from collections.abc import Awaitable

from anthropic import Anthropic
from anthropic.types.beta import BetaMessage, BetaMessageParam, BetaTextBlockParam

# Import the existing computer use components
# Note: These will need to be copied/adapted from the original demo
from app.agent.tools import ToolCollection, ToolResult
from app.agent.loop import sampling_loop, APIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class ComputerUseAgent:
    """
    Wrapper around the existing computer use agent that integrates with our session system
    """
    
    def __init__(
        self,
        session_id: str,
        model: str,
        api_provider: str,
        api_key: str,
        on_output: Callable[[str, Any], Awaitable[None]],
        on_tool_call: Callable[[str, str, Dict[str, Any], str], Awaitable[None]],
        on_tool_result: Callable[[str, str, Any, Optional[str]], Awaitable[None]],
        on_status_update: Callable[[str, str, Optional[Dict[str, Any]]], Awaitable[None]],
        api_base_url: Optional[str] = None
    ):
        self.session_id = session_id
        self.model = model
        self.api_provider = APIProvider(api_provider)
        self.api_key = api_key
        self.api_base_url = api_base_url
        
        # Callbacks
        self.on_output = on_output
        self.on_tool_call = on_tool_call
        self.on_tool_result = on_tool_result
        self.on_status_update = on_status_update
        
        # State
        self.messages: List[BetaMessageParam] = []
        self.is_running = False
        self.current_task = None
        
        # System prompt adapted from the original demo
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt based on the original computer use demo"""
        return f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine using {platform.machine()} architecture with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* To open firefox, please just click on the firefox icon. Note, firefox-esr is what is installed on your system.
* Using bash tool you can start GUI applications, but you need to set export DISPLAY={settings.VNC_DISPLAY} and use a subshell. For example "(DISPLAY={settings.VNC_DISPLAY} xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear. Take a screenshot to confirm it did.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_based_edit_tool or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page. Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you. Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

<IMPORTANT>
* When using Firefox, if a startup wizard appears, IGNORE IT. Do not even click "skip this step". Instead, click on the address bar where it says "Search or enter address", and enter the appropriate search term or URL there.
* If the item you are looking at is a pdf, if after taking a single screenshot of the pdf it seems that you want to read the entire document instead of trying to continue to read the pdf from your screenshots + navigation, determine the URL, use curl to download the pdf, install and use pdftotext to convert it to a text file, and then read that text file directly with your str_replace_based_edit_tool.
</IMPORTANT>"""

    async def initialize(self):
        """Initialize the agent"""
        await self.on_status_update(self.session_id, "initializing", {
            "model": self.model,
            "api_provider": self.api_provider.value,
            "api_base_url": self.api_base_url
        })
        
        # Initialize tool collection (this would use the existing computer use tools)
        self.tool_collection = ToolCollection()
        
        await self.on_status_update(self.session_id, "ready")
    
    async def process_message(self, user_message: str):
        """Process a user message through the agent loop"""
        if self.is_running:
            await self.on_status_update(self.session_id, "busy", {
                "message": "Agent is currently processing another request"
            })
            return
        
        self.is_running = True
        
        try:
            await self.on_status_update(self.session_id, "processing", {
                "user_message": user_message
            })
            
            # Add user message to conversation
            self.messages.append({
                "role": "user",
                "content": [BetaTextBlockParam(type="text", text=user_message)]
            })
            
            # Run the sampling loop (adapted from the original demo)
            self.messages = await sampling_loop(
                model=self.model,
                provider=self.api_provider,
                system_prompt_suffix="",
                messages=self.messages,
                output_callback=self._output_callback,
                tool_output_callback=self._tool_output_callback,
                api_response_callback=self._api_response_callback,
                api_key=self.api_key,
                api_base_url=self.api_base_url,
                only_n_most_recent_images=3,
                max_tokens=settings.MAX_OUTPUT_TOKENS,
                tool_version="computer_use_20250124"
            )
            
            await self.on_status_update(self.session_id, "completed")
            
        except Exception as e:
            logger.error(f"Error processing message for session {self.session_id}: {e}")
            await self.on_status_update(self.session_id, "error", {
                "error": str(e)
            })
        finally:
            self.is_running = False
    
    async def _output_callback(self, content_block):
        """Handle output from the agent"""
        await self.on_output(self.session_id, content_block)
    
    async def _tool_output_callback(self, tool_result: ToolResult, tool_id: str):
        """Handle tool output"""
        await self.on_tool_result(
            self.session_id,
            tool_id,
            tool_result.output if tool_result else None,
            tool_result.error if tool_result else None
        )
    
    async def _api_response_callback(self, request, response, error):
        """Handle API response for debugging"""
        if error:
            logger.error(f"API error for session {self.session_id}: {error}")
        # Could send debug info via websocket if needed
    
    async def cleanup(self):
        """Clean up agent resources"""
        self.is_running = False
        if self.current_task:
            self.current_task.cancel()
        
        await self.on_status_update(self.session_id, "terminated")
    
    def get_conversation_history(self) -> List[BetaMessageParam]:
        """Get the current conversation history"""
        return self.messages.copy()
