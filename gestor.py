"""
Gestor Financeiro Pessoal - Moçambique
Dev: abdullcadre
Requisitos: Python 3.8+ (stdlib apenas)
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

# ==================== CONFIG ====================
DATA_FILE = Path(__file__).parent / "dados_financeiros.json"

CATEGORIAS_RECEITA = ["Salário", "Negócio", "Freelance", "Remessa", "Outro"]
CATEGORIAS_DESPESA = ["Alimentação", "Renda", "Transporte (Chapa)", "Energia (EDM)",
                      "Água (FIPAG)", "Celular (Vodacom/Mcel)", "Saúde", "Escola",
                      "Família", "Lazer", "Outro"]


def fmt_mt(valor: float) -> str:
    """Formata valor em Metical: 1.234,56 MT"""
    s = f"{valor:,.2f}"
    return "MT " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_dados() -> dict:
    if not DATA_FILE.exists():
        return {"transacoes": [], "proximo_id": 1}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
            d.setdefault("transacoes", [])
            d.setdefault("proximo_id", 1)
            return d
    except (json.JSONDecodeError, OSError):
        return {"transacoes": [], "proximo_id": 1}


def salvar_dados(dados: dict) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except OSError as e:
        messagebox.showerror("Erro", f"Não foi possível salvar:\n{e}")


# ==================== APP ====================
class GestorFinanceiro:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gestor Financeiro 🇲🇿 — abdullcadre")
        self.root.geometry("820x580")
        self.root.minsize(520, 400)

        self.dados = carregar_dados()

        # Estilo
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TButton", padding=4)

        self._build_ui()
        self._refresh()

        # Atalho ENTER para adicionar
        self.root.bind("<Return>", lambda e: self._adicionar())

    # ---------- UI ----------
    def _build_ui(self):
        # --- Cabeçalho ---
        header = tk.Frame(self.root, bg="#1b5e20", height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="💰 Gestor Financeiro — Moçambique",
                 bg="#1b5e20", fg="white",
                 font=("Segoe UI", 13, "bold")).pack(side="left", padx=12)
        tk.Label(header, text="dev: abdullcadre",
                 bg="#1b5e20", fg="#c8e6c9",
                 font=("Segoe UI", 9, "italic")).pack(side="right", padx=12)

        # --- Cards resumo (3 colunas responsivas) ---
        cards = ttk.Frame(self.root, padding=(8, 8, 8, 4))
        cards.pack(fill="x")
        for i in range(3):
            cards.columnconfigure(i, weight=1, uniform="card")

        self.lbl_rec = self._card(cards, 0, "Receitas", "#2e7d32")
        self.lbl_des = self._card(cards, 1, "Despesas", "#c62828")
        self.lbl_sal = self._card(cards, 2, "Saldo", "#1565c0")

        # --- Formulário ---
        form = ttk.LabelFrame(self.root, text=" Nova Transação ", padding=8)
        form.pack(fill="x", padx=8, pady=4)
        for c in range(6):
            form.columnconfigure(c, weight=1)

        # Linha 1: Tipo | Descrição (2 cols) | Valor
        ttk.Label(form, text="Tipo").grid(row=0, column=0, sticky="w")
        self.cmb_tipo = ttk.Combobox(form, values=["Receita", "Despesa"],
                                     state="readonly", width=10)
        self.cmb_tipo.current(0)
        self.cmb_tipo.grid(row=1, column=0, sticky="ew", padx=(0, 4))
        self.cmb_tipo.bind("<<ComboboxSelected>>", lambda e: self._update_cats())

        ttk.Label(form, text="Descrição").grid(row=0, column=1, columnspan=2, sticky="w", padx=(4, 0))
        self.ent_desc = ttk.Entry(form)
        self.ent_desc.grid(row=1, column=1, columnspan=2, sticky="ew", padx=4)

        ttk.Label(form, text="Valor (MT)").grid(row=0, column=3, sticky="w", padx=(4, 0))
        self.ent_valor = ttk.Entry(form)
        self.ent_valor.grid(row=1, column=3, sticky="ew", padx=4)

        # Linha 2: Categoria | Data | Botões
        ttk.Label(form, text="Categoria").grid(row=2, column=0, columnspan=2,
                                                sticky="w", pady=(6, 0))
        self.cmb_cat = ttk.Combobox(form, state="readonly")
        self.cmb_cat.grid(row=3, column=0, columnspan=2, sticky="ew", padx=(0, 4))

        ttk.Label(form, text="Data (AAAA-MM-DD)").grid(row=2, column=2, sticky="w",
                                                        pady=(6, 0), padx=4)
        self.ent_data = ttk.Entry(form)
        self.ent_data.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_data.grid(row=3, column=2, sticky="ew", padx=4)

        btns = ttk.Frame(form)
        btns.grid(row=3, column=3, columnspan=3, sticky="e", padx=(4, 0))
        ttk.Button(btns, text="➕ Adicionar", command=self._adicionar).pack(side="left", padx=2)
        ttk.Button(btns, text="🗑 Excluir", command=self._excluir).pack(side="left", padx=2)

        self._update_cats()

        # --- Filtros ---
        filtro = ttk.Frame(self.root, padding=(8, 2))
        filtro.pack(fill="x")
        ttk.Label(filtro, text="Mostrar:").pack(side="left")
        self.var_filtro = tk.StringVar(value="Todas")
        for opt in ["Todas", "Receitas", "Despesas"]:
            ttk.Radiobutton(filtro, text=opt, value=opt,
                            variable=self.var_filtro,
                            command=self._refresh_tabela).pack(side="left", padx=4)
        ttk.Label(filtro, text="Buscar:").pack(side="left", padx=(12, 4))
        self.ent_busca = ttk.Entry(filtro, width=20)
        self.ent_busca.pack(side="left", fill="x", expand=True)
        self.ent_busca.bind("<KeyRelease>", lambda e: self._refresh_tabela())

        # --- Tabela ---
        wrap = ttk.Frame(self.root, padding=(8, 4, 8, 8))
        wrap.pack(fill="both", expand=True)

        cols = ("id", "data", "tipo", "descricao", "categoria", "valor")
        self.tree = ttk.Treeview(wrap, columns=cols, show="headings")
        heads = {"id": "ID", "data": "Data", "tipo": "Tipo",
                 "descricao": "Descrição", "categoria": "Categoria", "valor": "Valor"}
        widths = {"id": 40, "data": 90, "tipo": 75, "descricao": 200,
                  "categoria": 130, "valor": 110}
        for c in cols:
            self.tree.heading(c, text=heads[c])
            self.tree.column(c, width=widths[c], minwidth=40,
                             anchor="center" if c != "descricao" else "w",
                             stretch=True)

        self.tree.tag_configure("receita", foreground="#2e7d32")
        self.tree.tag_configure("despesa", foreground="#c62828")

        vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Rodapé
        self.lbl_status = tk.Label(self.root, text="", anchor="w",
                                    bg="#eeeeee", fg="#555",
                                    font=("Segoe UI", 8))
        self.lbl_status.pack(fill="x", side="bottom")

    def _card(self, parent, col, titulo, cor):
        f = tk.Frame(parent, bg=cor, padx=10, pady=8)
        f.grid(row=0, column=col, sticky="ew", padx=4)
        tk.Label(f, text=titulo, bg=cor, fg="white",
                 font=("Segoe UI", 9)).pack(anchor="w")
        lbl = tk.Label(f, text="MT 0,00", bg=cor, fg="white",
                       font=("Segoe UI", 13, "bold"))
        lbl.pack(anchor="w")
        return lbl

    # ---------- Lógica ----------
    def _update_cats(self):
        cats = CATEGORIAS_RECEITA if self.cmb_tipo.get() == "Receita" else CATEGORIAS_DESPESA
        self.cmb_cat["values"] = cats
        if cats:
            self.cmb_cat.current(0)

    def _adicionar(self):
        tipo = self.cmb_tipo.get()
        desc = self.ent_desc.get().strip()
        vtxt = self.ent_valor.get().strip().replace(",", ".")
        cat = self.cmb_cat.get()
        data = self.ent_data.get().strip()

        if not desc:
            messagebox.showwarning("Atenção", "Informe uma descrição.")
            return
        try:
            valor = float(vtxt)
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Atenção", "Valor inválido (ex: 150.50 ou 150,50).")
            return
        try:
            datetime.strptime(data, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Atenção", "Data inválida. Use AAAA-MM-DD.")
            return

        self.dados["transacoes"].append({
            "id": self.dados["proximo_id"],
            "data": data, "tipo": tipo, "descricao": desc,
            "categoria": cat, "valor": valor,
        })
        self.dados["proximo_id"] += 1
        salvar_dados(self.dados)

        self.ent_desc.delete(0, tk.END)
        self.ent_valor.delete(0, tk.END)
        self.ent_desc.focus_set()
        self._refresh()
        self._status(f"✔ Adicionado: {desc}")

    def _excluir(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecione uma transação.")
            return
        id_alvo = int(self.tree.item(sel[0], "values")[0])
        if not messagebox.askyesno("Confirmar", f"Excluir transação #{id_alvo}?"):
            return
        self.dados["transacoes"] = [t for t in self.dados["transacoes"]
                                     if t["id"] != id_alvo]
        salvar_dados(self.dados)
        self._refresh()
        self._status(f"🗑 Excluído #{id_alvo}")

    def _refresh_tabela(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        filtro = self.var_filtro.get()
        busca = self.ent_busca.get().strip().lower()

        lista = sorted(self.dados["transacoes"],
                       key=lambda t: (t["data"], t["id"]), reverse=True)
        for t in lista:
            if filtro == "Receitas" and t["tipo"] != "Receita":
                continue
            if filtro == "Despesas" and t["tipo"] != "Despesa":
                continue
            if busca and busca not in t["descricao"].lower() \
                    and busca not in t["categoria"].lower():
                continue
            tag = "receita" if t["tipo"] == "Receita" else "despesa"
            sinal = "+" if t["tipo"] == "Receita" else "−"
            self.tree.insert("", "end", values=(
                t["id"], t["data"], t["tipo"], t["descricao"],
                t["categoria"], f"{sinal} {fmt_mt(t['valor'])}"
            ), tags=(tag,))

    def _refresh_resumo(self):
        rec = sum(t["valor"] for t in self.dados["transacoes"] if t["tipo"] == "Receita")
        des = sum(t["valor"] for t in self.dados["transacoes"] if t["tipo"] == "Despesa")
        self.lbl_rec.config(text=fmt_mt(rec))
        self.lbl_des.config(text=fmt_mt(des))
        self.lbl_sal.config(text=fmt_mt(rec - des))

    def _refresh(self):
        self._refresh_tabela()
        self._refresh_resumo()

    def _status(self, msg):
        self.lbl_status.config(text="  " + msg)
        self.root.after(3000, lambda: self.lbl_status.config(text=""))


# ==================== MAIN ====================
def main():
    root = tk.Tk()
    GestorFinanceiro(root)
    root.mainloop()


if __name__ == "__main__":
    main()