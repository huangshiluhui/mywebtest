import pymysql

# 让 pymysql 作为 MySQLdb 的替代
pymysql.install_as_MySQLdb()

# 伪装版本号以兼容 Django 6.0
pymysql.version_info = (2, 2, 1, 'final', 0)
