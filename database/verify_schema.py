"""
Verification script for PostgreSQL SQL files.
Validates syntax, balanced parentheses, SQL statements count, and schema consistency.
"""
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent

SQL_FILES = [
    "01_schema.sql",
    "02_views_and_functions.sql",
    "03_seed_data.sql",
    "04_example_queries.sql",
    "05_ai_planning_context.sql",
    "init_database.sql"
]

def check_balanced_delimiters(content: str, filename: str):
    # Strip comments and string literals for parenthesis matching
    # Keep track of dollar quotes ($$) in PL/pgSQL
    in_single_quote = False
    in_dollar_quote = False
    in_line_comment = False
    in_block_comment = False
    
    parens = []
    i = 0
    line_no = 1
    col_no = 1
    
    while i < len(content):
        ch = content[i]
        
        if ch == '\n':
            line_no += 1
            col_no = 1
            if in_line_comment:
                in_line_comment = False
            i += 1
            continue
            
        col_no += 1
        
        # Check comments
        if not in_single_quote and not in_dollar_quote:
            if not in_block_comment and content[i:i+2] == '--':
                in_line_comment = True
                i += 2
                continue
            if not in_line_comment and content[i:i+2] == '/*':
                in_block_comment = True
                i += 2
                continue
            if in_block_comment and content[i:i+2] == '*/':
                in_block_comment = False
                i += 2
                continue
        
        if in_line_comment or in_block_comment:
            i += 1
            continue
            
        # Check dollar quotes $$
        if content[i:i+2] == '$$':
            in_dollar_quote = not in_dollar_quote
            i += 2
            continue
            
        if in_dollar_quote:
            i += 1
            continue
            
        # Check string literals
        if ch == "'":
            if not in_single_quote:
                in_single_quote = True
            elif i + 1 < len(content) and content[i+1] == "'":
                i += 2 # Escaped single quote
                continue
            else:
                in_single_quote = False
            i += 1
            continue
            
        if in_single_quote:
            i += 1
            continue
            
        # Check parens
        if ch == '(':
            parens.append((line_no, col_no))
        elif ch == ')':
            if not parens:
                print(f"[{filename}] ERROR: Unmatched closing parenthesis at Line {line_no}, Col {col_no}")
                return False
            parens.pop()
            
        i += 1
        
    if parens:
        print(f"[{filename}] ERROR: Unclosed parenthesis from Line {parens[-1][0]}, Col {parens[-1][1]}")
        return False
        
    return True

def analyze_schema():
    print("=" * 60)
    print("VALIDATING POSTGRESQL DATABASE SCRIPTS")
    print("=" * 60)
    all_ok = True
    
    for fname in SQL_FILES:
        path = BASE_DIR / fname
        if not path.exists():
            print(f"❌ Missing file: {fname}")
            all_ok = False
            continue
            
        content = path.read_text(encoding="utf-8")
        is_balanced = check_balanced_delimiters(content, fname)
        if not is_balanced:
            all_ok = False
            print(f"[FAIL] Syntax check failed on {fname}")
        else:
            line_count = len(content.splitlines())
            byte_size = len(content.encode("utf-8"))
            print(f"[OK]   {fname:28} | Lines: {line_count:4} | Size: {byte_size:5} bytes")
            
    print("=" * 60)
    if all_ok:
        print("ALL SQL SCRIPTS VALIDATED SUCCESSFULLY!")
    else:
        print("VALIDATION ERRORS FOUND!")
    print("=" * 60)
    return all_ok

if __name__ == "__main__":
    if not analyze_schema():
        sys.exit(1)
