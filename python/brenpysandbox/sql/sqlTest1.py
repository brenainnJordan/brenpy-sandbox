'''
Created on 3 Jun 2018

@author: Bren
'''

import sqlite3


def basic_table_example():
    """ basic example 1
        create a db in memory, add a table and one entry, then fetch all results
    """

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cmd = """
    CREATE TABLE butt(
        id integer,
        name text
    )
    """

    cursor.execute(cmd)

    cursor.execute("INSERT INTO butt VALUES (0, 'poop')")

    conn.commit()

    cursor.execute("SELECT * FROM butt")
    print cursor.fetchall()

    conn.commit()
    conn.close()


class PythonicTableExample():
    """ simple pythonic example of creating a db in memory,
        adding a table, inserting items and fetching results
    """

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        self.create_table()
        self.insert_item(0, "poop")
        self.fetch_all()
        self.conn.close()

    def insert_item(self, id, name):
        with self.conn:  # context manager
            self.cursor.execute(
                """
                INSERT INTO butt VALUES (:id, :name)
                """,
                {"id": id, "name": name}
            )

    def create_table(self):
        cmd = """
        CREATE TABLE butt(
            id integer,
            name text
        )
        """
        self.cursor.execute(cmd)
        self.conn.commit()

    def fetch_all(self):
        self.cursor.execute("SELECT * FROM butt")
        print self.cursor.fetchall()


def create_table_with_foreign_key():
    """ foreign keys, for creating relationships between entries
    """

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE Things
    (
        id integer PRIMARY KEY
    )
    """)

    cursor.execute("pragma foreign_keys=ON")

    cursor.execute("INSERT INTO Things VALUES(3)")

    cursor.execute("""
    CREATE TABLE ThingBox
    (
        id integer,
        FOREIGN KEY(id) REFERENCES Things(id)
    )
    """)

    # cursor.execute("INSERT INTO ThingBox VALUES(2)") # this would fail as
    # id=2 doesn't exist
    cursor.execute("INSERT INTO ThingBox VALUES(3)")

    conn.commit()

    cursor.execute("SELECT * FROM Things")
    print cursor.fetchall()
    cursor.execute("SELECT * FROM ThingBox")
    print cursor.fetchall()

    conn.commit()
    conn.close()


class UnionExample(object):
    """ https://www.tutorialspoint.com/sqlite/sqlite_using_joins.htm
    """

    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

        self.create_people_table()
        self.create_locations_table()
        self.populate()
        self.fetch_all()
        self.cross_join()
        self.inner_join()
        self.left_outer_join()
        self.where()
        self.conn.close()

    def insert_person(self, id, name, age):
        with self.conn:  # context manager
            self.cursor.execute(
                """
                INSERT INTO people VALUES (:id, :name, :age)
                """,
                {"id": id, "name": name, "age": age}
            )

    def insert_location(self, id, location, person_id):
        with self.conn:  # context manager
            self.cursor.execute(
                """
                INSERT INTO locations VALUES (:id, :location, :person_id)
                """,
                {"id": id, "location": location, "person_id": person_id}
            )

    def create_people_table(self):
        cmd = """
        CREATE TABLE people(
            id integer PRIMARY KEY,
            name text,
            age integer
        )
        """
        self.cursor.execute(cmd)
        self.conn.commit()

    def create_locations_table(self):
        cmd = """
        CREATE TABLE locations(
            id integer PRIMARY KEY,
            location text,
            person_id integer
        )
        """
        self.cursor.execute(cmd)
        self.conn.commit()

    def populate(self):
        for i, (name, age) in enumerate([
            ("john", 32),
            ("jack", 41),
            ("jeff", 16),
            ("bob", 22),
            ("jill", 19),
        ]):
            self.insert_person(i, name, age)

        for i, (location, person_id) in enumerate([
            ("leeds", 1),
            ("london", 0),
            ("scarborough", 4),
        ]):
            self.insert_location(i, location, person_id)

    def fetch_all(self):
        self.cursor.execute("SELECT * FROM people")
        print self.cursor.fetchall()
        self.cursor.execute("SELECT * FROM locations")
        print self.cursor.fetchall()

    def cross_join(self):
        self.cursor.execute(
            "SELECT person_id, name, location FROM people CROSS JOIN locations")
        print self.cursor.fetchall()

    def inner_join(self):
        self.cursor.execute("""
        SELECT person_id, name, location FROM people INNER JOIN locations
        ON people.id = locations.person_id
        """)
        print self.cursor.fetchall()

    def left_outer_join(self):
        self.cursor.execute("""
        SELECT people.id, name, location FROM people LEFT OUTER JOIN locations
        ON people.id = locations.person_id
        """)
        print self.cursor.fetchall()

    def where(self):
        self.cursor.execute("""
        SELECT * FROM people
        WHERE id > 2 
        """)
        print self.cursor.fetchall()


if __name__ == "__main__":
    UnionExample()
    # test1()
    # Example2()
