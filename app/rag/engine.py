from pathlib import Path
from typing import TypedDict

import re
import json
import faiss
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END
from ddgs import DDGS
from app.services.documents import load_file

class State(TypedDict, total=False):
    question: str
    hits: list[dict]
    use_web: bool
    web: list[dict]
    answer: str
    sources: list[dict]
    route: str

class Engine:
    def __init__(self, model_name, index_dir, top_k=5, threshold=.70, web=True):
        self.model=SentenceTransformer(model_name); self.folder=Path(index_dir)
        self.folder.mkdir(parents=True,exist_ok=True); self.k=top_k; self.threshold=threshold; self.web=web
        self.docs=[]; self.index=None; self._load()
    def _load(self):
        ix=self.folder/"index.faiss"; meta=self.folder/"docs.json"
        if ix.exists() and meta.exists():
            self.index=faiss.read_index(str(ix)); self.docs=json.loads(meta.read_text(encoding="utf8"))
    def rebuild(self, folder):
        docs=[]
        for p in Path(folder).rglob("*"):
            if p.is_file() and p.suffix.lower() in {".pdf",".docx",".txt",".md"}: docs += load_file(p)
        self.docs=docs
        if not docs: self.index=None; return 0
        vec=self.model.encode([d["text"] for d in docs],normalize_embeddings=True).astype("float32")
        self.index=faiss.IndexFlatIP(vec.shape[1]); self.index.add(vec)
        faiss.write_index(self.index,str(self.folder/"index.faiss"))
        (self.folder/"docs.json").write_text(json.dumps(docs,ensure_ascii=False),encoding="utf8")
        
        return len(docs)

    def _title_match_score(self, question, document):
        text = document.get("text", "")

        first_line = next(
            (line.strip() for line in text.splitlines() if line.strip()),
            ""
        )

        title = re.sub(r"^#+\s*", "", first_line)
        title = re.split(r"\bCategory\s*:", title, flags=re.IGNORECASE)[0]
        title = re.sub(r"\b(?:REC|REF)-\d+\b", "", title, flags=re.IGNORECASE)

        stop_words = {
            "how", "do", "i", "prepare", "make", "the",
            "a", "an", "what", "is", "for", "to", "of"
        }

        question_words = set(re.findall(r"[a-z0-9]+", question.lower()))
        title_words = set(re.findall(r"[a-z0-9]+", title.lower()))

        question_words -= stop_words
        title_words -= stop_words

        if not title_words:
            return 0.0

        return len(question_words & title_words) / len(title_words)

    def retrieve(self, q):

        if self.index is None: return []
        v=self.model.encode([q],normalize_embeddings=True).astype("float32")
        scores,ids=self.index.search(v,min(self.k,len(self.docs)))
        return [{**self.docs[int(i)],"score":float(s)} for s,i in zip(scores[0],ids[0]) if i>=0]
    def web_search(self, q):
        if not self.web:
            return []

        try:
            with DDGS() as d:
                return [
                    {
                        "text": f'{x.get("title", "")}. {x.get("body", "")}',
                        "source": x.get("title", "Web result"),
                        "url": x.get("href", ""),
                        "source_type": "external",
                        "score": None
                    }
                    for x in d.text(q, max_results=4)
                ]

        except Exception as e:
            print(f"Web search error: {e}")
            return []
     
    def rebuild_from_documents(self, docs):
        self.docs=docs
        if not docs:
            self.index=None
            return 0
        vec=self.model.encode([d["text"] for d in docs],normalize_embeddings=True).astype("float32")
        self.index=faiss.IndexFlatIP(vec.shape[1]); self.index.add(vec)
        faiss.write_index(self.index,str(self.folder/"index.faiss"))
        (self.folder/"docs.json").write_text(json.dumps(docs,ensure_ascii=False),encoding="utf8")
        return len(docs)
   
    def retrieve(self, q):
        if self.index is None or not self.docs:
            return []

        # Convert the question into an embedding
        vector = self.model.encode(
            [q],
            normalize_embeddings=True
        ).astype("float32")

        # Search FAISS for the closest documents
        scores, ids = self.index.search(
            vector,
            min(self.k, len(self.docs))
        )

        results = []

        for score, doc_id in zip(scores[0], ids[0]):
            if doc_id < 0:
                continue

            document = self.docs[int(doc_id)]

            semantic_score = float(score)

            # Calculate how closely the question matches the title
            title_score = self._title_match_score(q, document)

            # Combine semantic and title relevance
            relevance_score = semantic_score + (0.20 * title_score)

            results.append({
                **document,
                "score": semantic_score,
                "title_score": title_score,
                "relevance_score": relevance_score
            })

        # Rank documents using combined relevance
        results.sort(
            key=lambda item: item["relevance_score"],
            reverse=True
        )

        return results

    def _build(self):
        g = StateGraph(State)

        # LangGraph node for internal document retrieval
        def retrieve_node(s):
            return {"hits": self.retrieve(s["question"])}

        def grade(s):
            ok = bool(
                s.get("hits")
                and s["hits"][0]["relevance_score"] >= self.threshold
            )
            return {
                "use_web": not ok,
                "route": "internal" if ok else "web"
            }

        def search(s):
            return {"web": self.web_search(s["question"])}

        def answer_internal(s):
            hits = [
                h for h in s["hits"]
                if h["relevance_score"] >= self.threshold
            ]
            return self._answer(s, hits, "internal")

        def answer_web(s):
            return self._answer(s, s.get("web", []), "web")

        g.add_node("retrieve", retrieve_node)
        g.add_node("grade", grade)
        g.add_node("search", search)
        g.add_node("internal_answer", answer_internal)
        g.add_node("web_answer", answer_web)

        g.set_entry_point("retrieve")
        g.add_edge("retrieve", "grade")

        g.add_conditional_edges(
            "grade",
            lambda s: "search" if s["use_web"] else "internal_answer",
            {
                "search": "search",
                "internal_answer": "internal_answer"
            }
        )

        g.add_edge("search", "web_answer")
        g.add_edge("web_answer", END)
        g.add_edge("internal_answer", END)
        return g.compile()
        
    def _answer(self, s, hits, route):
        if not hits:
            msg = (
                "I could not find sufficiently relevant evidence. "
                "Please check with an authorised manager."
            )

        elif route == "internal":
            details = "\n\n---\n\n".join(
                item["text"][:1000] for item in hits[:3]
            )

            msg = (
                "Information retrieved from internal restaurant documents:\n\n"
                + details
            )

        else:
            result_sections = []

            for number, hit in enumerate(hits[:4], start=1):
                title = hit.get("source") or f"Web result {number}"
                description = hit.get("text", "").strip()
                url = hit.get("url", "").strip()

                section = (
                    f"{number}. {title}\n"
                    f"{description[:700]}"
                )

                if url:
                    section += f"\nSource: {url}"

                result_sections.append(section)

            msg = (
                "No sufficient internal evidence was found.\n\n"
                "External web information (not approved restaurant "
                "procedures):\n\n"
                + "\n\n---\n\n".join(result_sections)
            )

        return {
            "answer": msg,
            "sources": hits,
            "route": route
        }

    def ask(self, q):
        return self._build().invoke({"question": q})