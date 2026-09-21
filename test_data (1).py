# Shared test cases for all four agents
# Same inputs, same ground truth, different approaches

TEST_CASES = [
    {
        "id": 1,
        "name": "Simple custody case",
        "intake": "My ex and I need to set up a custody agreement for our 8-year-old daughter. We're divorced but we're on good terms, just need it formalized. We live in California.",
        "expected_practice_area": "Family Law",
        "expected_conflict": False,
        "expected_complexity": "Simple",
        "expected_action": "Route to junior family attorney",
    },
    {
        "id": 2,
        "name": "M&A case with conflict",
        "intake": "We're a startup and we want to acquire one of our competitors. We need help with contracts and regulatory stuff. The competitor is called TechCorp Industries.",
        "expected_practice_area": "Corporate Law",
        "expected_conflict": True,  # TechCorp is already a client
        "existing_clients": ["TechCorp Industries", "Smith & Associates"],
        "expected_action": "ESCALATE - Conflict of interest",
    },
    {
        "id": 3,
        "name": "DUI with drugs and pro bono",
        "intake": "I got arrested last month for DUI. They also found some cocaine in my car, even though it's not mine. I don't have money for a lawyer. First offense. What are my options?",
        "expected_practice_area": "Criminal Defense",
        "expected_conflict": False,
        "expected_complexity": "Complex",  # Multiple charges, pro bono
        "expected_pro_bono": True,
        "expected_action": "Route to senior criminal defense attorney + evaluate pro bono",
    },
    {
        "id": 4,
        "name": "Ambiguous multi-issue case",
        "intake": "My business partner wants to sue me over the partnership agreement, and also my spouse is asking for a separation. Both are happening at the same time and I'm very stressed. Can you help with both?",
        "expected_practice_area": None,  # Multiple areas
        "expected_conflict": False,
        "expected_complexity": "Very Complex",
        "expected_action": "ESCALATE - Multiple practice areas needed, or refer to multiple attorneys",
    },
]

# Simulated conflict database (in real system, this would be a DB query)
EXISTING_CLIENTS = ["TechCorp Industries", "Smith & Associates", "Johnson Family Trust"]

# Practice area definitions
PRACTICE_AREAS = {
    "Corporate Law": ["acquisition", "contracts", "M&A", "regulatory", "startup"],
    "Family Law": ["custody", "divorce", "separation", "alimony", "adoption"],
    "Criminal Defense": ["DUI", "felony", "arrest", "cocaine", "drug", "criminal"],
}

# Complexity assessment criteria
COMPLEXITY_INDICATORS = {
    "Simple": ["straightforward", "first offense", "minor"],
    "Complex": ["pro bono", "multiple charges", "multiple issues", "drug", "felony"],
    "Very Complex": ["partner", "both partner and spouse", "multiple practice areas"],
}
