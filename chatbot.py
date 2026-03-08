from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
import gradio as gr

from dotenv import load_dotenv
load_dotenv()

import re
import asyncio
from fastmcp import Client

# configuration
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"
MCP_MAIL_URL = "http://127.0.0.1:8000/mcp"   # <- dein separater MCP Mail Service

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")
llm = ChatOpenAI(temperature=0.5, model='gpt-4o-mini')

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings_model,
    persist_directory=CHROMA_PATH,
)

retriever = vector_store.as_retriever(search_kwargs={'k': 5})

def parse_mail_command(message: str):
    # Format: /mail empfaenger@mail.de | Betreff | Text
    if not message.strip().lower().startswith("/mail "):
        return None
    rest = message.strip()[6:].strip()
    parts = [p.strip() for p in rest.split("|", 2)]
    if len(parts) != 3:
        return {"error": "Format: /mail empfaenger@mail.de | Betreff | Text"}
    recipient, subject, body = parts
    if not re.search(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", recipient):
        return {"error": "Ungültige E-Mail-Adresse."}
    return {"recipient": recipient, "subject": subject, "body": body}

async def mcp_send_email(recipient: str, subject: str, body_text: str):
    async with Client(MCP_MAIL_URL) as c:
        return await c.call_tool(
            "send_email",
            {"recipient": recipient, "subject": subject, "body_text": body_text},
        )

def stream_response(message, history):
    # 0) /mail Command abfangen
    cmd = parse_mail_command(message or "")
    if cmd:
        if "error" in cmd:
            yield f"❌ {cmd['error']}"
            return

        yield "📨 Sende E-Mail über MCP… (ggf. im MCP-Server-Terminal Device-Code Login bestätigen)"
        try:
            res = asyncio.run(mcp_send_email(cmd["recipient"], cmd["subject"], cmd["body"]))
            yield f"✅ MCP Ergebnis: {res}"
        except Exception as e:
            yield f"❌ Fehler beim Mailversand: {e}"
        return

    # 1) normaler RAG-Chat
    docs = retriever.invoke(message)
    knowledge = "\n\n".join([doc.page_content for doc in docs])

    if message is not None:
        partial_message = ""
        rag_prompt = f"""
You are an assistent which answers questions based on knowledge which is provided to you.
While answering, you don't use your internal knowledge,
but solely the information in the "The knowledge" section.
You don't mention anything to the user about the povided knowledge.

The question: {message}

Conversation history: {history}

The knowledge: {knowledge}
"""
        for response in llm.stream(rag_prompt):
            partial_message += response.content
            yield partial_message

chatbot = gr.ChatInterface(
    stream_response,
    textbox=gr.Textbox(
        placeholder="Frage… oder: /mail empfaenger@mail.de | Betreff | Text",
        container=False,
        autoscroll=True,
        scale=7
    ),
)

chatbot.launch()