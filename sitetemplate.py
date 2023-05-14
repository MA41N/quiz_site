import sqlite3
from random import randint
from flask import Flask, session, redirect, url_for, request, render_template
from random import shuffle
import os
#from db_scripts import get_question_after
 
db_name = 'quiz.sqlite'
conn = None
curor = None
 
quiz = 0
last_question = 0
 
def open():
    global conn, cursor
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
 
def close():
    cursor.close()
    conn.close()
 
def do(query):
    cursor.execute(query)
    conn.commit()
 
def clear_db():
    ''' удаляет все таблицы '''
    open()
    query = '''DROP TABLE IF EXISTS quiz_content'''
    do(query)
    query = '''DROP TABLE IF EXISTS question'''
    do(query)
    query = '''DROP TABLE IF EXISTS quiz'''
    do(query)
    close()
 
def create():
    open()
    cursor.execute('''PRAGMA foreign_keys=on''')
 
    do('''CREATE TABLE IF NOT EXISTS quiz (
           id INTEGER PRIMARY KEY,
           name VARCHAR)''')
 
    do('''CREATE TABLE IF NOT EXISTS question (
               id INTEGER PRIMARY KEY,
               question VARCHAR,
               answer VARCHAR,
               wrong1 VARCHAR,
               wrong2 VARCHAR,
               wrong3 VARCHAR)''')
 
    do('''CREATE TABLE IF NOT EXISTS quiz_content (
               id INTEGER PRIMARY KEY,
               quiz_id INTEGER,
               question_id INTEGER,
               FOREIGN KEY (quiz_id) REFERENCES quiz (id),
               FOREIGN KEY (question_id) REFERENCES question (id) )''')
    close()
 
def add_questions():
    questions = [
        ('Сколько месяцев в году имеют 28 дней?', 'Все', 'Один', 'Ни одного', 'Два'),
        ('Каким станет зелёный утёс, если упадёт в Красное море?', 'Мокрым', 'Красным', 'Не изменится', 'Фиолетовым'),
        ('Какой рукой лучше размешивать чай?', 'Ложкой', 'Правой', 'Левой', 'Любой'),
        ('Что не имеет длины, глубины, ширины, высоты, а можно измерить?', 'Время', 'Глупость', 'Море', 'Воздух'),
        ('Когда сетью можно вытянуть воду?', 'Когда вода замерзла', 'Когда нет рыбы', 'Когда уплыла золотая рыбка',
         'Когда сеть порвалась'),
        ('Что больше слона и ничего не весит?', 'Тень слона', 'Воздушный шар', 'Парашют', 'Облако')
    ]
    open()
    cursor.executemany('''INSERT INTO question (question, answer, wrong1, wrong2, wrong3) VALUES (?,?,?,?,?)''',
                       questions)
    conn.commit()
    close()
 
def add_quiz():
    quizes = [
        ('Своя игра',),
        ('Кто хочет стать миллионером?',),
        ('Самый умный',)
    ]
    open()
    cursor.executemany('''INSERT INTO quiz (name) VALUES (?)''', quizes)
    conn.commit()
    close()
 
def add_links():
    open()
    cursor.execute('''PRAGMA foreign_keys=on''')
    query = "INSERT INTO quiz_content (quiz_id, question_id) VALUES (?,?)"
    answer = input("Добавить связь (y / n)?")
    while answer != 'n':
        quiz_id = int(input("id викторины: "))
        question_id = int(input("id вопроса: "))
        cursor.execute(query, [quiz_id, question_id])
        conn.commit()
        answer = input("Добавить связь (y / n)?")
    close()
 
def show(table):
    query = 'SELECT * FROM ' + table
    open()
    cursor.execute(query)
    print(cursor.fetchall())
    close()
 
def show_tables():
    show('question')
    show('quiz')
    show('quiz_content')
 
def get_question_after(question_id=0, quiz_id=1):
    ''' возвращает следующий вопрос после вопроса с переданным id
    для первого вопроса передаётся значение по умолчанию '''
    open()
    query = '''
    SELECT quiz_content.id, question.question, question.answer, question.wrong1, question.wrong2, question.wrong3
    FROM question, quiz_content
    WHERE quiz_content.question_id == question.id
    AND quiz_content.id > ? AND quiz_content.quiz_id == ?
    ORDER BY quiz_content.id '''
    cursor.execute(query, [question_id, quiz_id])
    result = cursor.fetchone()
    print(result)
    close()
    return result
 
