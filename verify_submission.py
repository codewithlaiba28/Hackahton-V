#!/usr/bin/env python3
"""
Customer Success FTE - Submission Verification Script

Run this before submitting to ensure all requirements are met.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def check_mark(passed):
    return f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"

def section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")

def subsection(title):
    print(f"\n{Colors.BOLD}{title}{Colors.RESET}")

# Load environment
load_dotenv('.env')

print(f"\n{Colors.BOLD}Customer Success FTE - Submission Verification{Colors.RESET}")
print("Checking all hackathon requirements before submission...\n")

passed = 0
failed = 0
warnings = 0

# =============================================================================
# 1. ENVIRONMENT VARIABLES
# =============================================================================
section("1. Environment Variables")

env_vars = {
    'CEREBRAS_API_KEY': 'Required for LLM (Cerebras)',
    'DATABASE_URL': 'Required for PostgreSQL connection',
    'NEXT_PUBLIC_API_URL': 'Required for frontend API calls',
}

for var, description in env_vars.items():
    value = os.getenv(var)
    if value and value != 'your_' + var.lower() + '_here':
        print(f"  {check_mark(True)} {var} {Colors.GREEN}configured{Colors.RESET}")
        passed += 1
    else:
        print(f"  {check_mark(False)} {var} {Colors.RED}NOT configured{Colors.RESET} - {description}")
        failed += 1

# Optional vars
optional_vars = {
    'TWILIO_ACCOUNT_SID': 'Twilio WhatsApp integration',
    'TWILIO_AUTH_TOKEN': 'Twilio authentication',
    'TWILIO_WHATSAPP_NUMBER': 'WhatsApp number (format: whatsapp:+1234567890)',
}

for var, description in optional_vars.items():
    value = os.getenv(var)
    if value and not value.startswith('your_'):
        print(f"  {check_mark(True)} {var} {Colors.GREEN}configured{Colors.RESET} ({description})")
        passed += 1
    else:
        print(f"  {check_mark(True)} {var} {Colors.YELLOW}optional{Colors.RESET} - {description}")
        warnings += 1

# =============================================================================
# 2. FILE STRUCTURE
# =============================================================================
section("2. File Structure")

required_files = {
    'backend/api/main.py': 'FastAPI backend',
    'backend/agent/customer_success_agent.py': 'Agent definition',
    'backend/agent/tools.py': 'Agent tools',
    'backend/database/schema.sql': 'Database schema',
    'backend/src/channels/gmail_handler.py': 'Gmail integration',
    'backend/src/channels/whatsapp_handler.py': 'WhatsApp integration',
    'frontend/app/page.tsx': 'Landing page',
    'frontend/app/login/page.tsx': 'Login page',
    'frontend/app/signup/page.tsx': 'Signup page',
    'frontend/app/dashboard/page.tsx': 'Dashboard',
    'frontend/app/dashboard/support/page.tsx': 'Support form',
    'frontend/app/components/SupportForm.tsx': 'Reusable form component',
    'frontend/lib/auth.ts': 'Better Auth configuration',
    'frontend/lib/auth-client.ts': 'Auth client',
    'docker-compose.yml': 'Docker orchestration',
    'specs/customer-success-fte-spec.md': 'Feature specification',
    'Hackahton.md': 'Hackathon requirements',
}

for file_path, description in required_files.items():
    if Path(file_path).exists():
        print(f"  {check_mark(True)} {file_path} {Colors.GREEN}✓{Colors.RESET}")
        passed += 1
    else:
        print(f"  {check_mark(False)} {file_path} {Colors.RED}MISSING{Colors.RESET} - {description}")
        failed += 1

# =============================================================================
# 3. SPECIFICATION DOCUMENTS
# =============================================================================
section("3. Specification Documents")

spec_files = {
    'specs/discovery-log.md': 'Discovery log from incubation',
    'specs/transition-checklist.md': 'Phase 1→2 transition checklist',
    'specs/phase1-incubation/spec.md': 'Phase 1 specification',
    'specs/phase2-specialization/spec.md': 'Phase 2 specification',
}

for file_path, description in spec_files.items():
    if Path(file_path).exists():
        print(f"  {check_mark(True)} {file_path}")
        passed += 1
    else:
        print(f"  {check_mark(False)} {file_path} {Colors.RED}MISSING{Colors.RESET}")
        failed += 1

# =============================================================================
# 4. BACKEND ENDPOINTS
# =============================================================================
section("4. Backend API Endpoints (Code Check)")

endpoint_checks = {
    'GET /health': 'backend/api/main.py',
    'POST /support/submit': 'backend/api/main.py',
    'POST /agent/chat': 'backend/api/main.py',
    'GET /support/ticket/{ticket_id}': 'backend/api/main.py',
    'GET /tickets': 'backend/api/main.py',
    'GET /metrics/channels': 'backend/api/main.py',
    'GET /customers': 'backend/api/main.py',
    'POST /webhook/whatsapp': 'backend/api/main.py',
    'GET /webhook/gmail/poll': 'backend/api/main.py',
}

for endpoint, file_path in endpoint_checks.items():
    if Path(file_path).exists():
        try:
            content = Path(file_path).read_text(encoding='utf-8')
        except:
            content = Path(file_path).read_text(encoding='cp1252', errors='ignore')
        # Simple check - look for endpoint pattern
        endpoint_path = endpoint.split(' ')[1].split('{')[0].rstrip('/')
        if endpoint_path in content:
            print(f"  {check_mark(True)} {endpoint}")
            passed += 1
        else:
            print(f"  {check_mark(False)} {endpoint} {Colors.RED}NOT FOUND{Colors.RESET}")
            failed += 1
    else:
        print(f"  {check_mark(False)} {endpoint} {Colors.RED}FILE MISSING{Colors.RESET}")
        failed += 1

# =============================================================================
# 5. AGENT TOOLS
# =============================================================================
section("5. Agent Tools (OpenAI Agents SDK)")

tools_file = Path('backend/agent/tools.py')
if tools_file.exists():
    try:
        content = tools_file.read_text(encoding='utf-8')
    except:
        content = tools_file.read_text(encoding='cp1252', errors='ignore')
    
    required_tools = [
        'search_knowledge_base',
        'create_ticket',
        'get_customer_history',
        'escalate_to_human',
        'send_response',
    ]
    
    for tool in required_tools:
        if f'async def {tool}' in content:
            print(f"  {check_mark(True)} {tool}()")
            passed += 1
        else:
            print(f"  {check_mark(False)} {tool}() {Colors.RED}MISSING{Colors.RESET}")
            failed += 1
else:
    print(f"  {check_mark(False)} tools.py {Colors.RED}MISSING{Colors.RESET}")
    failed += len(required_tools)

# =============================================================================
# 6. DATABASE SCHEMA
# =============================================================================
section("6. Database Schema")

schema_file = Path('backend/database/schema.sql')
if schema_file.exists():
    try:
        content = schema_file.read_text(encoding='utf-8')
    except:
        content = schema_file.read_text(encoding='cp1252', errors='ignore')
    
    required_tables = [
        'customers',
        'customer_identifiers',
        'conversations',
        'messages',
        'tickets',
        'knowledge_base',
        'channel_configs',
        'agent_metrics',
    ]
    
    for table in required_tables:
        if f'CREATE TABLE {table}' in content or f'create table {table}' in content:
            print(f"  {check_mark(True)} {table} table")
            passed += 1
        else:
            print(f"  {check_mark(False)} {table} table {Colors.RED}MISSING{Colors.RESET}")
            failed += 1
else:
    print(f"  {check_mark(False)} schema.sql {Colors.RED}MISSING{Colors.RESET}")
    failed += len(required_tables)

# =============================================================================
# 7. CHANNEL INTEGRATIONS
# =============================================================================
section("7. Channel Integrations")

channel_checks = {
    'Gmail': ['backend/src/channels/gmail_handler.py', 'fetch_messages', 'send_reply'],
    'WhatsApp': ['backend/src/channels/whatsapp_handler.py', 'send_message', 'parse_webhook'],
    'Web Form': ['frontend/app/components/SupportForm.tsx', 'handleSubmit'],
}

for channel, (file_path, *checks) in channel_checks.items():
    if Path(file_path).exists():
        try:
            content = Path(file_path).read_text(encoding='utf-8')
        except:
            content = Path(file_path).read_text(encoding='cp1252', errors='ignore')
        all_checks = all(check in content for check in checks)
        if all_checks:
            print(f"  {check_mark(True)} {channel} integration")
            passed += 1
        else:
            print(f"  {check_mark(False)} {channel} integration {Colors.RED}INCOMPLETE{Colors.RESET}")
            failed += 1
    else:
        print(f"  {check_mark(False)} {channel} integration {Colors.RED}FILE MISSING{Colors.RESET}")
        failed += 1

# =============================================================================
# 8. FRONTEND PAGES
# =============================================================================
section("8. Frontend Pages")

frontend_pages = {
    'Landing Page': 'frontend/app/page.tsx',
    'Login Page': 'frontend/app/login/page.tsx',
    'Signup Page': 'frontend/app/signup/page.tsx',
    'Dashboard': 'frontend/app/dashboard/page.tsx',
    'Support Form': 'frontend/app/dashboard/support/page.tsx',
    'Tickets List': 'frontend/app/dashboard/tickets/page.tsx',
    'Analytics': 'frontend/app/dashboard/analytics/page.tsx',
    'Customers': 'frontend/app/dashboard/customers/page.tsx',
    'Agent Chat': 'frontend/app/dashboard/agent/page.tsx',
}

for page, file_path in frontend_pages.items():
    if Path(file_path).exists():
        print(f"  {check_mark(True)} {page}")
        passed += 1
    else:
        print(f"  {check_mark(False)} {page} {Colors.RED}MISSING{Colors.RESET}")
        failed += 1

# =============================================================================
# 9. AUTHENTICATION
# =============================================================================
section("9. Authentication (Better Auth)")

auth_files = {
    'frontend/lib/auth.ts': 'Better Auth server configuration',
    'frontend/lib/auth-client.ts': 'Auth client for React',
    'frontend/app/api/auth/[...all]/route.ts': 'Auth API routes',
}

for file_path, description in auth_files.items():
    if Path(file_path).exists():
        print(f"  {check_mark(True)} {description}")
        passed += 1
    else:
        print(f"  {check_mark(False)} {description} {Colors.RED}MISSING{Colors.RESET}")
        failed += 1

# =============================================================================
# 10. MULTI-CHANNEL REQUIREMENTS
# =============================================================================
section("10. Multi-Channel Architecture")

multichannel_reqs = {
    'Email (Gmail) support': 'backend/src/channels/gmail_handler.py',
    'WhatsApp (Twilio) support': 'backend/src/channels/whatsapp_handler.py',
    'Web Form support': 'frontend/app/components/SupportForm.tsx',
    'Cross-channel customer ID': 'backend/agent/tools.py',
    'Channel-aware formatting': 'backend/agent/formatters.py',
}

for requirement, file_path in multichannel_reqs.items():
    if Path(file_path).exists():
        print(f"  {check_mark(True)} {requirement}")
        passed += 1
    else:
        print(f"  {check_mark(False)} {requirement} {Colors.RED}MISSING{Colors.RESET}")
        failed += 1

# =============================================================================
# 11. ESCALATION RULES
# =============================================================================
section("11. Escalation Rules")

tools_content = ''
if Path('backend/agent/tools.py').exists():
    try:
        tools_content = Path('backend/agent/tools.py').read_text(encoding='utf-8')
    except:
        tools_content = Path('backend/agent/tools.py').read_text(encoding='cp1252', errors='ignore')

escalation_triggers = {
    'Pricing inquiry escalation': 'pricing',
    'Legal threat escalation': 'legal',
    'Refund request escalation': 'refund',
    'Negative sentiment escalation': 'sentiment',
}

for trigger, keyword in escalation_triggers.items():
    if keyword.lower() in tools_content.lower():
        print(f"  {check_mark(True)} {trigger}")
        passed += 1
    else:
        print(f"  {check_mark(False)} {trigger} {Colors.RED}NOT FOUND{Colors.RESET}")
        failed += 1

# =============================================================================
# SUMMARY
# =============================================================================
section("VERIFICATION SUMMARY")

total = passed + failed
percentage = (passed / total * 100) if total > 0 else 0

print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")
print(f"  {Colors.YELLOW}Warnings: {warnings}{Colors.RESET}")
print(f"  {Colors.BOLD}Total: {total} checks ({percentage:.1f}% complete){Colors.RESET}")

print(f"\n{Colors.BOLD}Recommendation:{Colors.RESET}")

if failed == 0:
    print(f"  {Colors.GREEN}✓ READY FOR SUBMISSION!{Colors.RESET}")
    print(f"  All critical requirements are met.")
elif failed <= 5:
    print(f"  {Colors.YELLOW}⚠ ALMOST READY{Colors.RESET}")
    print(f"  Fix the {failed} failed checks before submitting.")
else:
    print(f"  {Colors.RED}✗ NOT READY FOR SUBMISSION{Colors.RESET}")
    print(f"  You have {failed} critical issues to fix.")

print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
print(f"1. Fix all {failed} failed checks")
print(f"2. Start PostgreSQL: docker-compose up -d postgres")
print(f"3. Setup database: cd backend && python setup_database.py")
print(f"4. Seed knowledge base: python database/seed_knowledge_base.py")
print(f"5. Start backend: python -m uvicorn api.main:app --reload")
print(f"6. Start frontend: cd frontend && npm run dev")
print(f"7. Test all channels work correctly")
print(f"8. Run this script again to verify")

print(f"\n{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

# Exit with error code if critical failures
sys.exit(1 if failed > 5 else 0)
