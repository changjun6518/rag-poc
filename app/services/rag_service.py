from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_openai.llms import OpenAI
import os
from typing import Tuple, List
from dotenv import load_dotenv
from pathlib import Path
import shutil
import time
from .document_loader import DocumentLoader

# Get the project root directory (where .env file is located)
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"
DATA_DIR = ROOT_DIR / "data"
CHROMA_DIR = ROOT_DIR / "chroma_db"

# Load environment variables from .env file
if ENV_FILE.exists():
    load_dotenv(ENV_FILE, override=True)
else:
    print(f"Warning: .env file not found at {ENV_FILE}")

class RAGService:
    def __init__(self):
        # OpenAI API 키 확인
        print(os.getenv("OPENAI_API_KEY"))
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set. Please set it in your .env file or environment variables.")

        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None
        self.qa_chain = None
        self.text_splitter = CharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separator="\n"
        )
        self._initialize_rag()

    def _update_qa_chain(self):
        """QA 체인을 업데이트합니다."""
        if self.vector_store is not None:
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=OpenAI(temperature=0),
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_kwargs={"k": 3}
                )
            )

    def _load_documents(self) -> List:
        """문서를 로드하고 분할합니다."""
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True)
            return []

        # DocumentLoader를 사용하여 문서 로드
        documents = DocumentLoader.load_documents(str(DATA_DIR))

        if not documents:
            print("No documents found in the data directory")
            return []

        # 문서 분할
        splits = self.text_splitter.split_documents(documents)

        if not splits:
            print("No text splits generated from documents")
            return []

        return splits

    def upload_document(self, file_path: str) -> bool:
        """새로운 문서를 업로드하고 벡터 저장소를 업데이트합니다."""
        try:
            # 1. data 디렉토리에 파일 저장
            if not DATA_DIR.exists():
                DATA_DIR.mkdir(parents=True)
            
            # 파일명에서 확장자 추출
            file_ext = os.path.splitext(file_path)[1]
            # 새로운 파일명 생성 (타임스탬프 추가)
            new_filename = f"document_{int(time.time())}{file_ext}"
            new_file_path = DATA_DIR / new_filename
            
            # 파일 복사
            shutil.copy2(file_path, new_file_path)

            # 2. 새 문서 로드 및 분할
            documents = DocumentLoader.load_documents(str(DATA_DIR))
            splits = self.text_splitter.split_documents(documents)

            if not splits:
                print("No text splits generated from new document")
                return False

            # 3. 벡터 저장소 업데이트
            if self.vector_store is None:
                # 첫 번째 문서인 경우 새로 생성
                self.vector_store = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embeddings,
                    persist_directory=str(CHROMA_DIR)
                )
            else:
                # 기존 벡터 저장소에 추가
                self.vector_store.add_documents(
                    documents=splits,
                    persist_directory=str(CHROMA_DIR)
                )

            # 4. QA 체인 업데이트
            self._update_qa_chain()

            return True
        except Exception as e:
            print(f"Error uploading document: {str(e)}")
            return False

    def _initialize_rag(self):
        """RAG 시스템을 초기화합니다."""
        try:
            # ChromaDB 디렉토리가 있으면 기존 벡터 저장소 로드
            if CHROMA_DIR.exists():
                print("Loading existing vector store...")
                self.vector_store = Chroma(
                    persist_directory=str(CHROMA_DIR),
                    embedding_function=self.embeddings
                )
            else:
                # 초기 문서 로드 및 벡터 저장소 생성
                print("Loading and splitting documents...")
                splits = self._load_documents()

                if splits:
                    print("Initializing vector store...")
                    self.vector_store = Chroma.from_documents(
                        documents=splits,
                        embedding=self.embeddings,
                        persist_directory=str(CHROMA_DIR)
                    )

            # QA 체인 초기화
            if self.vector_store is not None:
                print("Initializing QA chain...")
                self._update_qa_chain()
                print("RAG system initialized successfully!")
            else:
                print("No documents available for initialization")
        except Exception as e:
            print(f"Error initializing RAG: {str(e)}")
            raise

    def get_answer(self, question: str) -> Tuple[str, List[str], List[str]]:
        """질문에 대한 답변을 생성합니다."""
        try:
            if not self.qa_chain:
                return "죄송합니다. 아직 학습된 문서가 없습니다.", [], []

            logs = []
            logs.append(f"사용자 질문: '{question}'")

            # 벡터 DB에서 유사 문서 검색
            docs = self.vector_store.similarity_search(question, k=3)
            logs.append("\n벡터 검색 결과:")
            for i, doc in enumerate(docs, 1):
                logs.append(f"\n문서 {i}:")
                logs.append(f"출처: {doc.metadata.get('source', 'Unknown')}")
                logs.append(f"내용: {doc.page_content[:200]}...")  # 처음 200자만 출력

            result = self.qa_chain.invoke({"query": question})
            answer = result["result"]
            sources = [doc.metadata.get("source", "Unknown") for doc in result.get("source_documents", [])]

            logs.append("\n최종 응답:")
            logs.append(answer)
            logs.append(f"\n참고 문서: {', '.join(sources)}")

            return answer, sources, logs
        except Exception as e:
            error_msg = f"Error getting answer: {str(e)}"
            print(error_msg)
            raise 