# Sistema de login

Aplicativo desktop em Python com wxPython e MySQL.

## Requisitos

- Python 3
- Servidor MySQL

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Configure as variáveis de ambiente no PowerShell antes de iniciar:

```powershell
$env:DB_HOST = "localhost"
$env:DB_USER = "seu_usuario_mysql"
$env:DB_PASSWORD = "sua_senha_mysql"
$env:INITIAL_USER = "seu_usuario_inicial"
$env:INITIAL_PASSWORD = "uma_senha_forte"
python login.py
```

`INITIAL_USER` e `INITIAL_PASSWORD` são necessários somente quando a tabela de
usuários ainda está vazia. O usuário MySQL precisa ter permissão para criar o
banco definido em `login.py` e as tabelas do aplicativo.
