from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus as urlquote


# host = "120.79.225.116"
host = "127.0.0.1"
port = 3306
username = "root"
# password = "123456"
password = "123456"
database = "analysis_sys_db"
charset = "utf8mb4"

db_engine = create_engine("mysql+pymysql://{}:{}@{}/{}?charset={}"
                          .format(username, urlquote("123456"), host, database, charset),
                          pool_size=15, pool_recycle=1800, pool_timeout=60)


def get_db_session():
    Session = sessionmaker(autoflush=False, bind=db_engine)
    return Session()
