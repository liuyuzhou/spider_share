from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# 数据库连接
def db_conn():
    conn_info = "mysql+pymysql://root:root@localhost/share?charset=utf8"
    engine = create_engine(conn_info, echo=False)

    db_session = sessionmaker(bind=engine)
    session = db_session()
    return session


# 数据库查询
def query_mysql(sql_str):
    session = db_conn()
    return session.execute(sql_str)


# 数据库更新
def update_mysql(update_sql):
    session = db_conn()
    session.execute(update_sql)
    session.commit()
    session.close()


if __name__ == "__main__":
    sql = 'select * from song'
    result = query_mysql(sql)
    for item in result:
        print(item)
