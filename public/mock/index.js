// // import Mock from 'mockjs';

// Mock.setup({
//     timeout: '0-500'
// })

// // 新用户注册，管理员添加用户
// Mock.mock(/\/api\/users/, 'post', {
//     "status": 200,
//     "data": {
//         "userId": '@integer(100, 9999)',
//         "userEmail": "@email",
//         "userStuId": /^\d{12}$/,
//         "userName": "@cword(3, 5)",
//         "userGender": '@integer(0,2)',
//         "userAge": '@integer(0, 100)',
//         "userBio": "'@cparagraph(0, 5)'",
//         "userGroup": 0
//     },
//     "msg": "@cword(4, 10)"
// })

// // 用户归还某一本书
// Mock.mock(/\/api\/users\/.*/, 'put', {
//     "status": 200,
//     "msg": "修改成功"
// })

// // 登录
// Mock.mock(/\/api\/token/, 'post', {
//     "status": 200,
//     "data": {
//         "token": '@guid'
//     },
//     "msg": "登录成功"
// })

// // 用户自主注销，管理员删除用户
// Mock.mock(/\/api\/users\/.*/, 'delete', {
//     "status": 200,
//     "msg": "登录成功"
// })

// // 获取当前登录的用户的信息
// Mock.mock(/\/api\/users\/self.*/, 'get', {
//     "status": 200,
//     "data": {
//         "userId": '@integer(100, 9999)',
//         "userEmail": "@email",
//         "userStuId": /^\d{12}$/,
//         "userName": "@cword(3, 5)",
//         "userGender": '@integer(0,2)',
//         "userAge": '@integer(0, 100)',
//         "userBio": "'@cparagraph(0, 5)'",
//         "userGroup": 0
//     },
//     "msg": "获取成功"
// })

// // 获取当前登录的用户的信息
// Mock.mock(/\/api\/users.*/, 'get', {
//     "status": 200,
//     "data": {
//         "page": 1,
//         "page-size": 10,
//         "total-count": 125, // 匹配的查询结果数量
//         "total-page": 13, // 一共有多少页
//         "users|10": [
//             {
//                 "userId": '@integer(100, 9999)',
//                 "userEmail": "@email",
//                 "userStuId": /^\d{12}$/,
//                 "userName": "@cword(3, 5)",
//                 "userGender": '@integer(0,2)',
//                 "userAge": '@integer(0, 100)',
//                 "userBio": "'@cparagraph(0, 5)'",
//                 "userGroup": '@integer(0,2)'
//             }
//         ]
//     },
//     "msg": "获取成功"
// })

// // 新增书籍
// Mock.mock(/\/api\/books/, 'post', {
//     "status": 200,
//     "data": {
//         "bookId": '@natural(60, 100)',
//         "bookName": '@ctitle(3, 15)',
//         "bookAuthor": '@cword(3, 5)',
//         "bookISBN": /\d{13}/,
//         "bookPress": '@ctitle(3, 10)' + '出版社',
//         "bookExistingNumber": '@integer(0, 5)', // 现存总数量
//         "bookTotalNumber": '@integer(10, 16)' // 总数量
//     },
//     "msg": "新增成功"
// })

// // 查询书籍
// Mock.mock(/\/api\/books.*/, 'get', {
//     "status": 200,
//     "data": {
//         "page": '@increment',
//         "page-size": 10,
//         "total-count": 124, // 匹配的查询结果数量
//         "total-page": 13, // 一共有多少页
//         "books|10": [
//             {
//                 "bookId": '@natural(60, 100)',
//                 "bookName": '@ctitle(3, 15)',
//                 "bookAuthor": '@cword(3, 5)',
//                 "bookISBN": /\d{13}/,
//                 "bookPress": '@ctitle(3, 10)' + '出版社',
//                 "bookExistingNumber": '@integer(0, 5)', // 现存总数量
//                 "bookTotalNumber": '@integer(10, 16)' // 总数量
//             }
//         ]
//     },
//     "msg": "获取成功"
// })

// // 删除书籍
// Mock.mock(/\/api\/books\/.*/, 'delete', {
//     "status": 200,
//     "msg": "删除成功"
// })

// // 借阅书籍
// Mock.mock(/\/api\/records/, 'post', {
//     "status": 200,
//     "msg": "借阅成功"
// })

// // 查询借阅记录
// Mock.mock(/\/api\/records.*/, 'get', {
//     "status": 200,
//     "data": {
//         "page": '@increment',
//         "page-size": 10,
//         "total-count": 124, // 匹配的查询结果数量
//         "total-page": 13, // 一共有多少页
//         "records|10": [
//             {
//                 "rcdId": '@natural(60, 100)',
//                 "rcdUserID": '@natural(60, 100)',
//                 "rcdBookID": '@natural(60, 100)',
//                 "rcdBorrowDate": '@datetime("T")',
//                 "rcdReturnDate": '@datetime("T")',
//                 "rcdReturned": "@integer(0, 1)", // 归还状态
//                 "bookName": '@ctitle(3, 15)',
//                 "bookAuthor": '@cword(3, 5)',
//                 "bookISBN": /\d{13}/,
//                 "bookPress": '@ctitle(3, 10)' + '出版社',
//                 "bookExistingNumber": '@integer(0, 5)', // 现存总数量
//                 "bookTotalNumber": '@integer(10, 16)', // 总数量
//                 "userEmail": "@email",
//                 "userStuId": /^\d{12}$/,
//                 "userName": "@cword(3, 5)",
//                 "userGender": '@integer(0,3)',
//                 "userAge": '@integer(0, 100)',
//                 "userBio": "'@cparagraph(0, 5)'",
//                 "userGroup": '@integer(0, 2)'
//             }
//         ]
//     },
//     "msg": "获取成功"
// })


// // 用户归还某一本书
// Mock.mock(/\/api\/records.*/, 'put', {
//     "status": 200,
//     "msg": "归还成功"
// })

// // 删除记录
// Mock.mock(/\/api\/records\/.*/, 'delete', {
//     "status": 200,
//     "msg": "归还成功"
// })

// // 修改图书
// Mock.mock(/\/api\/books.*/, 'put', {
//     "status": 200,
//     "msg": "修改成功"
// })