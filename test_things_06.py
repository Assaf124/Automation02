import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData
engine = sqlalchemy.create_engine('sqlite:///assafaloni.db', echo=True)

meta = sqlalchemy.MetaData()

students = sqlalchemy.Table(
                            'students', meta,
                            Column('id', Integer, primary_key=True),
                            Column('name', String),
                            Column('surname', String)
                            )

meta.create_all(engine)
conn = engine.connect()

student = students.insert().values(id=1000001, name='Assaf', surname='Aloni')
result = conn.execute(student)

student = students.insert().values(id=1000002, name='Vicky', surname='Vanicheva')
result = conn.execute(student)