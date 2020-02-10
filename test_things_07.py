import sqlalchemy
from sqlalchemy.orm import sessionmaker


engine = sqlalchemy.create_engine('sqlite:///test_database.db', echo=True)

meta = sqlalchemy.MetaData()

students = sqlalchemy.Table(
                            'students', meta,
                            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                            sqlalchemy.Column('name', sqlalchemy.String),
                            sqlalchemy.Column('surname', sqlalchemy.String)
                            )

grades = sqlalchemy.Table(
                            'grades', meta,
                            sqlalchemy.Column('id', sqlalchemy.Integer,primary_key=True),
                            sqlalchemy.Column('grade',sqlalchemy.Integer)
                        )

meta.create_all(engine)
conn = engine.connect()

list_of_names = ['Erik', 'Ronna', 'Jack', 'Sharon', 'Dana']
list_of_surnames = ['Cohen', 'Chandler', 'Pollen', 'Allan', 'Sims']

for id in range(100001, 100006):
    index = id-100001
    name = list_of_names[index]
    surname = list_of_surnames[index]
    student = students.insert().values(id=id, name=name, surname=surname)
    conn.execute(student)

update = students.update().where(students.c.id == 100003).values(name='Mike')
# update = update(students).where(students.c.id == 1000003).values(name='Mike')
conn.execute(update)

query1 = sqlalchemy.text('SELECT * FROM students WHERE name LIKE "%na%"')
result = conn.execute(query1)

for student in result:
    print(f'- {student}')

s = students.select().where(students.c.id>100002)
result = conn.execute(s)

for student in result:
    print(f'- {student}')

