#!/usr/bin/env python3
"""
Test script for the AI Drafting Agent with Objection Handling.
Tests how the AI rebuts common objections using the Battlesheets in brine_faq.md.
"""

import os
import sys
from dotenv import load_dotenv

# Add execution to path
sys.path.append(os.path.join(os.getcwd(), 'execution'))

from drafting_agent import DraftingAgent

load_dotenv()

def test_objection_handling():
    agent = DraftingAgent()
    lead_name = "John"
    
    objections = [
        "This sounds interesting, but honestly, $1,000/month is just too expensive for us right now.",
        "We already use Hubspot for everything, so I think we are all set on tools.",
        "I'm hesitant about letting an AI bot talk to my potential clients. How do I know it won't say something wrong?",
        "We only have 2 people in our office. We are probably too small for an enterprise AI setup."
    ]
    
    print("--- TESTING AI OBJECTION HANDLING ---")
    
    for i, obj in enumerate(objections, 1):
        print(f"\nTEST {i}: Lead says: \"{obj}\"")
        draft = agent.draft_reply(obj, lead_name)
        print("-" * 30)
        print(draft)
        print("-" * 30)

if __name__ == "__main__":
    test_objection_handling()

