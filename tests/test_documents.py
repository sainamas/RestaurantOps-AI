from app.services.documents import chunks, SUPPORTED
def test_chunker():
    result=chunks(" ".join(["pasta"]*500))
    assert len(result)>1
    assert all(result)
def test_supported_extensions():
    assert SUPPORTED=={".pdf",".docx",".txt",".md"}
def test_empty():
    assert chunks("")==[]
