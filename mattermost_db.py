#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# mattermoat의 PostgresDB의 mattermost database 제어
# 현재 셋팅된 postgres db는 로컬에서만 실행가능하므로,
# 이파일을 192.168.10.133에 접속하여 실행시켜야함.
# 실행방법
#	$ python mattermost_db.py           # 전체 유저 조회
#	$ python mattermost_db.py hulk      # 하나의 유저 조회
# 	$ python mattermost_db.py hulk TD   # 부서 업데이트
"""

import sys
import psycopg2

def selectUser(id):
	"""
	user table 조회
	"""
	sql = """select * from users"""
	if id:
		sql += """ where username = %s"""

	try:
		conn = psycopg2.connect(user="mmuser",
					password="Fourth4th!",
					host="127.0.0.1",
					port="5432",
					database="mattermost"
		)
		cur = conn.cursor()
		if not id:
			# 전체 유저정보 조회
			cur.execute(sql)
			records = cur.fetchall()
		else:
			# 하나의 유저정보 조회
			cur.execute(sql,(id,))
			records = cur.fetchone()
		print("Print Mattermost Users values")
		print(records)
		#for row in records:
			#print(row)
	except (Exception, psycopg2.Error) as e:
		print ("Error while fetching data from PostgreSQL", e)
	finally:
		# db 연결 종료
		if(conn):
			cur.close()
			conn.close()
			print("PostgreSQL connection is closed")


def updateUserDept(id, dept):
	"""
	user table의 position 및 nickname 변경.
	부서정보를 넣기 위해 사용.
	"""
	sql = """update users set position = %s, nickname = %s where username = %s"""
	try:
		conn = psycopg2.connect(user="mmuser",
					password="Fourth4th!",
					host="127.0.0.1",
					port="5432",
					database="mattermost"
		)
		cur = conn.cursor()
		# Update postion, nickname
		cur.execute(sql, (dept, dept, id))
		conn.commit()
		count = cur.rowcount
		print(count, "Record Updated successfully ")
		print("Table After updating record ")
	except (Exception, psycopg2.Error) as e:
		print("Error in update operation", e)
	finally:
		# db 연결 종료
		if (conn):
			cur.close()
			conn.close()
			print("PostgreSQL connection is closed")


def main():
	id = ""
	dept = ""
	argNum = len(sys.argv)
	print argNum
	if argNum > 1:
		id = sys.argv[1]
	if argNum > 2:
		dept = sys.argv[2]
	print(id, dept)

	if argNum < 3:
		selectUser(id)
	elif argNum == 3:
		updateUserDept(id, dept)


if __name__ == '__main__':
	main()