from flask import jsonify
from domanda import Domanda
import sqlite3

class Questionario:

    def __init__(self,name):
        self.idx =0
        self.nome =name
        self.n_domande =0
        self.domande = list()


    def caricaDomande (self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        a = cur.execute("SELECT DISTINCT(d_id) FROM mesh WHERE q_id=? ORDER BY d_id",[self.idx]).fetchall()

        a_ = [int(x[0]) for x in a]

        self.n_domande = len(a_)

        for i in a_:

            my_dom = Domanda()
            my_dom.idx = i
            my_dom.nome = cur.execute("SELECT domanda FROM domande WHERE id_domande=?",[i]).fetchone()[0]

            self.domande.append(my_dom)

            b = cur.execute("SELECT r_id FROM mesh WHERE d_id=?",[i]).fetchall()

            b_ = [int(x[0]) for x in b]

            my_dom.caricaRisposte(b_)

            del my_dom

        con.close()


    def getJSON (self):

        qdata_list = []

        for i in range(0,self.n_domande):

            adata = []

            for j in range(0,self.domande[i].n_risposte):

                adata.append({self.domande[i].risposte[j].idx : self.domande[i].risposte[j].nome})

            qdata_diz = {self.domande[i].idx : self.domande[i].nome, 'risposte' : adata}

            qdata_list.append(qdata_diz)


        data = { 'questionario' : self.nome, 'questions' : qdata_list}

        j=jsonify(data)

        return j


    def inserisciTitolo(self):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        cur.execute("INSERT INTO questionari (questionario) VALUES (?)", [self.nome])
        con.commit()

        self.idx = cur.execute("SELECT id_questionari FROM questionari ORDER BY id_questionari DESC LIMIT 1").fetchone()[0]


        cur.execute("INSERT INTO mesh (q_id) VALUES (?)",[self.idx])
        con.commit()

    def inserisciDomanda(self, sentence):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        my_dom = Domanda()
        my_dom.nome = sentence

        cur.execute("INSERT INTO domande (domanda) VALUES (?)", [my_dom.nome])
        con.commit()

        my_dom.idx = cur.execute("SELECT id_domande FROM domande ORDER BY id_domande DESC LIMIT 1").fetchone()[0]

        if prima_domanda(self.idx):
            last = cur.execute("SELECT id_mesh FROM mesh WHERE q_id=?",[self.idx]).fetchone()[0]
            cur.execute("UPDATE mesh SET d_id=? WHERE id_mesh=?",[my_dom.idx,last])
            con.commit()

        else:
            cur.execute("INSERT INTO mesh (q_id,d_id) VALUES (?,?)",[self.idx,my_dom.idx])
            con.commit()

        con.close()


    def compila(self,id_surv,user_id,dom_id,risp_id):

        self.idx = id_surv

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        cur.execute("SELECT id_mesh FROM mesh WHERE q_id=? AND d_id =? AND r_id=?", [self.idx,dom_id,risp_id])
        id_m = cur.fetchone()[0]

        cur.execute("INSERT INTO compilati (id_mesh,id_user) VALUES (?,?)",[id_m,user_id])
        con.commit()

        con.close()

