"""L19 on Claude: the same three ways to answer Mona Store policy questions, with Haiku 5.5.
  prompt : persona only (watch it guess)   stuff : whole policy in the system prompt   rag : top-3 chunks only
On Claude the "whole policy" option gets better with prompt caching (L11) once the policy is long enough to cache,
and fine-tuning isn't the tool for facts at all: the only Claude fine-tuning offered was Claude 3 Haiku on Amazon Bedrock,
and that model has reached end of life. Facts go in the context (stuffed or retrieved); behaviour goes in the prompt + examples.
Needs ANTHROPIC_API_KEY.   python claude_choose.py
"""
import re
import anthropic
from choose import POLICY, QS, PERSONA, retrieve, grade

client = anthropic.Anthropic()
MODEL = "claude-haiku-5-5"

def ask(mode, q, gold, policy=POLICY):
    system = PERSONA
    if mode == "stuff": system += "\nAnswer ONLY from the store policy below. If it is not there, say you are not sure.\n\nSTORE POLICY:\n" + "\n".join(policy)
    if mode == "rag": system += "\nAnswer ONLY from the policy excerpts below. If it is not there, say you are not sure.\n\nPOLICY EXCERPTS:\n" + "\n".join(policy[i] for i in retrieve(q, policy))
    r = client.messages.create(model=MODEL, max_tokens=200, system=system, thinking={"type": "disabled"}, messages=[{"role": "user", "content": q}])
    text = "".join(b.text for b in r.content if b.type == "text")
    return grade(text, gold), r.usage.input_tokens, text

if __name__ == "__main__":
    for mode in ["prompt", "stuff", "rag"]:
        res = [ask(mode, q, g) for q, g in QS]
        print(f"{mode:6} correct {sum(r[0] == 'correct' for r in res):2}/12 | not sure {sum(r[0] == 'dont_know' for r in res)} | "
              f"avg input tokens {sum(r[1] for r in res) / len(res):.0f}")
    NEW = POLICY[:]; NEW[2] = NEW[2].replace("45", "60")
    print("after the price change (rag):", ask("rag", QS[2][0], "(60|٦٠|ستين)", NEW)[::2])
