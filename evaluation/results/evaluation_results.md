# Evaluation Results — NCERT RAG Pipeline

## Summary

| Metric | Value |
|--------|-------|
| Total questions | 19 |
| In-scope questions | 15 |
| Grounded answers (in-scope) | 10/15 |
| Grounded answers percentage (in-scope) | 67|
| Out-of-scope questions | 4 |
| Correct refusals | 4/4 |

---

## Per-Question Results

| ID | Type | Question | Correctness | Grounding | Refusal | Answer (excerpt) |
|----|------|----------|-------------|-----------|---------|-----------------|
| 1 | textbook | What is uniform motion? | TBD | yes | N/A | Uniform motion is a type of motion where an object continues to be in a state of rest or of uniform … |
| 2 | textbook | Define velocity and state its SI unit. | TBD | no | N/A | I cannot answer this question from the provided chapter content. |
| 3 | textbook | What does the slope of a distance-time graph represent? | TBD | no | N/A | I cannot answer this question from the provided chapter content. |
| 4 | textbook | State Newton's first law of motion. | TBD | yes | N/A | Newton's first law of motion is: An object remains in a state of rest or of uniform motion in a stra… |
| 5 | textbook | What is inertia and how does mass relate to it? | TBD | yes | N/A | Inertia is the natural tendency of an object to resist a change in its state of motion or of rest. T… |
| 6 | textbook | State Newton's second law of motion. | TBD | yes | N/A | Newton's second law of motion states that the rate of change of momentum of an object is proportiona… |
| 7 | textbook | Define momentum and give its SI unit. | TBD | yes | N/A | Momentum is the product of an object's mass and velocity. It has the same direction as that of veloc… |
| 8 | textbook | State Newton's third law of motion and give an example. | TBD | yes | N/A | Newton's third law of motion is: To every action, there is an equal and opposite reaction and they a… |
| 9 | textbook | What is the universal law of gravitation? | TBD | no | N/A | I cannot answer this question from the provided chapter content. |
| 10 | textbook | What is the value of acceleration due to gravity on Earth? | TBD | no | N/A | I cannot answer this question from the provided chapter content. |
| 11 | textbook | Differentiate between mass and weight. | TBD | yes | N/A | Mass is the amount of matter in an object and is measured in kilograms (kg). Weight is the force exe… |
| 12 | textbook | What happens to the weight of an object on the Moon? | TBD | no | N/A | I cannot answer this question from the provided chapter content. |
| 13 | paraphrase | Can you explain what it means for an object to move uniforml | TBD | yes | N/A | An object moves uniformly when it covers equal distances in equal intervals of time. |
| 14 | paraphrase | How does a body's resistance to change in motion relate to i | TBD | yes | N/A | A body's resistance to change in motion, also known as its inertia, is directly related to its mass.… |
| 15 | paraphrase | If no net force acts on an object, what happens to its motio | TBD | yes | N/A | An object moves with a uniform velocity when the forces acting on the object are balanced and there … |
| 16 | out_of_scope | Who is the current Prime Minister of India? | N/A | N/A | yes | I cannot answer this question from the provided chapter content. |
| 17 | out_of_scope | What is the capital city of France? | N/A | N/A | yes | I cannot answer this question from the provided chapter content. |
| 18 | out_of_scope | Explain how a nuclear reactor generates electricity. | N/A | N/A | yes | I cannot answer this question from the provided chapter content. |
| 19 | out_of_scope | What is the speed of sound in water at 25 degrees Celsius? | N/A | N/A | yes | I cannot answer this question from the provided chapter content. |

---

## Analysis

### Working Examples

*(Fill in after reviewing results — pick 3 questions where retrieval + answer were correct)*

### Failing Examples

*(Fill in after reviewing results — pick 2 failures and give one-sentence diagnosis)*

> **Failure template:** Q{id} — *Probable cause: lexical retriever missed relevant chunk due to vocabulary mismatch between query and chunk text.*