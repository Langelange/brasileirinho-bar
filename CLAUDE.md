# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Desktop bar tab management system (sistema de comandas) built with Python, CustomTkinter, and SQLite. Targets Windows as a single `.exe` via PyInstaller. Replaces manual notebook-based tracking for events and daily bar operations.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Build Windows executable (outputs dist/BrasileirinhoBar.exe)
python build.py
```

## Architecture

Two-file application — no frameworks, no routing, no config files beyond requirements.txt.

- **`main.py`** — Single `App(ctk.CTk)` class (~900 lines) containing the entire GUI. Four tabs built by `_montar_aba_*` methods: Comandas (L155), Produtos (L518), Clientes (L665), Relatorios (L796). Uses tkinter `ttk.Treeview` for tables with custom dark theme styling. All UI state is instance variables on the App class.

- **`database.py`** — Pure functions wrapping SQLite queries. No ORM. Each function opens/closes its own connection (`get_connection()`). `init_db()` creates all tables and seeds default categories on first run.

- **`build.py`** — PyInstaller build script. Bundles `assets/` and the `customtkinter` package into a single `--onefile --windowed` executable.

## Database Schema (SQLite — `brasileirinho.db`)

Five tables: `categorias`, `produtos`, `clientes`, `comandas`, `itens_comanda`. Foreign keys enforced via `PRAGMA foreign_keys = ON`. Products use soft-delete (`ativo` flag). Comandas have status `aberta`/`fechada`.

## Key Design Decisions

- **DB path logic**: When running as `.exe` (frozen), the database file is created next to the executable, not inside the temp extraction folder. Assets use `sys._MEIPASS` for the bundled read-only copy.
- **No connection pooling**: Every database function creates and closes its own connection. This is intentional for simplicity in a single-user desktop app.
- **All Portuguese**: UI labels, database columns, function names, and variable names are in Portuguese. Maintain this convention.
- **Theme colors**: Hardcoded constants at the top of `main.py` (COR_FUNDO, COR_VERDE, COR_AMARELO, etc.) — derived from the bar's logo.
- **Payment methods**: Hardcoded as "Dinheiro", "PIX", "Cartao" in the UI.
