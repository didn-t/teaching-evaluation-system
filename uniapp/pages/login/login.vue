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
					<input v-model="username" type="text" placeholder="请输入用户名" class="input" @input="onUsernameInput" @confirm="handleLogin" />
				</view>
				<view class="field">
					<text class="label">密码</text>
					<input v-model="password" type="password" placeholder="请输入密码" class="input"
						@input="onPasswordInput" @confirm="handleLogin" />
				</view>
				<view v-if="error" class="error-message">{{ error }}</view>
				<button @tap="handleLogin" class="primary-btn" :loading="loading" :disabled="loading">登录</button>
				<view class="login-tips">
					<text class="tips-title">提示信息</text>
					<text class="tip">• 教学质量评价系统</text>

				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import {
		simpleStore
	} from '@/utils/simpleStore';
	import {
		baseUrl
	} from '@/common/config.js'
	import {
		request
	} from '@/common/request.js';

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
			async handleLogin() {
				this.error = '';
				// 输入验证
				if (!this.username.trim()) {
					this.error = '请输入用户名';
					return;
				}
				if (!this.password) {
					this.error = '请输入密码';
					return;
				}
				// 禁止包含特殊字符的用户名
				if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(this.username.trim())) {
					this.error = '用户名包含非法字符';
					return;
				}
				this.loading = true;
				this.error = '';
				
				console.log('开始登录请求');
				try {
					const res = await request({
						url: '/user/login',
						method: 'POST',
						data: {
							user_on: this.username,
							password: this.password
						}
					});
					console.log('登录响应:', res)
					// 登录请求成功，直接进入角色获取流程
					if (res) {
						uni.showToast({
							title: "登录成功",
							icon: 'success'
						});

						try {
							console.log('开始获取用户角色');
							const user = await request({
								url: '/user/role',
								method: 'GET'
							})
							console.log('用户角色响应:', user)
							if (!user || !user.role_code) {
								this.error = '用户信息获取失败';
								this.loading = false;
								return;
							}
							const role_list = user.role_code
							// 根据用户角色直接跳转到相应页面（不进行任何网络检测）
							if (role_list.includes('teacher')) {
								uni.switchTab({
									url: '/pages/teacher/index'
								});
							} else if (role_list.includes('supervisor')) {
								// 督导老师直接跳转到督导端首页，不进行服务器连接检测
								uni.redirectTo({
									url: '/pages/supervisor/index'
								});
							} else if (role_list.includes('college_admin')) {
								uni.redirectTo({
									url: '/pages/college/index'
								});
							} else if (role_list.includes('school_admin') || role_list.includes('admin')) {
								uni.redirectTo({
									url: '/pages/school/index'
								});
							} else {
								uni.switchTab({
									url: '/pages/teacher/index'
								});
							}
						} catch (err) {
							console.error('获取用户角色失败:', err);
							this.error = '用户信息获取失败';
							this.loading = false;
							return;
						}
					}
				} catch (err) {
					console.error('登录失败:', err);
					// 显示具体的错误信息
					const errorMsg = err.msg || err.message || '登录失败';
					uni.showToast({
						title: errorMsg,
						icon: 'none'
					});
					this.loading = false;
					return;
				}
				
				this.loading = false;
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
		height: auto;
		/* 确保高度自适应 */
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
	
	.error-message {
		padding: 10px;
		border-radius: 4px;
		text-align: center;
		margin-top: 12px;
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
		height: auto;
		/* 确保高度自适应 */
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