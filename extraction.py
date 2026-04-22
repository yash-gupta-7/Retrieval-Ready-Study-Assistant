import pymupdf

file_path = input("Enter PDF file path: ")

doc = pymupdf.open(file_path)
all_text = ""

for page in doc:
    all_text = page.get_text() + "\n"

with open("pdf_text.txt", "w") as file:
    file.write(f"{all_text}")