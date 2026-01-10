#!/usr/bin/env python3
"""
Run Self-Healing Audit
Scheduled task to audit and heal the system automatically.
Can be run via cron or manually.
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(__file__))

from self_healing_agent import SelfHealingAgent

async def run_audit():
    """Run full system audit and self-healing."""
    print("=" * 70)
    print(f"SELF-HEALING AUDIT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    agent = SelfHealingAgent()
    
    # Run audit on Sheet2
    print("\n📊 Auditing Sheet2...")
    report = agent.audit_sheet_state("Sheet2")
    
    print(f"\n{report.get('summary', 'Audit complete')}")
    
    if report.get('statistics'):
        print(f"\n📈 Statistics:")
        for key, value in report.get('statistics', {}).items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    if report.get('issues_found'):
        print(f"\n⚠️  Issues Found ({len(report['issues_found'])}):")
        for issue in report['issues_found'][:10]:  # Show first 10
            print(f"  - {issue}")
        if len(report['issues_found']) > 10:
            print(f"  ... and {len(report['issues_found']) - 10} more")
    
    if report.get('fixes_applied'):
        print(f"\n✅ Fixes Applied ({len(report['fixes_applied'])}):")
        for fix in report['fixes_applied']:
            print(f"  - {fix}")
    
    # Health report
    print("\n" + "=" * 70)
    print("🏥 System Health Report:")
    health = agent.get_health_report()
    print(f"  • Issues Prevented (Total): {health['issues_prevented_count']}")
    print(f"  • Patterns Learned: {health['patterns_learned_count']}")
    print(f"  • Last Audit: {health.get('last_audit', 'Never')}")
    
    if health.get('recent_issues_prevented'):
        print(f"\n  🔒 Recent Issues Prevented (Last 5):")
        for issue in health['recent_issues_prevented'][-5:]:
            print(f"    - {issue.get('issue_type', 'unknown')}: {issue.get('reason', 'N/A')[:60]}")
    
    print("=" * 70)
    print("✅ Audit complete. System is self-healing and learning.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_audit())

