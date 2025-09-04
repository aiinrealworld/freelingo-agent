# tests/db/test_words.py

import pytest
from freelingo_agent.db import words

class MockResponse:
    def __init__(self, data=None):
        self.data = data or []

# ---- get_known_words ----
def test_get_known_words(monkeypatch):
    from freelingo_agent.db import words  # Ensure test gets the real context

    class MockQuery:
        def select(self, fields):
            return self

        def eq(self, key, value):
            return self

        def order(self, field, desc):
            return self

        def execute(self):
            return MockResponse(data=[{"word": "bonjour"}, {"word": "chat"}])

    class MockFrom:
        def __init__(self):
            pass

        def select(self, fields):
            return MockQuery()

    monkeypatch.setattr(words.supabase, "from_", lambda table: MockFrom())

    result = words.get_known_words("00000000-0000-0000-0000-000000000000")
    assert result == ["bonjour", "chat"]

# ---- get_user_words ----
def test_get_user_words(monkeypatch):
    from freelingo_agent.db import words  # Make sure this import is inside the test to access the right context
    from datetime import datetime

    class MockQuery:
        def select(self, fields):
            return self

        def eq(self, key, value):
            return self

        def order(self, field, desc):
            return self

        def execute(self):
            return MockResponse(data=[{
                "id": "123",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "word": "bonjour",
                "translation": "hello",
                "example": "Bonjour, comment allez-vous?",
                "created_at": "2024-01-01T00:00:00Z"
            }])

    class MockFrom:
        def select(self, fields):
            return MockQuery()

    # Patch supabase.from_ to return our MockFrom
    monkeypatch.setattr(words.supabase, "from_", lambda table: MockFrom())

    # Now run the test
    result = words.get_user_words("00000000-0000-0000-0000-000000000000")
    
    assert len(result) == 1
    assert result[0].word == "bonjour"
    assert result[0].translation == "hello"
    assert result[0].user_id == "00000000-0000-0000-0000-000000000000"

# ---- create_word ----
def test_create_word(monkeypatch):
    from freelingo_agent.db import words  # ensure you're importing the right context
    from freelingo_agent.models.words_model import WordCreate

    class MockInsert:
        def __init__(self, data):
            self.data = data

        def execute(self):
            return MockResponse(data=[{
                "id": "123",
                "user_id": "00000000-0000-0000-0000-000000000000",
                "word": "bonjour",
                "translation": "hello",
                "example": "Bonjour!",
                "created_at": "2024-01-01T00:00:00Z"
            }])

    class MockFrom:
        def insert(self, data):
            return MockInsert(data)

    monkeypatch.setattr(words.supabase, "from_", lambda table: MockFrom())

    # Run the function
    word_data = WordCreate(
        word="bonjour",
        translation="hello",
        example="Bonjour!",
        user_id="00000000-0000-0000-0000-000000000000"
    )
    result = words.create_word("00000000-0000-0000-0000-000000000000", word_data)

    # Assertions
    assert result.word == "bonjour"
    assert result.translation == "hello"
    assert result.user_id == "00000000-0000-0000-0000-000000000000"

# ---- delete_word ----
def test_delete_word(monkeypatch):
    from freelingo_agent.db import words  # Ensure correct context
    deleted = []

    class MockDeleteQuery:
        def eq(self, key, val):
            self.calls.append((key, val))
            return self

        def execute(self):
            deleted.append(self.calls)  # Store the full list of calls
            return MockResponse(data=[{"id": "123"}])

        def __init__(self):
            self.calls = []

    class MockFrom:
        def delete(self):
            return MockDeleteQuery()

    monkeypatch.setattr(words.supabase, "from_", lambda table: MockFrom())

    # Run test
    result = words.delete_word("123")

    # Assert expected delete arguments and return value
    assert deleted[0] == [("id", "123")]  # Check the full list of calls
    assert result == True
