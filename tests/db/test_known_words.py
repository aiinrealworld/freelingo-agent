# tests/db/test_known_words.py

import pytest
from db import known_words

class MockResponse:
    def __init__(self, data=None):
        self.data = data or []

# ---- get_known_words ----
def test_get_known_words(monkeypatch):
    from db import known_words  # Ensure test gets the real context

    class MockQuery:
        def select(self, fields):
            return self

        def eq(self, key, value):
            return self

        def execute(self):
            return MockResponse(data=[{"word": "bonjour"}, {"word": "chat"}])

    class MockFrom:
        def __init__(self):
            pass

        def select(self, fields):
            return MockQuery()

    monkeypatch.setattr(known_words.supabase, "from_", lambda table: MockFrom())

    result = known_words.get_known_words("00000000-0000-0000-0000-000000000000")
    assert result == ["bonjour", "chat"]

# ---- add_known_words ----
def test_add_known_words(monkeypatch):
    from db import known_words  # Make sure this import is inside the test to access the right context
    calls = []

    # Mock insert().execute() chain
    class MockInsert:
        def __init__(self, rows):
            self.rows = rows

        def execute(self):
            calls.append(self.rows)
            return {"status_code": 201}  # Optional mock return

    class MockFrom:
        def insert(self, rows):
            return MockInsert(rows)

    # Patch supabase.from_ to return our MockFrom
    monkeypatch.setattr(known_words.supabase, "from_", lambda table: MockFrom())

    # Now run the test
    result = known_words.add_known_words("00000000-0000-0000-0000-000000000000", ["chien", "maison"])
    
    assert result == 2
    assert calls[0][0]["word"] == "chien"
    assert calls[0][0]["user_id"] == "00000000-0000-0000-0000-000000000000"

# ---- replace_known_words ----
def test_replace_known_words(monkeypatch):
    from db import known_words  # ensure you're importing the right context
    delete_called = []
    insert_called = []

    class MockDeleteQuery:
        def eq(self, key, value):
            delete_called.append((key, value))
            return self

        def execute(self):
            return {"status_code": 200}

    class MockInsertQuery:
        def __init__(self, rows):
            self.rows = rows

        def execute(self):
            insert_called.append(self.rows)
            return {"status_code": 201}

    class MockFrom:
        def delete(self):
            return MockDeleteQuery()

        def insert(self, rows):
            return MockInsertQuery(rows)

    monkeypatch.setattr(known_words.supabase, "from_", lambda table: MockFrom())

    # Run the function
    known_words.replace_known_words("00000000-0000-0000-0000-000000000000", ["pomme"])

    # Assertions
    assert delete_called == [("user_id", "00000000-0000-0000-0000-000000000000")]
    assert insert_called[0][0]["word"] == "pomme"

# ---- delete_known_word ----
def test_delete_known_word(monkeypatch):
    from db import known_words  # Ensure correct context
    deleted = []

    class MockDeleteQuery:
        def eq(self, key, val):
            self.calls.append((key, val))
            return self

        def execute(self):
            # Expect two calls: first for user_id, then for word
            deleted.append(tuple(v for _, v in self.calls))
            return {"status_code": 200}

        def __init__(self):
            self.calls = []

    class MockFrom:
        def delete(self):
            return MockDeleteQuery()

    monkeypatch.setattr(known_words.supabase, "from_", lambda table: MockFrom())

    # Run test
    known_words.delete_known_word("00000000-0000-0000-0000-000000000000", "pomme")

    # Assert expected delete arguments
    assert deleted[0] == ("00000000-0000-0000-0000-000000000000", "pomme")
