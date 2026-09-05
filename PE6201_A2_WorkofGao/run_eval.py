#!/usr/bin/env python3
"""
PE6201 · A2 scaffold — ENTRY POINT
====================================================================
    python3 run_eval.py              run every SCRIPTED case
    python3 run_eval.py REF-5602     run one case, showing every turn
    python3 run_eval.py --all        run every case in the work queue
    python3 run_eval.py --prompt     print what the model is told, and stop

THIS IS WHAT A MARKER RUNS. Clone, `python3 run_eval.py`, numbers come
back. No key, no network, no arguments. If that does not work on a
clean machine, D5(a) has failed and Technical Execution is capped.

Test it the way a marker will: clone your own repository into a fresh
folder and run it there. "Works on my laptop" has caught out every
cohort so far.
====================================================================
"""
import json
import sys

import config
from backends import available_scripted_case_ids
from harness import load_cases, load_key, report, run_set


def main(argv):
    print()
    print(config.summary())
    print("data: %s" % config.data_root())

    raw = argv[1:]
    prompt_version = config.PROMPT_VERSION
    cleaned = []
    index = 0
    while index < len(raw):
        item = raw[index]
        if item.startswith("--prompt-version="):
            prompt_version = item.split("=", 1)[1]
        elif item == "--prompt-version":
            if index + 1 >= len(raw):
                raise SystemExit("--prompt-version needs v1 or v2")
            index += 1
            prompt_version = raw[index]
        else:
            cleaned.append(item)
        index += 1
    if prompt_version not in {"v1", "v2"}:
        raise SystemExit("--prompt-version must be v1 or v2")

    args = [a for a in cleaned if not a.startswith("-")]
    flags = {a for a in cleaned if a.startswith("-")}

    # ---- show exactly what the model is told, then stop ----------------
    if "--prompt" in flags:
        import prompt
        print()
        prompt.audit(version=prompt_version)
        return 0

    # ---- one named case, verbose --------------------------------------
    if args:
        case_id = args[0]
        print()
        print("-" * 68)
        print("  %s - every turn" % case_id)
        print("-" * 68)
        results, queue = run_set([case_id], verbose=True,
                                 prompt_version=prompt_version)
        if not results:
            return 1
        print()
        print("  DECISION RECORD")
        print(json.dumps(results[0]["record"], indent=2)[:2000])
        print()
        print("  CODE CHECK   %s" % ("PASS" if results[0]["passed"] else "FAIL"))
        for f in results[0]["fails"]:
            print("      %s" % f)
        print()
        print("  JUDGEMENT CHECK - not automated. Someone reads the reason")
        print("  and rules on each item:")
        for item in queue[0]["must_record"]:
            print("      [ ] %s" % item)
        print()
        return 0 if results[0]["passed"] else 1

    # ---- the set ------------------------------------------------------
    if "--all" in flags:
        cases = load_cases()
        print("\n  Running EVERY case in the work queue (%d)." % len(cases))
        print("  Every labelled Problem B referral has a deterministic")
        print("  fixture-derived path in the offline battery.")
    else:
        # Default: only what is scripted, so a clean clone always works.
        key = load_key()
        supported = set(available_scripted_case_ids())
        cases = [c for c in load_cases() if c in supported and c in key]
        print("\n  Running the full %d-case deterministic Problem B battery."
              % len(cases))
        print("  This is D5(a) reproducibility and guardrail integration, not")
        print("  a live-model quality claim. Use D5(b) for measured live runs.")

    if not cases:
        print("\n  Nothing to run for Problem %s." % config.PROBLEM)
        print("  config.PROBLEM is %r - is that the problem you chose?"
              % config.PROBLEM)
        return 1

    results, queue = run_set(cases, prompt_version=prompt_version)
    summary = report(results)

    with open("results.json", "w", encoding="utf-8") as fh:
        json.dump({"config": config.summary(), "prompt_version": prompt_version,
                   "summary": summary,
                   "results": [{k: v for k, v in r.items()} for r in results],
                   "judgement_queue": queue}, fh, indent=2, default=str)
    print("  Wrote results.json - commit it. Your result tables come from")
    print("  here, and a marker reads it alongside your report.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
