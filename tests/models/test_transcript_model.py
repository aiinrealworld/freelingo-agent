"""
Test the Transcript model validation and behavior.
"""
import pytest
from freelingo_agent.models.transcript_model import Transcript, TranscriptTurn, AiTurn, UserTurn
from freelingo_agent.models.dialogue_model import Rationale, AiReply, VocabularyChallenge, RuleChecks


class TestTranscriptModel:
    """Test the Transcript model validation and behavior."""

    @pytest.fixture
    def sample_rationale(self):
        """Create a sample rationale for testing."""
        return Rationale(
            reasoning_summary="Test reasoning",
            vocabulary_challenge=VocabularyChallenge(
                description="Test challenge",
                tags=["short_vocab"]
            ),
            rule_checks=RuleChecks(
                used_only_allowed_vocabulary=True,
                one_sentence=True,
                max_eight_words=True,
                no_corrections_or_translations=True
            )
        )

    @pytest.fixture
    def sample_ai_reply(self):
        """Create a sample AI reply for testing."""
        return AiReply(
            text="Bonjour! Comment allez-vous?",
            word_count=4
        )

    @pytest.fixture
    def sample_ai_turn(self, sample_rationale, sample_ai_reply):
        """Create a sample AI turn for testing."""
        return AiTurn(
            rationale=sample_rationale,
            ai_reply=sample_ai_reply
        )

    @pytest.fixture
    def sample_user_turn(self):
        """Create a sample user turn for testing."""
        return UserTurn(text="Bonjour")

    @pytest.fixture
    def sample_transcript_turn(self, sample_ai_turn, sample_user_turn):
        """Create a sample transcript turn for testing."""
        return TranscriptTurn(
            ai_turn=sample_ai_turn,
            user_turn=sample_user_turn
        )

    def test_empty_transcript_creation(self):
        """Test that an empty transcript can be created and validated."""
        # Test with empty transcript list
        empty_transcript = Transcript(transcript=[])
        
        # Verify the transcript is created successfully
        assert empty_transcript is not None
        assert isinstance(empty_transcript, Transcript)
        assert empty_transcript.transcript == []
        assert len(empty_transcript.transcript) == 0

    def test_transcript_with_single_turn(self, sample_transcript_turn):
        """Test transcript creation with a single turn."""
        transcript = Transcript(transcript=[sample_transcript_turn])
        
        # Verify the transcript is created successfully
        assert transcript is not None
        assert isinstance(transcript, Transcript)
        assert len(transcript.transcript) == 1
        assert transcript.transcript[0] == sample_transcript_turn

    def test_transcript_with_multiple_turns(self, sample_transcript_turn):
        """Test transcript creation with multiple turns."""
        # Create multiple turns
        turn1 = sample_transcript_turn
        turn2 = TranscriptTurn(
            ai_turn=AiTurn(
                rationale=Rationale(
                    reasoning_summary="Second turn reasoning",
                    vocabulary_challenge=VocabularyChallenge(
                        description="Second challenge",
                        tags=["no_verbs"]
                    ),
                    rule_checks=RuleChecks(
                        used_only_allowed_vocabulary=True,
                        one_sentence=True,
                        max_eight_words=True,
                        no_corrections_or_translations=True
                    )
                ),
                ai_reply=AiReply(
                    text="Très bien, merci!",
                    word_count=3
                )
            ),
            user_turn=UserTurn(text="Très bien")
        )
        
        transcript = Transcript(transcript=[turn1, turn2])
        
        # Verify the transcript is created successfully
        assert transcript is not None
        assert isinstance(transcript, Transcript)
        assert len(transcript.transcript) == 2
        assert transcript.transcript[0] == turn1
        assert transcript.transcript[1] == turn2

    def test_transcript_model_dump(self, sample_transcript_turn):
        """Test that transcript can be serialized to dict."""
        transcript = Transcript(transcript=[sample_transcript_turn])
        
        # Test model_dump
        transcript_dict = transcript.model_dump()
        
        # Verify the dict structure
        assert isinstance(transcript_dict, dict)
        assert "transcript" in transcript_dict
        assert isinstance(transcript_dict["transcript"], list)
        assert len(transcript_dict["transcript"]) == 1

    def test_transcript_model_validation(self):
        """Test transcript model validation with invalid data."""
        # Test with None transcript (should fail)
        with pytest.raises(Exception):
            Transcript(transcript=None)
        
        # Test with invalid transcript type (should fail)
        with pytest.raises(Exception):
            Transcript(transcript="invalid")

    def test_transcript_turn_validation(self, sample_ai_turn, sample_user_turn):
        """Test transcript turn validation."""
        # Valid turn
        valid_turn = TranscriptTurn(
            ai_turn=sample_ai_turn,
            user_turn=sample_user_turn
        )
        assert valid_turn is not None
        assert valid_turn.ai_turn == sample_ai_turn
        assert valid_turn.user_turn == sample_user_turn

        # Test with None values (should fail)
        with pytest.raises(Exception):
            TranscriptTurn(ai_turn=None, user_turn=sample_user_turn)
        
        with pytest.raises(Exception):
            TranscriptTurn(ai_turn=sample_ai_turn, user_turn=None)

    def test_user_turn_validation(self):
        """Test user turn validation."""
        # Valid user turn
        valid_turn = UserTurn(text="Bonjour")
        assert valid_turn is not None
        assert valid_turn.text == "Bonjour"

        # Test with empty text
        empty_turn = UserTurn(text="")
        assert empty_turn is not None
        assert empty_turn.text == ""

        # Test with None text (should fail)
        with pytest.raises(Exception):
            UserTurn(text=None)

    def test_ai_turn_validation(self, sample_rationale, sample_ai_reply):
        """Test AI turn validation."""
        # Valid AI turn
        valid_turn = AiTurn(
            rationale=sample_rationale,
            ai_reply=sample_ai_reply
        )
        assert valid_turn is not None
        assert valid_turn.rationale == sample_rationale
        assert valid_turn.ai_reply == sample_ai_reply

        # Test with None values (should fail)
        with pytest.raises(Exception):
            AiTurn(rationale=None, ai_reply=sample_ai_reply)
        
        with pytest.raises(Exception):
            AiTurn(rationale=sample_rationale, ai_reply=None)

    def test_transcript_immutability(self, sample_transcript_turn):
        """Test that transcript data is properly structured and accessible."""
        transcript = Transcript(transcript=[sample_transcript_turn])
        
        # Test accessing transcript data
        assert len(transcript.transcript) == 1
        turn = transcript.transcript[0]
        
        # Test accessing turn data
        assert turn.ai_turn is not None
        assert turn.user_turn is not None
        assert turn.user_turn.text == "Bonjour"
        assert turn.ai_turn.ai_reply.text == "Bonjour! Comment allez-vous?"

    def test_transcript_edge_cases(self):
        """Test transcript with edge cases."""
        # Test with very long text
        long_text = "A" * 1000
        long_turn = TranscriptTurn(
            ai_turn=AiTurn(
                rationale=Rationale(
                    reasoning_summary="Long text test",
                    vocabulary_challenge=VocabularyChallenge(
                        description="Long text challenge",
                        tags=["short_vocab"]
                    ),
                    rule_checks=RuleChecks(
                        used_only_allowed_vocabulary=True,
                        one_sentence=True,
                        max_eight_words=True,
                        no_corrections_or_translations=True
                    )
                ),
                ai_reply=AiReply(
                    text=long_text,
                    word_count=1000
                )
            ),
            user_turn=UserTurn(text=long_text)
        )
        
        transcript = Transcript(transcript=[long_turn])
        assert transcript is not None
        assert len(transcript.transcript) == 1
        assert transcript.transcript[0].user_turn.text == long_text

    def test_transcript_with_special_characters(self):
        """Test transcript with special characters and unicode."""
        special_text = "Bonjour! Ça va? 🎉 Émojis et accents: café, naïve, résumé"
        
        special_turn = TranscriptTurn(
            ai_turn=AiTurn(
                rationale=Rationale(
                    reasoning_summary="Special characters test",
                    vocabulary_challenge=VocabularyChallenge(
                        description="Special characters challenge",
                        tags=["short_vocab"]
                    ),
                    rule_checks=RuleChecks(
                        used_only_allowed_vocabulary=True,
                        one_sentence=True,
                        max_eight_words=True,
                        no_corrections_or_translations=True
                    )
                ),
                ai_reply=AiReply(
                    text=special_text,
                    word_count=12
                )
            ),
            user_turn=UserTurn(text=special_text)
        )
        
        transcript = Transcript(transcript=[special_turn])
        assert transcript is not None
        assert len(transcript.transcript) == 1
        assert transcript.transcript[0].user_turn.text == special_text
        assert "🎉" in transcript.transcript[0].user_turn.text
        assert "café" in transcript.transcript[0].user_turn.text
