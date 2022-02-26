var loginInfo = {
    user: {
        // "userId": 123,
        // "userEmail": "abc@email.com",
        // "userStuId": "202108010500",
        // "userName": "张三",
        // "userGender": 1,
        // "userAge": 16,
        // "userBio": "",
        // "userGroup": 1
    },
    getToken() {
        return localStorage.getItem('token')
    },
    login(token) {
        localStorage.setItem('token', token)
    },
    logout() {
        localStorage.removeItem('token')
        this.user = {}
    },
    isLogin() {
        if (this.getToken()) {
            return true
        } else {
            return false
        }
    },
    async update() {
        if(!this.isLogin()) {
            return;
        }
        let res = await axios.get('/users/self', {
            headers: {
                'token': this.getToken()
            }
        });

        if(res.status == 200) {
            this.user = res.data
        }else {
            Vue.prototype.$message.error('获取用户信息失败')
        }
    }
}

// localStorage.setItem('token', '123')
// localStorage.removeItem('token')


// loginInfo.init() // 异步，请在外部调用

