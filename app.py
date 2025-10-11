import os
import json

from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

import pandas as pd

# -----------------------------------------------------------------------------
#                             CONFIGURACIÓN RAG
# -----------------------------------------------------------------------------

DATA_DIR = "data"
VECTOR_DIR = "vectorstore"   # carpeta local para Chroma
PDF_PATH = os.path.join(DATA_DIR, "Politica_Devoluciones_Garantias_EcoMarket.pdf")
CSV_PATH = os.path.join(DATA_DIR, "catalogo_ecomarket.csv")
FAQ_PATH = os.path.join(DATA_DIR, "faq_ecomarket.json")

EMBEDDING_MODEL_NAME = "text-embedding-3-large"
EMBEDDINGS = OpenAIEmbeddings(
    model=EMBEDDING_MODEL_NAME,
    api_key=os.environ["OPENAI_API_KEY"]
)

OPENAI_MODEL = "gpt-4o-mini" 
LC_LLM = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0.2,
    api_key=os.environ["OPENAI_API_KEY"]
)

# -----------------------------------------------------------------------------
#                     INGESTA: CARGA Y CHUNKING DE DOCUMENTOS
# -----------------------------------------------------------------------------
def load_pdf_docs(pdf_path: str):
    """Carga PDF de políticas y lo chunkifica por secciones."""
    if not os.path.exists(pdf_path):
        return []
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()  
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=900,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_documents(pages)
    # Añadimos metadata tipo_documento
    for d in chunks:
        d.metadata["tipo_documento"] = "politicas"
    return chunks

def load_csv_catalog(csv_path: str):
    """Carga catálogo (CSV) y crea documentos por fila o grupos lógicos."""
    if not os.path.exists(csv_path):
        return []
    df = pd.read_csv(csv_path, encoding="utf-8")
    docs = []
    for _, row in df.iterrows():
        texto = (
            f"SKU: {row.get('sku','')}\n"
            f"Nombre: {row.get('nombre','')}\n"
            f"Categoría: {row.get('categoria','')}\n"
            f"Descripción: {row.get('descripcion','')}\n"
            f"Precio: {row.get('precio','')} {row.get('moneda','')}\n"
            f"Stock: {row.get('stock','')}\n"
            f"Material: {row.get('material','')}\n"
            f"Sostenible: {row.get('sostenible','')}\n"
            f"Garantía (meses): {row.get('garantia_meses','')}\n"
            f"Proveedor: {row.get('proveedor','')}\n"
            f"País de origen: {row.get('pais_origen','')}\n"
            f"URL: {row.get('url_producto','')}\n"
        )
        docs.append(Document(
            page_content=texto,
            metadata={
                "tipo_documento": "catalogo",
                "sku": row.get("sku",""),
                "categoria": row.get("categoria","")
            }
        ))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700, chunk_overlap=100
    )
    return splitter.split_documents(docs)

def load_faqs_json(faq_path: str):
    """Carga FAQs (JSON) y crea un Document por cada Q/A."""
    if not os.path.exists(faq_path):
        return []
    with open(faq_path, "r", encoding="utf-8") as f:
        faqs = json.load(f)
    docs = []
    for item in faqs:
        texto = f"P: {item.get('pregunta','')}\nR: {item.get('respuesta','')}\nCategoría: {item.get('categoria','')}"
        docs.append(Document(
            page_content=texto,
            metadata={
                "tipo_documento": "faq",
                "categoria": item.get("categoria","")
            }
        ))
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    )
    return splitter.split_documents(docs)

def build_vectorstore(reset: bool = False):
    """Crea (o reutiliza) el índice Chroma con embeddings y los tres tipos de documentos."""
    if reset and os.path.exists(VECTOR_DIR):
        import shutil
        shutil.rmtree(VECTOR_DIR)

    # 1) Cargar documentos
    pdf_docs = load_pdf_docs(PDF_PATH)
    csv_docs = load_csv_catalog(CSV_PATH)
    faq_docs = load_faqs_json(FAQ_PATH)

    all_docs = pdf_docs + csv_docs + faq_docs
    if not all_docs:
        raise RuntimeError("No se encontraron documentos para indexar. Verifica las rutas en data/")

    # 2) Crear / cargar Chroma
    vectordb = Chroma.from_documents(
        documents=all_docs,
        embedding=EMBEDDINGS,
        persist_directory=VECTOR_DIR,
        collection_name="ecomarket"
    )
    vectordb.persist()
    return vectordb

def get_retriever(top_k: int = 5):
    """Devuelve un retriever desde el índice en disco (si no existe, lo crea)."""
    if not os.path.exists(VECTOR_DIR):
        vectordb = build_vectorstore(reset=False)
    else:
        vectordb = Chroma(
            embedding_function=EMBEDDINGS,
            persist_directory=VECTOR_DIR,
            collection_name="ecomarket"
        )
    return vectordb.as_retriever(search_kwargs={"k": top_k})

def rag_answer(query: str, top_k: int = 5):
    """RAG: recupera contexto y responde con el LLM siguiendo reglas del agente."""
    retriever = get_retriever(top_k=top_k)

    # Ruta al archivo de reglas del sistema
    SYSTEM_RULES_PATH = os.path.join("prompts", "system_agent.txt")

    # Leer el contenido del archivo
    with open(SYSTEM_RULES_PATH, "r", encoding="utf-8") as f:
        system_rules = f.read().strip()

    # Cadena QA con retrieval
    chain = RetrievalQA.from_chain_type(
        llm=LC_LLM,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={
            "verbose": False,
            "document_variable_name": "context",
            "prompt": None 
        },
        return_source_documents=True
    )

    result = chain.invoke({"query": f"{system_rules}\n\nPregunta del cliente: {query}"})
    answer = result["result"]
    sources = result.get("source_documents", [])
    cited = "\n\nFuentes consultadas:\n" + "\n".join(
        f"- {s.metadata.get('tipo_documento','desconocido')} | {s.metadata}" for s in sources
    ) if sources else ""
    return answer + cited

# -----------------------------------------------------------------------------
#                               DEMOS
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    print("\n=== RAG demo ===")
    print(rag_answer("¿Cómo funciona la garantía y en cuánto tiempo realizan un reembolso?"))
    print()
    print(rag_answer("¿Tienen cepillos de bambú y cuál es su precio y disponibilidad?"))
    print()
    print(rag_answer("¿Cómo puedo rastrear mi pedido y cuánto tarda en llegar a Medellín?"))
