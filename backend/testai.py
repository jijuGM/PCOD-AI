from llm.ai_engine import generate_advice

user_state = {
    "sleep": 5,
    "stress": "high",
    "cycle_phase": "luteal",
    "craving": "sweet"
}

question = "I crave chocolate at night. What should I do?"

answer = generate_advice(question, user_state)

print("\nAI Advice:\n")
print(answer)