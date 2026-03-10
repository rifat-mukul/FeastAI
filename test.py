from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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"
)


questions = [
  "Gulshan",
  "Banani",
  "Uttara",
  "Dhanmondi",
  "Mirpur",
  "Mohammadpur",
  "Motijheel",
  "Farmgate",
  "New Market",
  "Jatrabari"
]

for question in questions:

    custom_prompt = f"Answer the following question one line: which resturent in {question} area serverd best Indian? Provide only the name of the restaurant. just maximum 5 resturent names. with rating is greater than 4.0 out of 5.0 ."
    completion = client.chat.completions.create(
        model="xiaomi/mimo-v2-flash:free",
        messages=[
        {
            "role": "user",
            "content": custom_prompt
        }
        ]
    )
    print(f"Q: {question}")
    print(f"A: {completion.choices[0].message.content}")
    print()