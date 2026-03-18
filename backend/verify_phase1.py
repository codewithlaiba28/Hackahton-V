"""
Phase 1 Verification Script

Run this to verify all Phase 1 deliverables are complete.
"""

import os
import sys
import json
from pathlib import Path

def check_file(path, description):
    """Check if file exists and report status."""
    exists = os.path.exists(path)
    status = "[PASS]" if exists else "[FAIL]"
    print(f"{status} {description}: {path}")
    return exists

def check_dir(path, description):
    """Check if directory exists and report status."""
    exists = os.path.isdir(path)
    status = "[PASS]" if exists else "[FAIL]"
    print(f"{status} {description}: {path}")
    return exists

def check_json_file(path, description, min_items=0):
    """Check if JSON file exists and has minimum items."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = len(data) if isinstance(data, list) else 1
        status = "[PASS]" if count >= min_items else "[FAIL]"
        print(f"{status} {description}: {count} items (min: {min_items})")
        return count >= min_items
    except Exception as e:
        print(f"[ERROR] {description}: {e}")
        return False

def main():
    print("=" * 60)
    print("Phase 1 Incubation - Verification")
    print("=" * 60)
    
    root = Path(__file__).parent.parent
    backend = root / "backend"
    specs = root / "specs"
    context = root / "context"
    
    all_pass = True
    
    print("\n1. Directory Structure")
    print("-" * 60)
    all_pass &= check_dir(backend / "src" / "agent", "Agent components")
    all_pass &= check_dir(backend / "src" / "channels", "Channel simulators")
    all_pass &= check_dir(backend / "tests", "Test suite")
    all_pass &= check_dir(context, "Context files")
    all_pass &= check_dir(specs, "Specifications")
    
    print("\n2. Context Files (Dossier)")
    print("-" * 60)
    all_pass &= check_file(context / "company-profile.md", "Company profile")
    all_pass &= check_file(context / "product-docs.md", "Product documentation")
    all_pass &= check_json_file(context / "sample-tickets.json", "Sample tickets", 50)
    all_pass &= check_file(context / "escalation-rules.md", "Escalation rules")
    all_pass &= check_file(context / "brand-voice.md", "Brand voice")
    
    print("\n3. Backend Components")
    print("-" * 60)
    all_pass &= check_file(backend / "src" / "channels" / "base.py", "Channel base model")
    all_pass &= check_file(backend / "src" / "channels" / "email_simulator.py", "Email simulator")
    all_pass &= check_file(backend / "src" / "channels" / "whatsapp_simulator.py", "WhatsApp simulator")
    all_pass &= check_file(backend / "src" / "channels" / "webform_simulator.py", "Web form simulator")
    all_pass &= check_file(backend / "src" / "agent" / "knowledge_base.py", "Knowledge base")
    all_pass &= check_file(backend / "src" / "agent" / "sentiment.py", "Sentiment analyzer")
    all_pass &= check_file(backend / "src" / "agent" / "escalation.py", "Escalation logic")
    all_pass &= check_file(backend / "src" / "agent" / "formatter.py", "Channel formatter")
    all_pass &= check_file(backend / "src" / "agent" / "memory.py", "Conversation memory")
    all_pass &= check_file(backend / "src" / "agent" / "normalizer.py", "Message normalizer")
    all_pass &= check_file(backend / "src" / "agent" / "core_loop.py", "Core agent loop")
    all_pass &= check_file(backend / "src" / "agent" / "prompts.py", "System prompts")
    all_pass &= check_file(backend / "src" / "mcp_server.py", "MCP server")
    all_pass &= check_file(backend / "src" / "skills_manifest.py", "Skills manifest")
    
    print("\n4. Test Suite")
    print("-" * 60)
    all_pass &= check_file(backend / "tests" / "test_core_loop.py", "Core loop tests")
    
    print("\n5. Documentation")
    print("-" * 60)
    all_pass &= check_file(specs / "discovery-log.md", "Discovery log")
    all_pass &= check_file(specs / "customer-success-fte-spec.md", "Crystallized spec")
    all_pass &= check_file(specs / "transition-checklist.md", "Transition checklist")
    
    print("\n6. Project Configuration")
    print("-" * 60)
    all_pass &= check_file(root / "requirements.txt", "Python dependencies")
    all_pass &= check_file(root / ".env.example", "Environment example")
    all_pass &= check_file(root / ".gitignore", "Git ignore")
    
    print("\n" + "=" * 60)
    if all_pass:
        print("[SUCCESS] ALL CHECKS PASSED - Phase 1 Complete!")
        print("\nNext Steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set ANTHROPIC_API_KEY in .env")
        print("3. Run tests: pytest backend/tests/ -v")
        print("4. Test MCP server: python backend/src/mcp_server.py")
        return 0
    else:
        print("[FAIL] SOME CHECKS FAILED - Review missing items above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
