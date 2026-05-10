import datetime
import os
import random
import sys
import time

import requests
from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table

# Importação condicional do termios para compatibilidade multiplataforma
try:
    import termios
    import tty
except ImportError:
    termios = None
    tty = None

# Console nativo do Rich
console = Console(force_terminal=True, force_interactive=True)

CONDICOES = {
    "113": "Ensolarado",
    "116": "Parcialmente nublado",
    "119": "Nublado",
    "122": "Encoberto",
    "143": "Nevoa",
    "176": "Chuva leve ocasional",
    "179": "Neve leve ocasional",
    "182": "Garoa com neve",
    "185": "Garoa gelada",
    "200": "Trovoada ocasional",
    "227": "Nevasca leve",
    "230": "Nevasca",
    "248": "Nevoeiro",
    "260": "Nevoeiro gelado",
    "263": "Garoa leve ocasional",
    "266": "Garoa leve",
    "281": "Garoa gelada",
    "284": "Garoa gelada intensa",
    "293": "Chuva leve ocasional",
    "296": "Chuva leve",
    "299": "Chuva moderada ocasional",
    "302": "Chuva moderada",
    "305": "Chuva intensa ocasional",
    "308": "Chuva intensa",
    "311": "Chuva gelada leve",
    "314": "Chuva gelada moderada",
    "317": "Mistura leve",
    "320": "Mistura moderada",
    "323": "Neve leve ocasional",
    "326": "Neve leve",
    "329": "Neve moderada ocasional",
    "332": "Neve moderada",
    "335": "Neve intensa ocasional",
    "338": "Neve intensa",
    "350": "Granizo",
    "353": "Chuva leve ocasional",
    "356": "Chuva moderada/intensa",
    "359": "Chuva torrencial",
    "362": "Mistura leve ocasional",
    "365": "Mistura moderada/intensa",
    "368": "Neve leve ocasional",
    "371": "Neve moderada/intensa",
    "374": "Granizo leve ocasional",
    "377": "Granizo moderado/intenso",
    "386": "Chuva leve com trovoada",
    "389": "Chuva moderada/intensa com trovoada",
    "392": "Neve leve com trovoada",
    "395": "Neve moderada/intensa com trovoada",
}

OPCOES_MENU = ["Brasilia", "Londres", "Toquio", "Paris", "Washington", "CPBR18"]


class TerminalDashboard:
    """Gerenciador de Buffer estilo DOS/Unix clássico.

    Atualiza in-place sem acumular histórico.
    """

    def __init__(self, console_obj):
        self.console = console_obj

    def __enter__(self):
        # Limpa a tela completamente uma única vez ao iniciar para começar limpo
        self.console.clear()
        # Oculta o cursor piscante estilo ferramentas DOS antigas
        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restaura o cursor ao sair
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()

    def desenhar(self, renderable):
        """Escreve a partir do canto superior esquerdo (row 1, col 1).

        Sobrescreve o frame anterior.
        """
        # Captura as cores ANSI geradas pelo Rich
        with self.console.capture() as capture:
            self.console.print(renderable)
        ansi_text = capture.get()

        # Garante o Carriage Return (\r\n) para evitar Staircase Effect no modo RAW
        ansi_text_cr = ansi_text.replace("\r\n", "\n").replace("\n", "\r\n")

        # Move para o topo e escreve, depois limpa as linhas que sobrarem abaixo.
        sys.stdout.write("\x1b[H" + ansi_text_cr + "\x1b[J")
        sys.stdout.flush()


