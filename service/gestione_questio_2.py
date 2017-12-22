from flask import g
from gestione_account_2 import *
import sqlite3


@app.route('/')
def hello():
    return jsonify({'Web':'Service'})


@app.route('/questionario/<session>/<title>')
def questionario(session,title):

    my_tok = Token()
    my_tok.nome = session

    if my_tok.esisteToken():

        if my_tok.ver_scad_tok():

            my_ut = Utente()
            my_ut.session = session

            if my_ut.ruolo_utente2() == 1 or my_ut.ruolo_utente2() == 2:

                q = Questionario(title)

                q.inserisciTitolo()

                return jsonify({'Risultato' : 'Inserito', 'id' : q.idx})

            else:
                return jsonify({'Risultato': 'Accesso negato.'})

        else:
            return jsonify({'Risultato':'Session scaduto'})

    else:
        return jsonify({'Risultato':'Session sbagliato'})



@app.before_request
def before_request():
    g.db = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')

@app.route('/domanda/<session>/<int:n_quest>/<sentence>')
def domanda(session,n_quest,sentence):

    my_tok = Token()
    my_tok.nome = session

    if my_tok.esisteToken():

        if my_tok.ver_scad_tok():

            my_ut = Utente()
            my_ut.session = session

            if my_ut.ruolo_utente2() == 1 or my_ut.ruolo_utente2() == 2:

                if first_time_dom(sentence) == 0:

                    g.db.execute("INSERT INTO domande (domanda) VALUES (?)", [sentence])
                    g.db.commit()
                    id_ = g.db.execute("SELECT id_domande FROM domande ORDER BY id_domande DESC LIMIT 1").fetchone()[0]

                else:
                    id_=first_time_dom(sentence)

                if prima_domanda(n_quest):

                    last = g.db.execute("SELECT id_mesh FROM mesh WHERE q_id=?",[n_quest]).fetchone()[0]
                    g.db.execute("UPDATE mesh SET d_id=? WHERE id_mesh=?",[id_,last])
                    g.db.commit()

                else:
                    g.db.execute("INSERT INTO mesh (q_id,d_id) VALUES (?,?)",[n_quest,id_])
                    g.db.commit()

                return jsonify({'Risultato' : 'Inserita', 'id' : id_, 'Questionario': n_quest})

            else:
                return jsonify({'Risultato':'Accesso negato.'})

        else:
            return jsonify({'Risultato':'Session scaduto'})

    else:
        return jsonify({'Risultato':'Session sbagliato'})


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/risposta/<session>/<int:n_quest>/<int:n_dom>/<sentence>')
def risposta(session,n_quest,n_dom,sentence):

    my_tok = Token()
    my_tok.nome = session

    if my_tok.esisteToken():

        if my_tok.ver_scad_tok():

            my_ut = Utente()
            my_ut.session = session

            if my_ut.ruolo_utente2() == 1 or my_ut.ruolo_utente2() == 2:

                if first_time_risp(sentence) == 0:

                    g.db.execute("INSERT INTO risposte (risposta) VALUES (?)", [sentence])
                    g.db.commit()
                    id_ = g.db.execute("SELECT id_risposte FROM risposte ORDER BY id_risposte DESC LIMIT 1").fetchone()[0]

                else:
                    id_ = first_time_risp(sentence)

                if prima_risposta(n_dom):
                    last = g.db.execute("SELECT id_mesh FROM mesh WHERE d_id=?",[n_dom]).fetchone()[0]
                    g.db.execute("UPDATE mesh SET r_id=? WHERE id_mesh=?",[id_,last])
                    g.db.commit()

                else:
                    g.db.execute("INSERT INTO mesh (q_id,d_id,r_id) VALUES (?,?,?)",[n_quest,n_dom,id_])
                    g.db.commit()

                return jsonify({'Risultato' : 'Inserita', 'Domanda':n_dom, 'Questionario':n_quest})

            else:
                return jsonify({'Risultato':'Accesso negato.'})

        else:
            return jsonify({'Risultato' : 'Session scaduto'})

    else:
        return jsonify({'Risultato' : 'Session sbagliato'})



@app.route('/richiesta/<session>/<survey_id>')
def visualizza(session, survey_id):

    my_tok = Token()
    my_tok.nome = session

    if my_tok.esisteToken():

        if my_tok.ver_scad_tok():

            con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
            cur = con.cursor()

            nome_ =cur.execute("SELECT questionario FROM questionari WHERE id_questionari=?", [survey_id]).fetchone()[0]

            q1 = Questionario(nome_)

            q1.idx = cur.execute("SELECT id_questionari FROM questionari WHERE questionario=?", [nome_]).fetchone()[0]

            con.close()

            q1.caricaDomande()

            result = q1.getJSON()

            return result

        else:
            return jsonify({'Risultato' : 'Session scaduto'})

    else:
        return jsonify({'Risultato' : 'Session sbagliato'})


@app.route('/compila/<session>/<survey_id>/<question_id>/<answer_id>')
def compila(session, survey_id, question_id, answer_id):

    my_ut = Utente()
    my_ut.session = session

    if my_ut.ruolo_utente2() == 3:

        my_tok = Token()
        my_tok.nome = session

        if my_tok.esisteToken():

            if my_tok.ver_scad_tok():

                con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
                cur = con.cursor()

                id_use = cur.execute("SELECT id_user FROM token WHERE n_token=?", [session]).fetchone()[0]

                value =cur.execute("SELECT questionario FROM questionari WHERE id_questionari=?", [survey_id]).fetchone()[0]

                my_surv = Questionario(value)

                my_surv.compila(survey_id, id_use, question_id, answer_id)

                return jsonify({'Risultato':'Compilato'})


            else:
                return jsonify({'Risultato' : 'Session scaduto'})
        else:
            return jsonify({'Risultato' : 'Session sbagliato'})

    else:
        return jsonify({'Risultato':'Accesso negato.'})


def prima_domanda(num):

    a=g.db.execute("SELECT d_id FROM mesh WHERE q_id=? ORDER BY d_id ASC LIMIT 1", [num]).fetchone()[0]

    if a:
        return False
    else:
        return True

def prima_risposta(nd):

    a = g.db.execute("SELECT r_id FROM mesh WHERE d_id=? ORDER BY r_id ASC LIMIT 1",[nd]).fetchone()[0]

    if a:
        return False
    else: return True

def first_time_risp(risp):

    con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
    cur = con.cursor()

    try:
        id_duplicate= cur.execute("SELECT id_risposte FROM risposte WHERE risposta=?",[risp]).fetchone()[0]

        con.close()

        return id_duplicate


    except TypeError:
        return 0

def first_time_dom(dom):

    con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
    cur = con.cursor()

    try:
        id_duplicate= cur.execute("SELECT id_domande FROM domande WHERE domanda=?",[dom]).fetchone()[0]

        con.close()

        return id_duplicate


    except TypeError:
        return 0

