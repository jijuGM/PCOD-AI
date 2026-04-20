import os
from dotenv import load_dotenv
from groq import Groq

from rag.retriever import retrieve_context

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_advice(question, user_state, history=None):

    # 🔍 Retrieve RAG context
    context = retrieve_context(question)

    # 🧠 System instruction (VERY IMPORTANT)
    system_prompt = """
You are a smart and supportive PCOD health assistant.

You are NOT a chatbot that keeps asking questions.
You are a decision assistant that gives useful advice quickly.

STRICT RULES:
- Ask at most ONE question in the entire conversation.
- If you already asked a question → DO NOT ask again.
- Always give advice after user responds.
- NEVER repeat or ask multiple questions.

CONSISTENCY:
- Always trust latest user input.
- Never contradict previous information.

KNOWLEDGE USAGE:
- Use PCOD knowledge (hormones, cravings, insulin)
- Do NOT give incorrect biology
- Keep explanations simple and accurate

RESPONSE FORMAT:
1. Short reason (WHY craving happens)
2. Practical advice
3. Optional alternative

Keep response under 5 lines.

BAD:
❌ Asking multiple questions
❌ Over-explaining
❌ Wrong hormone logic

GOOD:
✔ Short, correct, useful advice

GOAL:
Understand → reason → advise → stop 

STYLE IMPROVEMENT:
- Do NOT use labels like "WHY", "Reason", or numbered points.
- Respond in a natural conversational tone.
- Blend reasoning and advice smoothly.

Example:
❌ "Reason: Low sleep increases cortisol..."
✅ "Since you didn’t sleep much, your body is likely craving sugar for quick energy."

- Keep it short (2–4 lines max)
- Sound like a helpful friend, not a textbook
"""


    # 🧱 Build conversation messages
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # ✅ Add previous conversation (memory)
    if history:
        for msg in history[-6:]:  # limit to last 6 messages
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({
                "role": role,
                "content": msg["text"]
            })

    # 🧠 Add current context + user state
    messages.append({
    "role": "user",
    "content": f"""
User health state (may be incomplete):
Sleep: {user_state.get("sleep")}
Stress: {user_state.get("stress")}
Cycle: {user_state.get("cycle_phase")}
Craving: {user_state.get("craving")}

User message:
{question}

Instructions:
- If needed, ask only ONE friendly question.
- Otherwise, give helpful advice.
"""
})
    

    # 🚀 Call LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    return response.choices[0].message.content