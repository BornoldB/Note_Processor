# Date: 2025-11-03
# Author: Bornold 
# AI Assistant: Claude Sonnet 4 

# This is the main entry file to the note processor script 

import os
import sys
from pathlib import Path

# Import our processing modules
import extract_pdf_text as pdf2txt
import extract_pptx_text as pptx2txt
import txt_to_questions as txt2quest


class NoteProcessor:
    def __init__(self):
        """Initialize the Note Processor with required directories."""
        self.required_dirs = [
            "pdfs",
            "pptxs", 
            "text_output",
            "questions_output",
            "pdf_questionnaires"
        ]
        self.setup_directories()
    
    def setup_directories(self):
        """Create required directories if they don't exist."""
        print("🔧 Setting up directories...")
        
        for directory in self.required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"   📁 Created directory: {directory}/")
            else:
                print(f"   ✅ Directory exists: {directory}/")
        print()
    
    def check_files_in_directory(self, directory: str, extensions: list) -> int:
        """Check how many files with specified extensions exist in directory."""
        if not os.path.exists(directory):
            return 0
        
        count = 0
        for ext in extensions:
            count += len([f for f in os.listdir(directory) if f.lower().endswith(ext)])
        return count
    
    def display_status(self):
        """Display current status of files in directories."""
        print("📊 Current Status:")
        print("-" * 50)
        
        # Check PDFs
        pdf_count = self.check_files_in_directory("pdfs", [".pdf"])
        print(f"   📄 PDF files in pdfs/: {pdf_count}")
        
        # Check PowerPoints
        pptx_count = self.check_files_in_directory("pptxs", [".pptx"])
        print(f"   📊 PowerPoint files in pptxs/: {pptx_count}")
        
        # Check text files
        txt_count = self.check_files_in_directory("text_output", [".txt"])
        print(f"   📝 Text files in text_output/: {txt_count}")
        
        # Check question files
        question_count = self.check_files_in_directory("questions_output", [".json"])
        print(f"   ❓ Question files in questions_output/: {question_count}")
        
        # Check PDF questionnaires
        pdf_questionnaire_count = self.check_files_in_directory("pdf_questionnaires", [".pdf"])
        print(f"   📋 PDF questionnaires in pdf_questionnaires/: {pdf_questionnaire_count}")
        
        print()
    
    def extract_pdf_to_text(self):
        """Extract text from PDF files."""
        pdf_count = self.check_files_in_directory("pdfs", [".pdf"])
        
        if pdf_count == 0:
            print("❌ No PDF files found in pdfs/ directory!")
            print("   Please add some PDF files to the pdfs/ folder and try again.")
            return False
        
        print(f"📄 Found {pdf_count} PDF file(s). Starting extraction...")
        print("-" * 60)
        
        try:
            pdf2txt.extract_text_from_pdfs("pdfs", "text_output")
            print("\n✅ PDF text extraction completed!")
            return True
        except Exception as e:
            print(f"\n❌ Error during PDF extraction: {e}")
            return False
    
    def extract_pptx_to_text(self):
        """Extract text from PowerPoint files."""
        pptx_count = self.check_files_in_directory("pptxs", [".pptx"])
        
        if pptx_count == 0:
            print("❌ No PowerPoint files found in pptxs/ directory!")
            print("   Please add some .pptx files to the pptxs/ folder and try again.")
            return False
        
        print(f"📊 Found {pptx_count} PowerPoint file(s). Starting extraction...")
        print("-" * 60)
        
        try:
            pptx2txt.extract_text_from_pptx("pptxs", "text_output")
            print("\n✅ PowerPoint text extraction completed!")
            return True
        except Exception as e:
            print(f"\n❌ Error during PowerPoint extraction: {e}")
            return False
    
    def generate_questions(self):
        """Generate questions from text files."""
        txt_count = self.check_files_in_directory("text_output", [".txt"])
        
        if txt_count == 0:
            print("❌ No text files found in text_output/ directory!")
            print("   Please extract text from PDFs or PowerPoints first.")
            return False
        
        print(f"📝 Found {txt_count} text file(s). Starting question generation...")
        print("-" * 60)
        
        try:
            # Create question generator and run
            generator = txt2quest.OllamaQuestionGenerator("settings.json")
            
            # Test connection first
            if not generator.test_connection():
                print(f"❌ Cannot connect to Ollama at {generator.base_url}")
                print("   Please make sure Ollama is running with: ollama serve")
                return False
            
            print(f"✅ Connected to Ollama successfully!")
            print(f"🔧 Using model: {generator.model}")
            
            # Process files
            stats = generator.process_directory()
            
            print(f"\n🎓 Question Generation Complete!")
            print(f"   📄 Files processed: {stats['processed']}")
            print(f"   ❌ Files failed: {stats['failed']}")
            print(f"   ❓ Total questions generated: {stats['total_questions']}")
            print(f"   📁 Questions saved to: questions_output/")
            
            # Show token usage
            print(f"\n🔢 AI Token Usage:")
            print(f"   Input tokens: {generator.total_input_tokens:,}")
            print(f"   Output tokens: {generator.total_output_tokens:,}")
            if generator._used_estimates:
                print("   Note: Some token counts were estimated")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during question generation: {e}")
            return False
    
    def generate_pdf_questionnaires(self):
        """Generate PDF questionnaires from JSON question files."""
        json_count = self.check_files_in_directory("questions_output", [".json"])
        
        if json_count == 0:
            print("❌ No JSON question files found in questions_output/ directory!")
            print("   Please generate questions from text files first.")
            return False
        
        print(f"📋 Found {json_count} JSON question file(s). Starting PDF generation...")
        print("-" * 60)
        
        try:
            # Create the PDF questionnaires directory if it doesn't exist
            pdf_output_dir = "pdf_questionnaires"
            if not os.path.exists(pdf_output_dir):
                os.makedirs(pdf_output_dir)
                print(f"   📁 Created directory: {pdf_output_dir}/")
            
            # Generate PDFs from existing JSON files
            txt2quest.create_pdfs_from_existing_json("questions_output", pdf_output_dir)
            
            print(f"\n📋 PDF Questionnaire Generation Complete!")
            print(f"   📄 JSON files processed: {json_count}")
            print(f"   📁 PDFs saved to: {pdf_output_dir}/")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during PDF generation: {e}")
            return False
    
    def show_menu(self):
        """Display the main menu options."""
        print("=" * 60)
        print("📚 NOTE PROCESSOR - Main Menu")
        print("=" * 60)
        print()
        print("Choose an option:")
        print("  1.  Extract text from PowerPoint files (pptxs → text)")
        print("  2.  Extract text from PDF files (pdfs → text)")
        print("  3.  Generate questions from text files (text → questions)")
        print("  4.  Generate PDF questionnaires from JSON (questions → PDFs)")
        print("  5.  Show current status")
        print("  6.  Process all (PDFs + PowerPoints → text → questions → PDFs)")
        print("  7.  Exit")
        print()
    
    def process_all(self):
        """Process all files: PDFs + PowerPoints → text → questions → PDF questionnaires."""
        print("🚀 Starting complete processing pipeline...")
        print("=" * 60)
        
        success_count = 0
        total_operations = 0
        
        # Extract PowerPoints
        pptx_count = self.check_files_in_directory("pptxs", [".pptx"])
        if pptx_count > 0:
            print("📊 Step 1: Processing PowerPoint files...")
            if self.extract_pptx_to_text():
                success_count += 1
            total_operations += 1
            print()
        
        # Extract PDFs
        pdf_count = self.check_files_in_directory("pdfs", [".pdf"])
        if pdf_count > 0:
            print("📄 Step 2: Processing PDF files...")
            if self.extract_pdf_to_text():
                success_count += 1
            total_operations += 1
            print()
        
        # Generate questions
        if total_operations > 0 or self.check_files_in_directory("text_output", [".txt"]) > 0:
            print("❓ Step 3: Generating questions...")
            if self.generate_questions():
                success_count += 1
            total_operations += 1
            print()
            
            # Generate PDF questionnaires (only if questions were generated successfully)
            if success_count == total_operations:
                print("📋 Step 4: Generating PDF questionnaires...")
                if self.generate_pdf_questionnaires():
                    success_count += 1
                total_operations += 1
        
        # Summary
        print("=" * 60)
        print(f"🎯 Pipeline Complete! {success_count}/{total_operations} operations successful")
        
        if success_count == total_operations and total_operations > 0:
            print("🎉 All operations completed successfully!")
        elif total_operations == 0:
            print("⚠️  No files found to process. Please add files to pdfs/ or pptxs/ directories.")
        else:
            print("⚠️  Some operations failed. Check the output above for details.")
    
    def run(self):
        """Main application loop."""
        print("🎓 Welcome to the Note Processor!")
        print("This tool helps you convert PDFs and PowerPoints to study materials.")
        print()
        
        self.display_status()
        
        while True:
            self.show_menu()
            
            try:
                choice = input("Enter your choice (1-7): ").strip()
                print()
                
                if choice == "1":
                    self.extract_pptx_to_text()
                
                elif choice == "2":
                    self.extract_pdf_to_text()
                
                elif choice == "3":
                    self.generate_questions()
                
                elif choice == "4":
                    self.generate_pdf_questionnaires()
                
                elif choice == "5":
                    self.display_status()
                
                elif choice == "6":
                    self.process_all()
                
                elif choice == "7":
                    print("👋 Thank you for using Note Processor!")
                    print("Happy studying! 🎓")
                    break
                
                else:
                    print("❌ Invalid choice. Please enter a number between 1-7.")
                
                if choice in ["1", "2", "3", "4", "6"]:
                    input("\nPress Enter to continue...")
                    print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                input("Press Enter to continue...")


def main():
    """Main entry point."""
    try:
        processor = NoteProcessor()
        processor.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

