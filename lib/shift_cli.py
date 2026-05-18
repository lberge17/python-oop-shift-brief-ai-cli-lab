from ai_client import OllamaChatClient
from brief_builder import HandoffBriefBuilder


class ShiftBriefCLI:
    """Command-line workflow for generating and revising shift handoff briefs."""

    def __init__(self, ai_client, brief_builder=None):
        self.ai_client = ai_client
        self.brief_builder = brief_builder or HandoffBriefBuilder()
        self.running = True

    def display_welcome(self):
        """Print the welcome message and command guidance."""
        print("\nShift Handoff Brief CLI")
        print("Create and revise AI-assisted shift handoff briefs.")
        print(self.command_help())

    def command_help(self):
        """Return command guidance as a string."""
        return (
            "\nCommands:\n"
            "- brief <shift notes>     Create a new handoff brief.\n"
            "- revise <feedback>      Revise the previous brief using feedback.\n"
            "- history                Show the current conversation message count.\n"
            "- reset                  Clear conversation history.\n"
            "- help                   Show this command list.\n"
            "- exit or quit           Stop the program.\n"
        )

    def handle_command(self, raw_input):
        """Route a user command."""
        if not isinstance(raw_input, str) or not raw_input.strip():
            return "Input Error: Enter a command. Type 'help' for options."

        cleaned_input = raw_input.strip()
        command, separator, payload = cleaned_input.partition(" ")
        command = command.lower()
        payload = payload.strip()

        try:
            if command in ["exit", "quit"]:
                self.running = False
                return "Goodbye!"

            if command == "help":
                return self.command_help()

            if command == "reset":
                self.ai_client.reset()
                return "Conversation history reset."

            if command == "history":
                return f"Conversation messages: {self.ai_client.message_count()}"

            if command == "brief":
                if not payload:
                    return "Input Error: Shift notes cannot be empty."
                return self.brief_builder.create_brief(self.ai_client, payload)

            if command == "revise":
                if not payload:
                    return "Input Error: Revision feedback cannot be empty."
                return self.brief_builder.revise_brief(self.ai_client, payload)

            return "Input Error: Unknown command. Type 'help' for options."

        except ValueError as error:
            return f"Input Error: {error}"

        except RuntimeError as error:
            return f"Service Error: {error}"

    def run(self):
        """Run the CLI input loop."""
        self.display_welcome()

        while self.running:
            try:
                raw_input = input("> ")
            except EOFError:
                self.running = False
                break

            result = self.handle_command(raw_input)

            if result:
                print(result)


def main():
    client = OllamaChatClient(model_name="llama3.2")
    app = ShiftBriefCLI(client)
    app.run()


if __name__ == "__main__":
    main()