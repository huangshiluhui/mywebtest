<template>
  <div class="login">

    <el-form ref="loginRef" :model="loginForm"  :rules="loginRules" class="login-form">
      <h3 class="title">Django后台管理系统</h3>

      <el-form-item prop="username">

        <el-input
          v-model="loginForm.username"
            type="text"
            size="large"
            auto-complete="off"
            placeholder="账号"
        >
        <template #prefix>
          <login-icon icon="user" /></template>
        </el-input>
      </el-form-item>
      <el-form-item prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          size="large"
          auto-complete="off"
          placeholder="密码"
        >
        <template #prefix><login-icon icon="password" /></template>
        </el-input>
      </el-form-item>


      <el-checkbox  style="margin:0px 0px 25px 0px;">记住密码</el-checkbox>
      <el-form-item style="width:100%;">
        <el-button
            size="large"
            type="primary"
            style="width:100%;"
            @click.prevent="handleLogin"
        >
          <span>登 录</span>

        </el-button>

      </el-form-item>
    </el-form>
    <!--  底部  -->
    <div class="el-login-footer">
      <span>Copyright © 2013-2025 <a href="http://www.python222.com" target="_blank">python222.com</a> 版权所有.</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import requestUtil from '@/util/request.js'
import { ElMessage } from 'element-plus'

const loginForm = ref({
  username: '',
  password: ''
})
const loginRef=ref(null)

const loginRules = {
  username: [{required: true, trigger: "blur", message: "请输入您的账号"}],
  password: [{required: true, trigger: "blur", message: "请输入您的密码"}]
}

const handleLogin = async () => {
  // 先进行表单验证
  if (!loginRef.value) {
    ElMessage.warning('表单未初始化')
    return
  }
  
  try {
    // 验证表单
    await loginRef.value.validate()
  } catch (error) {
    console.log('表单验证失败:', error)
    ElMessage.warning('请填写完整的登录信息')
    return
  }
  
  try {
    // 记录请求开始时间
    const startTime = Date.now()
    const startTimeStr = new Date().toLocaleTimeString()
    
    ElMessage.info('正在发送登录请求...')
    console.log('⏱️ [LoginView] 请求开始时间:', startTimeStr)
    
    let result = await requestUtil.post("user/login/", loginForm.value)
    
    // 记录请求结束时间
    const endTime = Date.now()
    const endTimeStr = new Date().toLocaleTimeString()
    const duration = endTime - startTime
    
    console.log('⏱️ [LoginView] 请求结束时间:', endTimeStr)
    console.log('⏱️ [LoginView] 请求总耗时:', duration, 'ms')
    console.log('登录响应结果:', result)
    console.log('响应数据:', result.data)
    
    // 检查后端返回的状态码
    if (result.data && result.data.code === 200) {
      // 登录成功
      console.log('✅ 登录成功')
      
      // 保存 token 到 sessionStorage
      if (result.data.token) {
        window.sessionStorage.setItem('token', result.data.token)
        window.sessionStorage.setItem('currentUser', JSON.stringify(result.data.user))
        console.log('✅ Token 已保存到 sessionStorage')
      }
      
      // 延迟显示成功消息
      setTimeout(() => {
        if (typeof ElMessage.closeAll === 'function') {
          ElMessage.closeAll()
        }
        ElMessage.success({
          message: result.data.info || '登录成功！',
          duration: 2000
        })
        
        // 可以在这里添加页面跳转
        // 例如：router.push('/home')
      }, 300)
    } else {
      // 登录失败（用户名或密码错误等）
      const errorMsg = result.data?.info || '登录失败，请稍后重试'
      console.error('❌ 登录失败:', errorMsg)
      console.error('错误代码:', result.data?.code)
      
      setTimeout(() => {
        if (typeof ElMessage.closeAll === 'function') {
          ElMessage.closeAll()
        }
        ElMessage.error({
          message: errorMsg,
          duration: 3000
        })
      }, 300)
    }
  } catch (error) {
    // 网络错误或其他异常
    console.error('登录请求异常:', error)
    console.error('错误详情:', error.response)
    
    let errorMsg = '登录失败，请检查网络连接'
    if (error.response && error.response.data) {
      errorMsg = error.response.data.info || errorMsg
    } else if (error.message) {
      errorMsg = error.message
    }
    
    if (typeof ElMessage.closeAll === 'function') {
      ElMessage.closeAll()
    }
    ElMessage.error({
      message: errorMsg,
      duration: 3000
    })
  }
}
</script>

<style lang="scss" scoped>
a{
  color:white
}
.login {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  // background-image: url("../assets/images/ceshi.png");
  background-size: cover;
}
.title {
  margin: 0px auto 30px auto;
  text-align: center;
  color: #707070;
}

.login-form {
  border-radius: 6px;
  background: #ffffff;
  width: 400px;
  padding: 25px 25px 5px 25px;

  .el-input {
    height: 40px;



    input {
      display: inline-block;
      height: 40px;
    }
  }
  .input-icon {
    height: 39px;
    width: 14px;
    margin-left: 0px;
  }

}
.login-tip {
  font-size: 13px;
  text-align: center;
  color: #bfbfbf;
}
.login-code {
  width: 33%;
  height: 40px;
  float: right;
  img {
    cursor: pointer;
    vertical-align: middle;
  }
}
.el-login-footer {
  height: 40px;
  line-height: 40px;
  position: fixed;
  bottom: 0;
  width: 100%;
  text-align: center;
  color: #fff;
  font-family: Arial;
  font-size: 12px;
  letter-spacing: 1px;
}
.login-code-img {
  height: 40px;
  padding-left: 12px;
}
</style>
