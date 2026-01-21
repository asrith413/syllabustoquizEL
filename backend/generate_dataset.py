import json
import random
import os

# Define high-quality templates to teach the model "What Good Looks Like"
TEMPLATES = [
    {
        "pattern": "What is the primary definition of {topic}?",
        "correct": "The fundamental mathematical or scientific concept defining {topic}",
        "distractors": ["A totally unrelated historical event", "A type of biological organism", "A fictional character"]
    },
    {
        "pattern": "Which of the following is a key property of {topic}?",
        "correct": "It satisfies specific axioms and theorems related to {topic}",
        "distractors": ["It is edible", "It is only found in space", "It is a color"]
    },
    {
        "pattern": "How is {topic} typically calculated or derived?",
        "correct": "Using specific formulas and algorithmic steps",
        "distractors": ["By guessing randomly", "By measuring the temperature", "By asking a friend"]
    },
    {
        "pattern": "In the context of the syllabus, what does {topic} represent?",
        "correct": "A core unit of study with specific learning outcomes",
        "distractors": ["A type of food", "A musical instrument", "A holiday destination"]
    },
    {
        "pattern": "Why is {topic} considered important?",
        "correct": "It solves critical problems in the field",
        "distractors": ["It is not important at all", "It causes global warming", "It tastes good"]
    }
]

# Topics extracted from the user's syllabus (and general math topics)
TOPICS = [
    "Determinant of a Matrix", "Inverse of a Matrix", "System of Linear Equations",
    "Cramer's Rule", "Matrix Multiplication", "Eigenvalues", "Eigenvectors",
    "Vector Spaces", "Linear Independence", "Basis and Dimension",
    "Linear Transformations", "Rank of a Matrix", "Gaussian Elimination",
    "Orthogonal Matrices", "Diagonalization", "Inner Product Spaces",
    "Calculus", "Differential Equations", "Integration", "Limits"
]

def generate_example(topic):
    template = random.choice(TEMPLATES)
    
    question = template["pattern"].format(topic=topic)
    correct_opt = template["correct"].format(topic=topic)
    distractors = template["distractors"]
    
    # Randomize option position
    options = distractors[:]
    options.append(correct_opt)
    random.shuffle(options)
    
    # Find correct letter
    letters = ['A', 'B', 'C', 'D']
    correct_idx = options.index(correct_opt)
    correct_letter = letters[correct_idx]
    
    # Format Input and Output for T5
    # Input: "Task: Create question about {topic}"
    # Output: The formatted question
    
    input_text = f"Task: Create a multiple choice question about '{topic}'."
    
    output_text = f"Question: {question}\n"
    for i, opt in enumerate(options):
        output_text += f"{letters[i]}) {opt}\n"
    output_text += f"Correct: {correct_letter}"
    
    return {
        "input_text": input_text,
        "output_text": output_text
    }

def main():
    print("Generating synthetic training data...")
    dataset = []
    
    # Generate 200 examples (augmenting by repeating topics with different templates)
    for _ in range(10): 
        for topic in TOPICS:
            dataset.append(generate_example(topic))
            
    # Save to JSON
    out_file = "training_data.json"
    with open(out_file, "w") as f:
        json.dump(dataset, f, indent=2)
        
    print(f"Successfully generated {len(dataset)} training examples in {out_file}")
    
    # Preview
    print("\nSample Example:")
    print("INPUT:", dataset[0]["input_text"])
    print("OUTPUT:\n", dataset[0]["output_text"])

if __name__ == "__main__":
    main()
