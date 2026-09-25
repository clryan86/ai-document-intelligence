from app.services.nlp import chunk_text, extract_keywords, semantic_search, summarize

def test_chunk_text_adds_overlap_and_preserves_content():
    text=" ".join(f"word{i}" for i in range(450)); chunks=chunk_text(text,target_words=100,overlap_words=20); assert len(chunks)>4; assert "word0" in chunks[0]; assert "word99" in chunks[0]

def test_summarize_returns_compact_text():
    text=("Automation reduces repetitive manual work. Reliable automation needs observability and testing. Python is commonly used for APIs and workflow automation. Teams should measure failures and retry behavior. Documentation makes operational systems easier to maintain.")
    result=summarize(text,max_sentences=2); assert result; assert result.count(".")<=2

def test_keywords_excludes_common_stop_words():
    result=extract_keywords("Python automation automation data data data workflow testing"); assert result[0]=="data"; assert "automation" in result

def test_semantic_search_ranks_relevant_chunk_first():
    chunks=["tomatoes basil kitchen recipe cooking","python fastapi api automation testing deployment","garden soil irrigation plants"]
    ranked=semantic_search("python api automation",chunks); assert ranked[0][0]==1; assert ranked[0][1]>0
