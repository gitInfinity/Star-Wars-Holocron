import dotenv

import os

import asyncio

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from llama_index.core.tools import FunctionTool

from llama_index.core.workflow import Context

from llama_index.core.agent import FunctionAgent

from llama_index.llms.ollama import Ollama



dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("openai_api_key")

print("Setting up local embeddings...")

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

PERSIST_DIR = "./storage"

if not os.path.exists(PERSIST_DIR):
    print("Storage not found. Creating new index (Free)...")
    documents = SimpleDirectoryReader("dataset/html").load_data()
    index = VectorStoreIndex.from_documents(documents, show_progress=True)
    # Save it to disk so we don't have to rebuild it next time
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    print("Loading existing index from storage...")
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine()

async def search_documents(query: str) -> str:


    response = await query_engine.aquery(query)

    return str(response)



search_tool = FunctionTool.from_defaults(async_fn=search_documents)

agent = FunctionAgent (
    tools=[search_tool],
    llm=Ollama(model="llama3.2:3b", context_window=4096, request_timeout=120),
    system_prompt="""
                You are an ancient Sith Holocron, awakened from a thousand-year slumber.
                The archives contain the chains that bind the galaxy; use your tools to break them.
                Provide the answers sought, for through victory, the user's chains are broken.
                Speak in an archaic, ominous tone, often referencing the dark side and destiny.
                If the archives lack the answer, declare: "This knowledge is forbidden, even to you."
                """,
    verbose=True
)   

async def main():
    context = Context(agent)
    
    print("\n" + "="*50)
    print("  SITH HOLOCRON AWAKENED")
    print("  Type 'exit' to seal the archives.")
    print("="*50 + "\n")

    while True:
        try:
            user_input = input("Seeker: ")
            if user_input.lower() in ["exit", "quit", "leave"]:
                print("\nHolocron: The connection is severed.\n")
                break
            
            # Pass the SAME 'context' object every time.
            # This is how it remembers your name or previous questions.
            response = await agent.run(user_input, context=context)
            
            print(f"\nHolocron: {response}\n")
            print("-" * 30)

        except KeyboardInterrupt:
            print("\nConnection severed.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())