import openai
from audio.utils import extract_json_block


# Function to generate summary from transcript text
def generate_summary(transcript_text):
    system_prompt = """
You are an expert business analyst. You will be given a raw transcript from a client-agency meeting.

Your task is to extract a comprehensive and structured summary in JSON format using the schema below.

Please follow these guidelines strictly:
- Be concise but informative. Ensure each bullet is standalone and easy to understand.
- Use consistent formatting (no sentence fragments; start with verbs where applicable).
- For To-Do items, include responsible parties and estimated deadlines if mentioned or inferable.
- Include actionable insights and KPIs if discussed.
- Maintain professional tone. Avoid repetition.

Return **only valid JSON** with no extra text, markdown, or explanation.

Schema:
{
  "mom": ["<Key discussion points and agreements>", "..."],
  "todo_list": ["<Actionable task with responsible person and timeframe, if known>", "..."],
  "action_plan": {
    "decision_made": ["<Key decisions taken>", "..."],
    "key_services_to_promote": ["<Service list>", "..."],
    "target_geography": ["<Location list>", "..."],
    "budget_and_timeline": ["<Budget, timeline details>", "..."],
    "lead_management_strategy": ["<Lead handling strategy>", "..."],
    "next_steps_and_ownership": ["<Task and responsible person>", "..."]
  }
}
"""
    # Call OpenAI API to generate summary
    chat_response = openai.ChatCompletion.create(
        model="gpt-4.1-2025-04-14",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript_text},
        ],
        temperature=0.3,  # Lower temperature for more deterministic output
    )

    return extract_json_block(chat_response.choices[0].message.content)