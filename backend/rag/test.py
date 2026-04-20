from retriever import retrieve_context

query = "Why do women with PCOD crave sweets?"

context = retrieve_context(query)

print("\nRetrieved Knowledge:\n")
print(context)