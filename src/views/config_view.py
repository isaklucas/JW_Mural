"""abrir_configuracoes

Tela extraída de layout.py (SDD 03) — mixin de ModernApp.
Código movido verbatim; `self` e navegação inalterados.
"""
from views._shared import *  # noqa: F401,F403


class ConfigMixin:
    def abrir_configuracoes(self):
        import sys
        from pathlib import Path
        from util.backup import restore_database, _project_root

        dialog = ttk.Toplevel(self.root)
        dialog.title("Configurações")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=YES)

        ttk.Label(frame, text="⚙ Configurações", font=("Helvetica", 16, "bold"), bootstyle="primary").pack(anchor=W, pady=(0, 15))

        # --- Restaurar Banco ---
        restore_frame = ttk.LabelFrame(frame, text="Restaurar Banco", padding=15)
        restore_frame.pack(fill=X, pady=(0, 10))

        ttk.Label(restore_frame, text="Data do backup:").pack(anchor=W)

        backups_dir = _project_root() / "backups"
        datas = sorted(
            [d.name for d in backups_dir.iterdir() if d.is_dir()],
            reverse=True
        ) if backups_dir.exists() else []

        data_var = tk.StringVar(value=datas[0] if datas else "")
        combo = ttk.Combobox(restore_frame, textvariable=data_var, values=datas, state="readonly", width=20)
        combo.pack(anchor=W, pady=(2, 10))

        colecoes_frame = ttk.Frame(restore_frame)
        colecoes_frame.pack(fill=X)

        check_vars = {}

        def atualizar_colecoes(*_):
            for w in colecoes_frame.winfo_children():
                w.destroy()
            check_vars.clear()
            data = data_var.get()
            if not data:
                return
            pasta = backups_dir / data
            arquivos = sorted(pasta.glob("*.json"))
            for arq in arquivos:
                nome = arq.stem
                var = tk.BooleanVar(value=True)
                check_vars[nome] = var
                ttk.Checkbutton(colecoes_frame, text=nome, variable=var, bootstyle="primary").pack(anchor=W)

        combo.bind("<<ComboboxSelected>>", atualizar_colecoes)
        atualizar_colecoes()

        def fazer_restore():
            selecionadas = [nome for nome, var in check_vars.items() if var.get()]
            logger.info(f"Restore solicitado: coleções={selecionadas}")
            if not selecionadas:
                Messagebox.show_warning("Selecione ao menos uma coleção.", "Atenção", parent=dialog)
                return
            data = data_var.get()
            confirmar = Messagebox.yesno(
                f"Restaurar {len(selecionadas)} coleção(ões) do backup {data}?\n\nDados atuais serão substituídos.",
                "Confirmar Restauração",
                parent=dialog
            )
            logger.info(f"Confirmação restore: {confirmar!r}")
            if confirmar not in ("Yes", "Sim"):
                return
            try:
                resultados = restore_database(data, selecionadas)
                logger.info(f"Restore concluído: {resultados}")
                linhas = [f"✓ {col}: {res['count']} registros ({res['status']})" for col, res in resultados.items()]
                Messagebox.show_info("\n".join(linhas), "Restauração Concluída", parent=dialog)
            except Exception as e:
                logger.error(f"Erro no restore: {e}")
                Messagebox.show_error(f"Erro ao restaurar:\n{e}", "Erro", parent=dialog)

        ttk.Button(
            restore_frame,
            text="Restaurar",
            bootstyle="danger",
            command=fazer_restore,
            width=15
        ).pack(anchor=W, pady=(12, 0))

        # Centralizar dialog
        dialog.update_idletasks()
        w, h = 420, 480
        x = self.root.winfo_x() + (self.root.winfo_width() - w) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - h) // 2
        dialog.geometry(f"{w}x{h}+{x}+{y}")

