from pathlib import Path

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.prompt import Prompt
from rich.console import Console

from core.constants import CONSOLE_WIDTH

theme = Theme(
    {
        "info": "bold cyan",
        "dotted": "bold grey50",
        "warning": "bold yellow",
        "error": "bold red",
        "success": "bold green",
        "step": "bold white",
        "highlight": "bold magenta",
    }
)


class BashUI:
    def __init__(self) -> None:
        self.console = Console(width=CONSOLE_WIDTH, theme=theme, force_terminal=True)
        self.width = CONSOLE_WIDTH

    def clear(self) -> None:
        self.console.clear()

    def header(self, title: str, subtitle: str = "") -> None:
        self.clear()

        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row(f"[step]{title}[/step]")

        if subtitle:
            grid.add_row(f"[info]{subtitle}[/info]")

        grid.add_row("[dotted]@grausvera[/dotted]")

        self.console.print(
            Panel(
                grid,
                style="info",
                box=box.ROUNDED,
                width=self.width,
                padding=(1, 2),
            )
        )
        self.console.print()

    def _fmtDotted(self, key: str, value: object) -> str:
        padding = 10
        str_val = str(value)

        space_needed = self.width - len(key) - len(str_val) - padding
        dots = "." * max(1, space_needed)
        return f"[info]{key}[/info] [dotted]{dots}[/dotted] [step]{str_val}[/step]"

    def footer(self, context: dict[str, object]) -> None:
        rows = [
            (
                "Dataset Origen",
                f"{context.get('dataset_source', 'N/A')}",
            ),
            (
                "Dataset Procesado",
                f"{Path(*Path(context.get('dataset_path', 'N/A')).parts[-2:]).as_posix()}",
            ),
            (
                "Imágenes Total",
                f"{context.get('amount_pairs', 0)}"
                + f" (Train: {context.get('amount_train', 0)} | Val: {context.get('amount_val', 0)})",
            ),
            (
                "Etiquetas Total",
                f"{context.get('amount_pairs', 0)}"
                + f" (Train: {context.get('amount_train', 0)} | Val: {context.get('amount_val', 0)})",
            ),
            (
                "Clases",
                f"{len(context.get('classes', []))}"
                + f" ({', '.join(context.get('classes', []))})",
            ),
            (
                "Modelo Base",
                f"{Path(*Path(context.get('base_model_path', 'N/A')).parts[-3:]).as_posix()}",
            ),
            (
                "Configuración",
                f"Epochs: {context.get('epochs', 0)} | Batch: {context.get('batch', 0)} | Imgsz: {context.get('imgsz', 0)}",
            ),
            (
                "Modelo Entrenado",
                f"{Path(*Path(context.get('best_model_path', 'N/A')).parts[-3:]).as_posix()}",
            ),
        ]

        grid = Table.grid(expand=True)
        grid.add_column()

        for key, value in rows:
            grid.add_row(self._fmtDotted(key, value))

        self.console.print()
        self.console.print(
            Panel(
                grid,
                title="RESUMEN FINAL",
                style="info",
                box=box.ROUNDED,
                width=self.width,
                padding=(1, 2),
            )
        )
        self.console.print()

    def section(self, title: str, subtitle: str = "") -> None:
        self.console.print(f"\n[step] {title.upper()} [/step]")
        self.console.print(f"[info]{'─' * self.width}[/info]")
        self.console.print()

        if subtitle:
            self.console.print(f"[dotted]{subtitle}[/dotted]\n")

    def ask(
        self,
        question: str,
        choices: list[str] | None = None,
        default: str | None = None,
    ) -> str:
        choices_str = ""
        if choices and len(choices) > 0:
            choices_str = f" [bold magenta]({'/'.join(choices)})[/bold magenta]"

        default_str = f" [bold grey50]({default})[/bold grey50]" if default else ""

        prompt_str = (
            f"[bold cyan]?[/bold cyan] [bold white]{question}[/bold white]"
            + choices_str
            + default_str
        )

        raw_value = Prompt.ask(prompt_str, default=default, show_default=False)
        safe_value = str(raw_value) if raw_value is not None else ""
        value = safe_value.strip().lower()

        if choices is not None and value not in choices:
            self.stepWarning(
                f"Advertencia: Opción '{value}' no reconocida.\n"
                + f"  Por favor ingrese una de estas opciones: {', '.join(choices)}."
            )
            return self.ask(question, choices, default)

        if not value:
            self.stepWarning(
                "Advertencia: El valor no puede estar vacío.\n"
                + "  Por favor ingrese un valor válido."
            )
            return self.ask(question, choices, default)

        return str(value)

    def askConfirm(self, question: str, default: bool = False) -> bool:
        default_str = "(S/n)" if default else "(s/N)"
        raw_value = Prompt.ask(
            f"[bold cyan]?[/bold cyan] [bold white]{question}[/bold white]"
            + f" [bold grey50]{default_str}[/bold grey50]",
            default=("s" if default else "n"),
            show_default=False,
        )
        safe_value = str(raw_value) if raw_value is not None else ""
        value = safe_value.strip().lower()

        if value not in ["s", "si", "n", "no"]:
            self.stepWarning(
                f"Advertencia: Opción '{value}' no reconocida.\n"
                + f"  Por favor ingrese una de estas opciones: {', '.join(['s', 'si', 'n', 'no'])}."
            )
            return self.askConfirm(question, default)

        if not value:
            self.stepWarning(
                "Advertencia: El valor no puede estar vacío.\n"
                + "  Por favor ingrese un valor válido."
            )
            return self.askConfirm(question, default)

        return value in ["s", "si"]

    def askPath(self, question: str, default: Path | None = None) -> Path:
        raw_value = self.ask(question, default=str(default) if default else None)
        safe_value = str(raw_value) if raw_value is not None else ""
        clean_value = safe_value.strip().replace("'", "").replace('"', "")

        if not clean_value:
            self.stepWarning(
                "Advertencia: La ruta no puede estar vacía.\n"
                + "  Por favor escriba una ruta válida."
            )
            return self.askPath(question, default)

        return Path(clean_value)

    def askInt(self, question: str, default: int | None = None) -> int:
        try:
            value = self.ask(question, default=str(default))
            return int(value)
        except ValueError:
            self.stepWarning(
                f"Advertencia: Número '{value}' incorrecto.\n"
                + "  Por favor ingrese un número entero válido."
            )
            return self.askInt(question, default)

    def stepInfo(self, msg: str) -> None:
        # Se puede cambiar por el tag '⠋' por '🔹'
        self.console.print(f"[info]⠋ {msg}...[/info]")

    def stepSuccess(self, msg: str) -> None:
        self.console.print(f"[success]✔ {msg}[/success]")

    def stepWarning(self, msg: str) -> None:
        self.console.print(f"\n[warning]⚠ {msg}[/warning]\n")

    def stepError(self, msg: str) -> None:
        self.console.print(f"\n[error]✘ {msg}" + "\n\n Saliendo...[/error]\n")

    def stepInfoBox(self, key: str, value: str) -> None:
        padding = 6
        str_val = str(value)
        space_needed = self.width - len(key) - len(str_val) - padding
        dots = "." * max(1, space_needed)
        self.console.print(f"  [dotted]{key} {dots} {str_val}[dotted]")
