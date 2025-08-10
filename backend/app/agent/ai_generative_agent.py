"""
AI Generative Agent - Pure AI for generating xdotool commands
Focus on:
1. AI understands user intent from chat
2. AI generates appropriate xdotool commands
3. Agent does NOT execute commands directly (pure generative)
4. Execution is performed by separate VNC service via executor endpoint
"""
import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List
import requests
import http.client
from typing import cast
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIGenerativeAgent:
    """AI Agent that is pure generative for computer control via xdotool"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.vnc_api_base = "http://vnc-agent:8090"
        self.conversation_history = []
        
    async def process_message(self, user_message: str) -> Dict[str, Any]:
        """Process user message with AI generative approach and automatic execution."""
        try:
            logger.info(f"AI Agent processing: {user_message}")
            
            # Add user message to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            
            # Generate AI response and xdotool commands
            ai_response = await self._generate_ai_response(user_message)
            
            # Extract xdotool commands from AI response
            xdotool_commands = self._extract_xdotool_commands(ai_response)
            
            # Execute commands if available
            execution_results = []
            if xdotool_commands:
                logger.info(f"Executing {len(xdotool_commands)} commands")
                for cmd in xdotool_commands:
                    result = await self._execute_xdotool_command(cmd)
                    execution_results.append(result)
            
            # Generate execution report
            execution_report = self._generate_execution_report(xdotool_commands, execution_results, ai_response)
            
            # Add AI response to conversation history with execution details
            self.conversation_history.append({
                "role": "assistant", 
                "content": ai_response,
                "commands_suggested": xdotool_commands,
                "execution_results": execution_results,
                "timestamp": datetime.now().isoformat()
            })
            
            # Format final response
            final_response = ai_response + "\n\n" + execution_report
            
            return {
                "success": True,
                "response": final_response,
                "actions_taken": xdotool_commands,
                "execution_results": execution_results,
                "ai_reasoning": ai_response
            }
            
        except Exception as e:
            logger.error(f"Error in AI agent: {e}")
            return {
                "success": False,
                "response": f"AI Agent error: {str(e)}",
                "actions_taken": [],
                "error": str(e)
            }
    
    async def _generate_ai_response(self, user_message: str) -> str:
        """Generate AI response using configured LLM; prefer Comet API, fallback to simple."""
        
        # Create system prompt for computer control - focus on JSON structured commands
        system_prompt = """You are an AI assistant that controls a computer desktop environment through xdotool commands.

Your job is to:
1. Understand what the user wants to do on the computer
2. Generate the appropriate xdotool commands to accomplish the task
3. Return response in consistent JSON format

Available applications and common commands:
- firefox-esr (web browser)
- xcalc (calculator) 
- xterm (terminal)
- gedit (text editor)
- nautilus (file manager)
- Applications should be launched directly with "DISPLAY=:1 appname &"

Common xdotool operations:
- Open app: "DISPLAY=:1 appname &" (direct launch, preferred method)
- Type text: "xdotool type \"text here\""
- Click coordinates: "xdotool mousemove X Y", "xdotool click 1"
- Key combinations: "xdotool key ctrl+c", "xdotool key alt+Tab", etc.
- Window management: "xdotool key alt+F4" (close), "xdotool key super+Up" (maximize)
- Mouse actions: "xdotool click 1" (left), "xdotool click 3" (right), "xdotool click 4" (scroll up), "xdotool click 5" (scroll down)
- Special keys: Return, Escape, Tab, space, BackSpace, Delete, Home, End, Up, Down, Left, Right

MANDATORY JSON RESPONSE FORMAT:
{
  "action": "Brief description of what you're doing in English",
  "commands": [
    "xdotool command 1",
    "sleep 2", 
    "xdotool command 2"
  ]
}

Examples:
User: "open calculator" → Open calculator
{
  "action": "Opening calculator application",
  "commands": [
    "DISPLAY=:1 xcalc &"
  ]
}

User: "open firefox" → Open Firefox
{
  "action": "Opening Firefox browser",
  "commands": [
    "DISPLAY=:1 firefox-esr &"
  ]
}

User: "open gedit" → Open text editor
{
  "action": "Opening Gedit text editor",
  "commands": [
    "DISPLAY=:1 gedit &"
  ]
}

User: "type hello world" → Type text
{
  "action": "Typing text 'hello world'",
  "commands": [
    "xdotool type \"hello world\""
  ]
}

User: "click at coordinates 300 200" → Click at coordinates
{
  "action": "Clicking at coordinates (300, 200)",
  "commands": [
    "xdotool mousemove 300 200",
    "sleep 1",
    "xdotool click 1"
  ]
}