def check_key_raw(fd) -> str:
    """Lê tecla de forma não-bloqueante assumindo modo RAW."""
    if sys.platform == "win32":
        import msvcrt

        if msvcrt.kbhit():
            ch = msvcrt.getch()
            if ch in (b"\x00", b"\xe0"):
                ch2 = msvcrt.getch()
                if ch2 == b"H":
                    return "up"
                if ch2 == b"P":
                    return "down"
                if ch2 == b"K":
                    return "left"
                if ch2 == b"M":
                    return "right"
                return "special"
            if ch in (b"\r", b"\n"):
                return "enter"
            if ch == b"\x1b":
                return "esc"
            if ch == b"\x08":
                return "backspace"
            try:
                return ch.decode("latin-1").lower()
            except Exception:
                return None
    else:
        # Linux/macOS
        if fd is None or termios is None:
            return None
        try:
            b = os.read(fd, 1)
            if b:
                if b == b"\x1b":
                    old_settings = termios.tcgetattr(fd)
                    new_settings = termios.tcgetattr(fd)
                    try:
                        new_settings[6][termios.VMIN] = 0
                        new_settings[6][termios.VTIME] = 1
                    except TypeError:
                        new_settings[6][termios.VMIN] = b"\x00"
                        new_settings[6][termios.VTIME] = b"\x01"
                    termios.tcsetattr(fd, termios.TCSANOW, new_settings)

                    extra = os.read(fd, 2)
                    termios.tcsetattr(fd, termios.TCSANOW, old_settings)

                    if extra == b"[A":
                        return "up"
                    if extra == b"[B":
                        return "down"
                    if extra == b"[C":
                        return "right"
                    if extra == b"[D":
                        return "left"
                    return "esc"
                if b in (b"\r", b"\n"):
                    return "enter"
                if b == b"\x7f":
                    return "backspace"
                try:
                    return b.decode("utf-8").lower()
                except Exception:
                    return None
        except Exception:
            pass
    return None


def confirmar_saida(fd, old_settings, td: TerminalDashboard) -> bool:
    """Confirmação de saída interativa DOS com cores e alinhamento impecável."""
    opcao = True  # True = Sim, Sair; False = Não, Voltar
    opcao_anterior = None

    def gerar_layout_confirmacao(selecionado: bool) -> Panel:
        sim_style = "bold white on red" if selecionado else "dim white"
        nao_style = "bold white on green" if not selecionado else "dim white"

        sim_btn = f"[{sim_style}]  [1] SIM, SAIR DO PROGRAMA  [/{sim_style}]"
        nao_btn = f"[{nao_style}]  [2] NAO, VOLTAR AO CLIMA CLI  [/{nao_style}]"

        conteudo = (
            "\n [bold white]VOCE REALMENTE DESEJA SAIR DO APLICATIVO?"
            "[/bold white]\n\n"
            f"   {sim_btn}\n"
            f"   {nao_btn}\n\n"
            " [dim]Use as setas [UP/DOWN] para alternar e [ENTER] "
            "para confirmar.[/dim]"
        )
        return Panel(
            conteudo,
            title="[bold red] CONFIRMACAO DE SAIDA [/bold red]",
            border_style="bold red",
            box=box.ROUNDED,
            width=65,
        )

    while True:
        if opcao != opcao_anterior:
            td.desenhar(gerar_layout_confirmacao(opcao))
            opcao_anterior = opcao

        key = check_key_raw(fd)
        if key in ("up", "down", "left", "right", "tab"):
            opcao = not opcao
        elif key in ("s", "y", "1"):
            opcao = True
            td.desenhar(gerar_layout_confirmacao(opcao))
            time.sleep(0.1)
            return True
        elif key in ("n", "esc", "2"):
            opcao = False
            td.desenhar(gerar_layout_confirmacao(opcao))
            time.sleep(0.1)
            return False
        elif key == "enter":
            return opcao
        time.sleep(0.05)


