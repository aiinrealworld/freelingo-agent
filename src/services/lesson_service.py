from db.known_words import get_known_words
from services.llm_service import generate_lesson_conversation

def start_lesson(user_id: str) -> str:
    known_words = get_known_words(user_id)

    if not known_words:
        return "Looks like you haven't added any known words yet."

    return generate_lesson_conversation(known_words)
