<template>
	<view class="change-password-container">
		<view class="form-section">
			<view class="form-item">
				<text class="label">旧密码</text>
				<view class="password-input">
					<input 
						:value="form.oldPassword" 
						:type="showOldPassword ? 'text' : 'password'" 
						placeholder="请输入旧密码" 
						class="input"
						placeholder-class="placeholder"
						@input="handleOldPasswordInput"
					/>
					<text class="toggle-password" @tap="toggleOldPassword">
						{{ showOldPassword ? '隐藏' : '显示' }}
					</text>
				</view>
			</view>
			
			<view class="form-item">
				<text class="label">新密码</text>
				<view class="password-input">
					<input 
						:value="form.newPassword" 
						:type="showNewPassword ? 'text' : 'password'" 
						placeholder="请输入新密码（6-20位）" 
						class="input"
						placeholder-class="placeholder"
						@input="handleNewPasswordInput"
					/>
					<text class="toggle-password" @tap="toggleNewPassword">
						{{ showNewPassword ? '隐藏' : '显示' }}
					</text>
				</view>
			</view>
			
			<view class="form-item">
				<text class="label">确认新密码</text>
				<view class="password-input">
					<input 
						:value="form.confirmPassword" 
						:type="showConfirmPassword ? 'text' : 'password'" 
						placeholder="请再次输入新密码" 
						class="input"
						placeholder-class="placeholder"
						@input="handleConfirmPasswordInput"
					/>
					<text class="toggle-password" @tap="toggleConfirmPassword">
						{{ showConfirmPassword ? '隐藏' : '显示' }}
					</text>
				</view>
			</view>
			
			<button 
				@tap="changePassword" 
				class="change-btn"
				:loading="loading"
				:disabled="loading"
			>
				确认修改
			</button>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'change-password',
	data() {
		return {
			form: {
				oldPassword: '',
				newPassword: '',
				confirmPassword: ''
			},
			showOldPassword: false,
			showNewPassword: false,
			showConfirmPassword: false,
			loading: false
		};
	},
	methods: {
		// 兼容 web 和微信小程序的输入处理
		handleOldPasswordInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.form.oldPassword = value;
		},
		handleNewPasswordInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.form.newPassword = value;
		},
		handleConfirmPasswordInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.form.confirmPassword = value;
		},
		// 切换旧密码显示状态
		toggleOldPassword() {
			this.showOldPassword = !this.showOldPassword;
		},
		
		// 切换新密码显示状态
		toggleNewPassword() {
			this.showNewPassword = !this.showNewPassword;
		},
		
		// 切换确认密码显示状态
		toggleConfirmPassword() {
			this.showConfirmPassword = !this.showConfirmPassword;
		},
		
		// 修改密码
		async changePassword() {
			// 表单验证
			if (!this.form.oldPassword || !this.form.newPassword || !this.form.confirmPassword) {
				uni.showToast({
					title: '请填写完整信息',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			if (this.form.newPassword !== this.form.confirmPassword) {
				uni.showToast({
					title: '两次输入的新密码不一致',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			if (this.form.newPassword.length < 6 || this.form.newPassword.length > 20) {
				uni.showToast({
					title: '新密码长度应在6-20位之间',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			if (this.form.oldPassword === this.form.newPassword) {
				uni.showToast({
					title: '新密码不能与旧密码相同',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			this.loading = true;
			
			try {
				// 调用修改密码接口
				const res = await request({
					url: `/user/change-password?old_password=${encodeURIComponent(this.form.oldPassword)}&new_password=${encodeURIComponent(this.form.newPassword)}`,
					method: 'POST'
				});
				
				uni.showToast({
					title: '密码修改成功',
					icon: 'success',
					duration: 1500
				});
				
				// 跳回上一页
				setTimeout(() => {
					uni.navigateBack();
				}, 1500);
			} catch (error) {
				console.error('修改密码失败:', error);
				uni.showToast({
					title: error.msg || '修改密码失败，请重试',
					icon: 'none',
					duration: 2000
				});
			} finally {
				this.loading = false;
			}
		}
	}
};
</script>

<style scoped>
.change-password-container {
	padding: 40rpx 30rpx;
	background-color: #F5F7FA;
	min-height: 100vh;
}

.form-section {
	background-color: #FFFFFF;
	border-radius: 16rpx;
	padding: 40rpx;
	box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.form-item {
	margin-bottom: 40rpx;
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

.change-btn {
	width: 100%;
	height: 88rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 32rpx;
	font-weight: bold;
	border-radius: 44rpx;
	margin-top: 60rpx;
}

.change-btn::after {
	border: none;
}

.change-btn:active {
	background-color: #2D455A;
}
</style>