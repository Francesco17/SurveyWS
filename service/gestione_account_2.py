from webapp import app
from flask import jsonify
from questionario import Questionario
from token2 import Token
from utente import Utente
import sqlite3


@app.route('/subscribe/<username>/<password>/<age>/<number>/<id_role>')
def registra(username, password,age,number,id_role):

    my_utente = Utente()
    my_utente.nome = username
    my_utente.password = password
    my_utente.eta = age
    my_utente.n_telefono = number
    my_utente.ruolo = id_role

    return my_utente.registraUtente()


@app.route('/login/<username>/<passw>')
def accedi(username, passw):

    my_user = Utente()
    my_user.nome = username
    my_user.password = passw

    con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
    cur = con.cursor()

    my_user.id = cur.execute("SELECT id_user FROM user WHERE nome_utente = ?",[my_user.nome]).fetchone()[0]

    con.close()

    if my_user.loginUtente() == False:
        return jsonify({'Risultato' : 'Credenziali errate'})

    my_tok = Token()
    my_tok.assegnaToken(username)

    return jsonify({'Risultato' : {'Nome': my_user.nome, 'Session' : my_tok.nome}})


@app.route('/info/<token>')
def info(token):

    my_tok = Token()
    my_tok.nome = token

    if my_tok.esisteToken():

        if my_tok.ver_scad_tok():

            j = ricerca_quest_presenti()

            return j

        else: return jsonify({'Risultato' : 'Session scaduto'})

    else: return jsonify({'Risultato' : 'Session sbagliato'})

@app.route('/delete/<session>/<name>')
def elimina(session,name):

    my_tok = Token()
    my_tok.nome = session

    if my_tok.esisteToken():

        if my_tok.ver_scad_tok():

            my_user = Utente()
            my_user.session = session

            if my_ut.ruolo_utente2() == 1:

                my_user.eliminaUtente()

                return jsonify({'Risultato' : 'Utente eliminato'})

            else: return jsonify({'Risultato' : 'Accesso negato.'})

        else: return jsonify({'Risultato' : 'Session scaduto'})

    else: return jsonify({'Risultato' : 'Session sbagliato'})


def ricerca_quest_presenti():

    con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
    cur = con.cursor()

    resultSet = cur.execute("SELECT * FROM questionari").fetchall()

    data_list=list()

    for x in range(0,len(resultSet)):

        my_quest = Questionario(resultSet[x][1])

        my_quest.idx = resultSet[x][0]

        qdata = {'questionario' : my_quest.nome, 'id': my_quest.idx}

        data_list.append(qdata)

    data = {'questionari': data_list}

    j=jsonify(data)

    return j

def corrispondenza(tk):

    valore = False

    con = sqlite3.connect('/Users/Francesco/sqlite3/dBQuestionari.db')
    cur = con.cursor()

    id_user = cur.execute("SELECT id_user FROM token WHERE n_token=?",[tk]).fetchone()[0]

    state = cur.execute("SELECT id_token FROM user WHERE id_user=?",[id_user]).fetchone()[0]

    con.close()

    if state!=0:
        valore= True

    return valore
