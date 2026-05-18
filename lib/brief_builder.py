class HandoffBriefBuilder:
    """Builds prompts and verifies output for shift handoff briefs."""

    REQUIRED_SECTIONS = (
        "Shift Summary:",
        "Open Issues:",
        "Action Items:",
        "Follow-Up Questions:",
        "Risk Notes:",
    )

    def _clean_required_text(self, value, label):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} cannot be empty.")

        return value.strip()

    def build_brief_prompt(self, notes):
        """Build a prompt for creating a new shift handoff brief."""
        cleaned_notes = self._clean_required_text(notes, "Shift notes")
        section_list = "\n".join(self.REQUIRED_SECTIONS)

        return f"""
You are helping a store manager prepare a shift handoff brief from messy shift notes.

Use only the information provided in the notes. Do not invent unsupported details, causes, names, incidents, safety conditions, or next steps. If a detail is not provided, write "Unknown" instead of making it up.

Create a concise handoff brief using exactly these section labels:
{section_list}

Guidance:
- Shift Summary should briefly summarize what happened.
- Open Issues should list unresolved problems.
- Action Items should list specific follow-up tasks.
- Follow-Up Questions should identify missing information a manager may need.
- Risk Notes should explain operational, safety, staffing, or customer-experience risks if they are supported by the notes.

Shift Notes:
{cleaned_notes}
""".strip()

    def build_revision_prompt(self, feedback):
        """Build a prompt for revising the previous handoff brief."""
        cleaned_feedback = self._clean_required_text(feedback, "Revision feedback")
        section_list = "\n".join(self.REQUIRED_SECTIONS)

        return f"""
Revise the previous shift handoff brief in this conversation using the manager feedback below.

Keep the revised brief concise and use exactly these section labels:
{section_list}

Do not invent unsupported details. If the feedback asks for information that was not provided, write "Unknown" or note that the detail needs follow-up.

Manager Feedback:
{cleaned_feedback}
""".strip()

    def is_usable_brief(self, response_text):
        """Return True only when the response includes every required section."""
        if not isinstance(response_text, str) or not response_text.strip():
            return False

        return all(section in response_text for section in self.REQUIRED_SECTIONS)

    def format_brief(self, response_text):
        """Return a user-facing formatted handoff brief."""
        return f"\nShift Handoff Brief\n{response_text.strip()}"

    def create_brief(self, ai_client, notes):
        """Create a new shift handoff brief."""
        prompt = self.build_brief_prompt(notes)
        response = ai_client.send(prompt)

        if not self.is_usable_brief(response):
            raise RuntimeError("AI response did not include required sections.")

        return self.format_brief(response)

    def revise_brief(self, ai_client, feedback):
        """Revise the previous shift handoff brief."""
        prompt = self.build_revision_prompt(feedback)
        response = ai_client.send(prompt)

        if not self.is_usable_brief(response):
            raise RuntimeError("AI response did not include required sections.")

        return f"\nRevised Shift Handoff Brief\n{response.strip()}"