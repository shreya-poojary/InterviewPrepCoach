"""Ollama local LLM provider implementation"""

import json
import re
from typing import Dict, Any, Optional
import requests
from .base_provider import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def __init__(self, model_name: str = "llama3.2", 
                 base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(model_name, **kwargs)
        self.base_url = base_url.rstrip('/')
    
    def _strip_json_comments(self, text: str) -> str:
        """Remove comments from JSON string (// and /* */ style comments)
        
        Args:
            text: JSON string potentially containing comments
            
        Returns:
            JSON string with comments removed
        """
        # Remove single-line comments (// ...)
        # But preserve // inside strings
        lines = text.split('\n')
        result_lines = []
        in_string = False
        string_char = None
        
        for line in lines:
            cleaned_line = []
            i = 0
            while i < len(line):
                char = line[i]
                
                # Track string boundaries
                if char in ('"', "'") and (i == 0 or line[i-1] != '\\'):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                
                # Only remove // if we're not in a string
                if not in_string and i < len(line) - 1 and line[i:i+2] == '//':
                    # Found comment, skip rest of line
                    break
                
                cleaned_line.append(char)
                i += 1
            
            result_lines.append(''.join(cleaned_line))
        
        # Remove multi-line comments (/* ... */)
        result = '\n'.join(result_lines)
        result = re.sub(r'/\*.*?\*/', '', result, flags=re.DOTALL)
        
        return result
    
    def _repair_json(self, text: str) -> str:
        """Attempt to repair common JSON issues
        
        Args:
            text: Potentially malformed JSON string
            
        Returns:
            Repaired JSON string
        """
        # Fix missing quotes around unquoted strings in arrays
        # Pattern: [..., word, ...] -> [..., "word", ...]
        # But be careful not to break numbers, booleans, null
        def fix_unquoted_strings(match):
            content = match.group(1)
            # Split by comma, but preserve quoted strings
            parts = []
            current = ""
            in_quotes = False
            quote_char = None
            
            for char in content:
                if char in ('"', "'") and (not current or current[-1] != '\\'):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                    current += char
                elif char == ',' and not in_quotes:
                    parts.append(current.strip())
                    current = ""
                else:
                    current += char
            
            if current:
                parts.append(current.strip())
            
            # Fix each part
            fixed_parts = []
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                # If it's already quoted, keep it
                if (part.startswith('"') and part.endswith('"')) or \
                   (part.startswith("'") and part.endswith("'")):
                    fixed_parts.append(part)
                # If it's a number, boolean, or null, keep it
                elif part.lower() in ('true', 'false', 'null') or \
                     (part.replace('.', '').replace('-', '').isdigit()):
                    fixed_parts.append(part)
                # Otherwise, quote it
                else:
                    fixed_parts.append(f'"{part}"')
            
            return '[' + ', '.join(fixed_parts) + ']'
        
        # Simple approach: find patterns like [..., word, ...] and quote unquoted strings
        # This is a simplified fix - more complex repairs might be needed
        text = re.sub(r'\[([^\]]+)\]', lambda m: self._fix_array_items(m.group(0)), text)
        
        return text
    
    def _fix_array_items(self, text: str) -> str:
        """Fix unquoted strings in JSON arrays (e.g., [..., SQL, ...] -> [..., "SQL", ...])"""
        # Pattern to find array items that might be missing quotes
        # Look for patterns like: "item", unquoted_item, "item"
        def fix_array(match):
            array_content = match.group(0)
            # Find all items in the array
            # Split by comma, but respect quoted strings
            items = []
            current = ""
            in_quotes = False
            quote_char = None
            depth = 0  # Track nested brackets/braces
            
            for i, char in enumerate(array_content):
                if char in ('"', "'") and (i == 0 or array_content[i-1] != '\\'):
                    if not in_quotes:
                        in_quotes = True
                        quote_char = char
                    elif char == quote_char:
                        in_quotes = False
                        quote_char = None
                    current += char
                elif char == '[' and not in_quotes:
                    depth += 1
                    current += char
                elif char == ']' and not in_quotes:
                    depth -= 1
                    current += char
                elif char == '{' and not in_quotes:
                    depth += 1
                    current += char
                elif char == '}' and not in_quotes:
                    depth -= 1
                    current += char
                elif char == ',' and depth == 0 and not in_quotes:
                    items.append(current.strip())
                    current = ""
                else:
                    current += char
            
            if current.strip():
                items.append(current.strip())
            
            # Fix each item
            fixed_items = []
            for item in items:
                item = item.strip().rstrip(',')
                if not item:
                    continue
                # Already properly quoted
                if (item.startswith('"') and item.endswith('"')) or \
                   (item.startswith("'") and item.endswith("'")):
                    fixed_items.append(item)
                # Number, boolean, null, object, or array
                elif item.lower() in ('true', 'false', 'null') or \
                     item.startswith('{') or item.startswith('[') or \
                     (item.replace('.', '').replace('-', '').replace('e', '').replace('E', '').replace('+', '').isdigit()):
                    fixed_items.append(item)
                # Missing quotes - add them
                else:
                    # Remove any existing partial quotes
                    item = item.strip('"').strip("'")
                    fixed_items.append(f'"{item}"')
            
            return '[' + ', '.join(fixed_items) + ']'
        
        # Find all JSON arrays and fix them
        # Pattern: [ followed by content, ending with ]
        result = re.sub(r'\[[^\]]*\]', fix_array, text)
        return result
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from prompt
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
        """
        try:
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "temperature": self.temperature,
                    "stream": False
                },
                timeout=180  # Increased timeout for longer responses
            )
            
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
        
        except requests.exceptions.ConnectionError:
            error_msg = "Cannot connect to Ollama. Make sure Ollama is running on http://localhost:11434"
            print(f"[ERROR] {error_msg}")
            return f"Error: {error_msg}"
        except requests.exceptions.HTTPError as e:
            error_msg = f"Ollama server error: {e.response.status_code if hasattr(e, 'response') else str(e)}"
            print(f"[ERROR] {error_msg}")
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"Ollama API error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return f"Error: {error_msg}"
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Generate JSON response from prompt
        
        Args:
            prompt: User prompt (should request JSON format)
            system_prompt: Optional system prompt
            
        Returns:
            Parsed JSON response or error dict
        """
        try:
            if "JSON" not in prompt and "json" not in prompt:
                prompt += "\n\nRespond with valid JSON only."
            
            response_text = self.generate(prompt, system_prompt)
            
            # Check for errors in response
            if response_text.startswith("Error:"):
                return {"error": response_text}
            
            if not response_text or len(response_text.strip()) == 0:
                return {"error": "Empty response from Ollama"}
            
            # Clean response - remove markdown code blocks
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            if not response_text:
                return {"error": "Empty response after cleaning"}
            
            # If response doesn't start with [ or {, try to find JSON in the text
            # This handles cases where LLM adds explanatory text before JSON
            if not response_text.startswith(('[', '{')):
                # Look for first [ or { that starts valid JSON
                json_start = -1
                for i, char in enumerate(response_text):
                    if char in ['[', '{']:
                        # Check if this looks like the start of JSON (next char should be whitespace, newline, or quote/brace)
                        if i < len(response_text) - 1:
                            next_char = response_text[i+1]
                            if next_char in ['\n', '\r', '\t', ' ', '"', '{', '[']:
                                json_start = i
                                break
                
                if json_start > 0:
                    # Extract JSON part
                    response_text = response_text[json_start:]
                    print(f"[DEBUG] Extracted JSON starting at position {json_start}")
                elif json_start == -1:
                    # No JSON found, try to extract from common patterns
                    # Look for "Here are..." or similar intro text followed by JSON
                    import re
                    # Try to find JSON array or object after colon or newline
                    json_match = re.search(r'[:\n]\s*(\[[\s\S]*\]|\{[\s\S]*\})', response_text)
                    if json_match:
                        response_text = json_match.group(1)
                        print(f"[DEBUG] Extracted JSON using regex pattern")
            
            # Remove JSON comments (// and /* */) that some LLMs add
            response_text = self._strip_json_comments(response_text)
            response_text = response_text.strip()
            
            # Try parsing
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON parsing error: {e}")
                print(f"[DEBUG] Response text (first 500 chars): {response_text[:500]}")
                
                # Try to repair common issues
                try:
                    repaired = response_text
                    
                    # Fix missing opening quotes: , word" -> , "word" (most common issue)
                    repaired = re.sub(r',\s*([A-Za-z_][A-Za-z0-9_/() ]+?)"', r', "\1"', repaired)
                    # Fix missing opening quotes: [word" -> ["word"
                    repaired = re.sub(r'\[\s*([A-Za-z_][A-Za-z0-9_/() ]+?)"', r'["\1"', repaired)
                    # Fix missing opening quotes: , word, -> , "word",
                    repaired = re.sub(r',\s*([A-Za-z_][A-Za-z0-9_/() ]+?)\s*,', r', "\1",', repaired)
                    # Fix missing opening quotes at start: [word, -> ["word",
                    repaired = re.sub(r'\[\s*([A-Za-z_][A-Za-z0-9_/() ]+?)\s*,', r'["\1",', repaired)
                    # Fix missing closing quotes: , word] -> , "word"]
                    repaired = re.sub(r',\s*([A-Za-z_][A-Za-z0-9_/() ]+?)\s*\]', r', "\1"]', repaired)
                    
                    # Now apply the more comprehensive fix
                    repaired = self._fix_array_items(repaired)
                    repaired = self._strip_json_comments(repaired)
                    
                    print(f"[DEBUG] Attempting to parse repaired JSON...")
                    return json.loads(repaired)
                except Exception as repair_error:
                    print(f"[DEBUG] Repair attempt failed: {repair_error}")
                    import traceback
                    traceback.print_exc()
                    pass
                
                # Try to extract complete JSON object if response is truncated
                try:
                    # Find the last complete closing brace
                    last_brace = response_text.rfind('}')
                    if last_brace > 0:
                        # Find matching opening brace
                        first_brace = response_text.find('{')
                        if first_brace >= 0 and first_brace < last_brace:
                            potential_json = response_text[first_brace:last_brace + 1]
                            potential_json = self._strip_json_comments(potential_json)
                            
                            # Check for incomplete strings in arrays (common truncation issue)
                            # If we see an unclosed quote before the last brace, try to close it
                            lines = potential_json.split('\n')
                            fixed_lines = []
                            for i, line in enumerate(lines):
                                # Count unescaped quotes
                                quote_count = 0
                                escaped = False
                                for char in line:
                                    if escaped:
                                        escaped = False
                                        continue
                                    if char == '\\':
                                        escaped = True
                                        continue
                                    if char == '"':
                                        quote_count += 1
                                
                                # If odd number of quotes and line ends with comma or is in an array
                                if quote_count % 2 != 0 and ('[' in line or ',' in line):
                                    # Try to close the string if it looks incomplete
                                    if not line.rstrip().endswith('"') and not line.rstrip().endswith('",'):
                                        # Add closing quote and comma if needed
                                        stripped = line.rstrip()
                                        if stripped.endswith(','):
                                            line = stripped[:-1] + '",'
                                        else:
                                            line = stripped + '"'
                                fixed_lines.append(line)
                            potential_json = '\n'.join(fixed_lines)
                            
                            # Try to close any incomplete arrays/objects
                            # Count braces and brackets
                            open_braces = potential_json.count('{') - potential_json.count('}')
                            open_brackets = potential_json.count('[') - potential_json.count(']')
                            
                            # Close incomplete arrays first (remove trailing comma if present)
                            if open_brackets > 0:
                                potential_json = potential_json.rstrip().rstrip(',')
                                potential_json += ']' * open_brackets
                            
                            # Close incomplete objects
                            if open_braces > 0:
                                potential_json = potential_json.rstrip().rstrip(',')
                                potential_json += '}' * open_braces
                            
                            return json.loads(potential_json)
                except Exception as repair_error:
                    print(f"[DEBUG] Final repair attempt failed: {repair_error}")
                
                return {"error": f"Failed to parse JSON response: {str(e)}"}
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return {"error": "Failed to parse JSON response"}
        except Exception as e:
            print(f"Error: {e}")
            return {"error": str(e)}
    
    def list_models(self) -> list:
        """List available Ollama models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            result = response.json()
            return [model['name'] for model in result.get('models', [])]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

