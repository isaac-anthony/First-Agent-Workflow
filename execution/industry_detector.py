#!/usr/bin/env python3
"""
Industry Detection Module
Identifies if a business is in one of the 7 high-value industries for Brine.ai.
"""

from typing import Optional, List, Dict

HIGH_VALUE_INDUSTRIES = {
    "solar": {
        "keywords": ["solar", "photovoltaic", "pv panel", "solar panel", "solar installation", "solar energy"],
        "name": "Solar Panel Installers",
        "ltv": "$15k-$30k",
        "pain_point": "competing for shared leads"
    },
    "roofing_hvac_commercial": {
        "keywords": ["roofing", "roofer", "hvac", "heating", "cooling", "commercial roofing", "commercial hvac", "commercial contractor"],
        "name": "Roofing & HVAC Contractors (Commercial)",
        "ltv": "$20k-$100k+",
        "pain_point": "missing hot leads while in field"
    },
    "legal": {
        "keywords": ["attorney", "lawyer", "law firm", "personal injury", "estate attorney", "litigation", "legal"],
        "name": "Personal Injury & Estate Attorneys",
        "ltv": "Six-figure settlements",
        "pain_point": "flooded with junk inquiries"
    },
    "pool_builders": {
        "keywords": ["pool builder", "pool construction", "pool renovation", "custom pool", "pool design", "swimming pool"],
        "name": "Custom Pool Builders & Renovators",
        "ltv": "$50k+",
        "pain_point": "high volume but low tech"
    },
    "msp": {
        "keywords": ["msp", "managed service", "it support", "cybersecurity", "managed it", "it services", "network support"],
        "name": "Managed IT & Cybersecurity Firms (MSPs)",
        "ltv": "High-ticket recurring",
        "pain_point": "understand automation but need help with own sales"
    },
    "medical_spa": {
        "keywords": ["medical spa", "med spa", "regenerative medicine", "botox", "coolsculpting", "stem cell", "aesthetic"],
        "name": "Medical Spas & Regenerative Medicine",
        "ltv": "High-margin packages",
        "pain_point": "leads ghost easily"
    },
    "specialized_cpa": {
        "keywords": ["cpa", "tax credit", "r&d tax", "cost segregation", "tax specialist", "tax advisor", "accountant"],
        "name": "Specialized CPAs (R&D Tax Credits)",
        "ltv": "$5k-$20k",
        "pain_point": "need educational outreach at scale"
    }
}

def detect_industry(biz_name: str, markdown_dna: str = "", niche: str = "") -> Optional[Dict]:
    """
    Detects if a business is in one of the 7 high-value industries.
    
    Args:
        biz_name: Business name
        markdown_dna: Website content (markdown)
        niche: Industry/niche category from scraping
    
    Returns:
        Dict with industry info if detected, None otherwise
    """
    # Combine all text for keyword matching
    search_text = f"{biz_name} {markdown_dna} {niche}".lower()
    
    # Check each industry
    for industry_key, industry_info in HIGH_VALUE_INDUSTRIES.items():
        keywords = industry_info["keywords"]
        # Check if any keyword appears in the search text
        if any(keyword.lower() in search_text for keyword in keywords):
            return {
                "industry_key": industry_key,
                "industry_name": industry_info["name"],
                "ltv": industry_info["ltv"],
                "pain_point": industry_info["pain_point"]
            }
    
    return None

def is_high_value_industry(biz_name: str, markdown_dna: str = "", niche: str = "") -> bool:
    """
    Quick check if business is in a high-value industry.
    
    Returns:
        True if detected, False otherwise
    """
    return detect_industry(biz_name, markdown_dna, niche) is not None

if __name__ == "__main__":
    # Test
    test_cases = [
        ("Solar Solutions Inc", "We install solar panels", "Solar"),
        ("Meier Law Firm", "Personal injury attorney", "Legal"),
        ("Premier Pool Builders", "Custom pool construction", "Construction"),
        ("Tech Support MSP", "Managed IT services", "IT"),
        ("Regular Restaurant", "We serve great food", "Restaurant")
    ]
    
    for name, dna, niche in test_cases:
        result = detect_industry(name, dna, niche)
        if result:
            print(f"✅ {name}: {result['industry_name']} (LTV: {result['ltv']})")
        else:
            print(f"❌ {name}: Not a high-value industry")

