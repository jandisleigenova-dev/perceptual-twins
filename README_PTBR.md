# Perceptual Twins Replication Kit v1.0 — Guia em português

Este pacote foi preparado para permitir que um pesquisador independente reproduza a microimplementação sintética descrita no artigo **Testing Task-Relative Epistemic Autonomy in Artificial Agents: The Perceptual Twins Benchmark**, versão 2.1.1.

## Objetivo atual

A versão 1.0 **não pretende validar o benchmark completo**. Ela permite reproduzir exatamente o estágio experimental já documentado no artigo:

- seed determinística `20260805`;
- 600 âncoras pareadas;
- referência Monte Carlo independente com 20.000 âncoras;
- 1.000 reamostragens bootstrap;
- três contrastes causais em dois endpoints;
- diagnóstico de equivalência E/C_E.

O resultado esperado é a recuperação dos seis estimandos causais dentro dos intervalos de 95% e diferença de equivalência igual a zero.

## Para executar no Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r reference_implementation\requirements.txt
python reference_implementation\perceptual_twins_synthetic_poc.py --output-dir outputs
python scripts\verify_reproduction.py
```

## Limite interpretativo

Um resultado positivo nesta microimplementação **não demonstra autonomia epistêmica real**. Ele apenas confirma que o caminho de código, o pareamento e os estimadores recuperam os efeitos sintéticos deliberadamente codificados.

O valor científico da próxima etapa será submeter o desenho a outras arquiteturas, geradores e, futuramente, robótica física.

## Licenciamento

- **Código e scripts:** Apache License 2.0.
- **Documentação e resultados de referência:** CC BY 4.0.
- **Artigo científico assinado:** Copyright © 2026 Jandislei Antonio Genova — Todos os direitos reservados.

## Situação do pedido no INPI

A implementação de referência v2.1.1 teve **pedido de registro de programa de computador protocolado** no INPI em 12/08/2026, processo `512026006478-3`, petição `870260080966`. Esta informação não deve ser redigida como registro já concedido.
