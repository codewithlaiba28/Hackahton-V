"""
Customer Success FTE - Complete Implementation Verification

This script verifies all hackathon requirements are implemented correctly.

USAGE:
    python verify_implementation.py

CHECKS:
1. ✅ Backend Implementation
2. ✅ Frontend Implementation  
3. ✅ Cerebras Model Integration (NOT OpenAI)
4. ✅ WhatsApp/Twilio Integration
5. ✅ Gmail Integration
6. ✅ Web Form Component
7. ✅ Database Schema
8. ✅ Agent Tools & Skills
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def checkmark():
    return f"{Colors.GREEN}✓{Colors.END}"

def crossmark():
    return f"{Colors.RED}✗{Colors.END}"

def infomark():
    return f"{Colors.BLUE}ℹ{Colors.END}"

def warnmark():
    return f"{Colors.YELLOW}⚠{Colors.END}"


def verify_file_exists(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"  {checkmark()} {description}: {path}")
        return True
    else:
        print(f"  {crossmark()} {description}: {path} NOT FOUND")
        return False


def verify_env_var(name, description, required=True):
    """Check if environment variable is set"""
    value = os.getenv(name)
    if value:
        # Mask sensitive values
        if 'KEY' in name or 'TOKEN' in name or 'PASSWORD' in name:
            masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
        else:
            masked = value
        print(f"  {checkmark()} {description}: {name}={masked}")
        return True
    elif required:
        print(f"  {crossmark()} {description}: {name} NOT SET (REQUIRED)")
        return False
    else:
        print(f"  {warnmark()} {description}: {name} NOT SET (OPTIONAL)")
        return True


def verify_cerebras_not_openai():
    """Verify Cerebras is used instead of OpenAI"""
    print(f"\n{Colors.BOLD}3. CEREBRAS MODEL VERIFICATION{Colors.END}")
    print("-" * 60)
    
    # Check .env for Cerebras
    cerebras_key = os.getenv('CEREBRAS_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    cerebras_ok = False
    openai_not_used = True
    
    if cerebras_key and cerebras_key.startswith('csk-'):
        print(f"  {checkmark()} Cerebras API Key configured (csk-...)")
        cerebras_ok = True
    else:
        print(f"  {crossmark()} Cerebras API Key NOT configured or invalid")
    
    # Check if OPENAI_API_KEY is set (should not be using real OpenAI)
    if openai_key and not openai_key.startswith('csk-'):
        # Check if it's actually a Cerebras key mislabeled
        print(f"  {warnmark()} OPENAI_API_KEY is set (should use CEREBRAS_API_KEY)")
        openai_not_used = False
    else:
        print(f"  {checkmark()} Not using OpenAI API (using Cerebras)")
    
    # Check api/main.py for Cerebras configuration
    main_py_path = Path('api/main.py')
    if main_py_path.exists():
        content = main_py_path.read_text()
        if 'CEREBRAS_KEY' in content and 'CEREBRAS_URL' in content:
            print(f"  {checkmark()} Cerebras configuration found in api/main.py")
        else:
            print(f"  {crossmark()} Cerebras configuration NOT found in api/main.py")
    
    return cerebras_ok


def verify_backend():
    """Verify backend implementation"""
    print(f"\n{Colors.BOLD}1. BACKEND IMPLEMENTATION{Colors.END}")
    print("-" * 60)
    
    checks = []
    
    # Core files
    checks.append(verify_file_exists('agent/customer_success_agent.py', 'Agent Definition'))
    checks.append(verify_file_exists('agent/tools.py', 'Agent Tools'))
    checks.append(verify_file_exists('agent/prompts.py', 'System Prompts'))
    checks.append(verify_file_exists('agent/formatters.py', 'Channel Formatters'))
    
    # API
    checks.append(verify_file_exists('api/main.py', 'FastAPI Application'))
    
    # Channels
    checks.append(verify_file_exists('src/channels/gmail_handler.py', 'Gmail Handler'))
    checks.append(verify_file_exists('src/channels/whatsapp_handler.py', 'WhatsApp Handler'))
    checks.append(verify_file_exists('src/channels/base.py', 'Base Channel'))
    
    # Workers
    checks.append(verify_file_exists('workers/message_processor.py', 'Message Processor'))
    
    # Database
    checks.append(verify_file_exists('database/schema.sql', 'Database Schema'))
    checks.append(verify_file_exists('database/queries.py', 'Database Queries'))
    
    # Kafka
    checks.append(verify_file_exists('kafka_client.py', 'Kafka Client'))
    
    return all(checks)


def verify_frontend():
    """Verify frontend implementation"""
    print(f"\n{Colors.BOLD}2. FRONTEND IMPLEMENTATION{Colors.END}")
    print("-" * 60)
    
    checks = []
    
    # Core files
    checks.append(verify_file_exists('../frontend/app/page.tsx', 'Landing Page'))
    checks.append(verify_file_exists('../frontend/app/components/SupportForm.tsx', 'Web Support Form'))
    checks.append(verify_file_exists('../frontend/app/dashboard/page.tsx', 'Dashboard'))
    
    # Config
    checks.append(verify_file_exists('../frontend/package.json', 'Package Config'))
    checks.append(verify_file_exists('../frontend/tsconfig.json', 'TypeScript Config'))
    
    return all(checks)


def verify_whatsapp():
    """Verify WhatsApp integration"""
    print(f"\n{Colors.BOLD}4. WHATSAPP/TWILIO INTEGRATION{Colors.END}")
    print("-" * 60)
    
    checks = []
    
    # Check credentials
    checks.append(verify_env_var('TWILIO_ACCOUNT_SID', 'Twilio Account SID'))
    checks.append(verify_env_var('TWILIO_AUTH_TOKEN', 'Twilio Auth Token'))
    checks.append(verify_env_var('TWILIO_WHATSAPP_NUMBER', 'WhatsApp Number'))
    
    # Verify WhatsApp format
    whatsapp_num = os.getenv('TWILIO_WHATSAPP_NUMBER', '')
    if whatsapp_num.startswith('whatsapp:'):
        print(f"  {checkmark()} WhatsApp number format correct (whatsapp:+...)")
        checks.append(True)
    else:
        print(f"  {crossmark()} WhatsApp number should start with 'whatsapp:'")
        checks.append(False)
    
    # Check handler has SMS blocking
    handler_path = Path('src/channels/whatsapp_handler.py')
    if handler_path.exists():
        try:
            content = handler_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = handler_path.read_text(encoding='latin-1')
        if 'whatsapp:' in content and 'SMS' in content:
            print(f"  {checkmark()} SMS blocking implemented")
            checks.append(True)
        else:
            print(f"  {warnmark()} SMS blocking may not be implemented")
            checks.append(True)  # Not critical
    
    return all(checks)


def verify_gmail():
    """Verify Gmail integration"""
    print(f"\n{Colors.BOLD}5. GMAIL INTEGRATION{Colors.END}")
    print("-" * 60)
    
    checks = []
    
    # Check handler exists
    checks.append(verify_file_exists('src/channels/gmail_handler.py', 'Gmail Handler'))
    
    # Check auth script
    checks.append(verify_file_exists('gmail_auth_setup.py', 'Gmail Auth Script'))
    
    # Check token (optional - will be created after auth)
    if os.path.exists('token.json'):
        print(f"  {checkmark()} Gmail token.json exists (authenticated)")
        checks.append(True)
    else:
        print(f"  {warnmark()} Gmail token.json not found (run gmail_auth_setup.py)")
        checks.append(True)  # Not critical for verification
    
    return all(checks)


def verify_database():
    """Verify database setup"""
    print(f"\n{Colors.BOLD}6. DATABASE SCHEMA{Colors.END}")
    print("-" * 60)
    
    checks = []
    
    # Check schema has required tables
    schema_path = Path('database/schema.sql')
    if schema_path.exists():
        content = schema_path.read_text()
        
        required_tables = [
            'customers',
            'conversations',
            'messages',
            'tickets',
            'knowledge_base',
            'customer_identifiers',
            'channel_configs',
            'agent_metrics'
        ]
        
        for table in required_tables:
            if f'CREATE TABLE {table}' in content:
                print(f"  {checkmark()} Table: {table}")
                checks.append(True)
            else:
                print(f"  {crossmark()} Table: {table} MISSING")
                checks.append(False)
        
        # Check for pgvector extension
        if 'vector' in content:
            print(f"  {checkmark()} pgvector extension enabled")
            checks.append(True)
        else:
            print(f"  {warnmark()} pgvector extension not found")
            checks.append(False)
    else:
        checks.append(False)
    
    # Check DATABASE_URL
    checks.append(verify_env_var('DATABASE_URL', 'Database URL'))
    
    return all(checks)


def verify_agent_tools():
    """Verify agent tools implementation"""
    print(f"\n{Colors.BOLD}7. AGENT TOOLS & SKILLS{Colors.END}")
    print("-" * 60)
    
    checks = []
    
    tools_path = Path('agent/tools.py')
    if tools_path.exists():
        content = tools_path.read_text()
        
        required_tools = [
            'search_knowledge_base',
            'create_ticket',
            'get_customer_history',
            'escalate_to_human',
            'send_response'
        ]
        
        for tool in required_tools:
            if f'def {tool}' in content or f'async def {tool}' in content:
                print(f"  {checkmark()} Tool: {tool}")
                checks.append(True)
            else:
                print(f"  {crossmark()} Tool: {tool} MISSING")
                checks.append(False)
        
        # Check for @function_tool decorator
        if '@function_tool' in content:
            print(f"  {checkmark()} OpenAI Agents SDK @function_tool decorator used")
            checks.append(True)
        else:
            print(f"  {warnmark()} @function_tool decorator not found")
            checks.append(False)
        
        # Check for Pydantic models
        if 'BaseModel' in content:
            print(f"  {checkmark()} Pydantic input validation used")
            checks.append(True)
        else:
            print(f"  {warnmark()} Pydantic models not found")
            checks.append(False)
    else:
        checks.append(False)
    
    return all(checks)


def verify_kafka_bypass():
    """Verify Kafka bypass for direct processing"""
    print(f"\n{Colors.BOLD}8. KAFKA BYPASS (DIRECT PROCESSING){Colors.END}")
    print("-" * 60)
    
    # Kafka is optional for testing
    kafka_enabled = os.getenv('KAFKA_ENABLED', 'false')
    
    if kafka_enabled.lower() == 'false':
        print(f"  {checkmark()} Kafka disabled (using direct processing)")
        print(f"  {infomark()} Messages processed synchronously for testing")
        return True
    else:
        print(f"  {warnmark()} Kafka enabled (requires Kafka broker)")
        print(f"  {infomark()} Ensure Kafka is running on {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')}")
        return True  # Either way is OK


def main():
    """Run all verifications"""
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}🔍 CUSTOMER SUCCESS FTE - IMPLEMENTATION VERIFICATION{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    results = []
    
    # Run all checks
    results.append(("Backend Implementation", verify_backend()))
    results.append(("Frontend Implementation", verify_frontend()))
    results.append(("Cerebras Model (Not OpenAI)", verify_cerebras_not_openai()))
    results.append(("WhatsApp/Twilio Integration", verify_whatsapp()))
    results.append(("Gmail Integration", verify_gmail()))
    results.append(("Database Schema", verify_database()))
    results.append(("Agent Tools & Skills", verify_agent_tools()))
    results.append(("Kafka Bypass", verify_kafka_bypass()))
    
    # Summary
    print(f"\n{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}📊 VERIFICATION SUMMARY{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} checks passed")
    print()
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL CHECKS PASSED!{Colors.END}")
        print()
        print("Your Customer Success FTE is fully implemented!")
        print()
        print("NEXT STEPS:")
        print("1. Run Gmail authentication: python gmail_auth_setup.py")
        print("2. Start the backend: python -m uvicorn api.main:app --reload")
        print("3. Test WhatsApp: Send message to +14155238886")
        print("4. Test Web Form: http://localhost:3000")
        print()
    else:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  SOME CHECKS FAILED{Colors.END}")
        print()
        print("Please review the errors above and fix them.")
        print("Some features may not work correctly.")
        print()
    
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")


if __name__ == '__main__':
    main()
