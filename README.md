---
type: Note
_organized: true
---
# 🌤️ Clima CLI

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge\&logo=python\&logoColor=white)![Git](https://img.shields.io/badge/Git-Enabled-F05032?style=for-the-badge\&logo=git\&logoColor=white)![Rich](https://img.shields.io/badge/CLI-Rich-green?style=for-the-badge)

Uma aplicação de linha de comando (CLI) desenvolvida em Python para exibição de dados meteorológicos e informações de utilidade pública em tempo real, utilizando uma interface visual rica e interativa no terminal.

Este projeto foi originalmente concebido como projeto prático durante a aula do **Capítulo 3: Git – O CTRL+Z que a IA não te dá** do livro *Engenharia de Software com Agentes Inteligentes*.

***

## 🚀 Funcionalidades

- **Consulta em Tempo Real:** Obtém dados meteorológicos ao vivo consumindo a API [wttr.in](https://wttr.in).
- **Interface Rica e Dinâmica:** Dashboard elegante no terminal com relógio atualizado em tempo real, desenvolvido usando a biblioteca `rich`.
- **Tradução Automática:** Mais de 40 códigos climáticos traduzidos nativamente para o português.
- **Utilidade Pública Contextual:** Mostra alertas personalizados baseados na cidade escolhida (ex: Rodízio em São Paulo, Status do *Tube* em Londres, Alertas de umidade no Centro-Oeste).
- **Resiliência e Tratamento de Erros:** Atualizações em segundo plano com suporte contínuo a falhas momentâneas de conexão (cache).

## 📋 Pré-requisitos

Certifique-se de ter instalado em sua máquina:

- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

## 🛠️ Instalação e Configuração

Siga os passos abaixo para preparar o ambiente local e rodar a aplicação:

1. **Clone o repositório:**

```bash
git clone https://github.com/ecodelearn/clima-cli.git
cd clima-cli
```

1. **Crie o ambiente virtual:**

```bash
python -m venv .venv
```

1. **Ative o ambiente virtual:**
   - **Windows:**

```powershell
.\.venv\Scripts\activate
```

- **Linux / macOS:**

```bash
source .venv/bin/activate
```

1. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

## 💻 Como usar

Após a instalação das bibliotecas e ativação do ambiente, execute a aplicação passando o nome da cidade desejada como argumento:

```bash
python main.py "Nome da Cidade"
```

**Exemplo:**

```bash
python main.py "Rio de Janeiro"
```

O dashboard continuará aberto no seu terminal, exibindo um relógio digital animado e os dados meteorológicos atualizados.

Para encerrar a aplicação, pressione `CTRL+C`.

***

## 🤝 Créditos e Agradecimentos

Este projeto não seria possível sem a colaboração e os ensinamentos essenciais:

- **Desenvolvedor / Criador Principal:** [Daniel Dias ](https://github.com/ecodelearn/clima-cli)*[(Implementação, refatoração estrutural da aplicação e design da interface CLI)](https://github.com/ecodelearn/clima-cli)**.*
- **Professor e Idealizador:** [Prof. Sandeco](https://github.com/sandeco) *(Idealizador original do projeto na aula "Git – O CTRL+Z que a IA não te dá" e autor do livro **[Engenharia de Software com Agentes Inteligentes](https://physia.com.br/aieng)**).*

***

> *Desenvolvido com dedicação para a comunidade! Se gostou, considere deixar uma ⭐ no repositório original.*
