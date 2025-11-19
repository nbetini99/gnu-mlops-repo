#!/usr/bin/env python3
"""
Launch MLflow UI with different backend options
Author: Narsimha Betini
Usage: python scripts/launch_mlflow_ui.py [--backend databricks|sqlite] [--port 5000]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def launch_mlflow_ui(backend='databricks', port=5000):
    """
    Launch MLflow UI with specified backend
    
    Args:
        backend: 'databricks' or 'sqlite'
        port: Port number for MLflow UI
    """
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     🚀 Launching MLflow UI                                    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    if backend.lower() in ['databricks', 'db']:
        print("📊 Using Databricks MLflow tracking...")
        print("   Make sure DATABRICKS_HOST and DATABRICKS_TOKEN are set")
        print()
        
        cmd = ['mlflow', 'ui', '--port', str(port), '--host', '0.0.0.0']
        
    elif backend.lower() in ['sqlite', 'local', 'sql']:
        print("📊 Using SQLite MLflow tracking (local)...")
        print()
        
        # Find MLflow database
        base_dir = Path.cwd()
        db_path = base_dir / 'mlflow.db'
        
        if not db_path.exists():
            print(f"⚠️  Warning: mlflow.db not found in {base_dir}")
            print("   Will create new database on first run")
        
        db_uri = f"sqlite:///{db_path.absolute()}"
        artifacts_dir = base_dir / 'mlruns'
        artifacts_dir.mkdir(exist_ok=True)
        
        print(f"   Database: {db_uri}")
        print(f"   Artifacts: {artifacts_dir.absolute()}")
        print()
        
        cmd = [
            'mlflow', 'ui',
            '--backend-store-uri', db_uri,
            '--default-artifact-root', str(artifacts_dir.absolute()),
            '--port', str(port),
            '--host', '0.0.0.0'
        ]
    else:
        print(f"❌ Invalid backend option: {backend}")
        print()
        print("Usage: python scripts/launch_mlflow_ui.py [--backend databricks|sqlite] [--port 5000]")
        print()
        print("Options:")
        print("  --backend databricks|sqlite  - Backend to use (default: databricks)")
        print("  --port PORT                  - Port number (default: 5000)")
        print()
        print("Examples:")
        print("  python scripts/launch_mlflow_ui.py --backend databricks")
        print("  python scripts/launch_mlflow_ui.py --backend sqlite")
        print("  python scripts/launch_mlflow_ui.py --backend sqlite --port 5001")
        sys.exit(1)
    
    print(f"🌐 Starting MLflow UI on http://localhost:{port}")
    print("   Press Ctrl+C to stop")
    print()
    print("="*70)
    print()
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\n✓ MLflow UI stopped")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error launching MLflow UI: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Launch MLflow UI with different backend options',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/launch_mlflow_ui.py --backend databricks
  python scripts/launch_mlflow_ui.py --backend sqlite
  python scripts/launch_mlflow_ui.py --backend sqlite --port 5001
        """
    )
    
    parser.add_argument(
        '--backend',
        type=str,
        default='databricks',
        choices=['databricks', 'sqlite', 'db', 'local', 'sql'],
        help='Backend to use: databricks (default) or sqlite'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port number for MLflow UI (default: 5000)'
    )
    
    args = parser.parse_args()
    launch_mlflow_ui(backend=args.backend, port=args.port)

if __name__ == '__main__':
    main()

