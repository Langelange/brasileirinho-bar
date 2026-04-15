import sqlite3
import os
import sys
import shutil
import re
from datetime import datetime


def _resolver_caminho_banco():
    if getattr(sys, 'frozen', False):
        # Windows: usar %APPDATA%/BrasileirinhoBar/ (sempre gravavel)
        appdata = os.environ.get("APPDATA")
        if appdata:
            pasta = os.path.join(appdata, "BrasileirinhoBar")
        else:
            # Fallback: pasta do executavel (Linux ou APPDATA nao definido)
            pasta = os.path.dirname(sys.executable)
    else:
        # Modo desenvolvimento: pasta do projeto
        pasta = os.path.dirname(os.path.abspath(__file__))

    os.makedirs(pasta, exist_ok=True)
    return os.path.join(pasta, "brasileirinho.db")


DB_PATH = _resolver_caminho_banco()


def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        raise RuntimeError(
            f"Nao foi possivel acessar o banco de dados.\n"
            f"Caminho: {DB_PATH}\n"
            f"Erro: {e}"
        )


def init_db():
    try:
        conn = get_connection()
    except RuntimeError:
        raise
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria_id INTEGER,
            preco REAL NOT NULL DEFAULT 0,
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS comandas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            status TEXT NOT NULL DEFAULT 'aberta',
            forma_pagamento TEXT,
            desconto REAL DEFAULT 0,
            observacao TEXT,
            aberta_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fechada_em TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        );

        CREATE TABLE IF NOT EXISTS itens_comanda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comanda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 1,
            preco_unitario REAL NOT NULL,
            adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (comanda_id) REFERENCES comandas(id),
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        );
    """)

    # Inserir categorias padrão se tabela estiver vazia
    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        categorias_padrao = [
            "Cerveja", "Dose", "Drink", "Refrigerante",
            "Água", "Energético", "Petisco", "Porção", "Outro"
        ]
        cursor.executemany(
            "INSERT INTO categorias (nome) VALUES (?)",
            [(c,) for c in categorias_padrao]
        )

    conn.commit()
    conn.close()


# --- Produtos ---

def listar_produtos(apenas_ativos=True):
    conn = get_connection()
    filtro = "WHERE p.ativo = 1" if apenas_ativos else ""
    rows = conn.execute(f"""
        SELECT p.id, p.nome, p.preco, p.ativo, c.nome as categoria
        FROM produtos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        {filtro}
        ORDER BY c.nome, p.nome
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def salvar_produto(nome, categoria_id, preco, produto_id=None):
    conn = get_connection()
    if produto_id:
        conn.execute(
            "UPDATE produtos SET nome=?, categoria_id=?, preco=? WHERE id=?",
            (nome, categoria_id, preco, produto_id)
        )
    else:
        conn.execute(
            "INSERT INTO produtos (nome, categoria_id, preco) VALUES (?, ?, ?)",
            (nome, categoria_id, preco)
        )
    conn.commit()
    conn.close()


def excluir_produto(produto_id):
    conn = get_connection()
    conn.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (produto_id,))
    conn.commit()
    conn.close()


# --- Categorias ---

def listar_categorias():
    conn = get_connection()
    rows = conn.execute("SELECT id, nome FROM categorias ORDER BY nome").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def salvar_categoria(nome, categoria_id=None):
    conn = get_connection()
    if categoria_id:
        conn.execute("UPDATE categorias SET nome=? WHERE id=?", (nome, categoria_id))
    else:
        conn.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
    conn.commit()
    conn.close()


# --- Clientes ---

