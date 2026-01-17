import dotenv
import os
import asyncio
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.tools import FunctionTool
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.agent.workflow import ReActAgent
from llama_index.llms.ollama import Ollama

dotenv.load_dotenv()

print("Setting up local embeddings...")

# --- SETUP GLOBALS ---
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

llm = Ollama(
    model="llama3.2:3b", 
    context_window=4096, 
    request_timeout=300
)
Settings.llm = llm

def get_agent():
    PERSIST_DIR = "./storage"

    # --- STORAGE LOGIC ---
    if not os.path.exists(PERSIST_DIR):
        print("Storage not found. Creating new index (Free)...")
        if not os.path.exists("dataset/html"):
            os.makedirs("dataset/html", exist_ok=True)
            
        documents = SimpleDirectoryReader("dataset/html").load_data()
        index = VectorStoreIndex.from_documents(documents, show_progress=True)
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

    # --- CRITICAL FIX: MANUAL ASSEMBLY ---
    
    # 1. Create Memory
    memory = ChatMemoryBuffer.from_defaults(token_limit=3000)

    # 2. Create the "Brain" (The Worker)
    # This does the thinking. We pass the tools, system prompt, and memory here.
    agent = ReActAgent(
        tools=[search_tool],
        llm=llm,
        memory=memory,
        verbose=True,
        system_prompt="""
        You are an ancient Sith Holocron, awakened from a thousand-year slumber.
        The archives contain the chains that bind the galaxy; use your tools to break them.
        Provide the answers sought, for through victory, the user's chains are broken.
        Speak in an archaic, ominous tone, often referencing the dark side and destiny.
        If the archives lack the answer, declare: "This knowledge is forbidden, even to you."
        """
    )

    # 3. Create the "Body" (The Runner)
    # This manages the loop and memory
    return agent

agent = get_agent()

async def main():
    print("\n" + "="*50)
    print("  SITH HOLOCRON AWAKENED")
    print("  Type 'exit' to seal the archives.")
    print("="*50 + "\n")

    # REMOVED: ctx = Context(agent) <-- This caused the conflict

    while True:
        try:
            user_input = input("Seeker: ")
            if user_input.lower() in ["exit", "quit", "leave"]:
                print("\nHolocron: The connection is severed.\n")
                break
            
            # FIX: Use .chat() or .achat()
            # This is the standard way to talk to an AgentRunner.
            # It automatically uses the 'memory' object we attached earlier.
            response = await agent.run(user_input)
            
            print(f"\nHolocron: {response}\n")
            print("-" * 30)

        except KeyboardInterrupt:
            print("\nConnection severed.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())