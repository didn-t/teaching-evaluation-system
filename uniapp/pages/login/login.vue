<template>
  <view class="login-container">
    <view class="login-card">
      <view class="login-header">
        <text class="title">评教系统</text>
        <text class="subtitle">教学质量评价系统</text>
      </view>
      <view class="login-form">
        <view class="field">
          <text class="label">用户名</text>
          <input v-model="username" type="text" placeholder="请输入用户名" class="input" @input="onUsernameInput" />
        </view>
        <view class="field">
          <text class="label">密码</text>
          <input v-model="password" type="password" placeholder="请输入密码" class="input" @input="onPasswordInput" />
        </view>
        <view v-if="error" class="toast error">{{ error }}</view>
        <button @tap="handleLogin" class="primary-btn" :loading="loading">登录</button>
      </view>
      <view class="login-tips">
        <text class="tips-title">演示账号：</text>
        <text class="tip">教师：teacher1 / 123456</text>
        <text class="tip">督导老师：supervisor1 / 123456</text>
        <text class="tip">学院管理员：college1 / 123456</text>
        <text class="tip">学校管理员：school1 / 123456</text>
      </view>
    </view>
  </view>
</template>

<script>
import { simpleStore } from '../../utils/simpleStore';

export default {
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false
    };
  },
  methods: {
    onUsernameInput(e) {
      this.username = e.detail.value;
    },
    onPasswordInput(e) {
      this.password = e.detail.value;
    },
    handleLogin() {
      this.error = '';
      
      // 输入验证
      if (!this.username || !this.password) {
        this.error = '请输入用户名和密码';
        return;
      }
      
      // 本地验证登录（不进行服务器连接检测）
      // TODO: 后期接入后端接口时，可在此处调用登录API
      // 示例：const response = await uni.request({
      //   url: '/api/auth/login',
      //   method: 'POST',
      //   data: { username: this.username, password: this.password }
      // });
      // if (response.data.success) { ... }
      
      this.loading = true;
      
      // 使用本地存储进行验证，直接跳转，不检测服务器连接
      const success = simpleStore.login(this.username, this.password);
      
      if (success) {
        const user = simpleStore.state.currentUser;
        
        // 确保用户信息已设置
        if (!user || !user.role) {
          this.error = '用户信息获取失败';
          this.loading = false;
          return;
        }
        
        // 根据用户角色直接跳转到相应页面（不进行任何网络检测）
        if (user.role === 'teacher') {
          uni.switchTab({
            url: '/pages/teacher/index'
          });
        } else if (user.role === 'supervisor') {
          // 督导老师直接跳转到督导端首页，不进行服务器连接检测
          uni.redirectTo({
            url: '/pages/supervisor/index'
          });
        } else if (user.role === 'college_admin') {
          uni.redirectTo({
            url: '/pages/college/index'
          });
        } else if (user.role === 'school_admin') {
          uni.redirectTo({
            url: '/pages/school/index'
          });
        } else {
          this.error = '用户角色无效：' + user.role;
          this.loading = false;
        }
      } else {
        this.error = '登录失败，请检查用户名和密码';
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f5f5;
}

.login-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 16px 40px rgba(31, 41, 51, 0.1);
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.title {
  font-size: 28px;
  color: #4f46e5;
  display: block;
  margin-bottom: 8px;
}

.subtitle {
  color: #1f2933;
  font-size: 14px;
  display: block;
}

.login-form {
  margin-bottom: 24px;
}

.field {
  margin-bottom: 16px;
}

.label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  height: auto; /* 确保高度自适应 */
}

.toast {
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  margin-top: 12px;
}

.error {
  background-color: #fee;
  color: #e53e3e;
  border: 1px solid #fed7d7;
}

.primary-btn {
  width: 100%;
  margin-top: 16px;
  background-color: #4f46e5;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 4px;
  font-size: 16px;
  height: auto; /* 确保高度自适应 */
}

.primary-btn::after {
  border: none;
}

.login-tips {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #c7d2fe;
  font-size: 12px;
  color: #1f2933;
}

.tips-title {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
}

.tip {
  display: block;
  margin: 4px 0;
}
</style>