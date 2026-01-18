[![CI](https://github.com/rodrigols89/rag-project/actions/workflows/lint.yml/badge.svg)](https://github.com/rodrigols89/rag-project/actions/workflows/lint.yml)
[![CI](https://github.com/rodrigols89/rag-project/actions/workflows/test.yml/badge.svg)](https://github.com/rodrigols89/rag-project/actions/workflows/test.yml)
[![CI](https://github.com/rodrigols89/rag-project/actions/workflows/docker.yml/badge.svg)](https://github.com/rodrigols89/rag-project/actions/workflows/docker.yml)
[![codecov](https://codecov.io/github/rodrigols89/rag-project/graph/badge.svg?token=8OX6I7IKQB)](https://codecov.io/github/rodrigols89/rag-project)

# RAG Project

 - [**Introdução e Objetivos do Projeto**](#intro-to-the-project)
 - [**git workflow**](#git-workflow)
<!---
[WHITESPACE RULES]
- Different topic = "100" Whitespace character.
- Same topic = "50" Whitespace character.
- Subtopic = "10" Whitespace character.
--->




































































































<!--- ( Introdução e Objetivos do Projeto ) --->

---

<div id="intro-to-the-project"></div>

## Introdução e Objetivos do Projeto

O **RAG Project** foi desenvolvido para solucionar um problema recorrente na *Secretaria de Educação*, onde trabalho (Remígio-PB):

> A **"ausência de um mecanismo de consulta"** em um grande número de pastas, arquivos e formatos.

Para enfrentar esse desafio, o projeto adota uma arquitetura baseada em *Retrieval-Augmented Generation (RAG)*, integrando técnicas de *Processamento de Linguagem Natural (NLP)*, *modelos de linguagem (LLMs)* e *mecanismos de busca vetorial*. O sistema permite transformar dados institucionais estáticos em um repositório consultável e responsivo.

### 🎯 Objetivos Técnicos

 - Centralizar documentos institucionais de forma estruturada.
 - Indexar arquivos através de embeddings semânticos.
 - Realizar consultas híbridas (vetorial + keyword).
 - Fornecer respostas geradas por LLMs baseadas exclusivamente nos dados indexados.
 - Garantir rastreabilidade e auditoria das fontes utilizadas nas respostas.

### 🏗️ Arquitetura do Sistema

A solução é dividida em *quatro camadas* principais:

 - **1. Ingestão de Dados:**
   - Extração de conteúdo de PDFs, DOCXs, planilhas e documentos administrativos.
   - Normalização de texto e limpeza semântica.
   - Pipeline automatizado de pré-processamento (fragmentação, tokenização, chunking).
 - **2. Indexação e Armazenamento:**
   - Geração de embeddings com modelo compatível com LLM escolhido.
   - Armazenamento em banco vetorial.
 - **3. Recuperação da Informação (Retrieval):**
   - Recuperação baseada em similaridade vetorial.
   - Suporte a filtros estruturados (metadata filtering).
   - Opcional: rerankers para melhorar precisão do top-k.
 - **4. Geração da Resposta (LLM Layer):**
   - Pipeline RAG com prompt engineering focado em:
     - grounding em documentos institucionais;
     - citar fontes;
     - evitar alucinações;
     - manter conformidade administrativa.
   - Respostas são geradas usando LLMs locais ou hospedados (OpenAI, Azure, vLLM, etc.).




































































































<!--- ( git workflow ) --->

---

<div id="git-workflow"></div>

## git workflow

Esse projeto segue o seguinte workflow (fluxo de trabalho):

```mermaid
flowchart TD

    DEVELOP["🛠️ <b>develop</b>
    <hr/>
    **Branch de desenvolvimento**<br/>
    • Executa: lint, testes, coverage
    • Build Docker + validações
    • Pode conter código instável"]

    MAIN["🚀 <b>main</b>
    <hr/>
    • Branch estável
    • Apenas código validado
    • Pode acionar deploy"]


    DEVELOP -->|"🔄 Pull Request / Merge"| MAIN
```

### `develop — Desenvolvimento Ativo`

> **A branch develop é utilizada para o trabalho diário.**

 - Rodam os testes e o lint.
 - CI/CD são executados a cada push ou pull request.
 - Ela pode conter código instável, protótipos ou modificações ainda em validação.

### `main — Estável / Produção`

> **A branch main contém sempre o estado atual estável e validado do projeto.**

Boas práticas:

 - Não permite push direto (apenas via Pull Request vindo da ci);
 - Pode acionar workflows de build final e deploy;
 - Deve permanecer íntegra e confiável.

### `🎯 Vantagens desse fluxo`

 - **Segurança:**
   - Nada chega na `main` sem passar por todos os testes.
 - **Qualidade:**
   - Bugs são detectados antes de afetar a branch estável.
 - **Manutenabilidade:**
   - Branches com papéis bem definidos facilitam colaboração e revisão de código.
 - **Escalabilidade:**
   - Estrutura compatível com projetos profissionais e pipelines complexos.

---

**Rodrigo** **L**eite da **S**ilva - **rodirgols89**
