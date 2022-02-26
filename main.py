#!/usr/bin/python3
# -* - coding: UTF-8 -* -

# --------------
# 易千转正项目：图书管理系统
# 后端实现
# By SkyWT
# --------------

import configparser

import math

import hashlib
from pickle import NEWOBJ_EX
from re import M
import re
from sys import get_coroutine_origin_tracking_depth

import jwt
import time
from datetime import datetime, timedelta

# import mysql.connector
# from mysqlx import ColumnMetaData

from flask import Flask, jsonify, request
from flask_cors import CORS

from sqlalchemy import Column, String, Integer, DateTime, Boolean, create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --------------
# 数据库配置和连接部分
# --------------

# 载入配置文件
conf = configparser.ConfigParser()
conf.read('config.ini')
hash_secret = conf['secrets']['hash_secret']
jwt_secret = conf['secrets']['jwt_secret']

# 数据库连接初始化
engine = create_engine('mysql+mysqlconnector://' + conf['database']['dbuser'] + ':' + conf['database']['dbpass'] + '@' + conf['database']['dbhost'] + '/' + conf['database']['dbname'])
DBSession = sessionmaker(bind = engine)
session = DBSession()

# ORM 对象初始化
Base = declarative_base()
class User(Base):
    __tablename__ = 'lib_users'
    id = Column(Integer, primary_key=True)
    group = Column(Integer)
    email = Column(String(255), unique=True)
    passwd = Column(String(255))
    stuid = Column(String(20))
    name = Column(String(10))
    gender = Column(Integer)
    age = Column(Integer)
    bio = Column(String(255))
class Book(Base):
    __tablename__ = 'lib_books'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    author = Column(String(20))
    isbn = Column(String(20), unique=True)
    press = Column(String(20))
    existingNum = Column(Integer)
    totalNum = Column(Integer)
class Record(Base):
    __tablename__ = 'lib_records'
    id = Column(Integer, primary_key=True)
    userId = Column(Integer)
    bookId = Column(Integer)
    borrowDate = Column(DateTime)
    returnDate = Column(DateTime)
    returned = Column(Boolean)

# --------------
# 基础函数部分
# --------------

# 获取用户密码哈希
# 参数：密码明文
# 返回：哈希值
def get_hash(str):
    obj = hashlib.sha256(hash_secret.encode('utf-8'))
    # print('STR = ',str)
    obj.update(str.encode('utf-8'))
    return obj.hexdigest()

# 检查用户密码
# 参数：userid、密码明文
# 返回：是否成功
def auth(now_uid, now_passwd):
    now_user = session.query(User).filter_by(id = now_uid).first()
    return (now_user.passwd == get_hash(now_passwd))

# 获取用户 token
# 参数：userid
# 返回：token 字符串
# 备注：使用 JWT 技术的优点是服务器无状态，缺点是没法废除颁布的 token，可能有安全风险。
#      似乎这里的验证机制还可以更优化。
def get_token(uid):
    payload = {
        'exp': datetime.now() + timedelta(minutes = 30),
        'uid': uid
    }
    return jwt.encode(payload, jwt_secret, algorithm='HS256')

# 解码 token 获取 userid
# 参数：token 字符串
# 返回：如果 token 超时，返回空字符串；否则返回 email 字符串
def decode_token(token):
    tmp = jwt.decode(token, jwt_secret, algorithms=['HS256'])
    # datetime 转 Unix 时间戳再转 int 进行比较，暂时想不到更优雅的方法
    if (int(tmp['exp']) < int(time.mktime(datetime.now().timetuple()))): return ''
    return tmp['uid']

# 续租 token（暂时用不到）
# 参数：原 token
# 返回：新的 token
# 备注：由于 JWT 服务端无状态，要么前端每次更改 token，要么就干脆设置一个大一点的 expires 时间，不续租了。
def maintain_token(token):
    tmp = jwt.decode(token, jwt_secret, algorithms=['HS256'])
    return get_token(tmp.uid)

