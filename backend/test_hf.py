from transformers import pipeline

def main():
    pipe = pipeline(
        task="text-generation",
        model="gpt2",           # match HF_MODEL_ID
        temperature=0.2,
        max_new_tokens=32,
        do_sample=True,
    )
    out = pipe("Testing connectivity. The answer is", return_full_text=False)
    print(">> Pipeline output:", out)

if __name__ == "__main__":
    main()
