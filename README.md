# Gestor Financeiro Pessoal

Aplicação desktop de gestão financeira pessoal desenvolvida em Python com interface Tkinter. Permite registar receitas e despesas, organizar transações por categorias e acompanhar o saldo em tempo real, com persistência local em formato JSON.

## Funcionalidades

- Registo de receitas e despesas com descrição, valor, categoria e data
- Remoção de transações com confirmação
- Cálculo automático de receitas, despesas e saldo
- Filtros por tipo de transação e pesquisa por descrição ou categoria
- Categorias pré-definidas para receitas e despesas
- Persistência automática dos dados em ficheiro JSON local
- Interface responsiva com redimensionamento dinâmico
- Validação de entrada de valores e datas
- Atalho de teclado (Enter) para submissão rápida

## Stack Técnica

| Componente       | Tecnologia        |
|------------------|-------------------|
| Linguagem        | Python 3.8+       |
| Interface        | Tkinter / ttk     |
| Armazenamento    | JSON (local)      |
| Dependências     | Nenhuma (stdlib)  |

## Arquitetura

Aplicação single-file, sem dependências externas. A separação interna segue três camadas lógicas:

- **Persistência** — funções `carregar_dados()` e `salvar_dados()` gerem leitura e escrita do ficheiro JSON, com tratamento de corrupção e erros de I/O.
- **Interface** — classe `GestorFinanceiro` constrói e mantém os widgets Tkinter, organizados em grid responsivo.
- **Lógica de negócio** — métodos de adição, remoção, filtragem e cálculo de saldo, com validação de entrada.

## Requisitos

- Python 3.8 ou superior
- Tkinter (incluído na instalação padrão do Python)

## Instalação e Execução

```bash
git clone https://github.com/abdullcadre/gestor-financeiro.git
cd gestor-financeiro
python gestor.py
