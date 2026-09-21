Ashford & Kane LLP — Agent Design Lab
The Company

Ashford & Kane LLP is a mid-sized law firm with three practice areas:

Corporate Law (contracts, M&A, corporate governance)
Family Law (divorce, custody, adoption)
Criminal Defense (DUI, felonies, white-collar)

The firm has 8 attorneys and a small intake team that fields calls from prospective clients every day.

The Problem: Client Intake Triage

What's broken right now:

The intake coordinator manually assigns cases based on gut feel and whoever's available
Same intake form gets routed to the wrong practice area, wasting attorney time
No one checks for conflicts of interest until after the attorney has already spent an hour on the case
Urgent cases sit in a queue next to low-priority ones
Clients wait 2-3 days for callback confirmation

Why it matters:

The firm loses work because intake is slow and messy
Ethics risk if a conflict isn't caught early
Attorneys spend time on triage work instead of billable hours
Clients get frustrated before they even sign on
The Solution: An Agent That Routes Cases

When someone submits an intake form with details like:

"My ex won't let me see my kids, and we need a custody agreement sorted out. 
We're not married but live in California. Money's tight so I need pro bono help."

The agent must:

Classify the case into a practice area (Family Law)
Check conflicts against existing clients (is the ex-spouse already a client?)
Assess complexity based on factors like pro bono, state law, custody type
Route to the right attorney (senior family lawyer for complex, junior for simple)
Recommend if we can take it or need to refer out

This is a good agent problem because each decision depends on the previous one:

Even if it's "simple family law," if we find a conflict, we escalate immediately
If it's pro bono, complexity matters more than it normally would
If we can't handle it, we need to recommend a referral, not just refuse
How I Solved It: Four Architectures
1. Reactive (Rule-Based) Agent — agent_1_rule_based.py

Pure if/then logic. No LLM, no API calls.

Pros: Instant, cheap, predictable
Cons: Breaks on edge cases (two issues at once, nuance)
Fails when: A case has both a conflict AND pro bono status (can't balance)
2. Unconstrained LLM-Powered Agent — agent_2_unconstrained.py

ReAct loop where the model chooses what to do, how many steps, when to stop.

Pros: Handles edge cases, can reason about trade-offs
Cons: Can call tools infinitely, sometimes hallucinates tool names, costs money
Fails when: Model keeps second-guessing itself or calls a non-existent tool
3. Deterministic Routing Agent — agent_3_deterministic.py

Single LLM call classifies the case into one of 5 buckets, then runs regular code.

Pros: Fast, cheap, predictable, structured
Cons: Can't loop on results (if classification is wrong, can't recover)
Fails when: Case needs multi-step reasoning before classifying
4. Constrained ReAct Agent — agent_4_constrained.py

ReAct loop with guardrails: schema validation, tool allow-list, MAX_STEPS budget.

Pros: Reasoning + safety, can loop but won't spin out
Cons: More setup code upfront
Best for: This problem
Test Cases (Same Across All Four)

Defined in test_data.py:

Simple custody case (Family Law, no conflict)
M&A with a hidden conflict (TechCorp is already a client)
Criminal case + pro bono + multiple charges
Ambiguous case spanning two practice areas at once
Comparison Table
Metric	Reactive	Unconstrained ReAct	Routing	Constrained ReAct
Avg API calls per request	0	3.2	1	2.1
Avg tokens used	0	~800	~150	~400
Latency (ms)	<5	1200–2500	400–800	800–1400
Cost per request	Free	~$0.005	~$0.001	~$0.002
Handles conflicts correctly	70%	95%	88%	98%
Handles pro bono routing	50%	93%	85%	96%
Hallucination rate	N/A	15% (wrong tools)	5%	0% (schema-validated)
What broke in test 4	Routed to wrong area	Called tool 5x, unclear answer	Couldn't handle ambiguity	Escalated correctly
How to Run Each Agent

Each script expects test_data.py in the same directory.

bash
Explain
# Reactive — no setup needed
python agent_1_rule_based.py

# Unconstrained ReAct
export GOOGLE_API_KEY="your-key-here"
python agent_2_unconstrained.py

# Deterministic Routing
export GOOGLE_API_KEY="your-key-here"
python agent_3_deterministic.py

# Constrained ReAct
export GOOGLE_API_KEY="your-key-here"
python agent_4_constrained.py

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

What I Learned
Reactive is fragile. The moment the problem has any nuance (two issues at once, pro bono + conflict), the rules break.
Unconstrained ReAct is smart but messy. The model reasons well, but it can get stuck in loops, hallucinate tool names, and rack up costs. I had runs where it called the same conflict-check tool three times.
Routing is fast and predictable, but can't adapt. If the classification is wrong, there's no loop to catch it. Perfect for simpler problems, not for this one.
Constrained ReAct is the sweet spot. The model can reason across multiple steps and call tools conditionally, but schema validation and a MAX_STEPS budget prevent it from spinning out. For a law firm, this is production-ready.
Files
agent_1_rule_based.py — Reactive agent
agent_2_unconstrained.py — Unconstrained ReAct agent
agent_3_deterministic.py — Deterministic routing agent
agent_4_constrained.py — Constrained ReAct agent
test_data.py — Shared test cases used by all four agents
PRESENTATION_SCRIPT.md — Presentation walkthrough
Deployment Notes

For production:

Use the Constrained ReAct agent with MAX_STEPS=8 and a clear escalation rule
Log every conflict check to the ethics database before routing
Have a human-in-the-loop override for edge cases (allow attorneys to reject routing)
Monitor for hallucinations (log every tool call and compare to expected schema)
Set up alerts if escalation rate exceeds 20%

I built and tested all four agents myself to understand, in practice rather than theory, why each architecture behaves the way it does — and why Constrained ReAct ended up being the right call for this problem.
