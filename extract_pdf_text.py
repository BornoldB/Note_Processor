import os
import pdfplumber

def extract_text_from_pdfs(directory_path, output_directory):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory_path, filename)
            output_filename = os.path.splitext(filename)[0] + '.txt'
            output_path = os.path.join(output_directory, output_filename)
            
            try:
                # Open and extract text from PDF
                with pdfplumber.open(pdf_path) as pdf:
                    text = ''
                    for page in pdf.pages:
                        text += page.extract_text() or ''  # Handle cases where extract_text returns None
                        
                    # Save extracted text to a .txt file
                    with open(output_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(text)
                print(f"Successfully extracted text from {filename} to {output_filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    # Specify the input and output directories
    input_directory = "pdfs"  # Directory containing PDF files
    output_directory = "text_output"  # Directory to save text files
    
    extract_text_from_pdfs(input_directory, output_directory)