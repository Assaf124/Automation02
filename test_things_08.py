from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine


def mac_to_asset(mac_and_asset_list):
     """
     correlates device MAC address to system asset_id
     """
     my_dict = dict()
     for pair in mac_and_asset_list:
          my_dict[pair[0]] = pair[1]
     return my_dict

server = SSHTunnelForwarder(
     ('172.16.10.1', 22),
     ssh_password="coldplay",
     ssh_username="root",
     remote_bind_address=('198.51.100.12', 3306)
     )

server.start()

# parameters
user = 'root'
password = 'coldplay'
host = 'localhost'
port = server.local_bind_port
db = 'apollo'

# connect to db and run query
uri = f'mysql+mysqldb://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4'
engine = create_engine(uri, echo=False, pool_pre_ping=True)
con = engine.connect()
result = con.execute("SELECT id, mac_address FROM device;").fetchall()
# print(result)

print(mac_to_asset(result))
# close connection
con.invalidate()
con.close()
server.stop()
