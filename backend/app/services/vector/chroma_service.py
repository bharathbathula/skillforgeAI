import os
from typing import Dict, Any, List, Optional
from app.core.config import settings

class ChromaService:
    _client: Any = None

    @classmethod
    def get_client(cls) -> Any:
        if cls._client is None:
            try:
                import chromadb
                persist_dir = getattr(settings, "CHROMA_PERSIST_DIRECTORY", "./chroma_db")
                os.makedirs(persist_dir, exist_ok=True)
                cls._client = chromadb.PersistentClient(path=persist_dir)
            except Exception:
                cls._client = False
        return cls._client

    @classmethod
    def index_resume_sections(cls, resume_id: int, sections: Dict[str, str]) -> None:
        client = cls.get_client()
        if not client:
            return

        try:
            collection = client.get_or_create_collection(name="skillforge_resumes")
            documents = []
            metadatas = []
            ids = []

            for sec_name, sec_text in sections.items():
                if sec_text and sec_text.strip():
                    doc_id = f"resume_{resume_id}_{sec_name}"
                    documents.append(sec_text)
                    metadatas.append({"resume_id": resume_id, "section": sec_name})
                    ids.append(doc_id)

            if documents:
                collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        except Exception:
            pass

    @classmethod
    def index_job_sections(cls, job_id: int, sections: Dict[str, str]) -> None:
        client = cls.get_client()
        if not client:
            return

        try:
            collection = client.get_or_create_collection(name="skillforge_jobs")
            documents = []
            metadatas = []
            ids = []

            for sec_name, sec_text in sections.items():
                if sec_text and sec_text.strip():
                    doc_id = f"job_{job_id}_{sec_name}"
                    documents.append(sec_text)
                    metadatas.append({"job_id": job_id, "section": sec_name})
                    ids.append(doc_id)

            if documents:
                collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        except Exception:
            pass
