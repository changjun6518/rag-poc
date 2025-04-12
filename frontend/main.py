import streamlit as st
import requests
from typing import Dict, Any

st.set_page_config(
    page_title="전세 대출 Q&A 시스템",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 전세 대출 Q&A 시스템")

# API 엔드포인트 설정
API_URL = "http://localhost:8000"

# 세션 상태 초기화
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'processed_question' not in st.session_state:
    st.session_state.processed_question = None
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = None

def get_answer(question: str) -> Dict[str, Any]:
    """API를 통해 질문에 대한 답변을 가져옵니다."""
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"text": question}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류가 발생했습니다: {str(e)}")
        return None

def upload_document(file) -> bool:
    """문서를 업로드합니다."""
    try:
        files = {"file": file}
        response = requests.post(
            f"{API_URL}/upload",
            files=files
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"문서 업로드 중 오류가 발생했습니다: {str(e)}")
        return False

# 사이드바에 문서 업로드 기능 추가
with st.sidebar:
    st.title("📄 문서 업로드")
    uploaded_file = st.file_uploader("전세 대출 관련 문서를 업로드하세요", type=["txt", "pdf"])
    
    if uploaded_file is not None and uploaded_file != st.session_state.uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        if upload_document(uploaded_file):
            st.success("문서가 성공적으로 업로드되었습니다!")
            # 문서 업로드 후 질문 상태 초기화
            st.session_state.processed_question = None
            st.session_state.last_answer = None

# 사용자 입력
user_question = st.text_area("💬 질문을 입력하세요", height=100)

# 질문 처리 함수
def process_question(question: str):
    if question and question != st.session_state.processed_question:
        st.session_state.processed_question = question
        with st.spinner("답변을 생성하는 중..."):
            result = get_answer(question)
            
            if result:
                st.session_state.last_answer = result
                # 로그 표시
                with st.expander("🔍 처리 과정 보기", expanded=False):
                    if "logs" in result:
                        for log in result["logs"]:
                            if log.startswith("사용자 질문:"):
                                st.info(log)
                            elif log.startswith("벡터 검색 결과:"):
                                st.info(log)
                            elif log.startswith("문서"):
                                st.info(log)
                            elif log.startswith("출처:"):
                                st.info(log)
                            elif log.startswith("내용:"):
                                st.info(log)
                            elif log.startswith("최종 응답:"):
                                st.success(log)
                            elif log.startswith("참고 문서:"):
                                st.success(log)
                            else:
                                st.info(log)
                
                # 답변 표시
                st.markdown("### 답변")
                st.write(result["answer"])
                
                # 참조 문서 표시
                if result["sources"]:
                    st.markdown("### 참조 문서")
                    for source in result["sources"]:
                        st.write(f"- {source}")
            else:
                st.error("답변을 가져오는데 실패했습니다.")
    elif question:
        # 이전 답변 표시
        if st.session_state.last_answer:
            result = st.session_state.last_answer
            # 로그 표시
            with st.expander("🔍 처리 과정 보기", expanded=False):
                if "logs" in result:
                    for log in result["logs"]:
                        if log.startswith("사용자 질문:"):
                            st.info(log)
                        elif log.startswith("벡터 검색 결과:"):
                            st.info(log)
                        elif log.startswith("문서"):
                            st.info(log)
                        elif log.startswith("출처:"):
                            st.info(log)
                        elif log.startswith("내용:"):
                            st.info(log)
                        elif log.startswith("최종 응답:"):
                            st.success(log)
                        elif log.startswith("참고 문서:"):
                            st.success(log)
                        else:
                            st.info(log)
            
            # 답변 표시
            st.markdown("### 답변")
            st.write(result["answer"])
            
            # 참조 문서 표시
            if result["sources"]:
                st.markdown("### 참조 문서")
                for source in result["sources"]:
                    st.write(f"- {source}")
    else:
        st.warning("질문을 입력해주세요.")

# 질문 처리
if user_question:
    process_question(user_question)

# 사이드바에 정보 추가
with st.sidebar:
    st.write("---")
    st.write("이 서비스는 RAG(Retrieval-Augmented Generation) 기술을 사용하여 전세 대출 관련 질문에 답변합니다.")
    st.write("---")
    st.write("팀 소개: AI 팀")
    st.write("버전: 1.0.0")