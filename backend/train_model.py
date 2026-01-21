import json
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq

# Configuration
# We use 'flan-t5-small' for speed purely for this demo. 
# You can change to 'google/flan-t5-large' if you have a GPU or are running on Colab.
MODEL_NAME = "google/flan-t5-small" 
OUTPUT_DIR = "./fine_tuned_t5_quiz"
TRAIN_FILE = "training_data.json"

def main():
    print(f"Preparing to fine-tune {MODEL_NAME}...")
    
    # 1. Load Data
    with open(TRAIN_FILE, 'r') as f:
        data = json.load(f)
        
    # Convert to Hugging Face Dataset
    hf_data = {
        "input_text": [item["input_text"] for item in data],
        "output_text": [item["output_text"] for item in data]
    }
    dataset = Dataset.from_dict(hf_data)
    
    # Split Train/Test
    dataset = dataset.train_test_split(test_size=0.1)
    
    # 2. Tokenize
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    def preprocess_function(examples):
        inputs = examples["input_text"]
        targets = examples["output_text"]
        model_inputs = tokenizer(inputs, max_length=512, truncation=True)
        labels = tokenizer(targets, max_length=512, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized_datasets = dataset.map(preprocess_function, batched=True)
    
    # 3. Model
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    
    # 4. Training Arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=OUTPUT_DIR,
        evaluation_strategy="epoch",
        learning_rate=3e-4,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        weight_decay=0.01,
        save_total_limit=2,
        num_train_epochs=3, # Low epochs for demo
        predict_with_generate=True,
        logging_steps=10,
        use_cpu=not torch.cuda.is_available(), # Force CPU if no GPU
    )
    
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    # 5. Train
    print("Starting training (this may take a while on CPU)...")
    trainer.train()
    
    # 6. Save
    print(f"Saving fine-tuned model to {OUTPUT_DIR}...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Review complete!")

if __name__ == "__main__":
    main()