# 验证 Email 合法性
# 参数：email
# 返回：是否合法
def check_email(email):
    return True

# 验证密码合法性
# 参数：密码明文
# 返回：密码是否合法
def check_pass(passwd):
    return True

# Wash 如果是空串就返回 None 将字段值设置为 NULL
# 特别用于数据库字段类型不是字符串（无法存储空串）的数据清洗
# 参数：需要处理的字符串
# 返回：处理结果
def wash(str):
    if (str == ''): return None
    return str

# 返回信息和代码的统一定义
def __400_Incorrect_login():
    return jsonify({'status': 401, 'data': {}, 'msg': 'Invalid email or password. '}), 200
def __400_Permission_denied():
    return jsonify({'status': 401, 'data': {}, 'msg': 'Permission denied. '}), 200
def __400_Invalid_token():
    return jsonify({'status': 401, 'data': {}, 'msg': 'Invalid token. '}), 200
def __400_Books_not_returned():
    return jsonify({'status': 401, 'data': {}, 'msg': 'Books not returned. '}), 200
def __400_User_disabled():
    return jsonify({'status': 401, 'data': {}, 'msg': 'The user is disabled. '}), 200
def __400_No_such_user():
    return jsonify({'status': 401, 'data': {}, 'msg': 'No such user. '}), 200

def __400_No_such_book():
    return jsonify({'status': 400, 'data': {}, 'msg': 'No such book. '}), 200

def __400_No_such_record():
    return jsonify({'status': 400, 'data': {}, 'msg': 'No such record. '}), 200

def __200_OK():
    return jsonify({'status': 200, 'data': {}, 'msg': 'OK'}), 200
def __200_Return_data(data):
    return jsonify({'status': 200, 'data': data, 'msg': 'OK'}), 200

# --------------
# 数据初始化部分
# --------------

# 创建数据表
Base.metadata.create_all(engine)

# 检查如果没有根用户则添加一个根用户
now_user = session.query(User).filter_by(email = conf['users']['root_email']).first()
if (not now_user):
    new_user = User(
        email = conf['users']['root_email'],
        passwd = get_hash(conf['users']['root_pass']),
        group = 0
    )
    session.add(new_user)
    session.commit()

# --------------
# API 实现部分
# 用户相关
# --------------

app = Flask(__name__, static_folder = 'public', static_url_path = '/')

# 允许跨域请求
# CORS(app, resources = r'/*')

# 根目录的友情提示（已测试）
@app.route('/api/')
def hello():
    return '<h1>Welcome! </h1> Please refer to the docs to start using APIs. '

# 添加/注册用户功能（已测试）
@app.route('/api/users', methods=['POST'])
def add_user():
    now_token = request.headers.get('token')
    new_group = request.json.get('userGroup')
    if (new_group and new_group != 1):
        try: now_uid = decode_token(now_token)
        except: return __400_Invalid_token()
        now_user = session.query(User).filter_by(id = now_uid).first()
        if (not now_user or now_user.group != 0): return __400_Permission_denied()
    else: new_group = 1

    new_email = request.json.get('userEmail')
    print('user_email = ', new_email)
    new_passwd = request.json.get('userPwd')
    if (not check_email(new_email) or not check_pass(new_passwd)):
        return __400_Incorrect_login()
    new_user = User(
        email = new_email,
        passwd = get_hash(new_passwd),
        stuid = request.json.get('userStuId'),
        name = request.json.get('userName'),
        gender = wash(request.json.get('userGender')),
        age = wash(request.json.get('userAge')),
        bio = request.json.get('userBio'),
        group = new_group
    )
    session.add(new_user)
    session.commit()
    return __200_OK()

