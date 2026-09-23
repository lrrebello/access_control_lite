# Controle de Acesso Lite

Versão simplificada do Controle de Acesso, sem login, postos de trabalho, vigilantes, cadastros de autorizados, logo ou exportação para Excel.

## Recursos

- Dashboard direto na abertura da aplicação.
- Registro de entradas de veículos e pedestres.
- Acompanhantes opcionais.
- O formulário principal não exige tipo de veículo nem reboque; o tipo é mantido internamente a partir do último registro da matrícula ou usa "pesado" como padrão para novas matrículas.
- Autopreenchimento de nome, documento e empresa a partir do último registro da matrícula.
- Acompanhantes continuam sendo informados manualmente, pois podem mudar a cada entrada.
- Registro e remoção de saída.
- Edição dos registros.
- Um único botão para gerar relatório PDF, com filtro opcional por período.

## Execução

```bash
pip install -r requirements.txt
python run.py
```

A aplicação usa `lite.db` por padrão, separado do banco da aplicação principal. Para escolher outro banco, defina `DATABASE_URL` antes de iniciar.
