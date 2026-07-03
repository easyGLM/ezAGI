# streaming interface: chunk assembly, token forwarding, usage accounting
import asyncio


def test_mock_stream_assembles(mock_chatter):
    async def collect():
        pieces = []
        async for chunk in mock_chatter.generate_response_stream("hello"):
            pieces.append(chunk)
        return "".join(pieces).strip()

    assert asyncio.run(collect()) == mock_chatter.response
    assert mock_chatter.last_usage["output_tokens"] >= 1


def test_generate_response_with_tokens(mock_chatter):
    tokens = []
    full = mock_chatter.generate_response_with_tokens("hello", tokens.append)
    assert "".join(tokens).strip() == full == mock_chatter.response


def test_base_chatter_with_tokens_helper(mock_chatter):
    # the real BaseChatter helper drives any generate_response_stream
    from webmind.chatter import BaseChatter

    class Streamy(BaseChatter):
        provider = "mock"

        async def generate_response_stream(self, knowledge):
            for word in ("augmented", "generative", "intelligence"):
                yield word + " "

    tokens = []
    result = Streamy().generate_response_with_tokens("x", tokens.append)
    assert result == "augmented generative intelligence"
    assert len(tokens) == 3
