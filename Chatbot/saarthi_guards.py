from guardrails import Guard
from guardrails.hub import ToxicLanguage
from guardrails.errors import ValidationError
from guardrails.hub import RestrictToTopic
from guardrails import Guard


# Setup Guard
topic_guard = Guard().use(
    RestrictToTopic(
        valid_topics=["apartments", "boston", "apartment hunt", "food", "tourist","rent"],
        invalid_topics=["politics", "nuclear weapons","Adult movies", "Any political leader", "finance"],
        disable_classifier=True,
        disable_llm=False,
        on_fail="exception"
    )
)

guard = Guard().use(
    ToxicLanguage(threshold=0.7, validation_method="sentence", on_fail="exception"
))