# 删除用户（已测试）
@app.route('/api/users/<got_uid>', methods=['DELETE'])
def del_user(got_uid):
    now_token = request.headers.get('token')

    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (now_user.group != 0):
        if (now_user.id != got_uid): return __400_Permission_denied()

    # 检测是否归还了所有书籍
    not_returned = session.query(Book).filter_by(userId = now_uid, returned = False).all()
    if (not_returned): return __400_Books_not_returned()

    got_user = session.query(User).filter_by(id = got_uid).first()
    if (not got_user): return __400_No_such_user()
    session.delete(got_user)
    session.commit()
    return __200_OK()

# 用户登录（已测试）
@app.route('/api/token', methods=['POST'])
def login():
    now_email = request.json.get('userEmail')
    now_pass = request.json.get('userPwd')

    now_user = session.query(User).filter_by(email = now_email).first()
    if (not now_user): return __400_Incorrect_login()
    if (now_user.group == 2): return __400_User_disabled()
    if (not auth(now_user.id, now_pass)): return __400_Incorrect_login()
    return __200_Return_data({'token': get_token(now_user.id)})

# 获取当前用户（自己）的信息（已测试）
@app.route('/api/users/self', methods=['GET'])
def get_self_info():
    now_token = request.headers.get('token')

    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()

    return __200_Return_data({
        "userId": now_user.id,
        "userEmail": now_user.email,
        "userStuId": now_user.stuid,
        "userName": now_user.name,
        "userGender": now_user.gender,
        "userAge": now_user.age,
        "userBio": now_user.bio,
        "userGroup": now_user.group
    })

# 更改用户信息
@app.route('/api/users/<got_uid>/info', methods=['POST'])
def post_info(got_uid):
    now_token = request.headers.get('token')

    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()
    if (now_user.group != 0): return __400_Permission_denied()

    new_group = request.json.get('userGroup')
    new_stuid = request.json.get('userStuId')
    new_name = request.json.get('userName')
    new_gender = request.json.get('userGender')
    new_age = request.json.get('userAge')
    new_bio = request.json.get('userBio')

    got_user = session.query(User).filter_by(id = got_uid).first()
    if (new_group): got_user.group = new_group
    if (new_stuid): got_user.stuid = new_stuid
    if (new_name): got_user.name = new_name
    if (new_gender): got_user.gender = new_gender
    if (new_age): got_user.age = new_age
    if (new_bio): got_user.bio = new_bio
    session.add(got_user)
    session.commit()
    return __200_OK()

# 更改用户密码
@app.route('/api/users/<got_uid>/pass', methods=['POST'])
def post_pass(got_uid):
    now_token = request.headers.get('token')

    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()

    new_pass = request.json.get('userNewPwd')
    old_pass = request.json.get('userPwd')

    if (now_user.group != 0):
        if (now_user.id != got_uid): return __400_Permission_denied()
        if (get_hash(old_pass) != now_user.passwd): return __400_Incorrect_login()

    got_user = session.query(User).filter_by(id = got_uid).first()
    got_user.passwd = get_hash(new_pass)

# 查询用户
@app.route('/api/users', methods=['GET'])
def search_users():
    now_token = request.headers.get('token')

    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()
    if (now_user.group != 0): return __400_Permission_denied()

    if (not request.json.get('page')): page = 1
    else: page = int(request.json.get('page'))
    if (not request.json.get('page-size')): page_size = 10
    else: page_size = int(request.json.get('page-size'))

    # 多条件查询，如果遇字段为空则忽略条件
    got_users = session.query(User).filter(
        or_(User.name == request.json.get('name'), not request.json.get('name')),
        or_(User.gender == request.json.get('gender'), not request.json.get('gender')),
        or_(User.email == request.json.get('email'), not request.json.get('email')),
        or_(User.stuid == request.json.get('stuId'), not request.json.get('stuId')),
        or_(User.age == request.json.get('age'), not request.json.get('age')),
        or_(User.group == request.json.get('group'), not request.json.get('group')),
    ).all()

    ret_users = []
    total_num = 0
    for got_user in got_users:
        ret_user = {
            'userId': got_user.id,
            'userEmail': got_user.email,
            'userStuId': got_user.stuid,
            'userName': got_user.name,
            'userGender': got_user.gender,
            'userAge': got_user.age,
            'userBio': got_user.bio,
            'userGroup': got_user.group
        }
        total_num = total_num + 1
        if ((page-1) * page_size +1 <= total_num and total_num <= page * page_size): ret_users.append(ret_user)
    total_page = math.ceil(total_num / page_size)

    return __200_Return_data({
        'page': page,
        'page-size': page_size,
        'total-count': total_num,
        'total-page': total_page,
        'users': ret_users
    })

