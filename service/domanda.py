import sqlite3

from risposta import Risposta

class Domanda:
    def __init__(self):
        self.idx =0
        self.nome =''
        self.n_risposte =0
        self.risposte = list()


    def caricaRisposte(self,list_idrisp):

        con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
        cur = con.cursor()

        self.n_risposte = len(list_idrisp)

        for ide in list_idrisp:

            my_risp = Risposta()

            my_risp.idx = ide

            my_risp.nome = cur.execute("SELECT risposta FROM risposte WHERE id_risposte=?",[ide]).fetchone()[0]

            self.risposte.append(my_risp)

            del my_risp

        con.close()

