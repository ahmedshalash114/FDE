import json
from mona import V1, V2, reply
from graders import code_grade, model_grade

cases = json.load(open("dataset.json"))
for name, system in [("V1", V1), ("V2", V2)]:
    passed, scores = 0, []
    for msg in cases:
        r = reply(msg, system)
        c = code_grade(r); m = model_grade(msg, r)
        passed += all(c.values()); scores.append(m["score"])
        print(f"{name} | {msg[:30]:30s} | code {''.join('✓' if v else '✗' for v in c.values())} | model {m['score']:>4} | {r[:60]!r}")
    print(f"== {name}: code checks passed {passed}/{len(cases)} · model score avg {sum(scores)/len(scores):.1f}/10\n")
