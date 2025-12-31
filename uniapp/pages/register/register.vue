<template>
	<view class="register-container">
		<!-- Logo区域 -->
		<view class="logo-section">
			<image src="/static/logo.png" class="logo" mode="aspectFit"></image>
			<text class="subtitle">账号注册</text>
		</view>
		
		<!-- 注册表单 -->
		<view class="form-section">
			<view class="form-item">
				<text class="label">用户名</text>
				<input 
					v-model="form.user_on" 
					type="text" 
					placeholder="请输入用户名" 
					class="input"
					placeholder-class="placeholder"
				/>
			</view>
			
			<view class="form-item">
				<text class="label">密码</text>
				<view class="password-input">
					<input 
						v-model="form.password" 
						:type="showPassword ? 'text' : 'password'" 
						placeholder="请输入密码（6-20位）" 
						class="input"
						placeholder-class="placeholder"
					/>
					<text class="toggle-password" @tap="togglePassword">
						{{ showPassword ? '隐藏' : '显示' }}
					</text>
				</view>
			</view>
			
			<view class="form-item">
				<text class="label">确认密码</text>
				<input 
					v-model="form.confirmPassword" 
					:type="showPassword ? 'text' : 'password'" 
					placeholder="请再次输入密码" 
					class="input"
					placeholder-class="placeholder"
				/>
			</view>
			
			<view class="form-item">
				<text class="label">姓名</text>
				<input 
					v-model="form.user_name" 
					type="text" 
					placeholder="请输入姓名" 
					class="input"
					placeholder-class="placeholder"
				/>
			</view>
			
			<button 
				@tap="register" 
				class="register-btn"
				:loading="loading"
				:disabled="loading"
			>
				注册
			</button>
			
			<view class="login-link">
				<text>已有账号？</text>
				<text class="link" @tap="goLogin">立即登录</text>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '@/common/request.js';

export default {
	name: 'register',
	data() {
		return {
			form: {
				user_on: '',
				password: '',
				confirmPassword: '',
				user_name: ''
			},
			showPassword: false,
			loading: false
		};
	},
	methods: {
		// 切换密码显示状态
		togglePassword() {
			this.showPassword = !this.showPassword;
		},
		
		// 注册
		async register() {
			// 表单验证
			if (!this.form.user_on || !this.form.password || !this.form.confirmPassword || !this.form.user_name) {
				uni.showToast({
					title: '请填写完整信息',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			if (this.form.password !== this.form.confirmPassword) {
				uni.showToast({
					title: '两次输入的密码不一致',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			if (this.form.password.length < 6 || this.form.password.length > 20) {
				uni.showToast({
					title: '密码长度应在6-20位之间',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			this.loading = true;
			
			try {
				// 调用注册接口
				const res = await request({
					url: '/user/register',
					method: 'POST',
					data: {
						user_on: this.form.user_on,
						password: this.form.password,
						user_name: this.form.user_name
					}
				});
				
				uni.showToast({
					title: '注册成功',
					icon: 'success',
					duration: 1500
				});
				
				// 跳转到登录页面
				setTimeout(() => {
					uni.navigateTo({
						url: '/pages/login/login'
					});
				}, 1500);
			} catch (error) {
				console.error('注册失败:', error);
				uni.showToast({
					title: error.msg || '注册失败，请重试',
					icon: 'none',
					duration: 2000
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 跳转到登录页面
		goLogin() {
			uni.navigateTo({
				url: '/pages/login/login'
			});
		}
	}
};
</script>

<style scoped>
.register-container {
	padding: 40rpx 30rpx;
	background-color: #F5F7FA;
	min-height: 100vh;
	display: flex;
	flex-direction: column;
}

.logo-section {
	align-items: center;
	margin-bottom: 40rpx;
}

.logo {
	width: 120rpx;
	height: 120rpx;
	margin-bottom: 20rpx;
}

.subtitle {
	font-size: 32rpx;
	color: #333333;
	font-weight: bold;
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

.register-btn {
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

.register-btn::after {
	border: none;
}

.register-btn:active {
	background-color: #2D455A;
}

.login-link {
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