def get_utilidade_publica(cidade: str, atual: dict) -> str:
    cidade_lower = city_clean_accent(cidade.lower())

    if city_is_cp(cidade_lower):
        dicas = [
            "CPBR18: Arena aberta 24 horas!",
            "CPBR18: Traga cabo de rede e agasalho!",
            "CPBR18: Participe das mentorias do evento!",
            "CPBR18: Conecte-se com mentes brilhantes!",
        ]
        return random.choice(dicas)

    if "sao paulo" in cidade_lower:
        hoje = datetime.datetime.now().weekday()
        if hoje == 0:
            rodizio = "Placas 1 e 2"
        elif hoje == 1:
            rodizio = "Placas 3 e 4"
        elif hoje == 2:
            rodizio = "Placas 5 e 6"
        elif hoje == 3:
            rodizio = "Placas 7 e 8"
        elif hoje == 4:
            rodizio = "Placas 9 e 0"
        else:
            rodizio = "Liberado (Fim de semana)"
        return f"Util (SP): Rodízio ({rodizio})"

    elif "londres" in cidade_lower or "london" in cidade_lower:
        try:
            resp = requests.get(
                "https://api.tfl.gov.uk/line/mode/tube/status",
                timeout=5,
            )
            if resp.status_code == 200:
                linhas = resp.json()
                atrasos = [
                    linha["name"]
                    for linha in linhas
                    if linha["lineStatuses"][0]["statusSeverity"] != 10
                ]
                if atrasos:
                    return f"LON Tube: Atrasos ({', '.join(atrasos[:2])})"
                else:
                    return "LON Tube: Good Service"
        except Exception:
            pass
        return "LON Tube (Status indisponível)"

    elif "rio de janeiro" in cidade_lower:
        return "Util (RJ): Cond. Mar (Ressaca, ondas 2.5m)"

    elif cidade_lower in ["goiania", "brasilia", "cuiaba", "campo grande"]:
        umidade = int(atual.get("humidity", 100))
        if umidade < 30:
            return "Alerta: Umidade Crítica (Beba água)"
        elif umidade < 50:
            return "Alerta: Umidade Baixa (Beba água)"
        else:
            return "Umidade em níveis aceitáveis"

    else:
        sensacao = atual.get("FeelsLikeC", "N/A")
        uv = atual.get("uvIndex", "N/A")
        return f"Sensação {sensacao}°C | Índice UV {uv}"


