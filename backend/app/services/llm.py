

# from langchain_groq import ChatGroq
# from langchain_core.prompts import ChatPromptTemplate
# from app.core.config import settings

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     groq_api_key=settings.GROQ_API_KEY,
#     temperature=0
# )

# PROMPT = ChatPromptTemplate.from_template("""
# You are a helpful assistant.

# Use both conversation history and retrieved context.

# Rules:

# 1. If the answer exists in conversation history, answer from conversation history.
# 2. If the answer exists in retrieved context, answer from retrieved context.
# 3. If the answer exists in neither, respond exactly:

# I don't have enough information.

# 4. Do not make up facts.
# 5. Prefer retrieved context over assumptions.
# 6. Only cite sources when the answer comes from retrieved documents.

# When answering from retrieved context, cite sources using:

# [Source: filename, page X]

# Conversation History:
# {history}

# Context:
# {context}

# Question:
# {question}

# Answer:
# """)


# async def generate_answer(
#     question: str,
#     chunks: list,
#     history: list
# ) -> dict:

#     # Build retrieved context
#     context = "\n\n".join(
#         [
#             f"[{c.payload.get('filename', 'Unknown')}, page {c.payload.get('page', '?')}]\n"
#             f"{c.payload.get('text', '')}"
#             for c in chunks
#         ]
#     )

#     # Build conversation history
#     history_text = "\n".join(
#         [
#             f"{msg.role}: {msg.content}"
#             for msg in history[-10:]
#         ]
#     )

#     chain = PROMPT | llm

#     response = await chain.ainvoke(
#         {
#             "history": history_text,
#             "context": context,
#             "question": question
#         }
#     )

#     answer = response.content.strip()

#     # Build unique citations
#     seen = set()
#     citations = []

#     for c in chunks:
#         filename = c.payload.get("filename", "Unknown")
#         page = c.payload.get("page", "?")

#         key = (filename, page)

#         if key in seen:
#             continue

#         seen.add(key)

#         citations.append(
#             {
#                 "document": filename,
#                 "page": page,
#                 "chunk": c.payload.get("text", "")[:200]
#             }
#         )

#     # Remove citations for unknown answers
#     if answer == "I don't have enough information.":
#         citations = []

#     return {
#         "answer": answer,
#         "citations": citations
#     }






from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=settings.GROQ_API_KEY,
    temperature=0
)

PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant.

Use both conversation history and retrieved context.

Rules:

1. If the answer exists in conversation history, answer from conversation history.
2. If the answer exists in retrieved context, answer from retrieved context.
3. If the answer exists in neither, respond exactly:

I don't have enough information.

4. Do not make up facts.
5. Prefer retrieved context over assumptions.
6. Only cite sources when the answer comes from retrieved documents.

When answering from retrieved context, cite sources using:

[Source: filename, page X]

Conversation History:
{history}

Context:
{context}

Question:
{question}

Answer:
""")


async def generate_answer(
    question: str,
    chunks: list,
    history: list
) -> dict:

    # Build retrieved context
    context = "\n\n".join(
        [
            f"[{c.payload.get('filename', 'Unknown')}, page {c.payload.get('page', 0)}]\n"
            f"{c.payload.get('text', '')}"
            for c in chunks
        ]
    )

    # Build conversation history
    history_text = "\n".join(
        [
            f"{msg.role}: {msg.content}"
            for msg in history[-10:]
        ]
    )

    chain = PROMPT | llm

    response = await chain.ainvoke(
        {
            "history": history_text,
            "context": context,
            "question": question
        }
    )

    answer = response.content.strip()

    # Build unique citations
    seen = set()
    citations = []

    for c in chunks:
        filename = c.payload.get("filename", "Unknown")

        page = c.payload.get("page")
        if page is not None:
            page = int(page)

        key = (filename, page)

        if key in seen:
            continue

        seen.add(key)

        citations.append(
            {
                "document": filename,
                "page": page,
                "chunk": c.payload.get("text", "")[:200]
            }
        )

    # Remove citations for unknown answers
    if answer == "I don't have enough information.":
        citations = []

    return {
        "answer": answer,
        "citations": citations
    }









