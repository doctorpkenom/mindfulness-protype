"""
Display detailed information about the database.
Shows all tables, their schemas, row counts, and sample data.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, init_db
from backend.db_models import (
    User, Interaction, Simulation, ModelPerformance,
    ResearchModule, SystemLog, Account, Task, Schedule,
    ScheduleItem, TimerSession, UserMLWeights
)
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from backend.database import SessionLocal

def show_table_info(table_name, model_class):
    """Show detailed info about a table."""
    print(f"\n{'='*70}")
    print(f"Table: {table_name}")
    print('='*70)
    
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    
    print("\nColumns:")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col.get('default') else ""
        print(f"  - {col['name']:30} {str(col['type']):25} {nullable}{default}")
    
    # Get row count
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        print(f"\nRow Count: {count}")
    
    # Show sample data if any
    if count > 0:
        db = SessionLocal()
        try:
            records = db.query(model_class).limit(5).all()
            print(f"\nSample Data (showing up to 5 rows):")
            for i, record in enumerate(records, 1):
                print(f"\n  Row {i}:")
                # Get all attributes
                attrs = {key: getattr(record, key) for key in dir(record) 
                        if not key.startswith('_') and not callable(getattr(record, key, None))}
                # Filter to only show actual column values
                for key, value in attrs.items():
                    if not key.startswith('_') and not callable(value):
                        # Truncate long values
                        if isinstance(value, str) and len(value) > 50:
                            value = value[:50] + "..."
                        elif isinstance(value, (dict, list)):
                            value = str(value)[:50] + "..." if len(str(value)) > 50 else value
                        print(f"    {key}: {value}")
        except Exception as e:
            print(f"  Error reading data: {e}")
        finally:
            db.close()

def main():
    """Show all database information."""
    print("="*70)
    print("DATABASE DETAILS - Productivity Assistant")
    print("="*70)
    print(f"\nDatabase File: {os.path.abspath('mindfulness.db')}")
    print(f"File Size: {os.path.getsize('mindfulness.db') / 1024:.2f} KB")
    
    # Get all tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\nTotal Tables: {len(tables)}")
    print("\nTable List:")
    for table in sorted(tables):
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
        print(f"  - {table:30} ({count} rows)")
    
    # Show details for each table
    table_models = {
        'accounts': Account,
        'tasks': Task,
        'schedules': Schedule,
        'schedule_items': ScheduleItem,
        'timer_sessions': TimerSession,
        'user_ml_weights': UserMLWeights,
        'users': User,
        'interactions': Interaction,
        'simulations': Simulation,
        'model_performance': ModelPerformance,
        'research_modules': ResearchModule,
        'system_logs': SystemLog,
    }
    
    for table_name in sorted(tables):
        if table_name in table_models:
            show_table_info(table_name, table_models[table_name])
        else:
            print(f"\n{'='*70}")
            print(f"Table: {table_name} (no model class found)")
            print('='*70)
    
    # Show relationships summary
    print(f"\n{'='*70}")
    print("RELATIONSHIPS SUMMARY")
    print('='*70)
    
    db = SessionLocal()
    try:
        account_count = db.query(Account).count()
        task_count = db.query(Task).count()
        schedule_count = db.query(Schedule).count()
        timer_count = db.query(TimerSession).count()
        
        print(f"\nAccounts: {account_count}")
        print(f"Tasks: {task_count}")
        print(f"Schedules: {schedule_count}")
        print(f"Timer Sessions: {timer_count}")
        
        if account_count > 0:
            print(f"\nRecent Accounts:")
            accounts = db.query(Account).order_by(Account.created_at.desc()).limit(5).all()
            for acc in accounts:
                print(f"  - {acc.username} ({acc.email}) - Created: {acc.created_at}")
        
        if task_count > 0:
            print(f"\nRecent Tasks:")
            tasks = db.query(Task).order_by(Task.created_at.desc()).limit(5).all()
            for task in tasks:
                print(f"  - {task.title} (Status: {task.status}, Est: {task.estimated_minutes}m)")
    finally:
        db.close()
    
    print(f"\n{'='*70}")
    print("END OF DATABASE REPORT")
    print('='*70)

if __name__ == "__main__":
    main()