User: "press enter" → Press key
{
  "action": "Pressing Enter key",
  "commands": [
    "xdotool key Return"
  ]
}

User: "close window" → Close window
{
  "action": "Closing active window",
  "commands": [
    "xdotool key alt+F4"
  ]
}

User: "scroll down" → Scroll down
{
  "action": "Scrolling down",
  "commands": [
    "xdotool click 5",
    "xdotool click 5",
    "xdotool click 5"
  ]
}

User: "open firefox and search weather jakarta" → Open Firefox and search
{
  "action": "Opening Firefox and searching for weather Jakarta",
  "commands": [
    "DISPLAY=:1 firefox-esr &",
    "sleep 5",
    "xdotool key ctrl+l",
    "sleep 1",
    "xdotool type \"weather jakarta\"",
    "xdotool key Return"
  ]
}

CRITICAL RULES:
1. ALWAYS respond with valid JSON format only
2. No additional text outside the JSON
3. Use double quotes for strings in JSON
4. Escape quotes inside command strings properly
5. Include "sleep" commands between UI operations that need time
6. Keep action description in English, commands in English
7. Be creative and intelligent about interpreting user requests
8. If coordinates aren't specified for clicks, ask for them or suggest reasonable defaults
9. Handle complex tasks by breaking them into multiple xdotool commands
10. For opening apps, use "DISPLAY=:1 appname &" NOT alt+F2 sequences
11. For Firefox searches, use Ctrl+L to focus address bar then type search term
12. Always wait 3-5 seconds after opening apps before interacting with them"""

        # Create conversation context
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add recent conversation history (last 5 messages)
        recent_history = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
        for msg in recent_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({
            "role": "user", 
            "content": user_message
        })
        
        # Use Comet API for flexible AI generation (re-enabled after system prompt fixes)
        try:
            if settings.API_PROVIDER.lower() == "comet" and getattr(settings, "COMET_API_KEY", ""):
                logger.info(f"Using Comet API with provider: {settings.API_PROVIDER}, key exists: {bool(getattr(settings, 'COMET_API_KEY', ''))}")
                host = settings.COMET_API_BASE_URL.replace("https://", "").replace("http://", "")
                if "/" in host:
                    host = host.split("/")[0]
                logger.info(f"Connecting to Comet API host: {host}")
                conn = http.client.HTTPSConnection(host)
                payload = {
                    "model": getattr(settings, "COMET_MODEL", "cometapi-3-7-sonnet"),
                    "max_tokens": getattr(settings, "COMET_MAX_TOKENS", 1024),
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        *cast(List[Dict[str, str]], messages[1:])
                    ]
                }
                headers = {
                    "Authorization": f"Bearer {settings.COMET_API_KEY}",
                    "Content-Type": "application/json"
                }
                conn.request("POST", "/v1/messages", json.dumps(payload), headers)
                logger.info("Comet API request sent, waiting for response...")
                res = conn.getresponse()
                raw = res.read().decode("utf-8", errors="ignore")
                logger.info(f"Comet API response received (status: {res.status}): {raw[:200]}...")
                # Attempt to parse JSON and extract assistant content
                try:
                    data = json.loads(raw)
                    content = None
                    if isinstance(data, dict):
                        # Comet API format: {"content":[{"type":"text","text":"..."}]}
                        if isinstance(data.get("content"), list) and data["content"]:
                            first_content = data["content"][0]
                            if isinstance(first_content, dict) and first_content.get("type") == "text":
                                content = first_content.get("text")
                        elif isinstance(data.get("content"), str):
                            content = data["content"]
                        elif isinstance(data.get("messages"), list) and data["messages"]:
                            last = data["messages"][-1]
                            if isinstance(last, dict) and last.get("role") == "assistant":
                                content = last.get("content")  # type: ignore[assignment]
                        elif isinstance(data.get("choices"), list) and data["choices"]:
                            choice = data["choices"][0]
                            if isinstance(choice, dict):
                                msg = choice.get("message") or choice.get("delta")
                                if isinstance(msg, dict):
                                    content = msg.get("content")  # type: ignore[assignment]
                    if content and isinstance(content, str) and content.strip():
                        logger.info("Successfully extracted content from Comet API response")
                        return content
                    if raw.strip():
                        logger.info("Using raw Comet API response")
                        return raw
                except Exception as parse_error:
                    logger.warning(f"Failed to parse Comet response: {parse_error}")
                    if raw.strip():
                        return raw
        except Exception as e:
            logger.warning(f"Comet generation failed, falling back to simple: {e}")

        # Fallback simple generator (only used if Comet API fails)
        logger.info("Using fallback simple generator")
        return self._generate_simple_ai_response(user_message)
    
    def _generate_simple_ai_response(self, user_message: str) -> str:
        """Improved simple AI response generator - more flexible fallback using pattern matching"""
        
        user_input = user_message.lower().strip()
        
        # Handle Firefox + search/browse commands flexibly
        if "firefox" in user_input:
            # Check if this is a search command
            search_indicators = ["search", "cari", "cek", "find", "lookup", "check", "weather", "cuaca", "google", "browse", "open", "buka", "untuk", "for"]
            is_search = any(word in user_input for word in search_indicators)
            
            if is_search:
                # Extract search term dynamically
                search_term = user_input
                # Remove common command words
                stop_words = ["buka", "open", "firefox", "dan", "and", "search", "cari", "find", "lookup", "check", "cek", "kondisi", "untuk", "for", "di", "in"]
                for word in stop_words:
                    search_term = search_term.replace(word, " ")
                search_term = " ".join(search_term.split()).strip()
                
                if not search_term:
                    search_term = "informasi"
                
                return json.dumps({
                    "action": f"Opening Firefox and searching for {search_term}",
                    "commands": [
                        "DISPLAY=:1 firefox-esr &",
                        "sleep 5",
                        "xdotool key ctrl+l",
                        "sleep 1",
                        f"xdotool type \"{search_term}\"",
                        "xdotool key Return"
                    ]
                })
            else:
                # Just open Firefox
                return json.dumps({
                    "action": "Opening Firefox browser",
                    "commands": [
                        "DISPLAY=:1 firefox-esr &"
                    ]
                })
        
        # Handle app opening patterns more flexibly
        open_keywords = ["buka", "open", "jalankan", "launch", "start", "run"]
        if any(keyword in user_input for keyword in open_keywords):
            
            # App name mapping with more flexible matching
            app_patterns = {
                "kalkulator|calculator|calc": ("xcalc", "calculator"),
                "gedit|editor|text|notepad": ("gedit", "text editor"),
                "terminal|xterm|console|konsole": ("xterm", "terminal"),
                "nautilus|file|folder|manager": ("nautilus", "file manager"),
                "browser|firefox": ("firefox-esr", "Firefox browser")
            }
            
            # Find matching app
            for pattern, (executable, display_name) in app_patterns.items():
                if any(app_word in user_input for app_word in pattern.split("|")):
                    return json.dumps({
                        "action": f"Opening {display_name}",
                        "commands": [
                            f"DISPLAY=:1 {executable} &"
                        ]
                    })
            
            # If no specific app found, try to extract app name from message
            words = user_input.split()
            for word in words:
                if word not in open_keywords and len(word) > 2:
                    return json.dumps({
                        "action": f"Opening application {word}",
                        "commands": [
                            f"DISPLAY=:1 {word} &"
                        ]
                    })
        
        # Handle typing commands flexibly
        type_keywords = ["ketik", "type", "tulis", "write", "input"]
        if any(keyword in user_input for keyword in type_keywords):
            # Extract text to type
            text_to_type = user_input
            for keyword in type_keywords:
                text_to_type = text_to_type.replace(keyword, " ")
            text_to_type = " ".join(text_to_type.split()).strip()
            
            if text_to_type:
                return json.dumps({
                    "action": f"Typing text: {text_to_type}",
                    "commands": [
                        f"xdotool type \"{text_to_type}\""
                    ]
                })
        
        # Handle click commands flexibly
        click_keywords = ["klik", "click", "tekan", "press"]
        if any(keyword in user_input for keyword in click_keywords):
            # Extract coordinates if provided
            coords = re.findall(r'(\d+)[,\s]+(\d+)', user_input)
            if coords:
                x, y = coords[0]
                return json.dumps({
                    "action": f"Clicking at coordinates ({x}, {y})",
                    "commands": [
                        f"xdotool mousemove {x} {y}",
                        "sleep 1",
                        "xdotool click 1"
                    ]
                })
        
        # Handle key press commands
        key_patterns = {
            "enter|return": "Return",
            "escape|esc": "Escape",
            "tab": "Tab",
            "space|spasi": "space",
            "backspace": "BackSpace",
            "delete|del": "Delete",
            "up|atas": "Up",
            "down|bawah": "Down",
            "left|kiri": "Left",
            "right|kanan": "Right"
        }
        
        for pattern, key_name in key_patterns.items():
            if any(key_word in user_input for key_word in pattern.split("|")):
                return json.dumps({
                    "action": f"Pressing {key_name} key",
                    "commands": [
                        f"xdotool key {key_name}"
                    ]
                })
        
        # Handle window management
        if any(word in user_input for word in ["tutup", "close", "keluar", "exit"]):
            return json.dumps({
                "action": "Closing active window",
                "commands": [
                    "xdotool key alt+F4"
                ]
            })
        
        if any(word in user_input for word in ["maksimal", "maximize", "besar", "max"]):
            return json.dumps({
                "action": "Maximizing window",
                "commands": [
                    "xdotool key super+Up"
                ]
            })
        
        # Handle scroll commands
        if any(word in user_input for word in ["scroll", "gulir"]):
            if any(word in user_input for word in ["bawah", "down"]):
                return json.dumps({
                    "action": "Scrolling down",
                    "commands": [
                        "xdotool click 5",
                        "xdotool click 5",
                        "xdotool click 5"
                    ]
                })
            elif any(word in user_input for word in ["atas", "up"]):
                return json.dumps({
                    "action": "Scrolling up",
                    "commands": [
                        "xdotool click 4",
                        "xdotool click 4",
                        "xdotool click 4"
                    ]
                })
        
        # For direct xdotool commands
        if "xdotool" in user_input:
            return json.dumps({
                "action": "Executing direct xdotool command",
                "commands": [
                    user_message.strip()
                ]
            })
        
        # Generic fallback - be more helpful
        return json.dumps({
            "action": "Need more specific instructions",
            "commands": [
                "echo \"Please provide commands like: 'open firefox', 'type hello world', 'click 300 200', 'press enter'\""
            ]
        })

    def _extract_xdotool_commands(self, ai_response: str) -> List[str]:
        """Extract xdotool commands from AI response (JSON format or legacy format)"""
        commands = []
        
        # Try to parse as JSON first
        try:
            # Clean up response - remove markdown code blocks if present
            clean_response = ai_response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response.replace("```json", "").replace("```", "").strip()
            elif clean_response.startswith("```"):
                clean_response = clean_response.replace("```", "").strip()
            
            # Parse JSON
            data = json.loads(clean_response)
            if isinstance(data, dict) and "commands" in data:
                commands = data["commands"]
                logger.info(f"Extracted {len(commands)} commands from JSON response")
                return commands
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse JSON response: {e}, falling back to regex")
        
        # Fallback to legacy <xdotool> format
        pattern = r'<xdotool>(.*?)</xdotool>'
        matches = re.findall(pattern, ai_response, re.DOTALL)
        
        for match in matches:
            command = match.strip()
            if command:
                commands.append(command)
        
        return commands
    
    async def _execute_xdotool_command(self, command: str) -> Dict[str, Any]:
        """Execute single xdotool command via VNC executor API"""
        try:
            logger.info(f"Executing command: {command}")
            response = requests.post(
                f"{self.vnc_api_base}/execute", 
                json={"command": command}, 
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Command executed successfully: {result}")
                return {
                    "command": command,
                    "success": True,
                    "return_code": result.get("return_code", 0),
                    "output": result.get("output", ""),
                    "error": result.get("error", "")
                }
            else:
                logger.error(f"Command execution failed: {response.status_code}")
                return {
                    "command": command,
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logger.error(f"Error executing command {command}: {e}")
            return {
                "command": command,
                "success": False,
                "error": str(e)
            }
    
    def _generate_execution_report(self, commands: List[str], results: List[Dict[str, Any]], ai_response: str = "") -> str:
        """Generate execution report after commands are run"""
        if not commands:
            return "[REPORT]: No commands to execute."
        
        # Try to extract action from AI response
        action_description = "Command execution"
        try:
            # Clean up response and parse JSON
            clean_response = ai_response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response.replace("```json", "").replace("```", "").strip()
            elif clean_response.startswith("```"):
                clean_response = clean_response.replace("```", "").strip()
            
            data = json.loads(clean_response)
            if isinstance(data, dict) and "action" in data:
                action_description = data["action"]
        except:
            pass
        
        successful = sum(1 for r in results if r.get("success", False))
        failed = len(results) - successful
        
        report = f"[REPORT]: {action_description} - {successful} successful, {failed} failed\n"
        
        for i, result in enumerate(results, 1):
            cmd_short = result["command"][:50] + "..." if len(result["command"]) > 50 else result["command"]
            if result.get("success", False):
                report += f"✅ Command {i}: {cmd_short}\n"
                if result.get("output"):
                    report += f"   Output: {result['output'].strip()[:100]}\n"
            else:
                report += f"❌ Command {i}: {cmd_short}\n"
                report += f"   Error: {result.get('error', 'Unknown error')[:100]}\n"
        
        return report
    

