#!/usr/bin/env python3
"""Testes basicos para database.py"""

import unittest
import os
import sys
import tempfile

# Forcar banco em diretorio temporario antes de importar
_tmpdir = tempfile.mkdtemp()
os.environ["BRASILEIRINHO_TEST_DB"] = os.path.join(_tmpdir, "test.db")

# Monkey-patch o path do banco antes do import
import database as db
db.DB_PATH = os.environ["BRASILEIRINHO_TEST_DB"]


class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Banco limpo a cada teste
        if os.path.exists(db.DB_PATH):
            os.remove(db.DB_PATH)
        db.init_db()

    def tearDown(self):
        if os.path.exists(db.DB_PATH):
            os.remove(db.DB_PATH)

    # --- init_db ---

    def test_init_db_cria_tabelas(self):
        conn = db.get_connection()
        tabelas = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        conn.close()
        nomes = [t["name"] for t in tabelas]
        for t in ["categorias", "produtos", "clientes", "comandas", "itens_comanda"]:
            self.assertIn(t, nomes)

    def test_init_db_seed_categorias(self):
        cats = db.listar_categorias()
        self.assertEqual(len(cats), 9)

    def test_init_db_idempotente(self):
        db.init_db()  # chamar de novo
        cats = db.listar_categorias()
        self.assertEqual(len(cats), 9)

    # --- Produtos ---

    def test_salvar_e_listar_produto(self):
        cats = db.listar_categorias()
        db.salvar_produto("Skol Lata", cats[0]["id"], 8.00)
        produtos = db.listar_produtos()
        self.assertEqual(len(produtos), 1)
        self.assertEqual(produtos[0]["nome"], "Skol Lata")
        self.assertAlmostEqual(produtos[0]["preco"], 8.00)

    def test_editar_produto(self):
        cats = db.listar_categorias()
        db.salvar_produto("Skol", cats[0]["id"], 8.00)
        prod = db.listar_produtos()[0]
        db.salvar_produto("Skol 350ml", cats[0]["id"], 9.00, prod["id"])
        prod2 = db.listar_produtos()[0]
        self.assertEqual(prod2["nome"], "Skol 350ml")
        self.assertAlmostEqual(prod2["preco"], 9.00)

    def test_excluir_produto_soft_delete(self):
        cats = db.listar_categorias()
        db.salvar_produto("Teste", cats[0]["id"], 5.00)
        prod = db.listar_produtos()[0]
        db.excluir_produto(prod["id"])
        self.assertEqual(len(db.listar_produtos(apenas_ativos=True)), 0)
        self.assertEqual(len(db.listar_produtos(apenas_ativos=False)), 1)

    # --- Clientes ---

    def test_salvar_e_listar_cliente(self):
        db.salvar_cliente("Joao", "11999999999")
        clientes = db.listar_clientes()
        self.assertEqual(len(clientes), 1)
        self.assertEqual(clientes[0]["nome"], "Joao")

    def test_buscar_cliente(self):
        db.salvar_cliente("Maria Silva", "11988888888")
        db.salvar_cliente("Jose Santos", "11977777777")
        encontrados = db.listar_clientes("Maria")
        self.assertEqual(len(encontrados), 1)
        self.assertEqual(encontrados[0]["nome"], "Maria Silva")

    def test_buscar_cliente_por_telefone(self):
        db.salvar_cliente("Ana", "11966666666")
        encontrados = db.listar_clientes("9666")
        self.assertEqual(len(encontrados), 1)

    def test_excluir_cliente(self):
        db.salvar_cliente("Teste", "000")
        c = db.listar_clientes()[0]
        db.excluir_cliente(c["id"])
        self.assertEqual(len(db.listar_clientes()), 0)

    # --- Comandas ---

    def test_abrir_comanda_sem_cliente(self):
        cid = db.abrir_comanda()
        self.assertIsNotNone(cid)
        comandas = db.listar_comandas("aberta")
        self.assertEqual(len(comandas), 1)
        self.assertIsNone(comandas[0]["cliente_nome"])

    def test_abrir_comanda_com_cliente(self):
        db.salvar_cliente("Pedro", "000")
        cliente = db.listar_clientes()[0]
        cid = db.abrir_comanda(cliente["id"])
        comanda = db.get_comanda(cid)
        self.assertEqual(comanda["cliente_nome"], "Pedro")

    def test_fechar_comanda(self):
        cid = db.abrir_comanda()
        cats = db.listar_categorias()
        db.salvar_produto("Cerveja", cats[0]["id"], 10.00)
        prod = db.listar_produtos()[0]
        db.adicionar_item(cid, prod["id"], 2, prod["preco"])
        db.fechar_comanda(cid, "PIX", 0)
        abertas = db.listar_comandas("aberta")
        fechadas = db.listar_comandas("fechada")
        self.assertEqual(len(abertas), 0)
        self.assertEqual(len(fechadas), 1)

    # --- Itens da Comanda ---

    def test_adicionar_e_listar_itens(self):
        cid = db.abrir_comanda()
        cats = db.listar_categorias()
        db.salvar_produto("Dose Whisky", cats[0]["id"], 25.00)
        prod = db.listar_produtos()[0]
        db.adicionar_item(cid, prod["id"], 3, prod["preco"])
        itens = db.listar_itens_comanda(cid)
        self.assertEqual(len(itens), 1)
        self.assertEqual(itens[0]["quantidade"], 3)
        self.assertAlmostEqual(itens[0]["subtotal"], 75.00)

    def test_total_comanda(self):
        cid = db.abrir_comanda()
        cats = db.listar_categorias()
        db.salvar_produto("Item A", cats[0]["id"], 10.00)
        db.salvar_produto("Item B", cats[0]["id"], 15.00)
        prods = db.listar_produtos()
        db.adicionar_item(cid, prods[0]["id"], 2, prods[0]["preco"])
        db.adicionar_item(cid, prods[1]["id"], 1, prods[1]["preco"])
        total = db.total_comanda(cid)
        self.assertAlmostEqual(total, 35.00)

    def test_remover_item(self):
        cid = db.abrir_comanda()
        cats = db.listar_categorias()
        db.salvar_produto("X", cats[0]["id"], 5.00)
        prod = db.listar_produtos()[0]
        db.adicionar_item(cid, prod["id"], 1, prod["preco"])
        item = db.listar_itens_comanda(cid)[0]
        db.remover_item(item["id"])
        self.assertEqual(len(db.listar_itens_comanda(cid)), 0)
        self.assertAlmostEqual(db.total_comanda(cid), 0.00)

    # --- Relatorio ---

    def test_relatorio_vazio(self):
        rel = db.relatorio_vendas_dia("2020-01-01")
        self.assertEqual(rel["resumo"]["total_comandas"], 0)
        self.assertAlmostEqual(rel["resumo"]["faturamento"], 0.00)

    def test_relatorio_com_dados(self):
        cid = db.abrir_comanda()
        cats = db.listar_categorias()
        db.salvar_produto("Produto R", cats[0]["id"], 20.00)
        prod = db.listar_produtos()[0]
        db.adicionar_item(cid, prod["id"], 2, prod["preco"])
        db.fechar_comanda(cid, "Dinheiro", 0)
        # Usar data de hoje
        from datetime import datetime
        hoje = datetime.now().strftime("%Y-%m-%d")
        rel = db.relatorio_vendas_dia(hoje)
        self.assertEqual(rel["resumo"]["total_comandas"], 1)
        self.assertAlmostEqual(rel["resumo"]["faturamento"], 40.00)
        self.assertEqual(len(rel["produtos"]), 1)
        self.assertEqual(rel["produtos"][0]["nome"], "Produto R")

    # --- Limpeza ---

    def test_contar_comandas_fechadas_antes(self):
        cid = db.abrir_comanda()
        cats = db.listar_categorias()
        db.salvar_produto("P", cats[0]["id"], 1.00)
        prod = db.listar_produtos()[0]
        db.adicionar_item(cid, prod["id"], 1, prod["preco"])
        db.fechar_comanda(cid, "PIX")
        # Contar antes de amanha — deve encontrar a comanda de hoje
        from datetime import datetime, timedelta
        amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        qtd = db.contar_comandas_fechadas_antes(amanha)
        self.assertEqual(qtd, 1)

    def test_limpar_comandas_antigas(self):
        cid = db.abrir_comanda()
        cats = db.listar_categorias()
        db.salvar_produto("P", cats[0]["id"], 1.00)
        prod = db.listar_produtos()[0]
        db.adicionar_item(cid, prod["id"], 1, prod["preco"])
        db.fechar_comanda(cid, "Dinheiro")
        from datetime import datetime, timedelta
        amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        removidas = db.limpar_comandas_antigas(amanha)
        self.assertEqual(removidas, 1)
        self.assertEqual(len(db.listar_comandas("fechada")), 0)
        self.assertEqual(len(db.listar_itens_comanda(cid)), 0)

    def test_limpar_nao_afeta_abertas(self):
        cid = db.abrir_comanda()
        from datetime import datetime, timedelta
        amanha = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        removidas = db.limpar_comandas_antigas(amanha)
        self.assertEqual(removidas, 0)
        self.assertEqual(len(db.listar_comandas("aberta")), 1)

    # --- Backup ---

    def test_fazer_backup(self):
        import tempfile
        destino = os.path.join(tempfile.mkdtemp(), "backup_test.db")
        db.fazer_backup(destino)
        self.assertTrue(os.path.exists(destino))
        self.assertGreater(os.path.getsize(destino), 0)
        os.remove(destino)

    # --- Validacao ---

    def test_validar_data_valida(self):
        self.assertTrue(db.validar_data("2026-04-14"))
        self.assertTrue(db.validar_data("2020-01-01"))

    def test_validar_data_invalida(self):
        self.assertFalse(db.validar_data("lixo"))
        self.assertFalse(db.validar_data("14/04/2026"))
        self.assertFalse(db.validar_data("2026-4-1"))
        self.assertFalse(db.validar_data(""))

    # --- Inputs maliciosos (SQL injection) ---

    def test_sql_injection_nome_produto(self):
        cats = db.listar_categorias()
        db.salvar_produto("'; DROP TABLE produtos; --", cats[0]["id"], 1.00)
        produtos = db.listar_produtos()
        self.assertEqual(len(produtos), 1)
        self.assertEqual(produtos[0]["nome"], "'; DROP TABLE produtos; --")

    def test_sql_injection_busca_cliente(self):
        db.salvar_cliente("Normal", "000")
        resultado = db.listar_clientes("' OR 1=1 --")
        self.assertEqual(len(resultado), 0)


if __name__ == "__main__":
    unittest.main()
