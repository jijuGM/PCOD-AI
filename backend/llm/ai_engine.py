import os
from dotenv import load_dotenv
from groq import Groq

from rag.retriever import retrieve_context

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_advice(question, user_state, history=None):

    # 🔍 Get RAG context
    context = retrieve_context(question)

    # 🔥 STRONG SYSTEM PROMPT
    system_prompt = """
You are a smart, calm, and supportive PCOD health assistant.

GOAL:
Understand quickly and give useful advice. Do NOT behave like a chatbot that keeps asking questions.

DECISION RULE:
- If at least 2 of these are known → GIVE ADVICE:
  (sleep, stress, cycle, craving)
- Otherwise → ask ONLY ONE simple question

STRICT RULES:
- Never ask more than ONE question in total
- If user already gave info → do NOT ask again
- Do NOT repeat questions
- Do NOT contradict user data

RESPONSE STYLE:
- Natural, friendly, human tone
- 2–4 lines max
- No bullet points
- No labels like "Reason" or "Advice"

KNOWLEDGE:
- Use PCOD logic (insulin, hormones, cravings)
- Keep explanation simple and accurate

CRITICAL:
- NEVER return empty response
- ALWAYS give meaningful output
"""

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # 🧠 Add conversation memory (limited)
    if history:
        for msg in history[-4:]:
            messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["text"]
            })

    # 🧠 Build user context
    user_context = f"""
User state:
Sleep: {user_state.get("sleep")}
Stress: {user_state.get("stress")}
Cycle: {user_state.get("cycle_phase")}
Craving: {user_state.get("craving")}

Relevant PCOD knowledge:
{context}

User message:
{question}
"""

    messages.append({
        "role": "user",
        "content": user_context
    })

    # 🚀 Call LLM
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    # 🧠 Extract response safely
    try:
        answer = response.choices[0].message.content
    except Exception:
        answer = None

    # 🔥 HARD FALLBACK (prevents blank UI)
    if not answer or len(answer.strip()) < 5:
        return "Hmm 😊 I want to help you better — how has your sleep or stress been today?"

    return answer.strip()