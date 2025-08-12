from typing import List
import os
import re
import openai
import voyageai
import ollama


class AIService:
    def __init__(self):
        self.openrouter_client = None
        self.voyage_client = None
        self.ollama_client = None
        self.setup_clients()

    def setup_clients(self):
        """Setup AI service clients with error handling"""
        try:
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if openrouter_key:
                self.openrouter_client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_key,
                )
                print("OpenRouter client initialized")
        except Exception as e:
            print(f" OpenRouter setup failed: {e}")

        try:
            voyage_key = os.getenv("VOYAGE_API_KEY")
            if voyage_key:
                self.voyage_client = voyageai.Client(api_key=voyage_key)
                print(" Voyage client initialized")
        except Exception as e:
            print(f" Voyage setup failed: {e}")

        try:
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            self.ollama_client = ollama.Client(host=ollama_url)
            self.ollama_client.list()
            print(" Ollama client initialized")
        except Exception as e:
            print(f" Ollama setup failed: {e}")

    def strip_markdown(self, text: str) -> str:
        """Remove markdown formatting like **bold**, *italic*, headings, etc."""
        if not text:
            return ""
        
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"\*(.*?)\*", r"\1", text)
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"^[\-\*\+]\s*", "", text, flags=re.MULTILINE)
        return text.strip()

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with fallback mechanism"""
        if self.voyage_client:
            try:
                result = self.voyage_client.embed(texts, model="voyage-large-2")
                print(f" Generated embeddings using Voyage for {len(texts)} texts")
                return result.embeddings
            except Exception as e:
                print(f"Voyage embedding failed: {str(e)}")

        if self.openrouter_client:
            try:
                embeddings = []
                for text in texts:
                    response = self.openrouter_client.embeddings.create(
                        input=text,
                        model="text-embedding-ada-002"
                    )
                    embeddings.append(response.data[0].embedding)
                print(f" Generated embeddings using OpenRouter for {len(texts)} texts")
                return embeddings
            except Exception as e:
                print(f" OpenRouter embedding failed: {str(e)}")

        if self.ollama_client:
            try:
                embeddings = []
                for text in texts:
                    response = self.ollama_client.embeddings(
                        model="nomic-embed-text:latest",
                        prompt=text
                    )
                    embeddings.append(response['embedding'])
                print(f"Generated embeddings using Ollama for {len(texts)} texts")
                return embeddings
            except Exception as e:
                print(f"Ollama embedding failed: {str(e)}")

        print("All embedding services failed, using dummy embeddings")
        return [[0.0] * 384 for _ in texts]

    async def generate_response(self, query: str, context: List[str]) -> str:
        """Generate response with fallback mechanism"""
        context_text = "\n\n".join(context[:3])

        prompt = f"""Based on the following context from scraped web data, provide a clear and accurate answer to the user's question.

Context:
{context_text}

Question: {query}

Instructions:
- Only use information provided in the context.
- If the context does not contain relevant information, say so clearly.
- Provide specific details and examples when available.
- Do not use any markdown formatting (no bold, italics, lists, or special symbols).
- Write in plain text only.
- Keep the answer concise but thorough.

Answer:"""

        if self.ollama_client:
            try:
                response = self.ollama_client.chat(
                    model="deepseek-v2:latest",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant that answers questions based on provided web scraped context. Be accurate and cite information from the context when possible."},
                        {"role": "user", "content": prompt}
                    ]
                )
                print(" Generated response using Ollama DeepSeek-V2")
                return self.strip_markdown(response['message']['content'])
            except Exception as e:
                print(f" Ollama generation failed: {str(e)}")

        if self.openrouter_client:
            try:
                response = self.openrouter_client.chat.completions.create(
                    model="deepseek/deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI assistant that answers questions based on provided web scraped context. Be accurate and cite information from the context when possible."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                print("Generated response using OpenRouter DeepSeek")
                return self.strip_markdown(response.choices[0].message.content)
            except Exception as e:
                print(f" OpenRouter generation failed: {str(e)}")

        return f"I found relevant information about '{query}' in the scraped content, but I'm unable to generate a detailed response at the moment due to AI service unavailability. Here's what I found in the context:\n\n{self.strip_markdown(context_text[:500])}..."

    async def summarize_content(self, content: str, max_length: int = 500) -> str:
        """Summarize content using AI"""
        if len(content) <= max_length:
            return content

        prompt = f"""Summarize the following content clearly and concisely.
Rules:
- Use plain text only, no markdown formatting.
- Maximum length: {max_length} characters.

Content:
{content[:2000]}"""

        if self.ollama_client:
            try:
                response = self.ollama_client.chat(
                    model="deepseek-v2:latest",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return self.strip_markdown(response['message']['content'])
            except Exception as e:
                print(f" Ollama summarization failed: {str(e)}")

        if self.openrouter_client:
            try:
                response = self.openrouter_client.chat.completions.create(
                    model="deepseek/deepseek-chat",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.5
                )
                return self.strip_markdown(response.choices[0].message.content)
            except Exception as e:
                print(f" OpenRouter summarization failed: {str(e)}")

        return content[:max_length] + "..." if len(content) > max_length else content


ai_service = AIService()
