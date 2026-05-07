import sys
import time
import requests
import datetime
from rich.live import Live
from rich.table import Table
from rich.console import Console

console = Console()

CONDICOES = {
    "113": "Ensolarado", "116": "Parcialmente nublado", "119": "Nublado",
    "122": "Encoberto", "143": "Névoa", "176": "Chuva leve ocasional",
    "179": "Neve leve ocasional", "182": "Garoa com neve", "185": "Garoa gelada",
    "200": "Trovoada ocasional", "227": "Nevasca leve", "230": "Nevasca",
    "248": "Nevoeiro", "260": "Nevoeiro gelado", "263": "Garoa leve ocasional",
    "266": "Garoa leve", "281": "Garoa gelada", "284": "Garoa gelada intensa",
    "293": "Chuva leve ocasional", "296": "Chuva leve", "299": "Chuva moderada ocasional",
    "302": "Chuva moderada", "305": "Chuva intensa ocasional", "308": "Chuva intensa",
    "311": "Chuva gelada leve", "314": "Chuva gelada moderada", "317": "Mistura leve",
    "320": "Mistura moderada", "323": "Neve leve ocasional", "326": "Neve leve",
    "329": "Neve moderada ocasional", "332": "Neve moderada", "335": "Neve intensa ocasional",
    "338": "Neve intensa", "350": "Granizo", "353": "Chuva leve ocasional",
    "356": "Chuva moderada/intensa", "359": "Chuva torrencial", "362": "Mistura leve ocasional",
    "365": "Mistura moderada/intensa", "368": "Neve leve ocasional", "371": "Neve moderada/intensa",
    "374": "Granizo leve ocasional", "377": "Granizo moderado/intenso",
    "386": "Chuva leve com trovoada", "389": "Chuva moderada/intensa com trovoada",
    "392": "Neve leve com trovoada", "395": "Neve moderada/intensa com trovoada",
}

def get_utilidade_publica(cidade: str, atual: dict) -> str:
    cidade_lower = cidade.lower()
    
    if "sao paulo" in cidade_lower or "são paulo" in cidade_lower:
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
        return f"  Útil (SP)   : Rodízio ({rodizio})"
        
    elif "londres" in cidade_lower or "london" in cidade_lower:
        try:
            resp = requests.get("https://api.tfl.gov.uk/line/mode/tube/status", timeout=5)
            if resp.status_code == 200:
                linhas = resp.json()
                atrasos = [l["name"] for l in linhas if l["lineStatuses"][0]["statusSeverity"] != 10]
                if atrasos:
                    return f"  Útil (LON)  : Tube (Atrasos: {', '.join(atrasos[:2])})"
                else:
                    return "  Útil (LON)  : Tube (Good Service)"
        except Exception:
            pass
        return "  Útil (LON)  : Tube (Status indisponível)"
            
    elif "rio de janeiro" in cidade_lower:
        return "  Útil (RJ)   : Cond. Mar (Ressaca, ondas 2.5m)"
        
    elif cidade_lower in ["goiania", "goiânia", "brasilia", "brasília", "cuiaba", "cuiabá", "campo grande"]:
        umidade = int(atual.get("humidity", 100))
        if umidade < 30:
            return "  ⚠️ Alerta   : Umidade Crítica (Perigo à saúde)"
        elif umidade < 50:
            return "  ⚠️ Alerta   : Umidade Baixa (Beba água)"
        else:
            return "  Útil (C-O)  : Umidade em níveis aceitáveis"
            
    else:
        sensacao = atual.get("FeelsLikeC", "N/A")
        uv = atual.get("uvIndex", "N/A")
        return f"  Útil        : Sensação {sensacao}°C | Índice UV {uv}"

def obter_dados_clima(cidade: str) -> dict:
    url = f"https://wttr.in/{cidade}?format=j1"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    atual = data["current_condition"][0]

    temp = atual["temp_C"]
    umidade = atual["humidity"]
    vento = atual["windspeedKmph"]
    codigo = atual["weatherCode"]
    condicao = CONDICOES.get(codigo, f"Código {codigo}")
    
    # Reaproveitando a função existente, mas removendo os espaços extras
    utilidade = get_utilidade_publica(cidade, atual).strip()

    return {
        "temp": temp,
        "umidade": umidade,
        "vento": vento,
        "condicao": condicao,
        "utilidade": utilidade
    }

def obter_animacao_clima(segundos_atuais: int) -> str:
    frames = ["☀️  ", "🌞 ", "☀️  ", "🌤️  "]
    return frames[segundos_atuais % len(frames)]

def gerar_painel(cidade: str, clima_data: dict) -> Table:
    agora = datetime.datetime.now()
    hora_formatada = agora.strftime("%H:%M:%S")
    
    tabela = Table(title=f"Dashboard: {cidade.upper()}", title_style="bold cyan")
    tabela.add_column("Relógio", justify="center", style="cyan", vertical="middle")
    tabela.add_column("Status em Tempo Real", justify="left")

    animacao = obter_animacao_clima(agora.second)
    
    status = (
        f"{animacao} [bold yellow]{clima_data['condicao']}[/bold yellow] | [bold]{clima_data['temp']}°C[/bold]\n"
        f"💧 Umidade: {clima_data['umidade']}%\n"
        f"💨 Vento: {clima_data['vento']} km/h\n"
        f"📍 [bold green]{clima_data['utilidade']}[/bold green]"
    )
    
    relogio_gigante = f"[b]{hora_formatada}[/b]" 

    tabela.add_row(relogio_gigante, status)
    return tabela

def main():
    if len(sys.argv) < 2:
        console.print("[bold red]Uso: python main.py <cidade>[/bold red]")
        sys.exit(1)
        
    cidade = sys.argv[1]
    
    with console.status(f"[bold green]Buscando dados meteorológicos iniciais para {cidade}...", spinner="dots"):
        try:
            clima_data = obter_dados_clima(cidade)
        except Exception as e:
            console.print(f"[bold red]Erro ao buscar dados: {e}[/bold red]")
            sys.exit(1)
            
    ultima_atualizacao = time.time()
    
    with Live(gerar_painel(cidade, clima_data), refresh_per_second=2, console=console) as live:
        while True:
            try:
                agora = time.time()
                # Atualiza os dados meteorológicos a cada 5 minutos para evitar bloqueio da API
                if agora - ultima_atualizacao > 300:
                    try:
                        clima_data = obter_dados_clima(cidade)
                        ultima_atualizacao = agora
                    except:
                        pass # ignora erro temporário e continua mostrando cache
                        
                live.update(gerar_painel(cidade, clima_data))
                time.sleep(0.5)
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()
