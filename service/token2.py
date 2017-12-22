import string, random, datetime
import sqlite3


class Token():

    def __init__(self):
        self.nome =''
        self.id = 0
        self.scadenza = datetime.datetime.now() + datetime.timedelta(minutes=5)
        self.idu = 0

    def assegnaToken(self,username):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        self.nome = token_generator()

        self.idu = utente_id(username)

        cur.execute("INSERT INTO token (n_token, data_scad, id_user) VALUES (?,?,?)", [self.nome,self.scadenza,self.idu])
        con.commit()

        self.id = cur.execute("SELECT id_token FROM token ORDER BY id_token DESC LIMIT 1").fetchone()[0]

        #cur.execute("INSERT INTO scadenze (id_token,data_scad,id_user) VALUES (?,?,?)", [self.id,self.scadenza,self.idu])
        #con.commit()

        cur.execute("UPDATE user SET id_token=? WHERE nome_utente=?", [self.id, username])
        con.commit()

        #cur.execute("UPDATE user SET stato_token=1 WHERE nome_utente=?", [username])
        #con.commit()

        con.close()


    def ver_scad_tok(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        self.id = cur.execute("SELECT id_token FROM token WHERE n_token=?",[self.nome]).fetchone()[0]

        self.idu = cur.execute("SELECT id_user FROM user WHERE id_token=?",[self.id]).fetchone()[0]

        dt_scad_ = cur.execute("SELECT data_scad FROM token WHERE id_user=?",[self.idu]).fetchone()[0]

        con.close()

        self.scadenza=datetime.datetime.strptime(dt_scad_, "%Y-%m-%d %H:%M:%S.%f")

        now = datetime.datetime.now()

        if self.scadenza<now:

            elimina_tok_scad(self.nome)
            return False

        else: return True

    def esisteToken(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        rows = cur.execute("SELECT n_token FROM token WHERE n_token=?", [self.nome]).fetchone()

        con.close()

        if rows:
            return True

        else: return False

    def ruoloToken(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        id_u = cur.execute("SELECT id_user FROM token WHERE n_token=?",[self.nome]).fetchone()[0]

        id_r = cur.execute("SELECT id_ruolo FROM user WHERE id_user=?",[id_u]).fetchone()[0]

        con.close()

        return id_r

    def elimina_tok(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        cur.execute("DELETE FROM token WHERE id_token=?", [self.id])
        con.commit()

        con.close()


def token_generator(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def utente_id(name):
    con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
    cur = con.cursor()
    cur.execute("SELECT id_user FROM user WHERE nome_utente=?",[name])
    ide = cur.fetchone()[0]
    con.close()

    return ide

def elimina_tok_scad(token):

    con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
    cur=con.cursor()

    id_us = cur.execute("SELECT id_user FROM token WHERE n_token=?",[token]).fetchone()[0]

    id_tok = cur.execute("SELECT id_token FROM token WHERE n_token=?",[token]).fetchone()[0]

    #cur.execute("DELETE FROM scadenze WHERE id_token=?",[id_tok])
    #con.commit()

    cur.execute("DELETE FROM token WHERE id_token=?",[id_tok])
    con.commit()

    cur.execute("UPDATE user SET id_token=0 WHERE id_user=?", [id_us])
    con.commit()

    #cur.execute("UPDATE user SET stato_token=0 WHERE id_user=?", [id_us])
    #con.commit()

    con.close()

    pass


