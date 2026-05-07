# Clima CLI – Projeto prático do Capítulo 3: Git e GitHub

Este projeto foi desenvolvido durante a aula do **Capítulo 3: Git – O CTRL+Z que a IA não te dá** do livro *Engenharia de Software com Agentes Inteligentes*.

## 📚 Objetivo do capítulo

Demonstrar como usar **Git e GitHub** de forma segura e eficiente quando se trabalha com **agentes inteligentes**, transformando experimentos em **risco controlado** através de branches e commits descritivos.

## 🚀 Fluxo de desenvolvimento com agente

### 1. Inicialização do projeto
```bash
git init
git config --global init.defaultBranch main
git branch -m master main
```

### 2. Primeiro commit (estrutura básica)
```bash
git add .gitignore
git commit -m "chore: inicializa projeto com .gitignore"
```

### 3. Criação do repositório remoto
```bash
gh repo create clima-cli --public --source=. --remote=origin --push
```

### 4. Branch de desenvolvimento
```bash
git checkout -b feat/estrutura-inicial
```

### 5. Instrução ao agente
> *"Crie um script Python chamado `main.py` que aceite o nome de uma cidade como argumento de linha de comando e exiba a temperatura atual usando a API pública wttr.in. Use o módulo `requests`. Crie também um `requirements.txt` com as dependências."*

### 6. Teste e commit
```bash
git add main.py requirements.txt
git commit -m "feat: implementa consulta de clima via wttr.in"
```

### 7. Branch para experimentação
```bash
git checkout -b feat/clima-detalhado
```

### 8. Nova instrução ao agente
> *"Modifique o `main.py` para exibir também umidade, velocidade do vento e condição climática (ensolarado, nublado, etc.), ainda usando a API wttr.in. Mantenha o argumento de linha de comando."*

### 9. Merge seguro
```bash
git checkout feat/estrutura-inicial
git merge feat/clima-detalhado
git branch -d feat/clima-detalhado
```

### 10. Integração final
```bash
git checkout main
git merge feat/estrutura-inicial
git push
```

## 🛠️ Comandos Git essenciais

| Comando | Descrição |
|---------|-----------|
| `git status` | Estado atual do repositório |
| `git add .` | Prepara todos os arquivos |
| `git commit -m "mensagem"` | Registra snapshot com mensagem descritiva |
| `git checkout -b nome-branch` | Cria e entra em nova branch |
| `git merge branch` | Integra branch ao código atual |
| `git branch -d branch` | Deleta branch após merge |
| `git push` / `git pull` | Sincroniza com GitHub |
| `git log --oneline` | Histórico compacto |
| `git restore arquivo.py` | Descarta mudanças não commitadas |
| `git revert <hash>` | Desfaz commit já publicado |

## 🧠 Por que Git é obrigatório com IA

- **Agentes não têm memória**: operam sempre sobre o estado atual do código
- **Branches = experimentos seguros**: cada experimento fica isolado até aprovação
- **Histórico = pontos de restauração**: cada commit é um CTRL+Z recuperável
- **Mensagens descritivas**: explicam ao agente, a você e à equipe o que mudou

## 📁 Estrutura do projeto

```
clima-cli/
├── .gitignore          # Arquivos ignorados pelo Git
├── requirements.txt    # Dependências (requests)
├── main.py            # Script principal
└── .venv/             # Ambiente virtual (ignorado)
```

## 🧪 Como usar

```bash
# Clone o repositório
git clone https://github.com/ecodelearn/clima-cli.git
cd clima-cli

# Crie ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows

# Instale dependências
pip install -r requirements.txt

# Execute
python main.py Goiania
```

### Exemplo de saída

```
Clima em Goiania:
  Temperatura : 28°C
  Umidade     : 65%
  Vento       : 15 km/h
  Condição    : Parcialmente nublado
```

## ⚙️ Funcionalidades

- **Consulta em tempo real**: usa a API wttr.in para dados atualizados
- **Informações completas**: temperatura, umidade, velocidade do vento e condição climática
- **Tradução de condições**: 40+ códigos climáticos traduzidos para português
- **Tratamento de erros**: timeout de 10s e validação de resposta HTTP
- **Interface simples**: argumento de linha de comando direto

## 📖 Histórico de commits

```
1bc91fe feat: adiciona umidade, vento e condição climática
799de33 feat: implementa consulta de clima via wttr.in
f890fa6 chore: inicializa projeto com .gitignore
```

## 🔗 Links

- [Livro: Engenharia de Software com Agentes Inteligentes](https://physia.com.br/aieng)
- [API wttr.in](https://wttr.in)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub CLI](https://cli.github.com)

---

**Aula ministrada por:** Sandeco  
**Repositório:** https://github.com/ecodelearn/clima-cli  
**Data:** 06/05/2026