# --------------
# API 实现部分
# 书籍模块
# --------------

# 查询书籍
@app.route('/api/books', methods=['GET'])
def search_books():
    now_token = request.headers.get('token')

    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()

    if (not request.json.get('page')): page = 1
    else: page = int(request.json.get('page'))
    if (not request.json.get('page-size')): page_size = 10
    else: page_size = int(request.json.get('page-size'))

    got_books = session.query(Book).filter(
        or_(Book.name == request.json.get('name'), not request.json.get('name')),
        or_(Book.isbn == request.json.get('isbn'), not request.json.get('isbn')),
        or_(Book.author == request.json.get('author'), not request.json.get('author')),
    ).all()

    ret_books = []
    total_num = 0
    for got_book in got_books:
        ret_user = {
            'bookId': got_book.id,
            'bookName': got_book.name,
            'bookISBN': got_book.isbn,
            'bookPress': got_book.press,
            'bookExistingNumber': got_book.existingNum,
            'bookTotalNumber': got_book.totalNum
        }
        total_num = total_num + 1
        if ((page-1) * page_size +1 <= total_num and total_num <= page * page_size): ret_books.append(ret_user)
    total_page = math.ceil(total_num / page_size)

    return __200_Return_data({
        'page': page,
        'page-size': page_size,
        'total-count': total_num,
        'total-page': total_page,
        'books': ret_books
    })

# 添加书籍
@app.route('/api/books', methods=['POST'])
def add_book():
    now_token = request.headers.get('token')

    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()
    if (now_user.group != 0): return __400_Permission_denied()

    new_book = Book(
        name = request.json.get('bookName'),
        author = request.json.get('bookAuthor'),
        isbn = request.json.get('bookISBN'),
        press = request.json.get('bookPress'),
        existingNum = request.json.get('bookExistingNumber'),
        totalNum = request.json.get('bookTotalNumber')
    )
    session.add(new_book)
    session.commit()
    return __200_OK()

# 删除书籍
@app.route('/api/books/<got_bid>', methods=['DELETE'])
def del_book(got_bid):
    now_token = request.headers.get('token')

    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user or now_user.group != 0): return __400_Invalid_token()

    got_book = session.query(Book).filter_by(id = got_bid).first()
    if (not got_book): return __400_No_such_book()
    session.delete(got_book)
    session.commit()
    return __200_OK()

# 修改书籍信息
@app.route('/api/books/<got_bid>', methods=['PUT'])
def change_book_info(got_bid):
    new_name = request.json.get('bookName')
    new_author = request.json.get('bookAuthor')
    new_isbn = request.json.get('bookISBN')
    new_press = request.json.get('bookPress')
    new_existingNum = request.json.get('bookExistingNumber')
    new_totalNum = request.json.get('bookTotalNumber')

    now_token = request.headers.get('token')
    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()
    if (now_user.group != 0): return __400_Permission_denied()

    got_book = session.query(Book).filter_by(id = got_bid).first()
    if (not got_book): return __400_No_such_book()
    if (new_name): got_book.name = new_name
    if (new_author): got_book.author = new_author
    if (new_isbn): got_book.isbn = new_isbn
    if (new_press): got_book.press = new_press
    if (new_existingNum): got_book.existingNum = new_existingNum
    if (new_totalNum): got_book.totalNum = new_totalNum
    session.add(got_book)
    session.commit()
    return __200_OK()

