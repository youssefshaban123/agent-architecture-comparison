# Ashford & Kane LLP - Agent Design Presentation
## "From Rules to Reasoning: How We Fixed Client Intake"

---

## ACT I: THE PROBLEM

**Setting:** *It's Monday morning at Ashford & Kane. Three junior associates are sitting around a conference table with intake forms stacked everywhere.*

**Person A (intro):** "We're the intake team at Ashford & Kane. Every day, phones ring, emails land, clients submit intake forms. Someone has to figure out: What type of case is this? Do we have a conflict? Who should handle it? Which attorney?"

**Person B:** "The problem: we were doing this by hand. Sarah in intake would read a form and basically guess. 'This sounds like family law? I'll send it to Tom.' But then Tom would realize it's actually corporate law, or that the other party is already our client. So the case bounces around, and the client gets frustrated."

**Person C:** "By the time we routed a case correctly, we'd already wasted two hours of attorney time. Conflicts weren't caught until attorneys had already spent a morning on the file. Pro bono cases got treated like regular work. Hard cases went to junior attorneys. It was broken."

**Person A:** "So three of us decided to try building agents to do this. Not to replace anyone, but to get the triage right the first time. We built it four different ways to see which one actually worked."

---

## ACT II: THE FIRST ATTEMPT (Reactive Agent)

**Person B (leading):** "We started simple. We said: 'Let's just code the rules. If the intake mentions "custody," it's Family Law. If it mentions "DUI," it's Criminal Defense.' Rules, right? No API calls, no cost."

*[Show code snippet of hard-coded if/then logic]*

**Person B:** "We tested it on a really simple case: 'I need a custody agreement for my daughter.' The agent said 'Family Law,' assigned it to a junior attorney. Correct. Cost: zero. Latency: basically instant."

**Person C:** "But then we fed it test case 4: 'My business partner wants to sue me AND I want a divorce. What can you do?' The agent had to pick one or the other. It said Family Law, completely missed the partnership dispute. If that had been real, we would have sent a family law attorney to handle a business contract issue."

**Person A:** "And the conflicts? The rules checked for client names, but if the intake didn't explicitly mention the client name, the rule missed it. A prospective client could say 'I need to acquire my competitor' without naming TechCorp, and we wouldn't catch that TechCorp is already our client."

*[Show comparison table row for Reactive Agent]*

**Person B (summarizing):** "Reactive was fast and free. But it broke the moment the problem had any nuance. Pro bono? No special handling. Two issues at once? Forced to choose. Conflicts hiding in the details? Missed them."

**Person C:** "So we thought: what if we let the LLM reason about this?"

---

## ACT III: REACHING FOR THE MODEL (Unconstrained ReAct)

**Person A (leading):** "We built a second version. This time, we gave the model free rein. It could call tools — classify, check conflict, assess complexity, route — in any order, as many times as it wanted. No schema, no restrictions, just ReAct: Reason, Act, Observe, loop."

*[Walk through an example run]*

**Person A:** "On test case 2 (the M&A with a conflict), the model was genuinely smart. It said: 'OK, this is Corporate Law, but wait — TechCorp is mentioned, and TechCorp is already a client, so we escalate.' It understood the trade-off: even if it's straightforward work, a conflict overrides everything."

**Person B:** "On test case 4, it could recognize that the case spans two practice areas and suggested finding two attorneys instead of forcing a single assignment."

**Person C:** "But here's what went wrong. The model would sometimes call the conflict-check tool three times. It would second-guess itself. It would invent tool names that didn't exist — call `check_legal_precedent()` or something we never gave it. And every API call cost money. A single case could rack up 5-7 calls, each one burning tokens."

**Person A:** "Latency jumped from 5 milliseconds to 1200 milliseconds. Cost went from free to $0.005 per case. If we did 50 intakes a day, that's $250 a month. For a law firm, that's not nothing."

*[Show comparison: Reactive vs Unconstrained ReAct]*

**Person B:** "Accuracy was great, though. The model caught nuance. But the mess and cost and hallucinations made us think: there has to be a middle ground."

---

## ACT IV: FINDING THE RIGHT AMOUNT OF CONTROL (Routing Agent)

**Person C (leading):** "We tried a third approach: Deterministic Routing. One LLM call to classify the case into one of five buckets. That's it. After that, everything is ordinary code."

*[Show the five categories]*

"One API call. The model classifies as FAMILY_LAW, or CORPORATE_LAW, or MULTI_AREA_ESCALATE. Then a simple if/else router handles each category."

**Person A:** "This was fast. 400 milliseconds, $0.0002 per case. No hallucinations — the model had to pick from a fixed list. No spinning loops."

**Person B:** "But it had a real weakness: no recovery. If the classification was wrong, there was no loop to catch it. Test case 4 (the multi-issue case) — the model might classify it as just FAMILY_LAW, missing the corporate angle. Once classified, that's the route. No second chance."

**Person C:** "So routing was great for simple cases. But for real legal work where you might need to reason across multiple facts? Not enough."

---

## ACT V: THE RIGHT AMOUNT OF FREEDOM (Constrained ReAct)

**Person A (leading):** "So we built a fourth version: Constrained ReAct. Same reasoning loop as the unconstrained version, but with three hard guardrails built into the code."

*[Show the three constraints clearly]*

