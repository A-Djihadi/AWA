import os
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / '.env')

supabase = create_client(
    os.getenv('SUPABASE_URL'), 
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Récupérer des exemples
offers = supabase.table('offers').select('*').limit(10).execute()

print("\n📋 Valeurs existantes dans la BDD:\n")

# Contract types
contract_types = set(o.get('contract_type') for o in offers.data if o.get('contract_type'))
print(f"✅ contract_type valides: {contract_types}")

# Remote policies  
remote_policies = set(o.get('remote_policy') for o in offers.data if o.get('remote_policy'))
print(f"✅ remote_policy valides: {remote_policies}")

# Seniority levels
seniority_levels = set(o.get('seniority_level') for o in offers.data if o.get('seniority_level'))
print(f"✅ seniority_level valides: {seniority_levels}\n")
