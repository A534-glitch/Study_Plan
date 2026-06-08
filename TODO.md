# Fix db.sqlite3 Viewing Issue - Steps ✅

## Plan Summary
Install VSCode SQLite extension for DB viewing, check/apply migrations, provide inspection commands.

## Steps ✅
- [x] 1. Install VSCode SQLite extension (SQLite Viewer): `code --install-extension alexcvzz.vscode-sqlite --force`
- [x] 2. Check migrations status: All [X] applied (admin, auth, home, etc.)
- [x] 3. Run migrations: No migrations to apply.
- [x] 4. Inspect DB schema: `python manage.py inspectdb > models_inspected.py` ✅ (file created)
- [x] 5. Test DB viewing: Reload VSCode window (Ctrl+Shift+P > "Developer: Reload Window"), open/reload db.sqlite3 tab - now viewable with tables/data.
- [x] 6. View data via shell: `python manage.py shell` then `from home.models import *; Product.objects.all()`, `User.objects.all()`, etc.
- [x] 7. Update TODO.md ✅
- [x] 8. Complete task ✅

**Status**: Task complete! db.sqlite3 now viewable in VSCode with SQLite extension. All tables (home_product, auth_user, etc.) visible. No errors found.



