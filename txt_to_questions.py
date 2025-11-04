# Date: 2025-11-03
# Author: Bornold 
# AI Assistant: Claude Sonnet 4 

import os
import json
import requests
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import time


def load_settings(settings_file: str = "settings.json") -> Dict:
    """Load settings from JSON file with fallback defaults."""
    default_settings = {
        "ollama": {
            "base_url": "http://localhost:11434",
            "model": "llama3.1:8b",
            "timeout": 120,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 2000
            }
        },
        "question_generation": {
            "question_types": ["multiple_choice", "short_answer", "true_false", "essay"],
            "questions_per_chunk": 4,
            "max_chunk_size": 4000,
            "text_input_dir": "text_output",
            "questions_output_dir": "questions_output"
        }
    }
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                for key in default_settings:
                    if key not in settings:
                        settings[key] = default_settings[key]
                    elif isinstance(default_settings[key], dict):
                        for subkey in default_settings[key]:
                            if subkey not in settings[key]:
                                settings[key][subkey] = default_settings[key][subkey]
                return settings
        except Exception as e:
            print(f"⚠️  Error loading settings from {settings_file}: {e}")
            print("Using default settings...")
    else:
        print(f"⚠️  Settings file {settings_file} not found. Using default settings...")
    
    return default_settings


