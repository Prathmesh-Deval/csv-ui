from langchain.agents.agent_types import AgentType
from langchain_community.llms import Ollama
# from langchain_experimental.agents import create_csv_agent
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_community.chat_models import ChatOllama
import warnings


warnings.filterwarnings("ignore")
llm = ChatOllama(
    # model="mistral:7b-text-v0.2-q8_0",
    model="mistral:7b-instruct-v0.3-q8_0",
    # model="mistral:7b-instruct-q8_0",
    temperature=0.

)
# llm = Ollama(model="mistral:7b-instruct-q8_0")
print("\nLLM Loaded:", llm, "\n")

"""Params: {'model': 'mistral:7b-instruct-q8_0', 'format': None,
 'options': {'mirostat': None, 'mirostat_eta': None, 'mirostat_tau': None, 'num_ctx': None, 'num_gpu': None, 'num_thread': None, 'num_predict': None,
  'repeat_last_n': None, 'repeat_penalty': None, 'temperature': None, 'stop': None, 'tfs_z': None, 'top_k': None, 'top_p': None}, 'system': None, 'template': None, 
  'keep_alive': None, 'raw': None}
  
  prompt, temperature=0.1, max_length=500, top_p=0.95, top_k=5, repetition_penalty=1.2
  """

agent = create_csv_agent(
    llm,
    "F:\GenAI\chatbot\power_plant_database_global.csv",
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    # agent_type="openai-tools",
    allow_dangerous_code=True,
)

agent.invoke("what is commisioning_year for Koman power plant?")
