import json
from retriever import load_retriever
retriever = load_retriever()
print("Q6 results:")
for r in retriever.retrieve("State Newton's second law of motion.", k=3):
    print(r['text'])
print("---")
print("Q10 results:")
for r in retriever.retrieve("What is the value of acceleration due to gravity on Earth?", k=3):
    print(r['text'])