def listar_clientes(busca=""):
    conn = get_connection()
    if busca:
        rows = conn.execute(
            "SELECT * FROM clientes WHERE nome LIKE ? OR telefone LIKE ? ORDER BY nome",
            (f"%{busca}%", f"%{busca}%")
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def salvar_cliente(nome, telefone, cliente_id=None):
    conn = get_connection()
    if cliente_id:
        conn.execute(
            "UPDATE clientes SET nome=?, telefone=? WHERE id=?",
            (nome, telefone, cliente_id)
        )
    else:
        conn.execute(
            "INSERT INTO clientes (nome, telefone) VALUES (?, ?)",
            (nome, telefone)
        )
    conn.commit()
    conn.close()


def excluir_cliente(cliente_id):
    conn = get_connection()
    conn.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()


# --- Comandas ---

def abrir_comanda(cliente_id=None):
    conn = get_connection()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.execute(
        "INSERT INTO comandas (cliente_id, aberta_em) VALUES (?, ?)", (cliente_id, agora)
    )
    comanda_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return comanda_id


def listar_comandas(status="aberta"):
    conn = get_connection()
    rows = conn.execute("""
        SELECT c.id, c.status, c.aberta_em, c.fechada_em, c.forma_pagamento,
               c.desconto, c.observacao, cl.nome as cliente_nome, cl.telefone,
               COALESCE(SUM(ic.quantidade * ic.preco_unitario), 0) as total
        FROM comandas c
        LEFT JOIN clientes cl ON c.cliente_id = cl.id
        LEFT JOIN itens_comanda ic ON ic.comanda_id = c.id
        WHERE c.status = ?
        GROUP BY c.id
        ORDER BY c.aberta_em DESC
    """, (status,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fechar_comanda(comanda_id, forma_pagamento, desconto=0, observacao=""):
    conn = get_connection()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        UPDATE comandas
        SET status='fechada', forma_pagamento=?, desconto=?,
            observacao=?, fechada_em=?
        WHERE id=?
    """, (forma_pagamento, desconto, observacao, agora, comanda_id))
    conn.commit()
    conn.close()


def get_comanda(comanda_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT c.*, cl.nome as cliente_nome, cl.telefone
        FROM comandas c
        LEFT JOIN clientes cl ON c.cliente_id = cl.id
        WHERE c.id = ?
    """, (comanda_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# --- Itens da Comanda ---

def adicionar_item(comanda_id, produto_id, quantidade, preco_unitario):
    conn = get_connection()
    conn.execute("""
        INSERT INTO itens_comanda (comanda_id, produto_id, quantidade, preco_unitario)
        VALUES (?, ?, ?, ?)
    """, (comanda_id, produto_id, quantidade, preco_unitario))
    conn.commit()
    conn.close()


def listar_itens_comanda(comanda_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT ic.id, ic.quantidade, ic.preco_unitario, p.nome as produto_nome,
               (ic.quantidade * ic.preco_unitario) as subtotal
        FROM itens_comanda ic
        JOIN produtos p ON ic.produto_id = p.id
        WHERE ic.comanda_id = ?
        ORDER BY ic.adicionado_em
    """, (comanda_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def remover_item(item_id):
    conn = get_connection()
    conn.execute("DELETE FROM itens_comanda WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def total_comanda(comanda_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT COALESCE(SUM(quantidade * preco_unitario), 0) as total
        FROM itens_comanda WHERE comanda_id = ?
    """, (comanda_id,)).fetchone()
    conn.close()
    return row["total"]


# --- Relatórios ---

def relatorio_vendas_dia(data=None):
    conn = get_connection()
    if data is None:
        data = datetime.now().strftime("%Y-%m-%d")

    params = (data,)

    resumo = conn.execute("""
        SELECT COUNT(*) as total_comandas,
               COALESCE(SUM(sub.total), 0) as faturamento,
               COALESCE(SUM(c.desconto), 0) as total_descontos
        FROM comandas c
        LEFT JOIN (
            SELECT comanda_id, SUM(quantidade * preco_unitario) as total
            FROM itens_comanda GROUP BY comanda_id
        ) sub ON sub.comanda_id = c.id
        WHERE c.status = 'fechada' AND DATE(c.fechada_em) = ?
    """, params).fetchone()

    produtos = conn.execute("""
        SELECT p.nome, SUM(ic.quantidade) as qtd,
               SUM(ic.quantidade * ic.preco_unitario) as total
        FROM itens_comanda ic
        JOIN produtos p ON ic.produto_id = p.id
        JOIN comandas c ON ic.comanda_id = c.id
        WHERE c.status = 'fechada' AND DATE(c.fechada_em) = ?
        GROUP BY p.id
        ORDER BY qtd DESC
    """, params).fetchall()

    pagamentos = conn.execute("""
        SELECT forma_pagamento,
               COUNT(*) as qtd,
               COALESCE(SUM(sub.total), 0) as valor
        FROM comandas c
        LEFT JOIN (
            SELECT comanda_id, SUM(quantidade * preco_unitario) as total
            FROM itens_comanda GROUP BY comanda_id
        ) sub ON sub.comanda_id = c.id
        WHERE c.status = 'fechada' AND DATE(c.fechada_em) = ?
        GROUP BY forma_pagamento
    """, params).fetchall()

    conn.close()
    return {
        "resumo": dict(resumo),
        "produtos": [dict(r) for r in produtos],
        "pagamentos": [dict(r) for r in pagamentos]
    }


# --- Limpeza de dados ---

def contar_comandas_fechadas_antes(data_limite):
    conn = get_connection()
    row = conn.execute("""
        SELECT COUNT(*) as total
        FROM comandas
        WHERE status = 'fechada' AND DATE(fechada_em) < ?
    """, (data_limite,)).fetchone()
    conn.close()
    return row["total"]


def limpar_comandas_antigas(data_limite):
    conn = get_connection()
    # Deletar itens das comandas que serao removidas
    conn.execute("""
        DELETE FROM itens_comanda WHERE comanda_id IN (
            SELECT id FROM comandas
            WHERE status = 'fechada' AND DATE(fechada_em) < ?
        )
    """, (data_limite,))
    # Deletar as comandas
    cursor = conn.execute("""
        DELETE FROM comandas
        WHERE status = 'fechada' AND DATE(fechada_em) < ?
    """, (data_limite,))
    removidas = cursor.rowcount
    conn.commit()
    # Recuperar espaco em disco
    conn.execute("VACUUM")
    conn.close()
    return removidas


# --- Backup ---

def fazer_backup(destino):
    shutil.copy2(DB_PATH, destino)


# --- Validacao ---

def validar_data(data_str):
    return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', data_str))
