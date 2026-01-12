# -*- coding: utf-8 -*-
"""
Import Framework Skills to Platform Database
"""
import sys
from pathlib import Path

# Path configuration
current_file = Path(__file__).resolve()
backend_path = current_file.parent.parent  # backend/
project_root = backend_path.parent.parent.parent  # LingNexus/
framework_path = project_root / "packages" / "framework"

sys.path.insert(0, str(backend_path))
sys.path.insert(0, str(framework_path))

import yaml
from sqlalchemy import create_engine, text
from db.models import Base

# Database path
DB_PATH = backend_path / "lingnexus_platform_new.db"


def create_database():
    """Create new database"""
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(bind=engine)
    return engine


def import_skills(engine):
    """Import skills"""

    # Get skills directory
    skills_dir = framework_path / "skills"

    if not skills_dir.exists():
        print(f"[ERROR] Skills directory not found: {skills_dir}")
        return 0

    count = 0

    # Import external skills
    external_dir = skills_dir / "external"
    if external_dir.exists():
        count += import_from_directory(engine, external_dir, "external")

    # Import internal skills
    internal_dir = skills_dir / "internal"
    if internal_dir.exists():
        count += import_from_directory(engine, internal_dir, "internal")

    return count


def import_from_directory(engine, directory: Path, category: str) -> int:
    """Import skills from directory"""

    print(f"\n[Importing {category} skills...]")

    with engine.connect() as conn:
        count = 0

        for skill_path in directory.iterdir():
            if not skill_path.is_dir():
                continue

            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                continue

            try:
                # Read skill file (full content, including YAML front matter)
                full_content = skill_md.read_text(encoding="utf-8")

                # Parse YAML front matter (for meta field, but keep full content)
                meta = {}
                if full_content.startswith("---"):
                    parts = full_content.split("---", 2)
                    if len(parts) >= 3:
                        try:
                            meta = yaml.safe_load(parts[1]) or {}
                        except:
                            pass

                # Build skill data
                import json
                skill_data = {
                    "name": skill_path.name,
                    "category": category,
                    "content": full_content,  # Store full content with YAML front matter
                    "meta": json.dumps(meta) if meta else None,  # Convert to JSON string
                    "is_active": True,
                    "version": "1.0.0",
                    "created_by": 1,  # Default user ID
                    "sharing_scope": "public",  # Public
                    "is_official": True,
                    "usage_count": 0,
                    "rating": None,
                    "rating_count": 0,
                    "department": None,
                    "documentation": None,
                }

                # Insert data
                from datetime import datetime
                skill_data["created_at"] = datetime.utcnow()
                skill_data["updated_at"] = datetime.utcnow()

                conn.execute(text("""
                    INSERT INTO skills (
                        name, category, content, meta, is_active, version, created_by,
                        sharing_scope, department, is_official, usage_count, rating, rating_count, documentation,
                        created_at, updated_at
                    ) VALUES (
                        :name, :category, :content, :meta, :is_active, :version, :created_by,
                        :sharing_scope, :department, :is_official, :usage_count, :rating, :rating_count, :documentation,
                        :created_at, :updated_at
                    )
                """), skill_data)

                count += 1
                print(f"  [OK] {skill_path.name}")

            except Exception as e:
                print(f"  [FAIL] {skill_path.name}: {e}")

        conn.commit()
        print(f"[OK] Imported {count} {category} skills")
        return count


def show_statistics(engine):
    """Show statistics"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM skills"))
        total = result.scalar()

        result = conn.execute(text("SELECT COUNT(*) FROM skills WHERE category = 'external'"))
        external = result.scalar()

        result = conn.execute(text("SELECT COUNT(*) FROM skills WHERE category = 'internal'"))
        internal = result.scalar()

        result = conn.execute(text("SELECT COUNT(*) FROM skills WHERE sharing_scope = 'public'"))
        public = result.scalar()

        print(f"\n[Statistics]")
        print(f"  Total: {total}")
        print(f"  External skills: {external}")
        print(f"  Internal skills: {internal}")
        print(f"  Public skills: {public}")


if __name__ == "__main__":
    print("=" * 60)
    print("LingNexus Platform - Skill Import Tool")
    print("=" * 60)

    # Create new database
    print("\n[1/3] Creating new database...")
    engine = create_database()
    print(f"[OK] Database created: {DB_PATH}")

    # Import skills
    print("\n[2/3] Importing skills...")
    count = import_skills(engine)
    print(f"\n[OK] Successfully imported {count} skills!")

    # Show statistics
    show_statistics(engine)

    # Next steps
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print(f"1. New database created: {DB_PATH}")
    print("2. Update database configuration:")
    print(f"   Edit db/session.py and change DATABASE_URL to:")
    print(f"   sqlite:///{DB_PATH.name}")
    print("3. Restart backend server")
    print("4. Visit http://localhost:5173/marketplace")
    print("=" * 60)

    engine.dispose()
