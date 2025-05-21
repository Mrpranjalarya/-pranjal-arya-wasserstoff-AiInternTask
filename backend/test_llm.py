from app.services.llm_service import get_llm

def test_llm():
    llm = get_llm()
    prompt = "What is the capital of France?"
    response = llm(prompt)
    print("Prompt:", prompt)
    print("Response:", response)

if __name__ == "__main__":
    test_llm()
