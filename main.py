import psycopg2
class Database:

    def drop_db(self, conn):
        # Удаление таблиц
        with conn.cursor() as cur:
            cur.execute('''
            DROP TABLE IF EXISTS phone;
            DROP TABLE IF EXISTS client;
                    ''')
        conn.commit()

    def create_db(self, conn):
        #Создание таблиц
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE  IF NOT EXISTS client(
            id SERIAL PRIMARY KEY, 
            name VARCHAR(255), 
            last_name VARCHAR(255),
            email varchar(100),
            phones varchar(100));""")



            cur.execute("""
            CREATE TABLE  IF NOT EXISTS phone(
            id SERIAL PRIMARY KEY,
            phone VARCHAR(255), 
            client_id INTEGER REFERENCES client(id));""")

        conn.commit()
        print('Таблица создана')



    def add_client(self, conn, first_name, last_name, email, phones=None):
        # Добавление клиента
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO client(name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id;
            """,(first_name, last_name,  email))

            client_id = cur.fetchone()[0]
            if phones:
                for phone in phones:
                    cur.execute("""
                    INSERT INTO phone(phone, client_id)
                    VALUES (%s, %s);
                    """,(phone, client_id))
            conn.commit()
            print(f'Клиент {last_name} {first_name} добавлен ')
            return client_id

    def add_phone(self, conn, client_id, phone):
        # Добавление доп., номера телефона
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO phone(phone, client_id)
            VALUES (%s, %s);
            """,(phone, client_id))
        conn.commit()
        print(f'Клиенту {client_id} добавлен номер телефона')



    def change_client(self, conn, client_id, last_name=None, first_name=None, email=None, phones=None):
        # Обновление данных
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE client
            SET name = %s,last_name = %s, email = %s
            WHERE id = %s;
            """,( first_name, last_name, email, client_id))
            if phones:
                for phone in phones:
                    cur.execute("""
                    UPDATE phone
                    SET phone = %s
                    WHERE client_id = %s;
                    """,(phone, client_id))
        conn.commit()
        print(f'Данные о клиенте {client_id} изменены')

    def deleted_phone(self, conn, client_id, phone):
        #Удаление номера телефона
        with conn.cursor() as cur:
            if phone:
                cur.execute('''
                DELETE FROM phone
                WHERE client_id = %s AND phone = %s;
                ''', (client_id, phone))
                conn.commit()

        print(f'Телефон у клиента {client_id} удален')


    def delete_client(self, conn, client_id):
        #Удаление клиента
        with conn.cursor() as cur:
            if client_id:
                cur.execute("""
                DELETE FROM phone
                WHERE client_id = %s;
                """, (client_id,))

                cur.execute("""
                DELETE FROM client
                WHERE id = %s;
                """,(client_id,))


        conn.commit()
        print(f'Клиент{client_id} удален из списка')

    def find_client(self, conn, first_name=None, last_name=None, email=None, phone=None):
        #Поиск
        with conn.cursor() as cur:
            if first_name:
                cur.execute("""
                SELECT * FROM client
                where name = %s;
                """, (first_name,))
                return cur.fetchall()
            if last_name:
                cur.execute("""
                SELECT * FROM client
                where last_name = %s;
                """, (last_name,))
                return cur.fetchall()
            if email:
                cur.execute("""
                SELECT * FROM client
                where email = %s;
                """, (email,))
                return cur.fetchall()
            if phone:
                cur.execute("""
                SELECT * FROM phone
                where phone = %s;
                """, (phone,))
                return cur.fetchall()
        conn.rollback()
        conn.commit()








if __name__ == '__main__':

    with psycopg2.connect(database="clients", user='postgres', password='postgres') as conn:

        base = Database()

        base.drop_db(conn)
        base.create_db(conn)

        client_1 = base.add_client(conn, 'Ivan', 'Ivanov', 'ivan@mail.ru','89288553555')
        client_2 = base.add_client(conn, 'Petr', 'Petrov', 'petr@mail,ru')
        client_3 = base.add_client(conn, 'Semen', 'Semenov', 'semen@mail.ru',['89288553555','85556321144'])

        base.add_phone(conn, client_1, '89277553310')
        base.add_phone(conn, client_2, '89288543310')

        base.change_client(conn, client_1,'Anton')

        base.deleted_phone(conn, client_2, '89288543310')
        base.delete_client(conn, client_1)

        print(base.find_client(conn, "Petr"))
        print(base.find_client(conn, email="semen@mail.ru"))
        print(base.find_client(conn, phone='89288553555'))
    conn.rollback()
    conn.close()



