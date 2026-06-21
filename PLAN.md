## 기술 스택

| 역할 | 기술 |
|------|------|
| 백엔드 API | FastAPI |
| AI 파이프라인 | LangChain |
| VLM | Gemini 1.5 Flash (무료 티어) |
| 벡터 DB | FAISS |
| 프론트 UI | Gradio |
| 배포 | HuggingFace Spaces |

---

## 데이터셋 테마: 영화 추천 & 분석 어시스턴트

| 계층 | 처리 방식 | 데이터 |
|------|-----------|--------|
| SQL | 구조화 쿼리 | MovieLens DB |
| Pandas | CSV 분석 | 박스오피스 CSV |
| RAG | 문서 검색 | 영화 줄거리/리뷰 텍스트 |
| VLM | 이미지 이해 | 영화 포스터 이미지 |

예시 질문:
- "크리스토퍼 놀란 영화 추천해줘" → SQL
- "2023년 흥행 TOP 10 분석해줘" → Pandas
- "인터스텔라 줄거리 알려줘" → RAG
- (포스터 이미지 업로드) "이 포스터 무슨 영화야?" → VLM

---

## 폴더 구조

```
multimodal-query-pipeline/
│
├── app/                        # FastAPI 백엔드
│   ├── main.py                 # 서버 진입점
│   ├── router/
│   │   └── intent_router.py   # 1계층: 의도 분류
│   ├── mapping/
│   │   └── query_mapper.py    # 2계층: 분기 결정
│   ├── handlers/               # 3-4계층: 실제 처리
│   │   ├── sql_handler.py
│   │   ├── pandas_handler.py
│   │   ├── vlm_handler.py
│   │   └── rag_handler.py
│   ├── rag/
│   │   ├── indexer.py         # FAISS 인덱스 생성/갱신
│   │   └── retriever.py       # 문서 검색
│   └── schemas.py             # 요청/응답 데이터 형식
│
├── data/
│   ├── raw/                   # 공개 데이터셋 원본
│   └── processed/             # 전처리 완료 데이터
│
├── faiss_index/               # 벡터 인덱스 저장
├── frontend/
│   └── app.py                 # Gradio UI
├── .env                       # API 키 (git 제외)
├── requirements.txt
├── PLAN.md                    # 이 파일
└── README.md
```
