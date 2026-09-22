"""
Módulo de Gerenciamento do Banco de Dados (db_manager.py)
Ideal para iniciantes: centraliza a conexão SQLite, inicialização e execução de queries.
"""
import sqlite3
import os
from pathlib import Path

# Caminhos dos arquivos essenciais
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "smartstock.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
SEED_PATH = DB_DIR / "seed.sql"

def get_connection():
    """
    Retorna uma conexão configurada com o SQLite.
    Habilita suporte a chaves estrangeiras e retorno de linhas como dicionários.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(force: bool = False):
    """
    Inicializa o banco de dados criando as tabelas e inserindo os dados de teste (seed).
    Se o banco já existir e force=False, não recria para não perder novos dados.
    """
    db_exists = DB_PATH.exists()
    
    if force and db_exists:
        os.remove(DB_PATH)
        db_exists = False

    if not db_exists:
        print(f"[*] Criando e inicializando banco de dados em: {DB_PATH}")
        with get_connection() as conn:
            # 1. Executa o schema
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            
            # 2. Executa o seed
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
            
            conn.commit()
        print("[+] Banco de dados inicializado com sucesso com dados de exemplo!")
    else:
        print(f"[i] Banco de dados já existente em: {DB_PATH}")

def query_all(sql: str, params: tuple = ()):
    """Executa uma consulta SELECT e retorna uma lista de dicionários."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def query_one(sql: str, params: tuple = ()):
    """Executa uma consulta SELECT e retorna um único registro como dicionário ou None."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

def execute_commit(sql: str, params: tuple = ()):
    """Executa um comando INSERT, UPDATE ou DELETE e retorna o lastrowid."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