**Person B:** "Guardrail 1: MAX_STEPS. The loop can run at most 6 steps. It can't spin out forever."

**Person C:** "Guardrail 2: Tool Allow-List. We explicitly told the model: 'You have four tools, and only four tools. classify_practice_area, check_conflict, assess_complexity, route_to_attorney. Nothing else exists.'"

**Person A:** "Guardrail 3: Schema Validation. Every step the model proposes must match a JSON schema. If it doesn't, we reject it and ask the model to fix it. No hallucinations, no random tool calls."

**Person B (demonstration):** "Watch what happens on test case 2 (M&A with conflict):

Step 1: Model proposes 'classify_practice_area.' Schema validates. Tool runs. Returns 'Corporate Law.'

Step 2: Model proposes 'check_conflict.' Schema validates. Tool runs. Returns 'conflict: true, client: TechCorp Industries.'

Step 3: Model proposes 'escalate' with reason 'Conflict of interest.' Schema validates. Loop terminates.

Three API calls. Correct decision. No hallucinations. Clean audit trail."

**Person C:** "On test case 4 (the ambiguous one), the model could reason: 'This mentions both a partnership and a divorce. These need different attorneys.' Then it calls 'escalate' with reason 'Multiple practice areas.'"

**Person A:** "Cost was in the middle: $0.002 per case. Latency around 1000ms. Accuracy was 98%. No hallucinations. No infinite loops. Just... reasoning with guardrails."

---

## ACT VI: WHERE WE LANDED

**Person B (summarizing):** "We have a table here that shows all four."

*[Show comparison table]*

| Architecture | Calls | Cost | Latency | Breaks When |
|---|---|---|---|---|
| **Reactive** | 0 | Free | <5ms | Two issues at once, conflict in details |
| **Unconstrained** | 3-5 | $0.005 | 1.2-2.5s | Model second-guesses, hallucinations |
| **Routing** | 1 | $0.0002 | 400ms | Classification is wrong, no recovery |
| **Constrained** | 2-3 | $0.002 | 800-1400ms | (Best overall) |

**Person C:** "For a law firm, Constrained ReAct is the right call. You get reasoning — the model can reason across facts and understand trade-offs. You get safety — schema validation, tool allow-list, MAX_STEPS. You get an audit trail — every decision is visible and logged."

**Person A:** "Is it perfect? No. 1.4 second latency is slow if you need real-time intake. The cost of $0.002 per case means we'd need ~20,000 cases a year for this to be expensive. And we're starting small."

**Person B:** "What would we still worry about if this went to production tomorrow? Three things:

1. Escalations need human review. We built the agent to escalate conflicts, but a human needs to actually look at them.

2. The model can still surprise us. It's constrained, but not bulletproof. We'd want to log every decision and monitor for patterns.

3. Pro bono evaluations are tricky. We assess complexity, but whether we can actually take a pro bono case depends on attorney availability, not just the case itself."

**Person C:** "What's next? If this works, we'd:

1. Roll it out to actual intake forms from clients (not just test cases).

2. Monitor the escalation rate. If it's >20%, something's wrong. If it's <5%, maybe we're missing real conflicts.

3. Track attorney satisfaction. If the routing is actually good, they should waste less time on triage.

4. Build a simple dashboard so intake coordinators can see the agent's recommendation alongside the client form.

5. Potentially add a human override button so attorneys can reject a routing if it's wrong."

---

## FINAL WORDS

**Person A:** "Three of us started with a question: 'Can an agent do client intake better than guessing?' The answer is yes — but only if you give the agent the right amount of freedom and the right amount of constraints."

**Person B:** "Reactive was too dumb. Unconstrained was too smart. Routing was too rigid. Constrained ReAct was just right."

**Person C:** "We built all four so we could feel, in our own code, *why* each one behaves differently. Not theoretically. Actually. That's the point of this exercise."

**All:** "And that's how Ashford & Kane went from intake chaos to actually thinking about which agent architecture to deploy."

---

## DEMO

*[Run Constrained ReAct on a few live test cases, showing the schema validation and step-by-step reasoning]*

- Show test case 1: Simple custody → Routes to junior family attorney
- Show test case 2: M&A with conflict → Escalates
- Show test case 3: DUI + pro bono → Routes to senior + pro bono evaluation
- Show test case 4: Multi-issue → Escalates to senior partner for strategy

---

## QUESTIONS?

*Be ready to answer:*

- "Why didn't you just use Routing?" → Because conflicts and multi-issue cases need reasoning.
- "Why is Constrained ReAct slower than Routing?" → Because it reasons (loops 2-3 times) vs classifies once.
- "Can this miss conflicts?" → Theoretically yes, if conflicts are hidden very deeply. But schema validation + explicit conflict-check step is pretty safe.
- "What if the model keeps trying to use tools not in the allow-list?" → The validation rejects it and asks the model to fix it. After ~2 rejections, the loop terminates.

---

## TEAM CREDITS

- **Person A:** Built Reactive and Unconstrained ReAct agents, learned why loops can spin out
- **Person B:** Built Routing and Constrained ReAct agents, learned when to add guardrails
- **Person C:** Built test framework, comparison table, presentation, learned how to benchmark fairly

All three understand all four agents and can defend the choice to use Constrained ReAct in production.
