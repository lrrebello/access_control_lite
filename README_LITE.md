# Controle de Acesso Lite

Versão simplificada do Controle de Acesso, sem login, postos de trabalho, vigilantes, cadastros de autorizados, logo ou exportação para Excel.

## Recursos

- Dashboard direto na abertura da aplicação.
- Registro de entradas de veículos e pedestres.
- O formulário principal não exige tipo de veículo nem reboque; o tipo é mantido internamente a partir do último registro da matrícula ou usa "pesado" como padrão para novas matrículas.
- Cadastro de Produto, Destino e movimentação, com opções Carregar e Descarregar.
- Autopreenchimento de Produto, Destino, movimentação e nome do condutor a partir do último registro da matrícula.
- O cadastro de acompanhantes foi removido da operação atual.
- Bancos Lite existentes recebem automaticamente as novas colunas sem perder os registros anteriores; o campo antigo Empresa é usado como Produto na migração.
- Registro e remoção de saída.
- Edição dos registros.
- Um único botão para gerar relatório PDF, com filtro opcional por período.

## Execução

```bash
pip install -r requirements.txt
python run.py
```

A aplicação usa `lite.db` por padrão, separado do banco da aplicação principal. Para escolher outro banco, defina `DATABASE_URL` antes de iniciar.
