#!/usr/bin/env python3
"""
Brasileirinho Bar — Sistema de Comandas
Aplicação desktop para gerenciamento de comandas, produtos e clientes.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from PIL import Image
import os
import sys
import database as db
from datetime import datetime

# --- Cores do tema (extraídas da logo) ---
COR_FUNDO = "#1A1A2E"
COR_FUNDO_CARD = "#16213E"
COR_FUNDO_ENTRADA = "#0F3460"
COR_VERDE = "#2E7D32"
COR_VERDE_HOVER = "#388E3C"
COR_AMARELO = "#E8B830"
COR_AMARELO_HOVER = "#F0C850"
COR_VERMELHO = "#C62828"
COR_VERMELHO_HOVER = "#E53935"
COR_TEXTO = "#FFFFFF"
COR_TEXTO_SECUNDARIO = "#B0BEC5"
COR_BORDA = "#2A3A5E"

FONTE_TITULO = ("Segoe UI", 20, "bold")
FONTE_SUBTITULO = ("Segoe UI", 14, "bold")
FONTE_NORMAL = ("Segoe UI", 13)
FONTE_PEQUENA = ("Segoe UI", 11)
FONTE_TABELA = ("Segoe UI", 12)

# Compatível com PyInstaller (--onefile extrai em _MEIPASS)
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.title("Brasileirinho Bar — Sistema de Comandas")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(fg_color=COR_FUNDO)

        # Inicializar banco
        try:
            db.init_db()
        except RuntimeError as e:
            messagebox.showerror("Erro ao abrir banco de dados", str(e))
            self.destroy()
            return

        # Header com logo
        self._criar_header()

        # Abas
        self.tabview = ctk.CTkTabview(
            self, fg_color=COR_FUNDO_CARD,
            segmented_button_fg_color=COR_FUNDO_ENTRADA,
            segmented_button_selected_color=COR_VERDE,
            segmented_button_selected_hover_color=COR_VERDE_HOVER,
            segmented_button_unselected_color=COR_FUNDO_ENTRADA,
            segmented_button_unselected_hover_color=COR_BORDA,
            text_color=COR_TEXTO
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        self.tab_comandas = self.tabview.add("  Comandas  ")
        self.tab_produtos = self.tabview.add("  Produtos  ")
        self.tab_clientes = self.tabview.add("  Clientes  ")
        self.tab_relatorios = self.tabview.add("  Relatórios  ")

        # Montar cada aba
        self._montar_aba_comandas()
        self._montar_aba_produtos()
        self._montar_aba_clientes()
        self._montar_aba_relatorios()

        # Configurar estilo das Treeviews
        self._configurar_estilo_tabelas()

    def _criar_header(self):
        header = ctk.CTkFrame(self, fg_color=COR_FUNDO_CARD, height=80, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # Logo
        logo_path = os.path.join(ASSETS_DIR, "logo.jpeg")
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(60, 60)
            )
            logo_label = ctk.CTkLabel(header, image=logo_img, text="")
            logo_label.pack(side="left", padx=(20, 10), pady=10)

        # Título
        titulo_frame = ctk.CTkFrame(header, fg_color="transparent")
        titulo_frame.pack(side="left", pady=10)

        ctk.CTkLabel(
            titulo_frame, text="BRASILEIRINHO",
            font=("Segoe UI", 24, "bold"), text_color=COR_AMARELO
        ).pack(anchor="w")
        ctk.CTkLabel(
            titulo_frame, text="bar — Sistema de Comandas",
            font=("Segoe UI", 12), text_color=COR_TEXTO_SECUNDARIO
        ).pack(anchor="w")

        # Data/hora
        self.label_hora = ctk.CTkLabel(
            header, text="", font=FONTE_NORMAL, text_color=COR_TEXTO_SECUNDARIO
        )
        self.label_hora.pack(side="right", padx=20)
        self._atualizar_hora()

    def _atualizar_hora(self):
        agora = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        self.label_hora.configure(text=agora)
        self.after(1000, self._atualizar_hora)

    def _configurar_estilo_tabelas(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                         background=COR_FUNDO_CARD,
                         foreground=COR_TEXTO,
                         fieldbackground=COR_FUNDO_CARD,
                         borderwidth=0,
                         font=FONTE_TABELA,
                         rowheight=32)
        style.configure("Custom.Treeview.Heading",
                         background=COR_FUNDO_ENTRADA,
                         foreground=COR_AMARELO,
                         font=FONTE_SUBTITULO,
                         borderwidth=0,
                         relief="flat")
        style.map("Custom.Treeview",
                   background=[("selected", COR_VERDE)],
                   foreground=[("selected", COR_TEXTO)])
        style.map("Custom.Treeview.Heading",
                   background=[("active", COR_BORDA)])

    # ==========================================================
    #  ABA COMANDAS
    # ==========================================================
    def _montar_aba_comandas(self):
        tab = self.tab_comandas

        # Painel esquerdo — lista de comandas abertas
        painel_esq = ctk.CTkFrame(tab, fg_color=COR_FUNDO, corner_radius=10, width=400)
        painel_esq.pack(side="left", fill="both", padx=(0, 5), pady=0, expand=True)

        # Título + botão nova comanda
        top = ctk.CTkFrame(painel_esq, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(top, text="Comandas Abertas", font=FONTE_SUBTITULO,
                     text_color=COR_AMARELO).pack(side="left")
        ctk.CTkButton(
            top, text="+ Nova Comanda", font=FONTE_NORMAL, width=150,
            fg_color=COR_VERDE, hover_color=COR_VERDE_HOVER,
            command=self._nova_comanda
        ).pack(side="right")

        # Tabela de comandas
        cols_comandas = ("id", "cliente", "total", "hora")
        self.tree_comandas = ttk.Treeview(
            painel_esq, columns=cols_comandas, show="headings",
            style="Custom.Treeview"
        )
        self.tree_comandas.heading("id", text="#", anchor="center")
        self.tree_comandas.heading("cliente", text="Cliente", anchor="w")
        self.tree_comandas.heading("total", text="Total (R$)", anchor="e")
        self.tree_comandas.heading("hora", text="Aberta em", anchor="center")
        self.tree_comandas.column("id", width=50, anchor="center")
        self.tree_comandas.column("cliente", width=150)
        self.tree_comandas.column("total", width=100, anchor="e")
        self.tree_comandas.column("hora", width=120, anchor="center")
        self.tree_comandas.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree_comandas.bind("<<TreeviewSelect>>", self._selecionar_comanda)

        # Painel direito — detalhes da comanda selecionada
        painel_dir = ctk.CTkFrame(tab, fg_color=COR_FUNDO, corner_radius=10, width=500)
        painel_dir.pack(side="right", fill="both", padx=(5, 0), pady=0, expand=True)

        self.frame_detalhe_comanda = painel_dir
        self.comanda_selecionada_id = None

        # Título detalhe
        self.label_detalhe_titulo = ctk.CTkLabel(
            painel_dir, text="Selecione uma comanda", font=FONTE_SUBTITULO,
            text_color=COR_AMARELO
        )
        self.label_detalhe_titulo.pack(padx=10, pady=10, anchor="w")

        # Frame para adicionar item
        frame_add = ctk.CTkFrame(painel_dir, fg_color=COR_FUNDO_CARD, corner_radius=8)
        frame_add.pack(fill="x", padx=10, pady=(0, 5))

        ctk.CTkLabel(frame_add, text="Produto:", font=FONTE_PEQUENA,
                     text_color=COR_TEXTO_SECUNDARIO).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_produto_comanda = ctk.CTkComboBox(
            frame_add, width=250, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            button_color=COR_VERDE, button_hover_color=COR_VERDE_HOVER,
            dropdown_fg_color=COR_FUNDO_ENTRADA,
            state="readonly"
        )
        self.combo_produto_comanda.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_add, text="Qtd:", font=FONTE_PEQUENA,
                     text_color=COR_TEXTO_SECUNDARIO).grid(row=0, column=2, padx=5, pady=5)
        self.entry_qtd = ctk.CTkEntry(
            frame_add, width=60, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA
        )
        self.entry_qtd.insert(0, "1")
        self.entry_qtd.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkButton(
            frame_add, text="Adicionar", width=100, font=FONTE_NORMAL,
            fg_color=COR_VERDE, hover_color=COR_VERDE_HOVER,
            command=self._adicionar_item_comanda
        ).grid(row=0, column=4, padx=10, pady=5)

        # Tabela itens da comanda
        cols_itens = ("id", "produto", "qtd", "unitario", "subtotal")
        self.tree_itens = ttk.Treeview(
            painel_dir, columns=cols_itens, show="headings",
            style="Custom.Treeview"
        )
        self.tree_itens.heading("id", text="#", anchor="center")
        self.tree_itens.heading("produto", text="Produto", anchor="w")
        self.tree_itens.heading("qtd", text="Qtd", anchor="center")
        self.tree_itens.heading("unitario", text="Unit. (R$)", anchor="e")
        self.tree_itens.heading("subtotal", text="Subtotal (R$)", anchor="e")
        self.tree_itens.column("id", width=40, anchor="center")
        self.tree_itens.column("produto", width=180)
        self.tree_itens.column("qtd", width=50, anchor="center")
        self.tree_itens.column("unitario", width=90, anchor="e")
        self.tree_itens.column("subtotal", width=100, anchor="e")
        self.tree_itens.pack(fill="both", expand=True, padx=10, pady=5)

        # Rodapé — total + ações
        rodape = ctk.CTkFrame(painel_dir, fg_color=COR_FUNDO_CARD, corner_radius=8)
        rodape.pack(fill="x", padx=10, pady=(5, 10))

        self.label_total_comanda = ctk.CTkLabel(
            rodape, text="Total: R$ 0,00", font=("Segoe UI", 18, "bold"),
            text_color=COR_AMARELO
        )
        self.label_total_comanda.pack(side="left", padx=15, pady=10)

        ctk.CTkButton(
            rodape, text="Remover Item", width=120, font=FONTE_NORMAL,
            fg_color=COR_VERMELHO, hover_color=COR_VERMELHO_HOVER,
            command=self._remover_item_comanda
        ).pack(side="right", padx=5, pady=10)

        ctk.CTkButton(
            rodape, text="Fechar Comanda", width=140, font=FONTE_NORMAL,
            fg_color=COR_AMARELO, hover_color=COR_AMARELO_HOVER,
            text_color="#1A1A2E",
            command=self._fechar_comanda
        ).pack(side="right", padx=5, pady=10)

        # Carregar dados
        self._atualizar_combo_produtos()
        self._atualizar_lista_comandas()

    def _nova_comanda(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Nova Comanda")
        janela.geometry("450x350")
        janela.configure(fg_color=COR_FUNDO)
        janela.transient(self)
        janela.grab_set()

        ctk.CTkLabel(janela, text="Abrir Nova Comanda", font=FONTE_TITULO,
                     text_color=COR_AMARELO).pack(pady=(20, 15))

        # Buscar cliente
        ctk.CTkLabel(janela, text="Buscar cliente (nome ou telefone):",
                     font=FONTE_NORMAL, text_color=COR_TEXTO_SECUNDARIO).pack(padx=20, anchor="w")

        frame_busca = ctk.CTkFrame(janela, fg_color="transparent")
        frame_busca.pack(fill="x", padx=20, pady=5)

        entry_busca = ctk.CTkEntry(
            frame_busca, placeholder_text="Digite para buscar...",
            font=FONTE_NORMAL, fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA
        )
        entry_busca.pack(side="left", fill="x", expand=True, padx=(0, 5))

        combo_clientes = ctk.CTkComboBox(
            janela, width=410, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            button_color=COR_VERDE, button_hover_color=COR_VERDE_HOVER,
            dropdown_fg_color=COR_FUNDO_ENTRADA,
            state="readonly", values=["(Sem cliente)"]
        )
        combo_clientes.pack(padx=20, pady=5)
        combo_clientes.set("(Sem cliente)")

        # Mapa de clientes
        clientes_map = {}

        def buscar_clientes(*_):
            termo = entry_busca.get()
            clientes = db.listar_clientes(termo)
            valores = ["(Sem cliente)"]
            clientes_map.clear()
            for c in clientes:
                label = f"{c['nome']} — {c['telefone'] or 'sem tel'}"
                valores.append(label)
                clientes_map[label] = c["id"]
            combo_clientes.configure(values=valores)
            if valores:
                combo_clientes.set(valores[0])

        entry_busca.bind("<KeyRelease>", buscar_clientes)
        buscar_clientes()

        def confirmar():
            sel = combo_clientes.get()
            cliente_id = clientes_map.get(sel)
            comanda_id = db.abrir_comanda(cliente_id)
            janela.destroy()
            self._atualizar_lista_comandas()
            # Selecionar a comanda criada
            for item in self.tree_comandas.get_children():
                if self.tree_comandas.item(item)["values"][0] == comanda_id:
                    self.tree_comandas.selection_set(item)
                    self._selecionar_comanda(None)
                    break

        ctk.CTkButton(
            janela, text="Abrir Comanda", font=FONTE_NORMAL, height=40,
            fg_color=COR_VERDE, hover_color=COR_VERDE_HOVER,
            command=confirmar
        ).pack(pady=20)

    def _atualizar_lista_comandas(self):
        for item in self.tree_comandas.get_children():
            self.tree_comandas.delete(item)
        comandas = db.listar_comandas("aberta")
        for c in comandas:
            hora = c["aberta_em"][:16] if c["aberta_em"] else ""
            self.tree_comandas.insert("", "end", values=(
                c["id"],
                c["cliente_nome"] or "Sem cliente",
                f"{c['total']:.2f}",
                hora
            ))

    def _selecionar_comanda(self, _):
        sel = self.tree_comandas.selection()
        if not sel:
            return
        valores = self.tree_comandas.item(sel[0])["values"]
        self.comanda_selecionada_id = valores[0]
        cliente = valores[1]
        self.label_detalhe_titulo.configure(
            text=f"Comanda #{self.comanda_selecionada_id} — {cliente}"
        )
        self._atualizar_itens_comanda()

    def _atualizar_combo_produtos(self):
        produtos = db.listar_produtos()
        self._produtos_map = {}
        valores = []
        for p in produtos:
            label = f"{p['nome']} ({p['categoria'] or 'Sem cat.'}) — R$ {p['preco']:.2f}"
            valores.append(label)
            self._produtos_map[label] = p
        self.combo_produto_comanda.configure(values=valores)
        if valores:
            self.combo_produto_comanda.set(valores[0])

    def _adicionar_item_comanda(self):
        if not self.comanda_selecionada_id:
            messagebox.showwarning("Aviso", "Selecione uma comanda primeiro.")
            return

        sel = self.combo_produto_comanda.get()
        produto = self._produtos_map.get(sel)
        if not produto:
            messagebox.showwarning("Aviso", "Selecione um produto.")
            return

        try:
            qtd = int(self.entry_qtd.get())
            if qtd <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Aviso", "Quantidade inválida.")
            return

        db.adicionar_item(self.comanda_selecionada_id, produto["id"], qtd, produto["preco"])
        self._atualizar_itens_comanda()
        self._atualizar_lista_comandas()
        # Re-selecionar comanda
        for item in self.tree_comandas.get_children():
            if self.tree_comandas.item(item)["values"][0] == self.comanda_selecionada_id:
                self.tree_comandas.selection_set(item)
                break

    def _atualizar_itens_comanda(self):
        for item in self.tree_itens.get_children():
            self.tree_itens.delete(item)
        if not self.comanda_selecionada_id:
            return
        itens = db.listar_itens_comanda(self.comanda_selecionada_id)
        for it in itens:
            self.tree_itens.insert("", "end", values=(
                it["id"],
                it["produto_nome"],
                it["quantidade"],
                f"{it['preco_unitario']:.2f}",
                f"{it['subtotal']:.2f}"
            ))
        total = db.total_comanda(self.comanda_selecionada_id)
        self.label_total_comanda.configure(text=f"Total: R$ {total:.2f}")

    def _remover_item_comanda(self):
        sel = self.tree_itens.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecione um item para remover.")
            return
        item_id = self.tree_itens.item(sel[0])["values"][0]
        db.remover_item(item_id)
        self._atualizar_itens_comanda()
        self._atualizar_lista_comandas()
        for item in self.tree_comandas.get_children():
            if self.tree_comandas.item(item)["values"][0] == self.comanda_selecionada_id:
                self.tree_comandas.selection_set(item)
                break

    def _fechar_comanda(self):
        if not self.comanda_selecionada_id:
            messagebox.showwarning("Aviso", "Selecione uma comanda primeiro.")
            return

        total = db.total_comanda(self.comanda_selecionada_id)
        if total == 0:
            messagebox.showwarning("Aviso", "Comanda sem itens.")
            return

        janela = ctk.CTkToplevel(self)
        janela.title("Fechar Comanda")
        janela.geometry("400x350")
        janela.configure(fg_color=COR_FUNDO)
        janela.transient(self)
        janela.grab_set()

        ctk.CTkLabel(janela, text=f"Fechar Comanda #{self.comanda_selecionada_id}",
                     font=FONTE_TITULO, text_color=COR_AMARELO).pack(pady=(20, 5))

        ctk.CTkLabel(janela, text=f"Total: R$ {total:.2f}",
                     font=("Segoe UI", 22, "bold"), text_color=COR_VERDE).pack(pady=10)

        ctk.CTkLabel(janela, text="Forma de pagamento:", font=FONTE_NORMAL,
                     text_color=COR_TEXTO_SECUNDARIO).pack(padx=20, anchor="w")

        combo_pag = ctk.CTkComboBox(
            janela, values=["Dinheiro", "PIX", "Cartão Débito", "Cartão Crédito", "Misto"],
            width=360, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            button_color=COR_VERDE, button_hover_color=COR_VERDE_HOVER,
            dropdown_fg_color=COR_FUNDO_ENTRADA,
            state="readonly"
        )
        combo_pag.pack(padx=20, pady=5)
        combo_pag.set("Dinheiro")

        ctk.CTkLabel(janela, text="Desconto (R$):", font=FONTE_NORMAL,
                     text_color=COR_TEXTO_SECUNDARIO).pack(padx=20, anchor="w")
        entry_desc = ctk.CTkEntry(
            janela, width=360, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            placeholder_text="0.00"
        )
        entry_desc.pack(padx=20, pady=5)

        def confirmar():
            forma = combo_pag.get()
            try:
                desconto = float(entry_desc.get().replace(",", ".") or 0)
                if desconto < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Aviso", "Valor de desconto invalido.")
                return
            db.fechar_comanda(self.comanda_selecionada_id, forma, desconto)
            janela.destroy()
            self.comanda_selecionada_id = None
            self.label_detalhe_titulo.configure(text="Selecione uma comanda")
            self.label_total_comanda.configure(text="Total: R$ 0,00")
            for item in self.tree_itens.get_children():
                self.tree_itens.delete(item)
            self._atualizar_lista_comandas()
            messagebox.showinfo("Sucesso", f"Comanda fechada!\nTotal: R$ {total:.2f}\nPagamento: {forma}")

        ctk.CTkButton(
            janela, text="Confirmar Fechamento", font=FONTE_NORMAL, height=40,
            fg_color=COR_AMARELO, hover_color=COR_AMARELO_HOVER,
            text_color="#1A1A2E", command=confirmar
        ).pack(pady=20)

    # ==========================================================
    #  ABA PRODUTOS
    # ==========================================================
    def _montar_aba_produtos(self):
        tab = self.tab_produtos

        # Formulário
        form = ctk.CTkFrame(tab, fg_color=COR_FUNDO_CARD, corner_radius=10)
        form.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(form, text="Cadastro de Produto", font=FONTE_SUBTITULO,
                     text_color=COR_AMARELO).grid(row=0, column=0, columnspan=6, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(form, text="Nome:", font=FONTE_NORMAL,
                     text_color=COR_TEXTO_SECUNDARIO).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_prod_nome = ctk.CTkEntry(
            form, width=250, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA
        )
        self.entry_prod_nome.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text="Categoria:", font=FONTE_NORMAL,
                     text_color=COR_TEXTO_SECUNDARIO).grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.combo_prod_cat = ctk.CTkComboBox(
            form, width=180, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            button_color=COR_VERDE, button_hover_color=COR_VERDE_HOVER,
            dropdown_fg_color=COR_FUNDO_ENTRADA,
            state="readonly"
        )
        self.combo_prod_cat.grid(row=1, column=3, padx=5, pady=5)

        ctk.CTkLabel(form, text="Preço (R$):", font=FONTE_NORMAL,
                     text_color=COR_TEXTO_SECUNDARIO).grid(row=1, column=4, padx=10, pady=5, sticky="w")
        self.entry_prod_preco = ctk.CTkEntry(
            form, width=100, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            placeholder_text="0.00"
        )
        self.entry_prod_preco.grid(row=1, column=5, padx=5, pady=5)

        # Botões
        frame_btns = ctk.CTkFrame(form, fg_color="transparent")
        frame_btns.grid(row=2, column=0, columnspan=6, padx=10, pady=10, sticky="e")

        ctk.CTkButton(
            frame_btns, text="Salvar", width=100, font=FONTE_NORMAL,
            fg_color=COR_VERDE, hover_color=COR_VERDE_HOVER,
            command=self._salvar_produto
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_btns, text="Limpar", width=100, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, hover_color=COR_BORDA,
            command=self._limpar_form_produto
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_btns, text="Excluir", width=100, font=FONTE_NORMAL,
            fg_color=COR_VERMELHO, hover_color=COR_VERMELHO_HOVER,
            command=self._excluir_produto
        ).pack(side="left", padx=5)

        # Tabela
        cols_prod = ("id", "nome", "categoria", "preco")
        self.tree_produtos = ttk.Treeview(
            tab, columns=cols_prod, show="headings", style="Custom.Treeview"
        )
        self.tree_produtos.heading("id", text="#", anchor="center")
        self.tree_produtos.heading("nome", text="Nome", anchor="w")
        self.tree_produtos.heading("categoria", text="Categoria", anchor="w")
        self.tree_produtos.heading("preco", text="Preço (R$)", anchor="e")
        self.tree_produtos.column("id", width=50, anchor="center")
        self.tree_produtos.column("nome", width=300)
        self.tree_produtos.column("categoria", width=150)
        self.tree_produtos.column("preco", width=100, anchor="e")
        self.tree_produtos.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree_produtos.bind("<<TreeviewSelect>>", self._selecionar_produto)

        self._produto_editando_id = None
        self._carregar_categorias()
        self._atualizar_lista_produtos()

    def _carregar_categorias(self):
        cats = db.listar_categorias()
        self._categorias_map = {c["nome"]: c["id"] for c in cats}
        self.combo_prod_cat.configure(values=list(self._categorias_map.keys()))
        if cats:
            self.combo_prod_cat.set(cats[0]["nome"])

    def _atualizar_lista_produtos(self):
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        for p in db.listar_produtos():
            self.tree_produtos.insert("", "end", values=(
                p["id"], p["nome"], p["categoria"] or "—", f"{p['preco']:.2f}"
            ))
        # Atualizar combo na aba comandas também
        if hasattr(self, 'combo_produto_comanda'):
            self._atualizar_combo_produtos()

    def _selecionar_produto(self, _):
        sel = self.tree_produtos.selection()
        if not sel:
            return
        vals = self.tree_produtos.item(sel[0])["values"]
        self._produto_editando_id = vals[0]
        self.entry_prod_nome.delete(0, "end")
        self.entry_prod_nome.insert(0, vals[1])
        cat = vals[2]
        if cat in self._categorias_map:
            self.combo_prod_cat.set(cat)
        self.entry_prod_preco.delete(0, "end")
        self.entry_prod_preco.insert(0, vals[3])

    def _salvar_produto(self):
        nome = self.entry_prod_nome.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Informe o nome do produto.")
            return
        cat_nome = self.combo_prod_cat.get()
        cat_id = self._categorias_map.get(cat_nome)
        try:
            preco = float(self.entry_prod_preco.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Aviso", "Preço inválido.")
            return

        db.salvar_produto(nome, cat_id, preco, self._produto_editando_id)
        self._limpar_form_produto()
        self._atualizar_lista_produtos()

    def _limpar_form_produto(self):
        self._produto_editando_id = None
        self.entry_prod_nome.delete(0, "end")
        self.entry_prod_preco.delete(0, "end")
        self.tree_produtos.selection_remove(*self.tree_produtos.selection())

    def _excluir_produto(self):
        if not self._produto_editando_id:
            messagebox.showwarning("Aviso", "Selecione um produto na tabela.")
            return
        if messagebox.askyesno("Confirmar", "Desativar este produto?"):
            db.excluir_produto(self._produto_editando_id)
            self._limpar_form_produto()
            self._atualizar_lista_produtos()

    # ==========================================================
    #  ABA CLIENTES
    # ==========================================================
    def _montar_aba_clientes(self):
        tab = self.tab_clientes

        # Busca
        frame_busca = ctk.CTkFrame(tab, fg_color=COR_FUNDO_CARD, corner_radius=10)
        frame_busca.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(frame_busca, text="Buscar:", font=FONTE_NORMAL,
                     text_color=COR_TEXTO_SECUNDARIO).pack(side="left", padx=10, pady=10)
        self.entry_busca_cliente = ctk.CTkEntry(
            frame_busca, width=300, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            placeholder_text="Nome ou telefone..."
        )
        self.entry_busca_cliente.pack(side="left", padx=5, pady=10)
        self.entry_busca_cliente.bind("<KeyRelease>", lambda _: self._atualizar_lista_clientes())

        # Formulário
        form = ctk.CTkFrame(tab, fg_color=COR_FUNDO_CARD, corner_radius=10)
        form.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(form, text="Cadastro de Cliente", font=FONTE_SUBTITULO,
                     text_color=COR_AMARELO).grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(form, text="Nome:", font=FONTE_NORMAL,
                     text_color=COR_TEXTO_SECUNDARIO).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_cli_nome = ctk.CTkEntry(
            form, width=300, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA
        )
        self.entry_cli_nome.grid(row=1, column=1, padx=5, pady=5)

        ctk.CTkLabel(form, text="Telefone:", font=FONTE_NORMAL,
                     text_color=COR_TEXTO_SECUNDARIO).grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.entry_cli_tel = ctk.CTkEntry(
            form, width=200, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            placeholder_text="(00) 00000-0000"
        )
        self.entry_cli_tel.grid(row=1, column=3, padx=5, pady=5)

        frame_btns = ctk.CTkFrame(form, fg_color="transparent")
        frame_btns.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="e")

        ctk.CTkButton(
            frame_btns, text="Salvar", width=100, font=FONTE_NORMAL,
            fg_color=COR_VERDE, hover_color=COR_VERDE_HOVER,
            command=self._salvar_cliente
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_btns, text="Limpar", width=100, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, hover_color=COR_BORDA,
            command=self._limpar_form_cliente
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_btns, text="Excluir", width=100, font=FONTE_NORMAL,
            fg_color=COR_VERMELHO, hover_color=COR_VERMELHO_HOVER,
            command=self._excluir_cliente
        ).pack(side="left", padx=5)

        # Tabela
        cols_cli = ("id", "nome", "telefone", "desde")
        self.tree_clientes = ttk.Treeview(
            tab, columns=cols_cli, show="headings", style="Custom.Treeview"
        )
        self.tree_clientes.heading("id", text="#", anchor="center")
        self.tree_clientes.heading("nome", text="Nome", anchor="w")
        self.tree_clientes.heading("telefone", text="Telefone", anchor="w")
        self.tree_clientes.heading("desde", text="Cliente desde", anchor="center")
        self.tree_clientes.column("id", width=50, anchor="center")
        self.tree_clientes.column("nome", width=300)
        self.tree_clientes.column("telefone", width=150)
        self.tree_clientes.column("desde", width=120, anchor="center")
        self.tree_clientes.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.tree_clientes.bind("<<TreeviewSelect>>", self._selecionar_cliente)

        self._cliente_editando_id = None
        self._atualizar_lista_clientes()

    def _atualizar_lista_clientes(self):
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        busca = self.entry_busca_cliente.get() if hasattr(self, 'entry_busca_cliente') else ""
        for c in db.listar_clientes(busca):
            desde = c["criado_em"][:10] if c["criado_em"] else ""
            self.tree_clientes.insert("", "end", values=(
                c["id"], c["nome"], c["telefone"] or "—", desde
            ))

    def _selecionar_cliente(self, _):
        sel = self.tree_clientes.selection()
        if not sel:
            return
        vals = self.tree_clientes.item(sel[0])["values"]
        self._cliente_editando_id = vals[0]
        self.entry_cli_nome.delete(0, "end")
        self.entry_cli_nome.insert(0, vals[1])
        self.entry_cli_tel.delete(0, "end")
        tel = vals[2] if vals[2] != "—" else ""
        self.entry_cli_tel.insert(0, tel)

    def _salvar_cliente(self):
        nome = self.entry_cli_nome.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Informe o nome do cliente.")
            return
        telefone = self.entry_cli_tel.get().strip()
        db.salvar_cliente(nome, telefone, self._cliente_editando_id)
        self._limpar_form_cliente()
        self._atualizar_lista_clientes()

    def _limpar_form_cliente(self):
        self._cliente_editando_id = None
        self.entry_cli_nome.delete(0, "end")
        self.entry_cli_tel.delete(0, "end")
        self.tree_clientes.selection_remove(*self.tree_clientes.selection())

    def _excluir_cliente(self):
        if not self._cliente_editando_id:
            messagebox.showwarning("Aviso", "Selecione um cliente na tabela.")
            return
        if messagebox.askyesno("Confirmar", "Excluir este cliente?"):
            db.excluir_cliente(self._cliente_editando_id)
            self._limpar_form_cliente()
            self._atualizar_lista_clientes()

    # ==========================================================
    #  ABA RELATÓRIOS
    # ==========================================================
    def _montar_aba_relatorios(self):
        tab = self.tab_relatorios

        # Seleção de data
        frame_data = ctk.CTkFrame(tab, fg_color=COR_FUNDO_CARD, corner_radius=10)
        frame_data.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(frame_data, text="Data:", font=FONTE_NORMAL,
                     text_color=COR_TEXTO_SECUNDARIO).pack(side="left", padx=10, pady=10)
        self.entry_rel_data = ctk.CTkEntry(
            frame_data, width=120, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            placeholder_text="AAAA-MM-DD"
        )
        self.entry_rel_data.pack(side="left", padx=5, pady=10)
        self.entry_rel_data.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ctk.CTkButton(
            frame_data, text="Gerar Relatório", font=FONTE_NORMAL, width=150,
            fg_color=COR_VERDE, hover_color=COR_VERDE_HOVER,
            command=self._gerar_relatorio
        ).pack(side="left", padx=15, pady=10)

        ctk.CTkButton(
            frame_data, text="Hoje", font=FONTE_NORMAL, width=80,
            fg_color=COR_FUNDO_ENTRADA, hover_color=COR_BORDA,
            command=lambda: (
                self.entry_rel_data.delete(0, "end"),
                self.entry_rel_data.insert(0, datetime.now().strftime("%Y-%m-%d")),
                self._gerar_relatorio()
            )
        ).pack(side="left", padx=5, pady=10)

        # Botoes de manutencao (lado direito)
        ctk.CTkButton(
            frame_data, text="Fazer Backup", font=FONTE_NORMAL, width=130,
            fg_color=COR_FUNDO_ENTRADA, hover_color=COR_BORDA,
            command=self._fazer_backup
        ).pack(side="right", padx=5, pady=10)

        ctk.CTkButton(
            frame_data, text="Limpar Antigas", font=FONTE_NORMAL, width=130,
            fg_color=COR_VERMELHO, hover_color=COR_VERMELHO_HOVER,
            command=self._limpar_comandas_antigas
        ).pack(side="right", padx=5, pady=10)

        # Resumo cards
        self.frame_resumo = ctk.CTkFrame(tab, fg_color="transparent")
        self.frame_resumo.pack(fill="x", padx=10, pady=5)

        self.cards_resumo = {}
        for i, (key, titulo) in enumerate([
            ("total_comandas", "Comandas Fechadas"),
            ("faturamento", "Faturamento (R$)"),
            ("total_descontos", "Descontos (R$)")
        ]):
            card = ctk.CTkFrame(self.frame_resumo, fg_color=COR_FUNDO_CARD, corner_radius=10)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.frame_resumo.grid_columnconfigure(i, weight=1)

            ctk.CTkLabel(card, text=titulo, font=FONTE_PEQUENA,
                         text_color=COR_TEXTO_SECUNDARIO).pack(padx=15, pady=(10, 0))
            lbl = ctk.CTkLabel(card, text="0", font=("Segoe UI", 28, "bold"),
                               text_color=COR_AMARELO)
            lbl.pack(padx=15, pady=(0, 10))
            self.cards_resumo[key] = lbl

        # Tabela produtos vendidos
        ctk.CTkLabel(tab, text="Produtos Mais Vendidos", font=FONTE_SUBTITULO,
                     text_color=COR_AMARELO).pack(padx=15, pady=(10, 0), anchor="w")

        frame_tabelas = ctk.CTkFrame(tab, fg_color="transparent")
        frame_tabelas.pack(fill="both", expand=True, padx=10, pady=5)

        cols_vend = ("produto", "qtd", "total")
        self.tree_vendidos = ttk.Treeview(
            frame_tabelas, columns=cols_vend, show="headings", style="Custom.Treeview"
        )
        self.tree_vendidos.heading("produto", text="Produto", anchor="w")
        self.tree_vendidos.heading("qtd", text="Quantidade", anchor="center")
        self.tree_vendidos.heading("total", text="Total (R$)", anchor="e")
        self.tree_vendidos.column("produto", width=300)
        self.tree_vendidos.column("qtd", width=100, anchor="center")
        self.tree_vendidos.column("total", width=120, anchor="e")
        self.tree_vendidos.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Tabela formas de pagamento
        cols_pag = ("forma", "qtd", "valor")
        self.tree_pagamentos = ttk.Treeview(
            frame_tabelas, columns=cols_pag, show="headings", style="Custom.Treeview"
        )
        self.tree_pagamentos.heading("forma", text="Forma Pagamento", anchor="w")
        self.tree_pagamentos.heading("qtd", text="Qtd", anchor="center")
        self.tree_pagamentos.heading("valor", text="Valor (R$)", anchor="e")
        self.tree_pagamentos.column("forma", width=180)
        self.tree_pagamentos.column("qtd", width=60, anchor="center")
        self.tree_pagamentos.column("valor", width=120, anchor="e")
        self.tree_pagamentos.pack(side="right", fill="both", expand=True, padx=(5, 0))

    def _gerar_relatorio(self):
        data = self.entry_rel_data.get().strip()
        if not db.validar_data(data):
            messagebox.showwarning("Aviso", "Data invalida. Use o formato AAAA-MM-DD.")
            return
        rel = db.relatorio_vendas_dia(data)

        # Atualizar cards
        resumo = rel["resumo"]
        self.cards_resumo["total_comandas"].configure(text=str(resumo["total_comandas"]))
        self.cards_resumo["faturamento"].configure(text=f"R$ {resumo['faturamento']:.2f}")
        self.cards_resumo["total_descontos"].configure(text=f"R$ {resumo['total_descontos']:.2f}")

        # Tabela produtos
        for item in self.tree_vendidos.get_children():
            self.tree_vendidos.delete(item)
        for p in rel["produtos"]:
            self.tree_vendidos.insert("", "end", values=(
                p["nome"], p["qtd"], f"{p['total']:.2f}"
            ))

        # Tabela pagamentos
        for item in self.tree_pagamentos.get_children():
            self.tree_pagamentos.delete(item)
        for pg in rel["pagamentos"]:
            self.tree_pagamentos.insert("", "end", values=(
                pg["forma_pagamento"] or "—", pg["qtd"], f"{pg['valor']:.2f}"
            ))

    def _fazer_backup(self):
        destino = filedialog.asksaveasfilename(
            title="Salvar backup do banco de dados",
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db"), ("Todos", "*.*")],
            initialfile=f"brasileirinho_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        if not destino:
            return
        try:
            db.fazer_backup(destino)
            messagebox.showinfo("Backup", f"Backup salvo em:\n{destino}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar backup:\n{e}")

    def _limpar_comandas_antigas(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Limpar Comandas Antigas")
        janela.geometry("450x280")
        janela.configure(fg_color=COR_FUNDO)
        janela.transient(self)
        janela.grab_set()

        ctk.CTkLabel(janela, text="Limpar Comandas Fechadas", font=FONTE_TITULO,
                     text_color=COR_AMARELO).pack(pady=(20, 10))

        ctk.CTkLabel(janela, text="Remover comandas fechadas ANTES de:",
                     font=FONTE_NORMAL, text_color=COR_TEXTO_SECUNDARIO).pack(padx=20, anchor="w")

        entry_data = ctk.CTkEntry(
            janela, width=200, font=FONTE_NORMAL,
            fg_color=COR_FUNDO_ENTRADA, border_color=COR_BORDA,
            placeholder_text="AAAA-MM-DD"
        )
        entry_data.pack(padx=20, pady=5)

        self._label_preview_limpeza = ctk.CTkLabel(
            janela, text="", font=FONTE_NORMAL, text_color=COR_TEXTO_SECUNDARIO
        )
        self._label_preview_limpeza.pack(padx=20, pady=5)

        def preview(*_):
            data = entry_data.get().strip()
            if db.validar_data(data):
                qtd = db.contar_comandas_fechadas_antes(data)
                self._label_preview_limpeza.configure(
                    text=f"{qtd} comanda(s) sera(o) removida(s)")
            else:
                self._label_preview_limpeza.configure(text="")

        entry_data.bind("<KeyRelease>", preview)

        def confirmar():
            data = entry_data.get().strip()
            if not db.validar_data(data):
                messagebox.showwarning("Aviso", "Data invalida. Use AAAA-MM-DD.")
                return
            qtd = db.contar_comandas_fechadas_antes(data)
            if qtd == 0:
                messagebox.showinfo("Limpeza", "Nenhuma comanda encontrada nesse periodo.")
                return
            if not messagebox.askyesno(
                "Confirmar limpeza",
                f"Remover {qtd} comanda(s) fechada(s) antes de {data}?\n\n"
                f"Recomendado: faca um backup antes.\n"
                f"Esta acao NAO pode ser desfeita."
            ):
                return
            removidas = db.limpar_comandas_antigas(data)
            janela.destroy()
            messagebox.showinfo("Limpeza", f"{removidas} comanda(s) removida(s).")

        ctk.CTkButton(
            janela, text="Remover", font=FONTE_NORMAL, height=40,
            fg_color=COR_VERMELHO, hover_color=COR_VERMELHO_HOVER,
            command=confirmar
        ).pack(pady=15)


if __name__ == "__main__":
    app = App()
    app.mainloop()