class OllamaQuestionGenerator:
    def __init__(self, settings_file: str = "settings.json"):
        """
        Initialize the Ollama Question Generator from settings file.
        
        Args:
            settings_file (str): Path to settings JSON file
        """
        self.settings = load_settings(settings_file)
        
        # Extract Ollama settings
        ollama_config = self.settings["ollama"]
        self.base_url = ollama_config["base_url"]
        self.model = ollama_config["model"]
        self.timeout = ollama_config["timeout"]
        self.ollama_options = ollama_config["options"]
        self.api_url = f"{self.base_url}/api/generate"
        
        # Extract question generation settings
        self.question_config = self.settings["question_generation"]
        
        # Token accounting
        self.total_input_tokens = 0
        self.total_cached_input_tokens = 0
        self.total_output_tokens = 0
        self._used_estimates = False
        
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def chunk_text(self, text: str, max_chunk_size: int = None) -> List[str]:
        """
        Intelligently chunk text into manageable pieces.
        Tries to break at natural boundaries (slides, sections, paragraphs).
        """
        if max_chunk_size is None:
            max_chunk_size = self.question_config["max_chunk_size"]
            
        chunks = []
        
        # First, try to split by slides
        slide_sections = re.split(r'=== SLIDE \d+ ===', text)
        
        current_chunk = ""
        for section in slide_sections:
            section = section.strip()
            if not section:
                continue
                
            # If adding this section would exceed max size, save current chunk
            if len(current_chunk + section) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = section
            else:
                current_chunk += "\n" + section if current_chunk else section
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # If chunks are still too large, split by paragraphs
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= max_chunk_size:
                final_chunks.append(chunk)
            else:
                # Split by double newlines (paragraphs)
                paragraphs = chunk.split('\n\n')
                temp_chunk = ""
                for para in paragraphs:
                    if len(temp_chunk + para) > max_chunk_size and temp_chunk:
                        final_chunks.append(temp_chunk.strip())
                        temp_chunk = para
                    else:
                        temp_chunk += "\n\n" + para if temp_chunk else para
                if temp_chunk.strip():
                    final_chunks.append(temp_chunk.strip())
        
        return final_chunks
    
    def generate_questions(self, text_chunk: str, question_types: List[str] = None, 
                         num_questions: int = 5) -> Dict:
        """
        Generate study questions from a text chunk using Ollama.
        
        Args:
            text_chunk (str): Text content to generate questions from
            question_types (List[str]): Types of questions to generate
            num_questions (int): Number of questions to generate
        """
        if question_types is None:
            question_types = self.question_config["question_types"]
        
        # Create a comprehensive prompt
        prompt = f"""Based on the following educational content, generate {num_questions} study questions to help a student learn and review the material.

CONTENT:
{text_chunk}

INSTRUCTIONS:
Generate a mix of the following question types: {', '.join(question_types)}

For each question, provide:
1. Question type (multiple_choice, short_answer, true_false, or essay)
2. The question text
3. The correct answer(s)
4. For multiple choice: provide 4 options (A, B, C, D)
5. Brief explanation of why the answer is correct

Format your response as a JSON array where each question is an object with these fields:
- "type": question type
- "question": the question text
- "options": array of options (for multiple choice, empty array for others)
- "correct_answer": the correct answer
- "explanation": brief explanation

Generate questions that test understanding, not just memorization. Focus on key concepts, relationships, and practical applications.

Response (JSON only, no other text):"""

        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": self.ollama_options
            }
            
            response = requests.post(self.api_url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get('response', '').strip()
            # Try to extract token usage from the response (if the Ollama API provides it).
            token_info = self._extract_token_stats(result, prompt, response_text)
            # Update running totals
            self.total_input_tokens += token_info.get('input_tokens', 0)
            self.total_cached_input_tokens += token_info.get('cached_input_tokens', 0)
            self.total_output_tokens += token_info.get('output_tokens', 0)
            if token_info.get('used_estimate', False):
                self._used_estimates = True
            
            # Try to extract JSON from the response
            try:
                # Look for JSON array in the response
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    questions_data = json.loads(json_match.group())
                    return {
                        "success": True,
                        "questions": questions_data,
                        "raw_response": response_text,
                        "token_info": token_info
                    }
                else:
                    return {
                        "success": False,
                        "error": "No valid JSON found in response",
                        "raw_response": response_text,
                        "token_info": token_info
                    }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"JSON parsing error: {str(e)}",
                    "raw_response": response_text
                }
                
        except requests.exceptions.RequestException as e:
            # On request failure we can still estimate input tokens from the prompt
            estimated_input = self._estimate_tokens(prompt)
            self.total_input_tokens += estimated_input
            self._used_estimates = True
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
                "raw_response": "",
                "token_info": {
                    "input_tokens": estimated_input,
                    "cached_input_tokens": 0,
                    "output_tokens": 0,
                    "used_estimate": True
                }
            }

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimate (chars / 4). Used as a fallback when the API doesn't provide counts."""
        if not text:
            return 0
        return max(1, int(len(text) / 4))

    def _extract_token_stats(self, result_json: Dict, prompt: str, response_text: str) -> Dict:
        """Try to find token counts in the API response. If not available, return estimates.

        The function searches common keys used by LLM APIs and falls back to estimating
        tokens from prompt/response lengths.
        """
        token_info = {
            'input_tokens': 0,
            'cached_input_tokens': 0,
            'output_tokens': 0,
            'used_estimate': False
        }

        # Search known locations for usage/token fields
        def find_numbers(obj):
            results = {}
            if isinstance(obj, dict):
                for k, v in obj.items():
                    key = k.lower()
                    if isinstance(v, (int, float)) and any(sub in key for sub in ['token', 'tokens', 'usage', 'count']):
                        results[key] = int(v)
                    else:
                        results.update(find_numbers(v))
            elif isinstance(obj, list):
                for item in obj:
                    results.update(find_numbers(item))
            return results

        found = find_numbers(result_json)
        # Heuristics: look for likely keys
        for k, v in found.items():
            if 'input' in k and 'cached' in k:
                token_info['cached_input_tokens'] = v
            elif 'cached' in k and 'input' not in k and 'output' not in k:
                # generic cached tokens
                token_info['cached_input_tokens'] = v
            elif 'input' in k and 'token' in k:
                token_info['input_tokens'] = v
            elif 'output' in k or 'generation' in k or 'response' in k:
                token_info['output_tokens'] = v
            elif 'total' in k and 'token' in k:
                # if only total provided, split roughly
                total = v
                est_input = self._estimate_tokens(prompt)
                est_output = self._estimate_tokens(response_text)
                token_info['input_tokens'] = min(est_input, total)
                token_info['output_tokens'] = max(0, total - token_info['input_tokens'])

        # If we found nothing, estimate
        if token_info['input_tokens'] == 0 and token_info['output_tokens'] == 0 and token_info['cached_input_tokens'] == 0:
            token_info['input_tokens'] = self._estimate_tokens(prompt)
            token_info['output_tokens'] = self._estimate_tokens(response_text)
            token_info['used_estimate'] = True

        return token_info
    
    def process_text_file(self, file_path: str, output_dir: str = None, 
                         question_types: List[str] = None, questions_per_chunk: int = None) -> bool:
        """
        Process a single text file and generate questions.
        
        Args:
            file_path (str): Path to the text file
            output_dir (str): Directory to save generated questions (uses settings default if None)
            question_types (List[str]): Types of questions to generate (uses settings default if None)
            questions_per_chunk (int): Number of questions per text chunk (uses settings default if None)
        """
        if output_dir is None:
            output_dir = self.question_config["questions_output_dir"]
        if question_types is None:
            question_types = self.question_config["question_types"]
        if questions_per_chunk is None:
            questions_per_chunk = self.question_config["questions_per_chunk"]
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Read the text file
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            if not text_content.strip():
                print(f"Warning: {file_path} is empty, skipping...")
                return False
            
            # Chunk the text
            chunks = self.chunk_text(text_content)
            print(f"Processing {os.path.basename(file_path)}: {len(chunks)} chunks")
            
            all_questions = []
            
            # Process each chunk
            for i, chunk in enumerate(chunks, 1):
                print(f"  Generating questions for chunk {i}/{len(chunks)}...")
                
                result = self.generate_questions(chunk, question_types, questions_per_chunk)
                
                if result["success"]:
                    chunk_questions = result["questions"]
                    # Add chunk info to each question
                    for q in chunk_questions:
                        q["source_chunk"] = i
                        q["source_file"] = os.path.basename(file_path)
                    all_questions.extend(chunk_questions)
                else:
                    print(f"    Error processing chunk {i}: {result['error']}")
            
            if all_questions:
                # Save questions to JSON file
                output_filename = os.path.splitext(os.path.basename(file_path))[0] + "_questions.json"
                output_path = os.path.join(output_dir, output_filename)
                
                output_data = {
                    "source_file": os.path.basename(file_path),
                    "generated_at": datetime.now().isoformat(),
                    "total_questions": len(all_questions),
                    "model_used": self.model,
                    "questions": all_questions
                }
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                
                print(f"  Generated {len(all_questions)} questions → {output_filename}")
                return True
            else:
                print(f"  No questions generated for {file_path}")
                return False
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return False
    
    def process_directory(self, text_dir: str = None, output_dir: str = None,
                         question_types: List[str] = None, questions_per_chunk: int = None,
                         file_pattern: str = "*.txt") -> Dict[str, int]:
        """
        Process all text files in a directory and generate questions.
        
        Args:
            text_dir (str): Directory containing text files (uses settings default if None)
            output_dir (str): Directory to save questions (uses settings default if None)
            question_types (List[str]): Types of questions to generate (uses settings default if None)
            questions_per_chunk (int): Questions per chunk (uses settings default if None)
            file_pattern (str): File pattern to match
        
        Returns:
            Dict with processing statistics
        """
        if text_dir is None:
            text_dir = self.question_config["text_input_dir"]
        if output_dir is None:
            output_dir = self.question_config["questions_output_dir"]
        if question_types is None:
            question_types = self.question_config["question_types"]
        if questions_per_chunk is None:
            questions_per_chunk = self.question_config["questions_per_chunk"]
        if not os.path.exists(text_dir):
            print(f"Error: Directory '{text_dir}' not found")
            return {"processed": 0, "failed": 0, "total_questions": 0}
        
        # Get all text files
        txt_files = [f for f in os.listdir(text_dir) if f.endswith('.txt')]
        
        if not txt_files:
            print(f"No .txt files found in '{text_dir}'")
            return {"processed": 0, "failed": 0, "total_questions": 0}
        
        print(f"Found {len(txt_files)} text files to process...")
        print(f"Using model: {self.model}")
        
        stats = {"processed": 0, "failed": 0, "total_questions": 0}
        
        for filename in txt_files:
            file_path = os.path.join(text_dir, filename)
            success = self.process_text_file(file_path, output_dir, question_types, questions_per_chunk)
            
            if success:
                stats["processed"] += 1
                # Count questions in the generated file
                output_filename = os.path.splitext(filename)[0] + "_questions.json"
                output_path = os.path.join(output_dir, output_filename)
                try:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        stats["total_questions"] += data.get("total_questions", 0)
                except:
                    pass
            else:
                stats["failed"] += 1
        
        return stats


