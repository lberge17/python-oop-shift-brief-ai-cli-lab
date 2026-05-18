import ollama


class OllamaChatClient:
    """Generic reusable client for interacting with a local Ollama chat model."""

    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        self.history = []

    def _extract_assistant_content(self, response):
        """
        Extract assistant content from either:
        - a dict-like response: response["message"]["content"]
        - an object response: response.message.content
        """
        assistant_message = None

        # Dict-style response
        if isinstance(response, dict):
            assistant_message = response.get("message")

        # Object-style response from Ollama ChatResponse
        elif hasattr(response, "message"):
            assistant_message = response.message

        if assistant_message is None:
            raise ValueError("AI response is missing message data.")

        # Dict-style message
        if isinstance(assistant_message, dict):
            content = assistant_message.get("content")

        # Object-style message
        elif hasattr(assistant_message, "content"):
            content = assistant_message.content

        else:
            content = None

        if not isinstance(content, str) or not content.strip():
            raise ValueError("AI response did not include usable content.")

        return content.strip()

    def send(self, prompt):
        """Send a prompt to the AI service and return assistant response text."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        user_message = {
            "role": "user",
            "content": prompt.strip(),
        }

        self.history.append(user_message)

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=self.history,
            )

            cleaned_content = self._extract_assistant_content(response)

            self.history.append(
                {
                    "role": "assistant",
                    "content": cleaned_content,
                }
            )

            return cleaned_content

        except Exception as error:
            if self.history and self.history[-1] is user_message:
                self.history.pop()

            raise RuntimeError(f"AI service request failed: {error}")

    def reset(self):
        """Clear the conversation history."""
        self.history = []

    def message_count(self):
        """Return the number of stored messages."""
        return len(self.history)

    def get_transcript(self):
        """Return a copy of the conversation history."""
        return [message.copy() for message in self.history]