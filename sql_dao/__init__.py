from sqlalchemy import create_engine

host = "120.79.225.116"
# host = "127.0.0.1"
port = 3306
username = "root"
password = "123456"
database = "analysis_sys_db"
charset = "utf8mb4"

db_engine = create_engine("mysql+pymysql://root:123456@120.79.225.116/analysis_sys_db"
                          "?charset=utf8mb4")
