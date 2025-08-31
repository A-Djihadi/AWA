#!/usr/bin/env python3
"""
AWA Environment Configuration Manager
Utilitaire pour gérer et synchroniser les configurations .env across services
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class EnvConfigManager:
    """Gestionnaire de configuration d'environnement AWA"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.shared_env_path = self.project_root / ".env.shared"
        self.services_dir = self.project_root / "services"
        
        # Services avec leurs configurations spécifiques
        self.services = {
            "scraper": {
                "path": self.services_dir / "scraper",
                "template": "scraper.env.template",
                "env_files": [".env"],
                "specific_vars": [
                    "SCRAPY_",
                    "SCRAPER_",
                    "HTTP_PROXY",
                    "HTTPS_PROXY",
                    "SENTRY_DSN"
                ]
            },
            "etl": {
                "path": self.services_dir / "etl", 
                "template": "etl.env.template",
                "env_files": [".env"],
                "specific_vars": [
                    "ETL_",
                    "BATCH_SIZE",
                    "PARALLEL_WORKERS"
                ]
            },
            "frontend": {
                "path": self.services_dir / "frontend",
                "template": "frontend.env.template",
                "env_files": [".env.local", ".env"],
                "specific_vars": [
                    "NEXT_PUBLIC_",
                    "NODE_ENV",
                    "NEXT_",
                    "GA_"
                ]
            }
        }
        
    def load_shared_config(self) -> Dict[str, str]:
        """Charge la configuration partagée"""
        shared_config = {}
        
        if not self.shared_env_path.exists():
            print(f"⚠️  Fichier de configuration partagée introuvable: {self.shared_env_path}")
            return shared_config
            
        with open(self.shared_env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    shared_config[key.strip()] = value.strip()
                    
        return shared_config
        
    def load_service_config(self, service_name: str) -> Dict[str, str]:
        """Charge la configuration d'un service spécifique"""
        service_config = {}
        service_info = self.services.get(service_name)
        
        if not service_info:
            return service_config
            
        # Utiliser les fichiers .env spécifiés pour ce service
        env_files = []
        for env_file_name in service_info.get("env_files", [".env"]):
            env_files.append(service_info["path"] / env_file_name)
        
        for env_file in env_files:
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            service_config[key.strip()] = value.strip()
                            
        return service_config
        
    def validate_configuration(self) -> bool:
        """Valide la cohérence des configurations"""
        print("🔍 Validation des configurations...")
        
        shared_config = self.load_shared_config()
        issues = []
        
        # Configuration des variables requises par service
        service_requirements = {
            "scraper": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"],
            "etl": ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"], 
            "frontend": ["NEXT_PUBLIC_SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]
        }
        
        for service_name, service_info in self.services.items():
            service_config = self.load_service_config(service_name)
            required_vars = service_requirements.get(service_name, [])
            
            for var in required_vars:
                if var not in service_config:
                    issues.append(f"❌ {service_name}: Variable manquante {var}")
                elif var.startswith("NEXT_PUBLIC_"):
                    # Pour les variables frontend, vérifier contre la version non-préfixée
                    base_var = var.replace("NEXT_PUBLIC_", "")
                    if base_var in shared_config and service_config[var] != shared_config[base_var]:
                        issues.append(f"⚠️  {service_name}: {var} diffère de la config partagée")
                elif var in shared_config and service_config[var] != shared_config[var]:
                    issues.append(f"⚠️  {service_name}: {var} diffère de la config partagée")
                    
        if issues:
            print("🚨 Problèmes détectés:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("✅ Toutes les configurations sont cohérentes!")
            return True
            
    def sync_configurations(self, dry_run: bool = False):
        """Synchronise les configurations à partir du fichier partagé"""
        print("🔄 Synchronisation des configurations...")
        
        shared_config = self.load_shared_config()
        
        if not shared_config:
            print("❌ Impossible de charger la configuration partagée")
            return
            
        for service_name, service_info in self.services.items():
            service_path = service_info["path"]
            env_file = service_path / ".env"
            
            print(f"📝 Traitement de {service_name}...")
            
            if dry_run:
                print(f"  [DRY RUN] Mise à jour de {env_file}")
                continue
                
            # Backup du fichier existant
            if env_file.exists():
                backup_file = env_file.with_suffix('.env.backup')
                shutil.copy2(env_file, backup_file)
                print(f"  💾 Backup créé: {backup_file}")
                
            # Charger la config actuelle du service
            current_service_config = self.load_service_config(service_name)
            
            # Merger les configurations
            merged_config = {**shared_config}
            
            # Garder les variables spécifiques au service
            for key, value in current_service_config.items():
                if any(key.startswith(prefix) for prefix in service_info["specific_vars"]):
                    merged_config[key] = value
                    
            # Écrire la nouvelle configuration
            self._write_env_file(env_file, merged_config, service_name)
            print(f"  ✅ {env_file} mis à jour")
            
    def _write_env_file(self, file_path: Path, config: Dict[str, str], service_name: str):
        """Écrit un fichier .env avec formatage"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# ================================================\n")
            f.write(f"# {service_name.upper()} ENVIRONMENT CONFIGURATION\n")
            f.write(f"# ================================================\n")
            f.write(f"# Auto-generated by AWA Config Manager\n")
            f.write(f"# Source: ../../.env.shared + service-specific variables\n\n")
            
            # Grouper les variables par catégorie
            categories = {
                "SUPABASE": ["SUPABASE_"],
                "SERVICE_SPECIFIC": self.services[service_name]["specific_vars"],
                "GENERAL": []
            }
            
            written_keys = set()
            
            for category, prefixes in categories.items():
                if category == "GENERAL":
                    # Écrire le reste des variables
                    remaining_keys = [k for k in config.keys() if k not in written_keys]
                    if remaining_keys:
                        f.write(f"# {category} CONFIGURATION\n")
                        f.write(f"# ================================================\n")
                        for key in sorted(remaining_keys):
                            f.write(f"{key}={config[key]}\n")
                        f.write("\n")
                else:
                    # Écrire les variables de cette catégorie
                    category_keys = []
                    for key in config.keys():
                        if any(key.startswith(prefix) for prefix in prefixes):
                            category_keys.append(key)
                            
                    if category_keys:
                        f.write(f"# {category} CONFIGURATION\n")
                        f.write(f"# ================================================\n")
                        for key in sorted(category_keys):
                            f.write(f"{key}={config[key]}\n")
                            written_keys.add(key)
                        f.write("\n")
                        
    def generate_examples(self):
        """Génère les fichiers .env.example pour tous les services"""
        print("📋 Génération des fichiers .env.example...")
        
        for service_name, service_info in self.services.items():
            service_path = service_info["path"]
            example_file = service_path / ".env.example"
            env_file = service_path / ".env"
            
            if env_file.exists():
                # Lire le .env existant et créer l'example
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Masquer les valeurs sensibles
                example_content = self._mask_sensitive_values(content)
                
                with open(example_file, 'w', encoding='utf-8') as f:
                    f.write(example_content)
                    
                print(f"  ✅ {example_file} généré")
                
    def _mask_sensitive_values(self, content: str) -> str:
        """Masque les valeurs sensibles dans le contenu"""
        lines = content.split('\n')
        masked_lines = []
        
        sensitive_patterns = [
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_ANON_KEY", 
            "SUPABASE_URL",
            "PASSWORD",
            "SECRET",
            "TOKEN",
            "KEY",
            "DSN"
        ]
        
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                key = key.strip()
                
                if any(pattern in key.upper() for pattern in sensitive_patterns):
                    if "URL" in key.upper():
                        masked_lines.append(f"{key}=https://your-project.supabase.co")
                    else:
                        masked_lines.append(f"{key}=your_{key.lower()}")
                else:
                    masked_lines.append(line)
            else:
                masked_lines.append(line)
                
        return '\n'.join(masked_lines)


def main():
    parser = argparse.ArgumentParser(description="AWA Environment Configuration Manager")
    parser.add_argument("action", choices=["validate", "sync", "examples", "status"], 
                       help="Action à effectuer")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Mode simulation (ne modifie pas les fichiers)")
    
    args = parser.parse_args()
    
    manager = EnvConfigManager()
    
    if args.action == "validate":
        manager.validate_configuration()
    elif args.action == "sync":
        manager.sync_configurations(dry_run=args.dry_run)
    elif args.action == "examples":
        manager.generate_examples()
    elif args.action == "status":
        print("📊 Status des configurations:")
        shared_config = manager.load_shared_config()
        print(f"  📂 Config partagée: {len(shared_config)} variables")
        
        for service_name in manager.services.keys():
            service_config = manager.load_service_config(service_name)
            print(f"  🔧 {service_name}: {len(service_config)} variables")


if __name__ == "__main__":
    main()
