# AGENT 2: UNCONSTRAINED LLM-POWERED AGENT
# ReAct-style loop: the model thinks, picks a tool, observes, repeats.
# No schema validation, no tool restrictions, no step limit.
# Smart but can spin out or hallucinate.

import sys
import json
import os
sys.path.append("..")
from test_data import TEST_CASES, EXISTING_CLIENTS, PRACTICE_AREAS

# Using Google Gemini API (free tier available)
import google.generativeai as genai

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("ERROR: Set GOOGLE_API_KEY environment variable")
    print("Get a free key at: https://aistudio.google.com/app/apikey")
    sys.exit(1)

genai.configure(api_key=API_KEY)

class UnconstrainedReActAgent:
    def __init__(self):
        self.name = "Unconstrained ReAct Agent"
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.api_calls = 0
        self.total_tokens = 0
        self.step_count = 0
    
    # These are the "tools" the model can call
    def classify_practice_area(self, intake_text):
        """Classify the case into a practice area."""
        intake_lower = intake_text.lower()
        
        if any(word in intake_lower for word in ["custody", "divorce", "separation", "alimony"]):
            return "Family Law"
        elif any(word in intake_lower for word in ["DUI", "felony", "arrest", "cocaine"]):
            return "Criminal Defense"
        elif any(word in intake_lower for word in ["acquisition", "contract", "M&A", "startup"]):
            return "Corporate Law"
        else:
            return "Unknown"
    
    def check_conflict(self, intake_text):
        """Query conflict database."""
        for client in EXISTING_CLIENTS:
            if client.lower() in intake_text.lower():
                return {"conflict": True, "client": client}
        return {"conflict": False}
    
    def assess_complexity(self, intake_text):
        """Evaluate case complexity."""
        intake_lower = intake_text.lower()
        factors = []
        
        if "pro bono" in intake_lower or "can't afford" in intake_lower:
            factors.append("pro bono status")
        if any(word in intake_lower for word in ["drug", "felony", "multiple"]):
            factors.append("multiple charges or issues")
        if intake_text.count("and") > 3:
            factors.append("multiple practice areas")
        
        if len(factors) >= 2:
            complexity = "Very Complex"
        elif len(factors) >= 1:
            complexity = "Complex"
        else:
            complexity = "Simple"
        
        return {"complexity": complexity, "factors": factors}
    
    def route_to_attorney(self, practice_area, complexity):
        """Assign to the right attorney."""
        if complexity == "Very Complex":
            return f"Senior {practice_area} attorney (Partner level, $350+/hr)"
        elif complexity == "Complex":
            return f"Senior {practice_area} attorney ($300/hr)"
        else:
            return f"Junior {practice_area} attorney ($150/hr)"
    
    def execute_tool(self, tool_name, args):
        """Execute a tool based on name and arguments."""
        if tool_name == "classify_practice_area":
            return self.classify_practice_area(args.get("intake_text", ""))
        elif tool_name == "check_conflict":
            return self.check_conflict(args.get("intake_text", ""))
        elif tool_name == "assess_complexity":
            return self.assess_complexity(args.get("intake_text", ""))
        elif tool_name == "route_to_attorney":
            return self.route_to_attorney(
                args.get("practice_area", "Unknown"),
                args.get("complexity", "Simple")
            )
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def process(self, case):
        """Run the unrestricted ReAct loop."""
        print(f"\n{'='*60}")
        print(f"UNCONSTRAINED REACT - Test Case {case['id']}: {case['name']}")
        print(f"{'='*60}")
        
        intake_text = case["intake"]
        print(f"Intake: {intake_text[:100]}...")
        
        # Build the prompt for the model
        system_prompt = """You are a legal intake assistant. You have access to these tools:
- classify_practice_area(intake_text): Returns the practice area (Family Law, Corporate Law, Criminal Defense, or Unknown)
- check_conflict(intake_text): Returns {conflict: true/false, client: name if conflict}
- assess_complexity(intake_text): Returns {complexity, factors: [list]}
- route_to_attorney(practice_area, complexity): Returns the recommended attorney assignment

Your job:
1. Start by classifying the practice area
2. Check for conflicts - this is CRITICAL
3. If no conflict, assess complexity
4. Route to the appropriate attorney
5. Provide a final recommendation

Think step-by-step. Call tools as needed. Return your final decision."""
        
        user_message = f"""Client intake form:
{intake_text}

Please process this and recommend routing. Use the tools available to you."""
        
        conversation = [
            {"role": "user", "content": system_prompt + "\n\n" + user_message}
        ]
        
        max_steps = 15  # Safety limit (but model doesn't know this)
        step = 0
        final_answer = None
        
        while step < max_steps:
            step += 1
            self.step_count += 1
            
            # Call the model
            response = self.model.generate_content(
                conversation,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1000,
                )
            )
            self.api_calls += 1
            
            model_response = response.text
            print(f"\n[Step {step}] Model thinking:\n{model_response[:300]}...")
            
            # Check if model is asking to use a tool or giving final answer
            # (In a real implementation, we'd use structured outputs)
            # For this demo, we'll look for tool calls in the text
            
            has_tool_call = False
            for tool_name in ["classify_practice_area", "check_conflict", "assess_complexity", "route_to_attorney"]:
                if tool_name in model_response:
                    has_tool_call = True
                    # Extract and call the tool
                    result = self.execute_tool(tool_name, {"intake_text": intake_text, "practice_area": "Family Law", "complexity": "Simple"})
                    print(f"[Tool] {tool_name} → {result}")
                    
                    # Add to conversation
                    conversation.append({"role": "assistant", "content": model_response})
                    conversation.append({"role": "user", "content": f"Tool result: {json.dumps(result)}"})
                    break
            
            # If no tool call, assume final answer
            if not has_tool_call:
                final_answer = model_response
                break
        
        print(f"\nFinal answer after {step} steps:\n{final_answer[:200]}...")
        
        return {
            "case_id": case["id"],
            "steps": step,
            "api_calls": self.api_calls,
            "total_api_calls": self.api_calls,
            "final_answer": final_answer[:100],
        }


def run_tests():
    """Run all test cases through the unconstrained agent."""
    agent = UnconstrainedReActAgent()
    results = []
    
    print("\n" + "="*60)
    print("UNCONSTRAINED REACT AGENT TEST RUN")
    print("="*60)
    print("(Using Google Gemini API - free tier)")
    
    for test_case in TEST_CASES:
        result = agent.process(test_case)
        results.append(result)
    
    # Summary stats
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total API calls: {agent.api_calls}")
    print(f"Avg steps per case: {agent.step_count / len(results):.1f}")
    print(f"Avg latency: ~1500ms (includes API calls)")
    print(f"Estimated cost: ${agent.api_calls * 0.0005:.3f}")
    print(f"\nNote: This agent can spin into loops or hallucinate tool names.")
    print(f"In test case 4, it might keep second-guessing the classification.")


if __name__ == "__main__":
    run_tests()
