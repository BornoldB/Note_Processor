# 📚 Note Processor

**An AI-powered study companion that transforms your PDFs and PowerPoint presentations into interactive study materials.**

Transform your lecture notes, textbooks, and presentations into comprehensive study questions automatically using local AI processing.

## ✨ Features

- **📄 PDF Text Extraction**: Convert PDF documents to searchable text
- **📊 PowerPoint Processing**: Extract content from .pptx presentations 
- **🤖 AI Question Generation**: Create study questions using local Ollama AI
- **🎯 Multiple Question Types**: Generate multiple choice, short answer, true/false, and essay questions
- **⚙️ Configurable Settings**: Customize AI parameters and processing options
- **🖥️ Terminal Interface**: Easy-to-use command-line menu system
- **📊 Progress Tracking**: Monitor processing status and AI token usage

## 🚀 Quick Start

### Prerequisites

1. **Python 3.7+** installed on your system
2. **Ollama** installed and running locally ([Download Ollama](https://ollama.ai))
3. An Ollama model downloaded (recommended: `llama3.1:8b`)

### Installation

1. **Clone or download** this repository to your computer

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Ollama** (required for question generation):
   ```bash
   ollama serve
   ```

4. **Download an AI model** (if you haven't already):
   ```bash
   ollama pull llama3.1:8b
   ```

5. **Run the Note Processor**:
   ```bash
   python note_processor.py
   ```

## 📖 How to Use

### Step 1: Prepare Your Files
- Place PDF files in the `pdfs/` folder
- Place PowerPoint files in the `pptxs/` folder
- The tool will create these folders automatically if they don't exist

### Step 2: Run the Program
```bash
python note_processor.py
```

### Step 3: Choose Your Workflow

The tool offers several options through an interactive menu:

1. **📊 Extract PowerPoint → Text**: Converts .pptx files to readable text
2. **📄 Extract PDF → Text**: Converts PDF files to readable text  
3. **❓ Generate Questions**: Creates study questions from text files
4. **📊 Show Status**: View current file counts in each folder
5. **🚀 Process All**: Complete pipeline from files to questions
6. **🚪 Exit**: Close the application

### Example Workflow:
1. Add your study materials to `pdfs/` and `pptxs/` folders
2. Choose option **5** (Process All) for complete automation
3. Find your generated questions in `questions_output/` folder
4. Review extracted text in `text_output/` folder

## 🛠️ How It Works

### The Magic Behind the Scenes

**Note Processor** uses a simple but powerful three-step process:

1. **📝 Text Extraction**
   - Reads through your PDF and PowerPoint files
   - Extracts all the readable text content
   - Organizes slide-by-slide for presentations
   - Saves clean text files for further processing

2. **🧠 AI Processing** 
   - Sends text to your local Ollama AI (runs on your computer - no data sent online!)
   - Uses intelligent prompts to understand the educational content
   - Identifies key concepts, formulas, and important information
   - Breaks down complex topics into digestible chunks

3. **❓ Question Generation**
   - Creates multiple types of study questions:
     - **Multiple Choice**: Test recall and understanding
     - **Short Answer**: Practice explaining concepts
     - **True/False**: Quick knowledge checks  
     - **Essay**: Deep thinking prompts
   - Includes correct answers and explanations
   - Saves questions in organized JSON files for easy review

### Privacy & Performance
- **100% Local Processing**: Your data never leaves your computer
- **Customizable AI**: Adjust creativity, response length, and model selection
- **Batch Processing**: Handle multiple files efficiently
- **Smart Chunking**: Breaks large documents into manageable pieces

## ⚙️ Configuration

### Settings File (`settings.json`)

Customize the tool's behavior by editing `settings.json`:

```json
{
  "ollama": {
    "base_url": "http://localhost:11434",    // Ollama server address
    "model": "llama3.1:8b",                  // AI model to use
    "timeout": 120,                          // Request timeout (seconds)
    "options": {
      "temperature": 0.7,                    // AI creativity (0.0-1.0)
      "top_p": 0.9,                         // Response focus
      "num_predict": 2000                    // Max response length
    }
  },
  "question_generation": {
    "question_types": ["multiple_choice", "short_answer", "true_false", "essay"],
    "questions_per_chunk": 4,               // Questions per text section
    "max_chunk_size": 4000,                 // Characters per processing chunk
    "text_input_dir": "text_output",        // Where to find text files
    "questions_output_dir": "questions_output"  // Where to save questions
  }
}
```

### Common Customizations

**Use a different AI model:**
```json
{
  "ollama": {
    "model": "llama3.2:8b"
  }
}
```

**Generate only multiple choice questions:**
```json
{
  "question_generation": {
    "question_types": ["multiple_choice"],
    "questions_per_chunk": 6
  }
}
```

**Connect to remote Ollama server:**
```json
{
  "ollama": {
    "base_url": "http://192.168.1.100:11434"
  }
}
```

## 📁 Project Structure

```
note_processor/
├── note_processor.py          # Main application entry point
├── extract_pdf_text.py        # PDF text extraction
├── extract_pptx_text.py       # PowerPoint text extraction  
├── txt_to_questions.py        # AI question generation
├── settings.json              # Configuration file
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── pdfs/                      # Place PDF files here
├── pptxs/                     # Place PowerPoint files here
├── text_output/               # Extracted text files
└── questions_output/          # Generated question files
```

## 🔧 Troubleshooting

### "Cannot connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check if the model is downloaded: `ollama list`
- Verify the base_url in settings.json matches your Ollama installation

### "No files found"
- Ensure files are in the correct folders (`pdfs/` or `pptxs/`)
- Check file extensions (.pdf, .pptx)
- The tool creates folders automatically on first run

### "Permission denied" or file errors
- Run as administrator if needed
- Check that files aren't open in other applications
- Ensure you have write permissions in the tool directory

### Slow processing
- Large files take more time to process
- Consider using a faster AI model
- Reduce `questions_per_chunk` in settings
- Check your hardware (AI processing is CPU/GPU intensive)

## 🎯 Tips for Best Results

1. **File Preparation**
   - Use high-quality PDFs with selectable text (not scanned images)
   - Ensure PowerPoint files aren't password protected
   - Organize files by subject for easier management

2. **AI Model Selection**
   - `llama3.1:8b` - Good balance of speed and quality
   - `llama3.1:13b` - Higher quality, slower processing
   - `llama3.2:3b` - Faster processing, basic quality

3. **Question Quality**
   - Process related content together
   - Use descriptive filenames for better organization
   - Review generated questions and refine settings as needed

## 📊 Example Output

The tool generates comprehensive study questions like:

**Multiple Choice:**
```
Question: What is the primary function of the mitochondria?
A) Protein synthesis
B) ATP production
C) DNA storage  
D) Waste removal
Correct Answer: B) ATP production
Explanation: Mitochondria are known as the powerhouse of the cell...
```

**Short Answer:**
```
Question: Explain the process of photosynthesis in plants.
Answer: Photosynthesis is the process by which plants convert sunlight...
Explanation: This process involves chlorophyll capturing light energy...
```

## 🤝 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Ensure Ollama is running with a compatible model
4. Review the settings.json configuration

## 📝 License

This project is open source. Feel free to modify and distribute according to your needs.

---

**Happy Studying! 🎓**

*Transform your notes into knowledge with AI-powered question generation.*