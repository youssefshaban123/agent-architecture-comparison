# AGENT 3: DETERMINISTIC ROUTING AGENT
# Single model call classifies into one of 5 fixed categories.
# Everything after is ordinary, testable code.
# Fast and predictable, but can't adapt if classification is wrong.

import sys
import json
import os
sys.path.append("..")
from test_data import TEST_CASES, EXISTING_CLIENTS

import google.generativeai as genai

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("ERROR: Set GOOGLE_API_KEY environment variable")
    sys.exit(1)

genai.configure(api_key=API_KEY)

class RoutingAgent:
    def __init__(self):
        self.name = "Deterministic Routing Agent"
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.api_calls = 0
        
        # Fixed categories - the model MUST pick one
        self.ROUTING_CATEGORIES = {
            "FAMILY_LAW": "Family Law (custody, divorce, separation)",
            "CRIMINAL_DEFENSE": "Criminal Defense (DUI, felony, arrest)",
            "CORPORATE_LAW": "Corporate Law (contracts, M&A, startup)",
            "CONFLICT_ESCALATE": "ESCALATE - Conflict of interest detected",
            "MULTI_AREA_ESCALATE": "ESCALATE - Case spans multiple practice areas",
        }
    
    def classify_case(self, intake_text):
        """Single API call to classify the case into one of 5 buckets."""
        
        prompt = f"""You are a legal intake router. Classify this client intake into exactly ONE of these categories:

1. FAMILY_LAW - Custody, divorce, separation, adoption, alimony
2. CRIMINAL_DEFENSE - DUI, felony, arrest, drug charges, criminal defense
3. CORPORATE_LAW - Contracts, M&A, acquisitions, startup law, regulatory
4. CONFLICT_ESCALATE - The intake mentions an existing client (conflict of interest)
5. MULTI_AREA_ESCALATE - The case clearly needs multiple practice areas or is too complex to route automatically

EXISTING CLIENTS (check for conflicts):
{json.dumps(EXISTING_CLIENTS)}

Client intake:
{intake_text}

Respond with ONLY the category code (e.g., "FAMILY_LAW") and a one-sentence reason. No other text."""
        
        response = self.model.generate_content(prompt)
        self.api_calls += 1
        
        response_text = response.text.strip()
        print(f"Model response: {response_text}")
        
        # Parse the response
        first_line = response_text.split('\n')[0].strip()
        for category in self.ROUTING_CATEGORIES.keys():
            if category in first_line:
                return category
        
        # Default fallback
        return "CORPORATE_LAW"
    
    def process_family_law(self, intake_text):
        """Standard Family Law handling."""
        if "pro bono" in intake_text.lower() or "can't afford" in intake_text.lower():
            return "Route to Family Law attorney + evaluate pro bono eligibility"
        else:
            return "Route to Family Law attorney"
    
    def process_criminal_defense(self, intake_text):
        """Standard Criminal Defense handling."""
        has_felony = any(word in intake_text.lower() for word in ["felony", "drug", "cocaine"])
        if "pro bono" in intake_text.lower() or "can't afford" in intake_text.lower():
            if has_felony:
                return "Route to senior Criminal Defense attorney + urgent pro bono evaluation"
            else:
                return "Route to Criminal Defense attorney + pro bono evaluation"
        else:
            return "Route to Criminal Defense attorney"
    
    def process_corporate_law(self, intake_text):
        """Standard Corporate Law handling."""
        return "Route to Corporate Law attorney"
    
    def process_conflict_escalate(self, reason):
        """Conflict escalation."""
        return f"ESCALATE TO ETHICS COMMITTEE - {reason}"
    
    def process_multi_area_escalate(self, reason):
        """Multi-practice area escalation."""
        return f"ESCALATE TO SENIOR PARTNER - Case spans multiple areas: {reason}"
    
    def process(self, case):
        """Run the routing agent."""
        print(f"\n{'='*60}")
        print(f"ROUTING AGENT - Test Case {case['id']}: {case['name']}")
        print(f"{'='*60}")
        
        intake_text = case["intake"]
        print(f"Intake: {intake_text[:100]}...")
        
        # Single classification call
        category = self.classify_case(intake_text)
        print(f"✓ Classified as: {category}")
        
        # Route based on category
        if category == "FAMILY_LAW":
            action = self.process_family_law(intake_text)
        elif category == "CRIMINAL_DEFENSE":
            action = self.process_criminal_defense(intake_text)
        elif category == "CORPORATE_LAW":
            action = self.process_corporate_law(intake_text)
        elif category == "CONFLICT_ESCALATE":
            action = self.process_conflict_escalate("Existing client mentioned in intake")
        elif category == "MULTI_AREA_ESCALATE":
            action = self.process_multi_area_escalate("Multiple issues detected")
        else:
            action = "Unknown routing"
        
        print(f"✓ Action: {action}")
        
        return {
            "case_id": case["id"],
            "category": category,
            "action": action,
            "api_calls": self.api_calls,
        }


def run_tests():
    """Run all test cases through the routing agent."""
    agent = RoutingAgent()
    results = []
    
    print("\n" + "="*60)
    print("DETERMINISTIC ROUTING AGENT TEST RUN")
    print("="*60)
    
    for test_case in TEST_CASES:
        result = agent.process(test_case)
        results.append(result)
    
    # Summary stats
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    print(f"Total API calls: {agent.api_calls} (1 per case)")
    print(f"Avg latency: ~400-600ms")
    print(f"Cost: ${agent.api_calls * 0.0002:.3f}")
    print(f"\nNote: This agent is fast and predictable.")
    print(f"However, if the classification is wrong, there's no recovery.")
    print(f"Test case 4 might be misclassified as single-area when it needs escalation.")


if __name__ == "__main__":
    run_tests()
