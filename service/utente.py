from passlib.hash import pbkdf2_sha256
from flask import jsonify
from token2 import Token
import sqlite3

class Utente:

    def __init__(self):
        self.nome = ''
        self.password = ''
        self.eta = 0
        self.n_telefono=0
        self.id=0
        self.id_t=0
        self.session=0
        self.ruolo= ''

    def registraUtente(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        rows = cur.execute("SELECT nome_utente FROM user WHERE nome_utente=?", [self.nome]).fetchone()

        if rows==None:

            hash = pbkdf2_sha256.encrypt(self.password, rounds=10000, salt_size=16)

            cur.execute("INSERT INTO user (nome_utente,password,eta,n_telefono,id_token,id_ruolo) VALUES (?,?,?,?,0,?)",
                         [self.nome, hash,
                          self.eta, self.n_telefono,self.ruolo])
            con.commit()

            con.close()

            return jsonify({'Risultato': 'Registrato'})

        else:
            return jsonify({'Risultato': 'Nome utente gia\' presente'})



    def loginUtente(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        rows = cur.execute("SELECT nome_utente,password FROM user WHERE nome_utente=?", [self.nome]).fetchone()


        self.id_t = int(cur.execute("SELECT id_token FROM user WHERE nome_utente=?",[self.nome]).fetchone()[0])

        con.close()

        if self.id_t != 0:

            my_tok = Token()
            my_tok.id = self.id_t
            my_tok.elimina_tok()

        if rows:

            if pbkdf2_sha256.verify(self.password, str(rows[1])):

                return  True

        else: return False


    def eliminaUtente(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        state = cur.execute("SELECT id_token FROM user WHERE nome_utente=?",[self.nome]).fetchone()[0]

        if state!=0:

            self.id_t = cur.execute("SELECT id_token FROM user WHERE nome.utente=?",[self.nome]).fetchone()[0]

            cur.execute("DELETE FROM token WHERE id_token=?",[self.id_t])
            con.commit()

        if self.ruoloUtente() == 3:
            cur.execute("DELETE FROM compilati WHERE id_user=?", [self.id])
            con.commit()

        cur.execute("DELETE FROM user WHERE nome_utente=?", [self.nome])
        con.commit()


    def ruoloUtente(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        self.ruolo = cur.execute("SELECT id_ruolo FROM user WHERE nome_utente=?",[self.nome]).fetchone()[0]

        con.close()

        return self.ruolo

    def ruolo_utente2(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        try:

            self.id_t = cur.execute("SELECT id_token FROM token WHERE n_token=?",[self.session]).fetchone()[0]

            self.ruolo = cur.execute("SELECT id_ruolo FROM user WHERE id_token=?",[self.id_t]).fetchone()[0]

            con.close()

            return int(self.ruolo)

        except TypeError:
            return 0

