import sqlite3
from sqlalchemy import create_engine, text
from transformers import AutoTokenizer
from llama_index.core import SQLDatabase
from llama_index.core import Settings
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.llama_cpp import LlamaCPP


engine = create_engine('sqlite:///')
filedb = sqlite3.connect('file:' + 'DATABASE.db' + '?mode=ro', uri=True)
print("loading database to memory ...")
filedb.backup(engine.raw_connection().driver_connection)
print("loading database to memory ... done")
filedb.close()
with engine.connect() as con:
    rows = con.execute(text("SELECT COUNT(*) from data"))
    print(rows.all())

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.3")

SHOW_LLM_CALL_TOKENS = True
def messages_to_prompt(messages):
    inst_buffer = []

    prompt = ""

    for message in messages:
        if message.role == 'system' or message.role == 'user':
            inst_buffer.append(str(message.content).strip())

        elif message.role == 'assistant':
            prompt += "[INST] " + "\n".join(inst_buffer) + " [/INST]"
            prompt += " " + str(message.content).strip() + "</s>"
            inst_buffer.clear()
        else:
            raise ValueError(f"Unknown message role {message.role}")

    if len(inst_buffer) > 0:
        prompt += "[INST] " + "\n".join(inst_buffer) + " [/INST]"



def completion_to_prompt(completion):

    return "[INST] " + str(completion).strip() + " [/INST]"


llm = LlamaCPP(
    model_path="C:\llm_weights\mistral-7b-instruct-v0.2.Q4_K_S.gguf",
    temperature=0.1,
    max_new_tokens=1024,
    context_window=16348,  # max 32k
    generate_kwargs={},
    model_kwargs={"n_gpu_layers": -1},
    messages_to_prompt=messages_to_prompt,
    completion_to_prompt=completion_to_prompt,
    verbose=False,
)

embed = HuggingFaceEmbedding(model_name="BAAI/bge-m3")

Settings.llm = llm
Settings.embed_model = embed
Settings.tokenizer = tokenizer

sql_database = SQLDatabase(engine, include_tables=["data"])

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["data"],
    llm=llm,
    embed_model=embed)


def ask_sk1(query):
    try:
        response = query_engine.query(query)

        print(f"Question: \n{query}")
        print(f"\nSQL Query used:\n{response.metadata['sql_query']}\n")
        print(f"Answer: \n{response}\n")

    except Exception as e:
        print(f"Error during query execution: {e}")

ask_sk1("How many unique room numbers are there in the database?")