def get_quises():
    open()
    query = '''SELECT * FROM quiz ORDER BY id'''
    cursor.execute(query)
    result = cursor.fetchall()
    close()
    return result
 
def check_answer(q_id, ans_text):
    query = '''
            SELECT question.answer 
            FROM quiz_content, question 
            WHERE quiz_content.id = ? 
            AND quiz_content.question_id = question.id
        '''
    open()
    cursor.execute(query, str(q_id))
    result = cursor.fetchone()
    close()
    # print(result)
    if result is None:
        return False # не нашли
    else:
        if result[0] == ans_text:
            # print(ans_text)
            return True # ответ совпал
        else:
            return False # нашли, но ответ не совпал
 
def save_answers():
    '''получает данные из формы, проверяет, верен ли ответ, записывает итоги в сессию'''
    answer = request.form.get('ans_text')
    quest_id = request.form.get('q_id')
    # этот вопрос уже задан:
    session['last_question'] = quest_id
    # увеличиваем счетчик вопросов:
    session['total'] += 1
    # проверить, совпадает ли ответ с верным для этого id
    if check_answer(quest_id, answer):
        session['answers'] += 1
 
def main():
    clear_db()
    create()
    add_questions()
    add_quiz()
    add_links()
    show_tables()
    #q()
 
 
main()
 
# Здесь будет код веб-приложения
def quiz_form():
    ''' функция получает список викторин из базы и формирует форму с выпадающим списком'''
    html_beg = '''<html><body><h2>Выберите викторину:</h2><form method="post" action="/"><select name="quiz">'''
    frm_submit = '''<p><input type="submit" value="Выбрать"> </p>'''
 
    html_end = '''</select>''' + frm_submit + '''</form></body></html>'''
    options = ''' '''
    q_list = get_quises()
    for id, name in q_list:
        option_line = ('''<option value="''' + str(id) + '''">''' + str(name) + '''</option> ''')
        options = options + option_line
    return html_beg + options + html_end
 
 
 
def test_form(question):
    answers_list = [question[2], question[3], question[4], question[5]]
    shuffle(answers_list)
 
    return render_template("test.html", question=question[1], quest_id=question[0], answers_list=answers_list)
 
 
def start_quiz(quiz_id):
    '''создаёт нужные значения в словаре session'''
    session['quiz'] = quiz_id
    session['last_question'] = 0
    session['answers'] = 0
    session['total'] = 0
 
def end_quiz():
    session.clear()
 
def index():
 
    '''global quiz, last_question
    max_quiz = 3
    quiz = randint(1,1)
    last_question = 0'''
    #list_quizes = get_quises()
 
    ''' Первая страница: если пришли запросом GET, то выбрать викторину, 
    если POST - то запомнить id викторины и отправлять на вопросы'''
    if request.method == 'GET':
        # викторина не выбрана, сбрасываем id викторины и показываем форму выбора
        start_quiz(-1)
        return quiz_form()
    else:
        # получили дополнительные данные в запросе! Используем их:
        quest_id = request.form.get('quiz') # выбранный номер викторины
        start_quiz(quest_id)
        return redirect(url_for('test'))
 
    #return '<br><h1><a href="/test">Тест</a><h1>'
 
def test():
    #global last_question
 
    '''result = get_question_after(last_question,quiz)
    print(result)
    '''
 
    if not ('quiz' in session) or int(session['quiz']) < 0:
        return redirect(url_for('index'))
    else:
        # если нам пришли данные, то их надо прочитать и обновить информацию:
        if request.method == 'POST':
            save_answers()
        result = get_question_after(session['last_question'], session['quiz'])
        if result is None or len(result) == 0:
            return redirect(url_for('results'))
        else:
            return test_form(result)
            '''session['last_question'] = result[0]
            print(last_question, quiz) return '<h1>' + str(session['quiz']) + '<br>' + str(result) + '</h1>'''
 
def results():
    session.clear()
    return "THE END!"
 
folder = os.getcwd() # запомнили текущую рабочую папку
 
app = Flask(__name__, template_folder=folder, static_folder=folder)
#main()
 
app.add_url_rule('/', 'index', index, methods=["POST", "GET"])
app.add_url_rule('/test', 'test', test, methods=["POST", "GET"])
app.add_url_rule('/results', 'results', results, methods=["POST", "GET"])
 
app.config['SECRET_KEY'] = '123'
 
if __name__ == "__main__":
    app.run()