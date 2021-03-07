import vk_api
import random
import time
import sqlite3
import os
from googletrans import Translator
from kinopoisk.movie import Movie


def set_state(state, id):
    sql = f'''UPDATE Users SET state='{state}' WHERE id={id} '''
    cursor.execute(sql)
    conn.commit()


def set_property(name, value, id):
    sql = f'''UPDATE Users SET {name}='{value}' WHERE id={id} '''
    cursor.execute(sql)
    conn.commit()


def get_property(name, id):
    sql = f"SELECT {name} FROM Users WHERE id={from_id} "
    cursor.execute(sql)
    return cursor.fetchone()[0]



conn = sqlite3.connect("database.db")
cursor = conn.cursor()

token = "07ee268bf348515317ca0de566c591ec91d07cb188fbbe71c817a0395ccfa4ce0704666b1b892f242f0e6"

vk = vk_api.VkApi(token=token)
vk._auth_token()
uploader = vk_api.upload.VkUpload(vk)

value = {"count": 20, "offset": 0, "filter": "unanswered"}


kbrd = open("keyboards/empty.json", "r", encoding="UTF-8").read()

translator = Translator()

while True:
    messages = vk.method("messages.getConversations", value)

    if messages["count"] > 0:
        from_id = messages["items"][0]["last_message"]["from_id"]
        in_text = messages["items"][0]["last_message"]["text"]

        sql = f"SELECT * FROM Users WHERE id={from_id}"
        cursor.execute(sql)
        if len(cursor.fetchall()) == 0:
            sql = f'''
            INSERT INTO Users (id, state)
            VALUES ({from_id}, 'start')
            '''
            cursor.execute(sql)
            conn.commit()


        sql = f"SELECT state FROM Users WHERE id={from_id} "
        cursor.execute(sql)
        state = cursor.fetchone()[0]
        print(state)

        ############################################################

        if state == "start":
            out_text = "Привет!"
            set_state("menu", from_id)
            kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()

        elif state == "menu":
            if in_text == "Перевод":
                set_state("translation", from_id)
                out_text = "Введите фразу для перевода"
                kbrd = open("keyboards/empty.json", "r", encoding="UTF-8").read()

            elif in_text == "Поиск фильма":
                set_state("random_film", from_id)
                out_text = "Введите название фильма"
                kbrd = open("keyboards/empty.json", "r", encoding="UTF-8").read()

            elif in_text == "История одного фильма":
                set_state("text", from_id)
                # построчно
                # номера
                # убрать расширение
                files = os.listdir(path='./data/text')
                out_text = "Выберите файл:\n"
                for i in range(len(files)):
                    out_text += f"{i+1}) {files[i].split('.')[0]}\n"

                kbrd = open("keyboards/files.json", "r", encoding="UTF-8").read()

            else:
                out_text = "Неправильный пункт меню"
                set_state("menu", from_id)
                kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()

        elif state == "translation":
            out_text = translator.translate(in_text, dest='ru').text

            set_state("menu", from_id)
            kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()

        elif state == "random_film":
            movie_list = Movie.objects.search(in_text)
            if len(movie_list) > 0:
                movie = movie_list[0]
                out_text = movie.title + "\n" + str(movie.id)
            else:
                out_text = "Ничего не найдено"

            set_state("menu", from_id)
            kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()

        elif state == "text":
            try:
                n = int(in_text)
                f = open(f"data/text/{os.listdir(path='./data/text')[n-1]}", "r", encoding="UTF-8")
                out_text = f.read()
                f.close()
            except Exception:
                out_text = "Нет такого файла &#128532; "
            
            set_state("menu", from_id)
            kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()


        #elif state == "Состояние":
        #   out_text = "Ответное сообщение"
        #   set_state("Новое состояние", from_id)
        #   kbrd = open("keyboards/Новая клава.json", "r", encoding="UTF-8").read()

        ############################################################

        else:
            out_text = "Неизвестная команда"
            set_state("menu", from_id)
            kbrd = open("keyboards/menu.json", "r", encoding="UTF-8").read()




        vk.method("messages.send", {"peer_id": from_id, "message": out_text, "random_id": random.randint(1, 1000),
                                 "keyboard": kbrd})
    time.sleep(1)

