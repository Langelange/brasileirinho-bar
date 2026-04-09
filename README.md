<p align="center">
  <img src="assets/logo.jpeg" alt="Brasileirinho Bar" width="250">
</p>

<h1 align="center">Brasileirinho Bar</h1>
<p align="center">Sistema de Comandas</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/CustomTkinter-UI-green" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/SQLite-database-yellow" alt="SQLite">
  <img src="https://img.shields.io/badge/plataforma-Windows-blue?logo=windows" alt="Windows">
</p>

---

Sistema desktop para gerenciamento de comandas de bar. Substitui o controle manual em caderno por uma interface simples e rápida, ideal para eventos e operação diária.

## Funcionalidades

- **Comandas** — Abre comanda, associa cliente, adiciona produtos, exibe total em tempo real, fecha com forma de pagamento e desconto
- **Produtos** — Cadastro com nome, categoria (Cerveja, Dose, Drink, Refrigerante, etc.) e preço
- **Clientes** — Cadastro com nome e telefone, busca instantânea ao digitar
- **Relatórios** — Vendas do dia, produtos mais vendidos, faturamento por forma de pagamento (Dinheiro, PIX, Cartão)

## Instalação

### Opção 1 — Executável (recomendado)

Baixe o `BrasileirinhoBar.exe` na aba [Releases](../../releases) e execute. Não precisa instalar nada.

### Opção 2 — A partir do código-fonte

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```

### Gerar o executável (.exe)

```bash
python build.py
```

O executável será gerado em `dist/BrasileirinhoBar.exe`.

## Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3 | Linguagem principal |
| CustomTkinter | Interface gráfica moderna (tema escuro) |
| SQLite | Banco de dados local (arquivo único) |
| Pillow | Manipulação da logo |
| PyInstaller | Geração do executável Windows |

## Estrutura

```
brasileirinho-bar/
├── assets/
│   ├── logo.jpeg       # Logo do bar
│   └── logo.ico        # Ícone do executável
├── main.py             # Interface gráfica
├── database.py         # Banco de dados e queries
├── build.py            # Script para gerar o .exe
├── requirements.txt    # Dependências Python
└── brasileirinho.db    # Banco de dados (criado automaticamente)
```

## Backup

O arquivo `brasileirinho.db` contém todos os dados (produtos, clientes, comandas). Para fazer backup, basta copiar esse arquivo.

## Licença

Uso privado — Brasileirinho Bar.
