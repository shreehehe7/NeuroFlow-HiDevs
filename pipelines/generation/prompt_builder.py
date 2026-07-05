class PromptBuilder:
    def __init__(self):
        self.base_prompt = """You are a precise research assistant. Answer the user's question using ONLY the provided context.
If the context does not contain enough information to answer fully, say so explicitly.
For every factual claim, include a citation in the format [Source N].
Do not introduce information not present in the context."""

        self.type_additions = {
            "factual": "Provide a direct, concise answer. If multiple sources agree, cite all of them.",
            "analytical": "Analyze and synthesize across the provided sources. Identify agreements and contradictions.",
            "comparative": "Organize your response as a structured comparison. Use a table if appropriate.",
            "procedural": "Provide numbered steps. Each step must be cited."
        }

    def build_prompt(self, query: str, context: str, query_type: str = "factual") -> str:
        type_prompt = self.type_additions.get(query_type, self.type_additions["factual"])
        
        system_prompt = f"{self.base_prompt}\n{type_prompt}"
        
        if query_type in ["analytical", "comparative"]:
            # Chain of thought optimization
            system_prompt += "\nFirst, think step-by-step inside <think>...</think> tags before answering."
            
        full_prompt = f"{system_prompt}\n\n<context>\n{context}\n</context>\n\nUser Question: {query}"
        return full_prompt