def main():
    """Main function to demonstrate usage."""
    start = time.time()
    
    # Initialize the question generator from settings
    generator = OllamaQuestionGenerator("settings.json")
    
    # Test Ollama connection
    if not generator.test_connection():
        print(f"❌ Error: Cannot connect to Ollama at {generator.base_url}")
        print("Make sure Ollama is running with: ollama serve")
        return
    
    print("✅ Connected to Ollama successfully!")
    print(f"🔧 Using model: {generator.model}")
    print(f"🌐 Ollama URL: {generator.base_url}")
    
    # Process all text files using settings
    print("\nStarting question generation...")
    stats = generator.process_directory()
    
    print(f"\n🎓 Question Generation Complete!")
    print(f"   📄 Files processed: {stats['processed']}")
    print(f"   ❌ Files failed: {stats['failed']}")
    print(f"   ❓ Total questions generated: {stats['total_questions']}")
    print(f"   📁 Questions saved to: {generator.question_config['questions_output_dir']}/")

    # Print AI token usage statistics (if available or estimated)
    try:
        print("\n🔢 AI token usage summary:")
        print(f"   Total input tokens (sum): {generator.total_input_tokens}")
        print(f"   Total cached input tokens (sum): {generator.total_cached_input_tokens}")
        print(f"   Total output tokens (sum): {generator.total_output_tokens}")
        if generator._used_estimates:
            print("   Note: some token counts were estimated (no exact counts returned by the API)")
    except Exception:
        pass

    end = time.time()
    print(f"\n\nExecution Time: {(end-start):.4f} seconds")


if __name__ == "__main__":
    main()