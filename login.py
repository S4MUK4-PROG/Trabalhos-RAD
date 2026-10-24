import os
import wx
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Samuka@028' 
}
DB_NAME = 'sistema_db'

def inicializar_banco():
    """Cria o banco de dados, a tabela de usuários e insere o usuário inicial se não existirem."""
    try:
        # Conexão inicial para criar o banco de dados
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.close()

        # Conexão direta com o banco criado
        conn = mysql.connector.connect(**DB_CONFIG, database=DB_NAME)
        cursor = conn.cursor()

        # Tabela de Usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario VARCHAR(50) NOT NULL UNIQUE,
                senha VARCHAR(100) NOT NULL
            )
        """)

        # Insere o usuário padrão se a tabela estiver vazia
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        if cursor.fetchone()[0] == 0:
            initial_user = os.environ.get("INITIAL_USER")
            initial_password = os.environ.get("INITIAL_PASSWORD")
            if not initial_user or not initial_password:
                raise RuntimeError("Configure INITIAL_USER and INITIAL_PASSWORD to create the first user")
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)", (initial_user, initial_password))
            conn.commit()

        cursor.close()
        conn.close()
    except Error as e:
        print(f"Erro ao inicializar o banco de dados MySQL: {e}")


def get_conexao():
    """Retorna uma conexão ativa com o banco de dados MySQL."""
    return mysql.connector.connect(**DB_CONFIG, database=DB_NAME)


class JanelaPrincipal(wx.Frame):
    """Janela exibida após o login com sucesso."""
    def __init__(self, usuario, senha):
        super().__init__(None, title="Painel Principal", size=(400, 350))
        self.SetBackgroundColour(wx.Colour(220, 220, 220))

        sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_login = wx.StaticText(self, label=f"Login: {usuario}")
        font = lbl_login.GetFont()
        font.SetPointSize(12)
        lbl_login.SetFont(font)

        lbl_senha = wx.StaticText(self, label=f"Senha: {senha}")
        lbl_senha.SetFont(font)

        sizer.Add(lbl_login, 0, wx.ALL, 20)
        sizer.Add(lbl_senha, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 20)

        self.SetSizer(sizer)
        self.Center()


class JanelaRedefinirSenha(wx.Frame):
    """Janela para redefinição de senha com consulta no MySQL."""
    def __init__(self, parent):
        super().__init__(parent, title="Redefinir Senha", size=(350, 400))
        self.SetBackgroundColour(wx.Colour(220, 220, 220))

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Título
        lbl_titulo = wx.StaticText(panel, label="Redefinir senha")
        font_titulo = lbl_titulo.GetFont()
        font_titulo.SetPointSize(14)
        font_titulo.SetWeight(wx.FONTWEIGHT_BOLD)
        lbl_titulo.SetFont(font_titulo)
        sizer.Add(lbl_titulo, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 20)

        # Grid para os inputs
        grid_sizer = wx.FlexGridSizer(3, 2, 10, 10)

        lbl_usuario = wx.StaticText(panel, label="Usuário:")
        self.txt_usuario = wx.TextCtrl(panel)

        lbl_senha = wx.StaticText(panel, label="Senha:")
        self.txt_senha = wx.TextCtrl(panel, style=wx.TE_PASSWORD)

        lbl_confirmar = wx.StaticText(panel, label="Confirme a\nsenha:")
        self.txt_confirmar = wx.TextCtrl(panel, style=wx.TE_PASSWORD)

        grid_sizer.Add(lbl_usuario, 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_usuario, 1, wx.EXPAND)

        grid_sizer.Add(lbl_senha, 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_senha, 1, wx.EXPAND)

        grid_sizer.Add(lbl_confirmar, 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_confirmar, 1, wx.EXPAND)

        grid_sizer.AddGrowableCol(1, 1)
        sizer.Add(grid_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 20)

        # Botão Salvar
        btn_salvar = wx.Button(panel, label="Salvar Nova Senha")
        btn_salvar.Bind(wx.EVT_BUTTON, self.on_salvar)
        sizer.Add(btn_salvar, 0, wx.ALIGN_CENTER | wx.TOP, 25)

        panel.SetSizer(sizer)
        self.Center()

    def on_salvar(self, event):
        usuario = self.txt_usuario.GetValue().strip()
        senha = self.txt_senha.GetValue()
        confirmar = self.txt_confirmar.GetValue()

        if not usuario or not senha:
            wx.MessageBox("Preencha todos os campos!", "Aviso", wx.OK | wx.ICON_WARNING)
            return

        if senha != confirmar:
            wx.MessageBox("As senhas não coincidem!", "Erro", wx.OK | wx.ICON_ERROR)
            return

        try:
            conn = get_conexao()
            cursor = conn.cursor()

            # Verifica se o usuário existe
            cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
            if not cursor.fetchone():
                wx.MessageBox("Usuário não encontrado!", "Erro", wx.OK | wx.ICON_ERROR)
                cursor.close()
                conn.close()
                return

            # Atualiza a senha no MySQL
            cursor.execute("UPDATE usuarios SET senha = %s WHERE usuario = %s", (senha, usuario))
            conn.commit()

            cursor.close()
            conn.close()

            wx.MessageBox("Senha redefinida com sucesso!", "Sucesso", wx.OK | wx.ICON_INFORMATION)
            self.Close()

        except Error as e:
            wx.MessageBox(f"Erro ao conectar com o banco de dados: {e}", "Erro DB", wx.OK | wx.ICON_ERROR)


class JanelaLogin(wx.Frame):
    """Janela principal de Login."""
    def __init__(self):
        super().__init__(None, title="Sistema de Cadastro", size=(350, 400))
        self.SetBackgroundColour(wx.Colour(220, 220, 220))

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Título
        lbl_titulo = wx.StaticText(panel, label="Sistema de Cadastro")
        font_titulo = lbl_titulo.GetFont()
        font_titulo.SetPointSize(16)
        font_titulo.SetWeight(wx.FONTWEIGHT_BOLD)
        lbl_titulo.SetFont(font_titulo)
        main_sizer.Add(lbl_titulo, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 25)

        # Formulário
        grid_sizer = wx.FlexGridSizer(2, 2, 12, 10)

        lbl_usuario = wx.StaticText(panel, label="Usuário:")
        self.txt_usuario = wx.TextCtrl(panel)

        lbl_senha = wx.StaticText(panel, label="Senha:")
        self.txt_senha = wx.TextCtrl(panel, style=wx.TE_PASSWORD)

        grid_sizer.Add(lbl_usuario, 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_usuario, 1, wx.EXPAND)

        grid_sizer.Add(lbl_senha, 0, wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_senha, 1, wx.EXPAND)

        grid_sizer.AddGrowableCol(1, 1)
        main_sizer.Add(grid_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 30)

        # Botões Entrar / Sair
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        btn_entrar = wx.Button(panel, label="Entrar", size=(90, 30))
        btn_sair = wx.Button(panel, label="Sair", size=(90, 30))

        btn_entrar.Bind(wx.EVT_BUTTON, self.on_entrar)
        btn_sair.Bind(wx.EVT_BUTTON, self.on_sair)

        btn_sizer.Add(btn_entrar, 0, wx.RIGHT, 10)
        btn_sizer.Add(btn_sair, 0, wx.LEFT, 10)

        main_sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.TOP, 25)

        # Link para Redefinir Senha
        lbl_redefinir = wx.StaticText(panel, label="Redefinir senha")
        lbl_redefinir.SetForegroundColour(wx.Colour(0, 0, 150))
        font_link = lbl_redefinir.GetFont()
        font_link.SetUnderlined(True)
        lbl_redefinir.SetFont(font_link)

        lbl_redefinir.Bind(wx.EVT_LEFT_DOWN, self.on_redefinir_senha)
        main_sizer.Add(lbl_redefinir, 0, wx.ALIGN_CENTER | wx.TOP, 15)

        panel.SetSizer(main_sizer)
        self.Center()

    def on_entrar(self, event):
        usuario = self.txt_usuario.GetValue().strip()
        senha = self.txt_senha.GetValue()

        try:
            conn = get_conexao()
            cursor = conn.cursor()

            # Consulta SQL para autenticação
            query = "SELECT * FROM usuarios WHERE usuario = %s AND senha = %s"
            cursor.execute(query, (usuario, senha))
            resultado = cursor.fetchone()

            cursor.close()
            conn.close()

            if resultado:
                # Login válido: abre a janela de sucesso com o usuário logado
                self.janela_principal = JanelaPrincipal(usuario, senha)
                self.janela_principal.Show()
                self.Close()
            else:
                wx.MessageBox("Usuário ou senha incorretos!", "Acesso Negado", wx.OK | wx.ICON_ERROR)

        except Error as e:
            wx.MessageBox(f"Erro ao conectar ao MySQL: {e}", "Erro DB", wx.OK | wx.ICON_ERROR)

    def on_sair(self, event):
        self.Close()

    def on_redefinir_senha(self, event):
        janela_redefinir = JanelaRedefinirSenha(self)
        janela_redefinir.Show()


if __name__ == "__main__":
    inicializar_banco()
    app = wx.App(False)
    frame = JanelaLogin()
    frame.Show()
    app.MainLoop()
