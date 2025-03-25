import sqlite3
from config import DATABASE

class DB_Manager:
    def __init__(self, database):
        self.database = database
        self.create_tables()

    def create_tables(self):
        """Veritabanı tablolarını oluşturur."""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS cards")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                puan INTEGER DEFAULT 0
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                user_id INTEGER,
                kart_name TEXT,
                overall INTEGER,
                club TEXT,
                nationality TEXT,
                rarity TEXT,
                value TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
            """)

            conn.commit()

    def __execute(self, sql, data=tuple()):
        """Tek bir SQL komutu çalıştırır."""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()

    def __select(self, sql, data=tuple()):
        """Veri seçme sorguları için kullanılır."""
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute(sql, data)
            return cursor.fetchall()

    def kullanici_ekle(self, user_id, username):
        """Kullanıcıyı veritabanına ekler, eğer yoksa."""
        if not self.__select("SELECT user_id FROM users WHERE user_id = ?", (user_id,)):
            self.__execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))

    def kullanici_puan_guncelle(self, user_id, puan_ekle):
        """Kullanıcının puanını günceller."""
        mevcut_puan = self.__select("SELECT puan FROM users WHERE user_id = ?", (user_id,))
        if mevcut_puan:
            yeni_puan = mevcut_puan[0][0] + puan_ekle
            self.__execute("UPDATE users SET puan = ? WHERE user_id = ?", (yeni_puan, user_id))
        else:
            self.__execute("INSERT INTO users (user_id, puan) VALUES (?, ?)", (user_id, puan_ekle))

    def kart_ekle(self, user_id, kart_name, overall, club, nationality, rarity, value):
        """Kullanıcının koleksiyonuna yeni bir kart ekler."""
        self.__execute(
            "INSERT INTO cards (user_id, kart_name, overall, club, nationality, rarity, value) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, kart_name, overall, club, nationality, rarity, value)
        )

    def kullanici_kartlari(self, user_id):
        """Belirtilen kullanıcının kartlarını döndürür."""
        return self.__select("SELECT kart_name, overall, rarity FROM cards WHERE user_id = ?", (user_id,))

    def liderlik_siralamasi(self):
        """En yüksek puanlı 10 kullanıcıyı getirir."""
        return self.__select("SELECT user_id, puan FROM users ORDER BY puan DESC LIMIT 10")

    def rastgele_kart_cek(self):
        """Rastgele bir futbolcu kartı çeker."""
        sonuc = self.__select("SELECT Name, Overall, Club, Nationality, Value FROM data ORDER BY RANDOM() LIMIT 1")
        return sonuc[0] if sonuc else None
