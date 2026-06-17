import sqlite3

class DatabaseProxy:
    def __init__(self, db_name: str = "highscores.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        """Inicializa o banco SQLite3 e cria a tabela se não existir"""
        # O Proxy abre a conexão apenas para criar a estrutura e já fecha
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def save_score(self, name: str, score: int):
        """Garante que a conexão abra e feche apenas na hora de salvar"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO scores (player_name, score) VALUES (?, ?)", (name, score))
            conn.commit()
            conn.close()
            print(f"📋 Pontuação de {name} ({score} pts) salva com sucesso via Proxy!")
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")

    def get_top_scores(self, limit: int = 5):
        """Busca os maiores recordes do banco de dados"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT player_name, score FROM scores ORDER BY score DESC LIMIT ?", (limit,))
        top_scores = cursor.fetchall()
        conn.close()
        return top_scores