import mysql.connector

DB = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="user_info",
    port=3306,
)

# 使用cursor()方法获取操作游标
cursor = DB.cursor()

# 查询数据
sql = """
SELECT * FROM users_test
"""
cursor.execute(sql)
records = cursor.fetchall() # 在执行 INSERT 之前，先 fetch 完 SELECT 的结果，不然会报错
print("查询结果:")
for record in records:
    print(record)

# 插入数据
sqlInsert = """
INSERT INTO users_test (username, is_active) VALUES ('python insert', 1)
"""
cursor.execute(sqlInsert)
DB.commit()  # 提交事务
print(f"\n插入成功，影响行数: {cursor.rowcount}")

# 更新数据
sqlUpdate = """
UPDATE users_test SET is_active = 0 WHERE username = 'python insert'
"""
cursor.execute(sqlUpdate)
DB.commit()  # 提交事务
print(f"\n更新成功，影响行数: {cursor.rowcount}")

# 删除数据
sqlDelete = """
DELETE FROM users_test WHERE username = 'python insert' limit 3
"""
cursor.execute(sqlDelete)
DB.commit()  # 提交事务
print(f"\n删除成功，影响行数: {cursor.rowcount}")

# 再次查询验证
cursor.execute(sql)
records = cursor.fetchall()
print("\n插入后查询结果:")
for record in records:
    print(record)

# 关闭游标和连接，要在数据库操作完成后关闭，否则会报错
cursor.close()

DB.close()
