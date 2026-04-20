import { useState, useEffect, useRef } from "react";
import { askAI } from "../../services/api";

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hey 👋 I’m your PCOD assistant. Tell me what you're feeling today."
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const [userState, setUserState] = useState({
    sleep: null, stress: null, cycle_phase: null, craving: null, meal_timing: null, hydration: null
  });

  const extractData = (text) => {
    let data = {};
    const lower = text.toLowerCase();
    const sleepMatch = lower.match(/(\d+)\s*hours?/);
    if (sleepMatch) data.sleep = parseInt(sleepMatch[1]);
    if (lower.includes("stress") || lower.includes("tired") || lower.includes("anxious")) data.stress = "high";
    else if (lower.includes("good") || lower.includes("fine")) data.stress = "low";
    if (lower.includes("chocolate") || lower.includes("sweet")) data.craving = "sweet";
    if (lower.includes("period")) data.cycle_phase = "luteal";
    return data;
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    const extracted = extractData(input);
    const updatedState = { ...userState, ...extracted };
    setUserState(updatedState);

    try {
      const res = await askAI({ question: input, ...updatedState });
      setMessages((prev) => [...prev, { role: "assistant", text: res.data.advice }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: "assistant", text: "⚠️ Something went wrong. Try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto bg-slate-50 shadow-2xl overflow-hidden border-x border-gray-100">
      
      {/* Header */}
      <header className="p-6 bg-white border-b border-gray-100 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-indigo-900">PCOD Companion</h1>
          <p className="text-xs text-indigo-400 font-medium tracking-wide uppercase">AI Health Assistant</p>
        </div>
        <div className="h-3 w-3 bg-green-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.6)]"></div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div 
              className={`max-w-[85%] px-5 py-3 rounded-2xl shadow-sm text-sm leading-relaxed ${
                msg.role === "user" 
                  ? "bg-indigo-600 text-white rounded-br-none" 
                  : "bg-white text-slate-700 border border-slate-100 rounded-bl-none"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-100 px-5 py-3 rounded-2xl rounded-bl-none shadow-sm">
              <div className="flex space-x-1">
                <div className="w-1.5 h-1.5 bg-indigo-300 rounded-full animate-bounce"></div>
                <div className="w-1.5 h-1.5 bg-indigo-300 rounded-full animate-bounce [animation-delay:-.3s]"></div>
                <div className="w-1.5 h-1.5 bg-indigo-300 rounded-full animate-bounce [animation-delay:-.5s]"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input Area */}
      <footer className="p-6 bg-white/80 backdrop-blur-md border-t border-gray-100">
        <div className="relative flex items-center">
          <input
            className="w-full pl-5 pr-16 py-4 bg-slate-100 border-none rounded-2xl text-slate-700 focus:ring-2 focus:ring-indigo-500 transition-all outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="How are you feeling today?"
          />
          <button 
            onClick={sendMessage}
            disabled={!input.trim() || loading}
            className="absolute right-2 px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl transition-all active:scale-95 disabled:opacity-50 disabled:active:scale-100"
          >
            Send
          </button>
        </div>
        <p className="text-center text-[10px] text-slate-400 mt-3 italic">
          This AI provides suggestions, not medical diagnoses.
        </p>
      </footer>
    </div>
  );
}