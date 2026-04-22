import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# download once
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    # 1. Remove unwanted characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # 2. Convert to lowercase
    text = text.lower()

    # 3. Tokenization
    tokens = word_tokenize(text)

    # 4. Remove stopwords
    tokens = [word for word in tokens if word not in stop_words]

    # 5. Lemmatization (optional but recommended)
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    return tokens


file_path = input("Enter PDF file path: ")

with open(file_path, "r") as infile:
    data = infile.read()

result = preprocess_text(data)

with open("preprocess.txt", "w") as outfile:
    outfile.write(" ".join(result))