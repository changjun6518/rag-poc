from langchain_community.document_loaders import TextLoader, PyPDFLoader
from typing import List
import os

class DocumentLoader:
    """문서 로더 클래스"""
    
    @staticmethod
    def load_documents(data_dir: str) -> List:
        """지원하는 모든 파일 형식의 문서를 로드합니다."""
        documents = []
        
        # 지원하는 파일 확장자와 해당 로더 매핑
        loaders = {
            '.txt': TextLoader,
            '.pdf': PyPDFLoader
        }
        
        # data 디렉토리의 모든 파일 로드
        for filename in os.listdir(data_dir):
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in loaders:
                file_path = os.path.join(data_dir, filename)
                try:
                    loader = loaders[file_ext](file_path)
                    documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading file {file_path}: {str(e)}")
        
        return documents 