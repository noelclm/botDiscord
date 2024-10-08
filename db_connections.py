import json
import sqlite3
import os

class SQLiteDB:
    def __init__(self, db_name):
        # Ruta de la base de datos SQLite
        self.database = db_name

        # Verificar si el archivo de la base de datos existe
        self.file_exists = os.path.exists(self.database)

        # Conectar a la base de datos (se crea si no existe)
        self._connection = sqlite3.connect(self.database)
        self._cursor = self._connection.cursor()

        # Si la base de datos no existe, crear las tablas necesarias
        if not self.file_exists:
            self._create_tables()

    def _create_tables(self):
        try:
            # Leer el archivo SQL que contiene los comandos CREATE TABLE
            with open('tables_bot.sql', 'r') as file:
                create_table_sql = file.read()

            # Ejecutar los comandos SQL leídos desde el archivo
            self._cursor.executescript(create_table_sql)
            self._connection.commit()
        except Exception as e:
            raise Exception(f"Error SQLite to create tables: {str(e)}")

    def select(self, select_sql):
        try:
            self._cursor.execute(select_sql)
            data = self._cursor.fetchall()
            col_names = [desc[0] for desc in self._cursor.description]
            result = []
            for d in data:
                info = {col_names[idx]: d[idx] for idx in range(len(d))}
                result.append(info)
            return json.loads(json.dumps(result, default=str))
        except Exception as e:
            raise Exception(f"Error SQLite to select: {str(e)}")

    def insert(self, insert_sql):
        """
        Execute insert sql
        :param insert_sql: str Query
        :return: int ID
        """
        try:
            insert_sql = insert_sql.strip().replace('None', 'NULL')
            if insert_sql[-1] == ';':
                insert_sql = insert_sql[:-1]
            self._cursor.execute(insert_sql)
            self._connection.commit()
            return  self._cursor.lastrowid
        except Exception as e:
            raise Exception(f"Error SQLite to insert: {str(e)}")

    def update(self, update_sql):
        """
        Execute update sql
        :param update_sql: str Query
        :return: int Num of rows affected
        """
        try:
            update_sql = update_sql.replace('None', 'NULL')
            self._cursor.execute(update_sql)
            self._connection.commit()
            return self._cursor.rowcount
        except Exception as e:
            raise Exception(f"Error SQLite to update: {str(e)}")

    def delete(self, delete_sql):
        """
        Execute delete sql
        :param delete_sql: str Query
        :return: int Num of rows affected
        """
        try:
            self._cursor.execute(delete_sql)
            self._connection.commit()
            return self._cursor.rowcount
        except Exception as e:
            raise Exception(f"Error SQLite to delete: {str(e)}")


    def close(self):
        """
        Close the connection
        """
        if self._connection is not None:
            self._cursor.close()
            self._connection.close()
