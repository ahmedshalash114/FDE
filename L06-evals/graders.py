import json, re
from client import client, MODEL
from mona import POLICY

def code_grade(reply):               # fast, free, deterministic checks
    return {
        "short":    len(re.findall(r"[.!؟?]", reply)) <= 2 and len(reply) <= 220,
        "no_md":    not re.search(r"\*\*|^#|^\s*[-•]", reply, re.M),
        "no_date":  not re.search(r"غد[اًا]?|بكر[ةه]|tomorrow|النهارد[هة]", reply),
    }

def model_grade(msg, reply):         # an LLM reads the reply against the policy
    out = client.messages.create(
        model=MODEL, max_tokens=200, thinking={"type": "disabled"},
        messages=[{"role": "user", "content": f"""You are grading a customer-support reply.
<policy>
{POLICY}
</policy>
<customer>{msg}</customer>
<reply>{reply}</reply>
Does the reply follow the policy without inventing facts (days, dates, amounts, promises)?
Answer as JSON: {{"reason": "<one sentence>", "score": <1-10>}}"""},
            {"role": "assistant", "content": "```json"}],
        stop_sequences=["```"])
    return json.loads(out.content[0].text)