# --------------
# API 实现部分
# 记录模块
# --------------

# 借阅图书
@app.route('/api/records', methods=['POST'])
def borrow_book():
    now_token = request.headers.get('token')
    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()
    # 普通用户只能以自己的名义借书
    if (now_user.group != 0 and now_user.id != request.json.get('userId')): return __400_Permission_denied()

    now_book = session.query(Book).filter_by(id = request.json.get('bookId')).first()
    if (not now_book): return __400_No_such_book()

    borrow_date = request.json.get('rcdBorrowDate')
    if (not borrow_date): borrow_date = datetime.now()

    new_record = Record(
        bookId = now_book.id,
        userId = now_user.id,
        borrowDate = borrow_date,
        returned = False
    )
    session.add(new_record)
    session.commit()
    return __200_OK()

# 归还图书
@app.route('/api/records/<got_rid>', methods=['PUT'])
def return_book(got_rid):
    now_token = request.headers.get('token')
    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()

    return_date = request.json.get('rcdReturnDate')
    if (not return_date): return_date = datetime.now()
    now_record = session.query(Record).filter_by(id = got_rid).first()
    if (not now_record): return __400_No_such_record()

    now_record.returned = True
    now_record.returnDate = return_date
    session.add(now_record)
    session.commit()
    return __200_OK()

# 删除记录
@app.route('/api/records/<got_rid>', methods=['DELETE'])
def del_record(got_rid):
    now_token = request.headers.get('token')
    try: now_uid = decode_token(now_token)
    except: return __400_Invalid_token()
    now_user = session.query(User).filter_by(id = now_uid).first()
    if (not now_user): return __400_Invalid_token()
    if (now_user.group != 0): return __400_Permission_denied()

    now_record = session.query(Record).filter_by(id = got_rid).first()
    if (not now_record): return __400_No_such_record()

    session.delete(now_record)
    session.commit()
    return __200_OK()

# 查询记录
@app.route('/api/records', methods=['GET'])
def search_records():
    now_token = request.headers.get('token')

    # try: now_uid = decode_token(now_token)
    # except: return __400_Invalid_token()
    # now_user = session.query(User).filter_by(id = now_uid).first()
    # if (not now_user): return __400_Invalid_token()

    # if (not request.json.get('page')): page = 1
    # else: page = int(request.json.get('page'))
    # if (not request.json.get('page-size')): page_size = 10
    # else: page_size = int(request.json.get('page-size'))

    # got_books = session.query(Book).filter(
    #     or_(Book.name == request.json.get('name'), not request.json.get('name')),
    #     or_(Book.isbn == request.json.get('isbn'), not request.json.get('isbn')),
    #     or_(Book.author == request.json.get('author'), not request.json.get('author')),
    # ).all()

    # ret_rcds = []
    # total_num = 0
    # for got_book in got_books:
    #     ret_user = {
    #         'bookId': got_book.id,
    #         'bookName': got_book.name,
    #         'bookISBN': got_book.isbn,
    #         'bookPress': got_book.press,
    #         'bookExistingNumber': got_book.existingNum,
    #         'bookTotalNumber': got_book.totalNum
    #     }
    #     total_num = total_num + 1
    #     if ((page-1) * page_size +1 <= total_num and total_num <= page * page_size): ret_books.append(ret_user)
    # total_page = math.ceil(total_num / page_size)

    # return __200_Return_data({
    #     'page': page,
    #     'page-size': page_size,
    #     'total-count': total_num,
    #     'total-page': total_page,
    #     'books': ret_books
    # })


if __name__ == '__main__':
    app.run(
        host = conf['server']['listen'],
        port = conf['server']['port'],
        debug = conf['server']['debug']
    )