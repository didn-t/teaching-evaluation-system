<template>
	<view class="login-container">
		<!-- Logo区域 -->
		<view class="logo-section">
			<image src="/static/logo.png" class="logo" mode="aspectFit"></image>
			<text class="title">南宁理工学院</text>
			<text class="subtitle">听课评教系统</text>
		</view>
		
		<!-- 登录表单 -->
		<view class="form-section">
			<view class="form-item">
				<text class="label">用户名</text>
				<input 
					:value="form.user_on" 
					type="text" 
					placeholder="请输入用户名" 
					class="input"
					placeholder-class="placeholder"
					@input="handleUserOnInput"
				/>
			</view>
			
			<view class="form-item">
				<text class="label">密码</text>
				<view class="password-input">
					<input 
						:value="form.password" 
						:type="showPassword ? 'text' : 'password'" 
						placeholder="请输入密码" 
						class="input"
						placeholder-class="placeholder"
						@input="handlePasswordInput"
					/>
					<text class="toggle-password" @tap="togglePassword">
						{{ showPassword ? '隐藏' : '显示' }}
					</text>
				</view>
			</view>
			
			<button 
				@tap="login" 
				class="login-btn"
				:loading="loading"
				:disabled="loading"
			>
				登录
			</button>
			
			<view class="register-link">
				<text>还没有账号？</text>
				<text class="link" @tap="goRegister">立即注册</text>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'login',
	data() {
		return {
			form: {
				user_on: '',
				password: ''
			},
			showPassword: false,
			loading: false
		};
	},
	methods: {
		// 兼容 web 和微信小程序的输入处理
		handleUserOnInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.form.user_on = value;
		},
		handlePasswordInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.form.password = value;
		},
		// 切换密码显示状态
		togglePassword() {
			this.showPassword = !this.showPassword;
		},
		
		// 登录
			async login() {
				// 表单验证
				if (!this.form.user_on || !this.form.password) {
					uni.showToast({
						title: '请输入用户名和密码',
						icon: 'none',
						duration: 2000
					});
					return;
				}
			
			this.loading = true;
			
			try {
				// 调用登录接口
					const res = await request({
						url: '/user/login',
						method: 'POST',
						data: this.form
					});
				
				// 保存用户信息（token已在request.js中自动保存）
				uni.setStorageSync('userInfo', res.user || {});
				
				uni.showToast({
					title: '登录成功',
					icon: 'success',
					duration: 1500
				});
				
				// 跳转到首页
				setTimeout(() => {
					uni.switchTab({
						url: '/pages/index/index'
					});
				}, 1500);
			} catch (error) {
				console.error('登录失败:', error);
				uni.showToast({
					title: error.msg || '登录失败，请重试',
					icon: 'none',
					duration: 2000
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 跳转到注册页面
		goRegister() {
			uni.navigateTo({
				url: '/pages/register/register'
			});
		}
	}
};
</script>

<style scoped>
.login-container {
	padding: 40rpx 30rpx;
	background-color: #F5F7FA;
	min-height: 100vh;
	display: flex;
	flex-direction: column;
}

.logo-section {
	align-items: center;
	margin-bottom: 60rpx;
}

.logo {
	width: 160rpx;
	height: 160rpx;
	margin-bottom: 20rpx;
}

.title {
	font-size: 36rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 10rpx;
}

.subtitle {
	font-size: 28rpx;
	color: #666666;
}

.form-section {
	background-color: #FFFFFF;
	border-radius: 16rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.form-item {
	margin-bottom: 30rpx;
}

.label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 12rpx;
	font-weight: 500;
}

.input {
	width: 100%;
	height: 80rpx;
	border: 2rpx solid #E4E7ED;
	border-radius: 8rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #333333;
	background-color: #F5F7FA;
}

.input:focus {
	border-color: #3E5C76;
	background-color: #FFFFFF;
}

.placeholder {
	color: #C0C4CC;
}

.password-input {
	display: flex;
	align-items: center;
}

.password-input .input {
	flex: 1;
	margin-right: 20rpx;
}

.toggle-password {
	font-size: 24rpx;
	color: #3E5C76;
	padding: 10rpx;
}

.login-btn {
	width: 100%;
	height: 88rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 32rpx;
	font-weight: bold;
	border-radius: 44rpx;
	margin-top: 40rpx;
	margin-bottom: 30rpx;
}

.login-btn::after {
	border: none;
}

.login-btn:active {
	background-color: #2D455A;
}

.register-link {
	display: flex;
	justify-content: center;
	align-items: center;
	font-size: 26rpx;
	color: #666666;
}

.link {
	color: #3E5C76;
	margin-left: 10rpx;
	font-weight: 500;
}
</style>