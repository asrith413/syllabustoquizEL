import sys
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

def test_phi3():
    print("Testing Phi-3 Loading...")
    model_name = "microsoft/Phi-3-mini-4k-instruct"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        print("Tokenizer loaded.")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Phi-3 Failed: {e}")

def test_flan_t5():
    print("\nTesting Flan-T5-Base Loading (Backup Option)...")
    model_name = "google/flan-t5-base"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("Tokenizer loaded.")
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            low_cpu_mem_usage=True
        )
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Flan-T5 Failed: {e}")

if __name__ == "__main__":
    print(f"Python: {sys.version}")
    print(f"Torch: {torch.__version__}")
    test_phi3()
    # test_flan_t5()
