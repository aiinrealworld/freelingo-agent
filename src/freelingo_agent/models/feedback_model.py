from typing import List
from pydantic import BaseModel, Field


class Mistake(BaseModel):
    what_you_said: str = Field(description="The exact phrase or sentence the learner said that has an issue")
    simple_explanation: str = Field(description="Simple English explanation of what went wrong")
    better_way: str = Field(description="How to say it better, with English translation in parentheses")


class FeedbackAgentOutput(BaseModel):
    strengths: List[str] = Field(description="What the learner did well in the conversation", max_length=3)
    mistakes: List[Mistake] = Field(description="Key mistakes to focus on, maximum 3", max_length=3)
    conversation_examples: List[str] = Field(description="Examples of how to build conversation using existing vocabulary", max_length=2)


