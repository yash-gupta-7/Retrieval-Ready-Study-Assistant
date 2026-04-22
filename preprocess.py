import re
import nltk

# Ensure required tokenizers are downloaded
nltk.download('punkt', quiet=True)
try:
    nltk.download('punkt_tab', quiet=True)
except:
    pass

def chunk_text(text):
    # Replace newlines and excessive spaces with a single space
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Chunk the text into individual sentences
    sentences = nltk.tokenize.sent_tokenize(text)
    return sentences

# Use the existing pdf_text.txt file instead of an interactive prompt for smoother pipeline runs
file_path = "pdf_text.txt"

with open(file_path, "r", encoding="utf-8") as infile:
    data = infile.read()

# Chunk into sentences
sentences = chunk_text(data)

# Filter out empty or extremely short sentences
sentences = [s.strip() for s in sentences if len(s.split()) > 3]

# Write each sentence on a new line so that the next stage registers them as multiple chunks
with open("preprocess.txt", "w", encoding="utf-8") as outfile:
    for s in sentences:
        outfile.write(s + "\n")