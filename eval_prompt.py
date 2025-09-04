from openai import OpenAI
import re

# Sets prompt for attribute exploration
def set_prompt(objects, frames, examples, implications="", premise=[], conclusion=[]):
    if len(premise) == 0 and len(conclusion) == 0:
        implications = implications.split('=>')
        premise = [line.strip() for line in implications[0].split(',')]
        conclusion = [line.strip() for line in implications[1].split(',')]
    else:
        premise = list(premise)
        conclusion = list(conclusion)

    prompt = ""
    prompt += "We are analyzing word meanings for multilingual verbs using the framework of Formal Concept Analysis (FCA).\n"
    prompt += "\n"
    prompt += "Word Meaning List:\n"

    if examples[0] != " ":
        for i in range(len(frames)):
            prompt += f'{i}. "{frames[i]}" (e.g. {examples[i]})\n'

    else:
        for i in range(len(frames)):
            prompt += f'{i}. "{frames[i]}"\n'

    prompt += "\n"
    prompt += "Already Checked Verbs: \n"
    objects = ', '.join(objects)
    prompt += f'{objects}\n'
    prompt += "\n"
    prompt += "Hypothesis to Test:\n"

    premise_prompt = ' and '.join(f'"{word}"' for word in premise)
    conclusion_prompt = ' and '.join(f'"{word}"' for word in conclusion)
    prompt += f'Every verb that conveys the meaning(s) {premise_prompt} also conveys the meaning(s) {conclusion_prompt}?\n'
    # Every verb in any language that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"
    # Every verb in any language other than English that conveys the meaning "{premise_prompt}" also conveys the meanings "{conclusion_prompt}"

    prompt += f"""
Instructions:
1. Search for all verbs that include the meaning(s) {premise_prompt}.
2. Ignore any verbs already in the checked list.
3. For each remaining verb:
    - Check whether it also conveys the meanings {conclusion_prompt}
"""
    prompt += "4. Return the result as a valid JSON object using the following logic : \n\n"
    prompt += f"If the hypothesis holds (i.e., all relevant verbs have {conclusion_prompt})"
    prompt += """
{
"output": "YES"
}
"""
    conclusion_prompt_or = ' or '.join(f'"{word}"' for word in conclusion)
    prompt += f"\nOtherwise, return a verb that has all of the following meaning(s): {premise_prompt}, but does not have at least one of the following meaning(s): {conclusion_prompt_or}"
    prompt += """
{
"output": "NO",
"verb": "<Language of the verb> : <name of the verb>",
"meaning": ["""

    for premise in premise:
        prompt += f'"{premise}",'
    prompt += f'"<other meanings from the Word Meaning List, if any apply>"],\n'
    prompt += '''"language": "<Give the language of the verb>"
"explanation": "<Give a brief explanation of your result, and also describe the general meaning of the verb and also give from which language the verb is taken>"
"example": "<Explain your results using some examples for all the meanings, in the same language of the verb>">}"
'''
    prompt += """

Constraints:
- Ensure the returned verb is not in the already checked list.
- Use all the meanings from the list that applies to this word.
- Do not include meanings not on the list.

Respond with only a valid JSON object. Do not include markdown syntax (like triple backticks) or any explanatory text."""

    return prompt


# Sets prompt for object exploration
def set_prompt_object(objects, frames, premise_verbs, conclusion_verbs):
    prompt = ""
    prompt += "We are analyzing word meanings for multilingual verbs using the framework of Formal Concept Analysis (FCA), with a focus on object exploration.\n\n"

    prompt += "Word Meanings List:\n"
    for i in range(len(frames)):
        prompt += f'{i + 1}. "{frames[i]}"\n'

    prompt += "\nVerbs List:\n"
    prompt += ', '.join(objects) + "\n\n"

    # Hypothesis
    premise_list = ', '.join(f'"{verb}"' for verb in premise_verbs)
    conclusion_list = ', '.join(f'"{verb}"' for verb in conclusion_verbs)

    prompt += "Hypothesis to Test:\n"
    if len(premise_list) != 0:
        prompt += f'Every verb that shares all meanings of the verbs {premise_list} also shares all meanings of {conclusion_list}?\n\n'
    else:
        prompt += f'Every verb that shares all meanings of all the verbs in the list also shares all meanings of {conclusion_list}?\n\n'
        # f"Every verb that exhibits all the semantic features (meanings) common to verbs {premise_list}  must also exhibit all the semantic features shared by verbs {conclusion_list}.""""

    prompt += "Instructions:\n"
    prompt += f"1. Consider the verbs: {premise_list}.\n"
    prompt += f"2. Think if there is a meaning outside of the Word Meanings List that is shared by {premise_list}.\n"
    prompt += f"""3. If there is one, determine whether all of the following verbs share it:
"""
    for conclusion in conclusion_verbs:
        prompt += f'-"{conclusion}"\n'
    prompt += """
4. If not all those verbs share this meaning, return:
{
"output": "NO",
"meaning": "<the meaning>",
"verbs": ["""

    for premise in premise_verbs:
        prompt += f'"{premise}",'
    prompt += f'"<other verbs from the Verbs List the have this meaning>"],\n'

    prompt += f'"explanation": "<Brief explanation of why the meaning does not apply to all verbs>"'
    prompt += "\n"
    prompt += f'"example": "<Example sentences demonstrating the meaning>"'
    prompt += "}\n\n"
    prompt += f"5. If no such meaning exists — i.e., every proposed meaning that applies to {premise_list} also applies to both {conclusion_list} — return:"
    prompt += """
{
"output": "YES"
}
"""

    prompt += """
Constraints:
- Use only the verbs listed above.
- Do not reuse meanings from the Word Meanings List list.
- Do not include verbs not on the list.
- Do not propose meanings that are similar to the checked meanings; all meanings must be distinct and linguistically valid.

Respond with only a valid JSON object. Do not include markdown syntax (like triple backticks) or any explanatory text."""

    return prompt

def evaluate_prompt(prompt):
    try:
        client = OpenAI(base_url="https://llm.scads.ai/v1", api_key="sk-SsE9pY-GlGryX0NH3driHw")
        models = []
        for model in client.models.list().data:
            models.append(model.id)
        # model_name = "meta-llama/Llama-4-Scout-17B-16E-Instruct"
        model_name = "meta-llama/Llama-3.3-70B-Instruct"
        response = client.chat.completions.create(messages=prompt, model=model_name)
        response_content = response.choices[0].message.content
        return response_content
    except Exception as e:
        return "CLIENT_ERROR"
        print(e)

