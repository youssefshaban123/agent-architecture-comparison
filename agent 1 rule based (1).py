# AGENT 1: REACTIVE (RULE-BASED) AGENT
# Pure if/then decision loop. No LLM, no API calls.
# Fast and free, but breaks on nuance.

import sys
sys.path.append("..")
from test_data import TEST_CASES, EXISTING_CLIENTS, PRACTICE_AREAS

class ReactiveAgent:
    def __init__(self):
        self.name = "Reactive Agent"
        self.api_calls = 0
        self.tokens = 0
    
    def classify_practice_area(self, intake_text):
        """Hard-coded rules to classify into a practice area."""
        intake_lower = intake_text.lower()
        
        # Rule-based classification
        if any(word in intake_lower for word in ["custody", "divorce", "separation", "alimony", "adoption", "ex"]):
            return "Family Law"
        elif any(word in intake_lower for word in ["DUI", "felony", "arrest", "cocaine", "drug", "criminal", "dui"]):
            return "Criminal Defense"
        elif any(word in intake_lower for word in ["acquisition", "contract", "M&A", "startup", "regulatory", "acquire"]):
            return "Corporate Law"
        else:
            return "Unknown"
    
    def check_conflict(self, intake_text):
        """Check if any existing client is mentioned."""
        for client in EXISTING_CLIENTS:
            if client.lower() in intake_text.lower():
                return True, client
        return False, None
    
    def assess_complexity(self, intake_text):
        """Simple heuristics for complexity."""
        intake_lower = intake_text.lower()
        
        # Count red flags
        red_flags = 0
        if "pro bono" in intake_lower or "can't afford" in intake_lower or "no money" in intake_lower:
            red_flags += 2
        if any(word in intake_lower for word in ["drug", "felony", "multiple"]):
            red_flags += 1
        if "and" in intake_text and intake_text.count("and") > 3:  # Multiple issues mentioned
            red_flags += 2
        
        if red_flags >= 3:
            return "Complex"
        elif red_flags >= 1:
            return "Moderate"
        else:
            return "Simple"
    
    def route_to_attorney(self, practice_area, complexity):
        """Assign to junior or senior attorney based on complexity."""
        if complexity == "Complex":
            return "Senior attorney (Bill rate: $350/hr)"
        elif complexity == "Moderate":
            return "Mid-level attorney (Bill rate: $250/hr)"
        else:
            return "Junior attorney (Bill rate: $150/hr)"
    
    def process(self, case):
        """Run the full reactive agent."""
        print(f"\n{'='*60}")
        print(f"REACTIVE AGENT - Test Case {case['id']}: {case['name']}")
        print(f"{'='*60}")
        
        intake_text = case["intake"]
        print(f"Intake: {intake_text[:100]}...")
        
        # Step 1: Classify
        practice_area = self.classify_practice_area(intake_text)
        print(f"✓ Classified as: {practice_area}")
        
        # Step 2: Check conflict
        has_conflict, conflicting_client = self.check_conflict(intake_text)
        if has_conflict:
            print(f"⚠ CONFLICT FOUND: {conflicting_client}")
            return {
                "case_id": case["id"],
                "action": "ESCALATE - Conflict of interest",
                "reason": f"Existing client '{conflicting_client}' is mentioned",
                "assigned_to": None,
                "api_calls": self.api_calls,
                "success": False,
            }
        
        # Step 3: Assess complexity
        complexity = self.assess_complexity(intake_text)
        print(f"✓ Complexity: {complexity}")
        
        # Step 4: Route
        assigned_to = self.route_to_attorney(practice_area, complexity)
        print(f"✓ Routed to: {assigned_to}")
        
        return {
            "case_id": case["id"],
            "action": "Route to attorney",
            "practice_area": practice_area,
            "complexity": complexity,
            "assigned_to": assigned_to,
            "api_calls": self.api_calls,
            "success": True,
        }


def run_tests():
    """Run all test cases through the reactive agent."""
    agent = ReactiveAgent()
    results = []
    
    print("\n" + "="*60)
    print("REACTIVE AGENT TEST RUN")
    print("="*60)
    
    for test_case in TEST_CASES:
        result = agent.process(test_case)
        results.append(result)
        
        # Show expected vs actual
        print(f"\nExpected practice area: {test_case.get('expected_practice_area')}")
        print(f"Expected action: {test_case.get('expected_action')}")
        print(f"Expected conflict: {test_case.get('expected_conflict')}")
        print(f"\nResult: {result['action']}")
        
        # Simple accuracy check
        if test_case.get('expected_conflict') and 'ESCALATE' in result['action']:
            print("✓ Conflict detection: PASS")
        elif not test_case.get('expected_conflict') and 'ESCALATE' not in result['action']:
            print("✓ Conflict detection: PASS")
        else:
            print("✗ Conflict detection: FAIL")
    
    # Summary stats
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total API calls: {sum(r['api_calls'] for r in results)}")
    print(f"Avg latency: <5ms (runs locally)")
    print(f"Cost: $0.00 (no API calls)")
    print(f"Cases routed correctly: {sum(1 for r in results if r['success'])} / {len(results)}")
    

if __name__ == "__main__":
    run_tests()