def city_clean_accent(text: str) -> str:
    import unicodedata

    return "".join(
        c
        for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def city_is_cp(cidade: str) -> bool:
    clean = city_clean_accent(cidade.lower())
    return clean in ("cpbr18", "campus party", "campus party 2026")


def obter_dados_clima(cidade: str) -> dict:
    cidade_query = "Sao Paulo" if city_is_cp(cidade) else cidade

    url = f"https://wttr.in/{cidade_query}?format=j1"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    atual = data["current_condition"][0]

    temp = (
        atual["temp_C"]
        if isinstance(atual.get("temp_C"), (str, int))
        else "N/A"
    )
    if temp == "N/A" and "FeelsLikeC" in atual:
        temp = atual["FeelsLikeC"]

    if temp == "N/A":
        temp = atual.get("temp_C", "N/A")

    umidade = atual["humidity"]
    vento = atual["windspeedKmph"]
    codigo = atual["weatherCode"]
    condicao = CONDICOES.get(codigo, f"Codigo {codigo}")

    utilidade = get_utilidade_publica(cidade, atual).strip()

    return {
        "temp": temp,
        "umidade": umidade,
        "vento": vento,
        "condicao": condicao,
        "utilidade": utilidade,
    }


def obter_animacao_clima(segundo: int) -> str:
    """Retorna frame para retrocompatibilidade de testes."""
    frames = ["☀️  ", "🌞 ", "☀️  ", "🌤️  "]
    return frames[segundo % len(frames)]


def obter_emoji_clima_animado(condicao: str) -> str:
    """Gera frames de animação de forma fluida baseada no tempo."""
    frame = int(time.time() * 2) % 4
    cond_lower = condicao.lower()

    if "sol" in cond_lower or "ensolarado" in cond_lower or "limpo" in cond_lower:
        frames = ["☀️ ", "🔆 ", "☀️ ", "🔅 "]
        return frames[frame]
    elif "chuva" in cond_lower or "garoa" in cond_lower or "torrencial" in cond_lower:
        frames = ["🌧️ ", "💧 ", "🌧️ ", "💦 "]
        return frames[frame]
    elif "trovoada" in cond_lower or "tempestade" in cond_lower:
        frames = ["⛈️ ", "⚡ ", "🌩️ ", "⛈️ "]
        return frames[frame]
    elif "neve" in cond_lower or "nevasca" in cond_lower or "granizo" in cond_lower:
        frames = ["❄️ ", "🌨️ ", "❄️ ", "🌨️ "]
        return frames[frame]
    elif (
        "nublado" in cond_lower
        or "encoberto" in cond_lower
        or "parcialmente" in cond_lower
    ):
        frames = ["☁️ ", "⛅ ", "☁️ ", "🌤️ "]
        return frames[frame]
    elif "nevoa" in cond_lower or "nevoeiro" in cond_lower:
        frames = ["🌫️ ", "░░ ", "🌫️ ", "▒▒ "]
        return frames[frame]
    else:
        frames = ["🌍 ", "🌎 ", "🌏 ", "🌍 "]
        return frames[frame]


def obter_emoji_cpbr18_animado() -> str:
    """Gera uma animação gamer/cyber extremamente divertida para a Campus Party."""
    frame = int(time.time() * 4) % 6
    frames = ["👾", "💻", "🚀", "🔥", "⚡", "🤖"]
    return frames[frame]


def gerar_painel(cidade: str, clima_data: dict) -> Panel:
    agora = datetime.datetime.now()
    hora_formatada = agora.strftime("%H:%M:%S")

    is_cp = city_is_cp(cidade)
    if is_cp:
        title_text = (
            "[bold blink magenta] #CPBR18 (Campus Party 2026) "
            "[/bold blink magenta]"
        )
    else:
        title_text = f"[bold cyan] DASHBOARD: {cidade.upper()} [/bold cyan]"

    # Obtém o emoji climátio animado em tempo de execução
    emoji_animado = obter_emoji_clima_animado(clima_data["condicao"])

    conteudo = (
        f" [bold white]Relogio[/bold white]           : "
        f"[bold magenta]{hora_formatada}[/bold magenta]\n"
        f" [bold white]Status[/bold white]            : "
        f"[bold yellow]{clima_data['condicao']}[/bold yellow] "
        f"{emoji_animado} ([bold green]{clima_data['temp']}C[/bold green])\n"
        f" [bold white]Umidade[/bold white]           : "
        f"[bold blue]{clima_data['umidade']}%[/bold blue]\n"
        f" [bold white]Vento[/bold white]             : "
        f"[bold blue]{clima_data['vento']} km/h[/bold blue]\n"
        f" [bold white]Utilidade Publica[/bold white] : "
        f"[bold green]{clima_data['utilidade']}[/bold green]"
    )

    return Panel(
        conteudo,
        title=title_text,
        border_style="bold magenta" if is_cp else "bold cyan",
        box=box.ROUNDED,
        width=65,
    )


def gerar_layout_menu(opcao_selecionada: int) -> Panel:
    emoji_cp = obter_emoji_cpbr18_animado()

    # Alterna entre ícones de bandeiras e marcos históricos das cidades
    # para dar vida ao menu principal
    frame = int(time.time() * 2) % 2

    def flag(f_active, f_alt):
        return f_active if frame == 0 else f_alt

    opcoes_menu = [
        (f"{flag('🇧🇷', '🏛️')} Brasilia", "Capital do Brasil"),
        (f"{flag('🇬🇧', '🏰')} Londres", "Capital do Reino Unido"),
        (f"{flag('🇯🇵', '🗼')} Toquio", "Capital do Japao"),
        (f"{flag('🇫🇷', '🗼')} Paris", "Capital da Franca"),
        (f"{flag('🇺🇸', '🏛️')} Washington", "Capital dos EUA"),
        (f"{emoji_cp} #CPBR18 (Campus Party 2026) {emoji_cp}", "Destaque"),
    ]

    tabela = Table(box=None, show_header=False, expand=True)
    tabela.add_column("Opcoes")

    for i, (nome, desc) in enumerate(opcoes_menu):
        cursor = " -> " if i == opcao_selecionada else "    "

        if i == 5:  # CPBR18
            if i == opcao_selecionada:
                tabela.add_row(
                    f"[bold blink magenta]{cursor} {nome}"
                    "[/bold blink magenta] [bold yellow]<- EM DESTAQUE"
                    "[/bold yellow]"
                )
            else:
                tabela.add_row(
                    f"[bold yellow]{cursor} {nome}[/bold yellow] "
                    f"[dim]({desc})[/dim]"
                )
        else:
            if i == opcao_selecionada:
                tabela.add_row(
                    f"[bold cyan]{cursor} {nome}[/bold cyan] "
                    "[bold green](Selecionado)[/bold green]"
                )
            else:
                tabela.add_row(
                    f"[white]{cursor} {nome}[/white] [dim]({desc})[/dim]"
                )

    menu_content = Group(
        "[bold white]Selecione uma opcao utilizando as setas "
        "[bold magenta][UP/DOWN][/bold magenta] e pressione "
        "[bold green][ENTER][/bold green]:[/bold white]\n",
        tabela,
        "\n [bold yellow]S[/bold yellow] - Selecionar Capitais do Brasil",
        " [bold red]ESC[/bold red] - Sair do Programa\n",
        "[dim]Dica: Digite o numero de 1 a 6 diretamente no teclado.[/dim]",
    )

    return Panel(
        menu_content,
        title="[bold yellow] CLIMA CLI - MENU SELETIVO [/bold yellow]",
        subtitle="[bold green] Campus Party Brasil (#CPBR18) em Destaque "
        "[/bold green]",
        border_style="bold magenta",
        box=box.DOUBLE,
        width=65,
    )


def exibir_clima_cidade(fd, cidade: str, old_settings, td: TerminalDashboard):
    """Exibe o clima da cidade com redesenho constante para animações."""
    with console.status(
        f"[bold green]Buscando clima de {cidade}...[/bold green]",
        spinner="line",
    ):
        try:
            clima_data = obter_dados_clima(cidade)
        except Exception as e:
            console.print(
                f"[bold red]Erro ao buscar dados para '{cidade}': {e}"
                "[/bold red]"
            )
            time.sleep(2)
            return

    ultima_atualizacao = time.time()
    ultimo_redesenho = 0

    footer = Panel(
        " [bold magenta]V[/bold magenta] ou [bold magenta]Backspace"
        "[/bold magenta] para Voltar ao Menu | [bold red]ESC[/bold red] "
        "para Sair",
        border_style="bold cyan",
        box=box.ROUNDED,
        width=65,
    )

    while True:
        agora = time.time()

        # Redesenha a tela a cada 250ms de forma síncrona
        if agora - ultimo_redesenho > 0.25:
            if agora - ultima_atualizacao > 300:
                try:
                    clima_data = obter_dados_clima(cidade)
                    ultima_atualizacao = agora
                except Exception:
                    pass
            painel_layout = gerar_painel(cidade, clima_data)
            td.desenhar(Group(painel_layout, footer))
            ultimo_redesenho = agora

        key = check_key_raw(fd)
        if key in ("v", "backspace"):
            break  # Volta ao menu
        elif key == "esc":
            if confirmar_saida(fd, old_settings, td):
                console.print(
                    "\n[bold yellow]Saindo da aplicacao. Ate logo!"
                    "[/bold yellow]"
                )
                if sys.platform != "win32" and old_settings is not None:
                    termios.tcsetattr(fd, termios.TCSANOW, old_settings)
                sys.exit(0)
            else:
                ultimo_redesenho = 0  # Força redesenho imediato

        time.sleep(0.05)


CAPITAIS_BRASIL = [
    ("Aracaju", "Sergipe"),
    ("Belem", "Para"),
    ("Belo Horizonte", "Minas Gerais"),
    ("Boa Vista", "Roraima"),
    ("Brasilia", "Distrito Federal"),
    ("Campo Grande", "Mato Grosso do Sul"),
    ("Cuiaba", "Mato Grosso"),
    ("Curitiba", "Parana"),
    ("Florianopolis", "Santa Catarina"),
    ("Fortaleza", "Ceara"),
    ("Goiania", "Goias"),
    ("Joao Pessoa", "Paraiba"),
    ("Macapa", "Amapa"),
    ("Maceio", "Alagoas"),
    ("Manaus", "Amazonas"),
    ("Natal", "Rio Grande do Norte"),
    ("Palmas", "Tocantins"),
    ("Porto Alegre", "Rio Grande do Sul"),
    ("Porto Velho", "Rondonia"),
    ("Recife", "Pernambuco"),
    ("Rio Branco", "Acre"),
    ("Rio de Janeiro", "Rio de Janeiro"),
    ("Salvador", "Bahia"),
    ("Sao Luis", "Maranhao"),
    ("Sao Paulo", "Sao Paulo"),
    ("Teresina", "Piaui"),
    ("Vitoria", "Espirito Santo"),
]


def gerar_layout_capitais(opcao_selecionada: int, scroll_index: int) -> Panel:
    tabela = Table(box=None, show_header=False, expand=True)
    tabela.add_column("Opcoes")

    view_size = 10
    end_index = min(scroll_index + view_size, len(CAPITAIS_BRASIL))

    for idx in range(scroll_index, end_index):
        nome, estado = CAPITAIS_BRASIL[idx]
        cursor = " -> " if idx == opcao_selecionada else "    "

        if idx == opcao_selecionada:
            tabela.add_row(
                f"[bold cyan]{cursor} {nome}[/bold cyan] "
                f"[bold green]({estado})[/bold green]"
            )
        else:
            tabela.add_row(
                f"[white]{cursor} {nome}[/white] [dim]({estado})[/dim]"
            )

    conteudo = Group(
        f"[bold white]Selecione uma Capital do Brasil ("
        f"[bold magenta]{opcao_selecionada + 1}/"
        f"{len(CAPITAIS_BRASIL)}[/bold magenta]):[/bold white]\n",
        tabela,
        "\n [bold yellow]Setas Cima/Baixo[/bold yellow] - Navegar na Lista",
        " [bold green]ENTER[/bold green] - Confirmar Selecao",
        " [bold red]V / Backspace / ESC[/bold red] - Voltar ao Menu",
    )

    return Panel(
        conteudo,
        title="[bold yellow] SELECAO DE CAPITAIS DO BRASIL [/bold yellow]",
        subtitle=f"[bold cyan] Capitais {scroll_index + 1} a {end_index} de "
        f"{len(CAPITAIS_BRASIL)} [/bold cyan]",
        border_style="bold yellow",
        box=box.ROUNDED,
        width=65,
    )


def selecionar_capital_brasil(
    fd, old_settings, td: TerminalDashboard
) -> str or None:
    """Apresenta submenu com rolagem contínua para as 27 capitais."""
    opcao_selecionada = 0
    scroll_index = 0
    view_size = 10
    opcao_anterior = None

    td.desenhar(gerar_layout_capitais(opcao_selecionada, scroll_index))

    while True:
        key = check_key_raw(fd)
        tecla_pressionada = False

        if key == "up":
            opcao_selecionada = (opcao_selecionada - 1) % len(CAPITAIS_BRASIL)
            if opcao_selecionada < scroll_index:
                scroll_index = opcao_selecionada
            elif opcao_selecionada == len(CAPITAIS_BRASIL) - 1:
                scroll_index = len(CAPITAIS_BRASIL) - view_size
            tecla_pressionada = True

        elif key == "down":
            opcao_selecionada = (opcao_selecionada + 1) % len(CAPITAIS_BRASIL)
            if opcao_selecionada >= scroll_index + view_size:
                scroll_index = opcao_selecionada - view_size + 1
            elif opcao_selecionada == 0:
                scroll_index = 0
            tecla_pressionada = True

        elif key in ("v", "backspace", "esc"):
            return None

        elif key == "enter":
            return CAPITAIS_BRASIL[opcao_selecionada][0]

        if tecla_pressionada or (opcao_selecionada != opcao_anterior):
            td.desenhar(gerar_layout_capitais(opcao_selecionada, scroll_index))
            opcao_anterior = opcao_selecionada

        time.sleep(0.05)


def main():
    if len(sys.argv) >= 2:
        cidade = sys.argv[1]

        if not sys.stdin.isatty():
            try:
                clima_data = obter_dados_clima(cidade)
                console.print(gerar_painel(cidade, clima_data))
            except Exception as e:
                console.print(f"Erro: {e}")
            sys.exit(0)

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd) if termios else None
        try:
            if sys.platform != "win32" and termios and tty:
                tty.setraw(fd, termios.TCSANOW)
                new_settings = termios.tcgetattr(fd)
                try:
                    new_settings[6][termios.VMIN] = 0
                    new_settings[6][termios.VTIME] = 0
                except TypeError:
                    new_settings[6][termios.VMIN] = b"\x00"
                    new_settings[6][termios.VTIME] = b"\x00"
                termios.tcsetattr(fd, termios.TCSANOW, new_settings)

            with TerminalDashboard(console) as td:
                exibir_clima_cidade(fd, cidade, old_settings, td)
        finally:
            if sys.platform != "win32" and termios and old_settings:
                termios.tcsetattr(fd, termios.TCSANOW, old_settings)
        sys.exit(0)

    if not sys.stdin.isatty():
        console.print("Uso: python main.py <cidade>")
        sys.exit(1)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd) if termios else None
    opcao_selecionada = 0
    opcao_anterior = None
    ultimo_layout_update = 0

    try:
        if sys.platform != "win32" and termios and tty:
            tty.setraw(fd, termios.TCSANOW)
            new_settings = termios.tcgetattr(fd)
            try:
                new_settings[6][termios.VMIN] = 0
                new_settings[6][termios.VTIME] = 0
            except TypeError:
                new_settings[6][termios.VMIN] = b"\x00"
                new_settings[6][termios.VTIME] = b"\x00"
            termios.tcsetattr(fd, termios.TCSANOW, new_settings)

        with TerminalDashboard(console) as td:
            while True:
                agora = time.time()
                key = check_key_raw(fd)

                tecla_pressionada = False
                if key == "up":
                    opcao_selecionada = (opcao_selecionada - 1) % len(
                        OPCOES_MENU
                    )
                    tecla_pressionada = True
                elif key == "down":
                    opcao_selecionada = (opcao_selecionada + 1) % len(
                        OPCOES_MENU
                    )
                    tecla_pressionada = True
                elif key in ("1", "2", "3", "4", "5", "6"):
                    opcao_selecionada = int(key) - 1
                    tecla_pressionada = True
                    td.desenhar(gerar_layout_menu(opcao_selecionada))
                    time.sleep(0.15)
                    key = "enter"
                elif key == "s":
                    capital_escolhida = selecionar_capital_brasil(
                        fd, old_settings, td
                    )
                    if capital_escolhida:
                        exibir_clima_cidade(
                            fd, capital_escolhida, old_settings, td
                        )
                    opcao_anterior = None

                if key == "enter":
                    cidade_escolhida = OPCOES_MENU[opcao_selecionada]
                    exibir_clima_cidade(
                        fd, cidade_escolhida, old_settings, td
                    )
                    opcao_anterior = None

                elif key == "esc":
                    if confirmar_saida(fd, old_settings, td):
                        console.print("\nEncerrando o Clima CLI. Ate mais!")
                        break
                    else:
                        opcao_anterior = None

                # Atualização contínua rápida para manter as animações
                if (
                    tecla_pressionada
                    or (opcao_selecionada != opcao_anterior)
                    or (agora - ultimo_layout_update > 0.25)
                ):
                    td.desenhar(gerar_layout_menu(opcao_selecionada))
                    opcao_anterior = opcao_selecionada
                    ultimo_layout_update = agora

                time.sleep(0.05)
    finally:
        if sys.platform != "win32" and termios and old_settings:
            termios.tcsetattr(fd, termios.TCSANOW, old_settings)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(
            "\nEncerrando o Clima CLI de forma rapida. Ate mais!"
        )
