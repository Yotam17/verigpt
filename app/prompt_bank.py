#!/usr/bin/env python3
"""
Prompt Bank - Manages loading and formatting of prompt templates
"""

import os
from typing import Dict, Any
from pathlib import Path

class PromptBank:
    """Manages prompt templates with placeholder substitution"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        """Initialize with prompts directory"""
        self.prompts_dir = Path(prompts_dir)
        self._prompts_cache: Dict[str, str] = {}
        
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompts directory '{prompts_dir}' not found")
    
    def load_prompt(self, name: str) -> str:
        """Load prompt template from file"""
        if name in self._prompts_cache:
            return self._prompts_cache[name]
        
        prompt_file = self.prompts_dir / f"{name}.txt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt template '{name}.txt' not found in {self.prompts_dir}")
        
        try:
            with open(prompt_file, 'r', encoding='utf-8') as file:
                prompt_content = file.read()
                self._prompts_cache[name] = prompt_content
                return prompt_content
        except Exception as e:
            raise Exception(f"Error loading prompt '{name}': {e}")
    
    def format_prompt(self, name: str, **kwargs: Any) -> str:
        """Load and format prompt template with provided arguments"""
        prompt_template = self.load_prompt(name)
        
        try:
            # Simple placeholder substitution using {{placeholder}} format
            formatted_prompt = prompt_template
            for key, value in kwargs.items():
                placeholder = f"{{{{{key}}}}}"
                if placeholder in formatted_prompt:
                    formatted_prompt = formatted_prompt.replace(placeholder, str(value))
                else:
                    print(f"Warning: Placeholder '{placeholder}' not found in prompt template")
            
            return formatted_prompt
        except Exception as e:
            raise Exception(f"Error formatting prompt '{name}': {e}")
    
    def list_prompts(self) -> list:
        """List all available prompt templates"""
        prompt_files = []
        for file_path in self.prompts_dir.glob("*.txt"):
            prompt_files.append(file_path.stem)
        return sorted(prompt_files)
    
    def clear_cache(self):
        """Clear the prompts cache"""
        self._prompts_cache.clear()
