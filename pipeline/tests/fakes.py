import json


class FakeBedrock:
    """Minimal bedrock-runtime stand-in. `replies` is a list of text bodies returned in order."""

    def __init__(self, replies, reasoning_first=True):
        self.replies, self.calls, self.reasoning_first = list(replies), [], reasoning_first

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        text = self.replies[min(len(self.calls) - 1, len(self.replies) - 1)]
        content = [{"text": text}]
        if self.reasoning_first:
            content.insert(0, {"reasoningContent": {"reasoningText": {"text": "thinking..."}}})
        return {"output": {"message": {"role": "assistant", "content": content}},
                "usage": {"inputTokens": 100, "outputTokens": 50, "totalTokens": 150}}


GOOD = {"what_is_bought": "Cloud software licences", "product_category": "software", "is_software": True,
        "is_renewal": True, "summary": "Renewal of licences.", "keywords": ["software", "license"], "confidence": 0.9}
GOOD_JSON = json.dumps(GOOD)
