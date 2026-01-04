<template>
	<view class="profile-container">
		<!-- 个人信息卡片 -->
		<view class="profile-card">
			<view class="avatar-section">
				<image :src="logoUrl" class="avatar" mode="aspectFit"></image>
				<view class="user-info">
					<text class="username">{{ userInfo.user_name || '未设置' }}</text>
					<text class="user-role">{{ getUserRoleText() }}</text>
				</view>
			</view>
		</view>
		
		<!-- 信息列表 -->
		<view class="info-section">
			<view class="info-item">
				<text class="info-label">用户名</text>
				<text class="info-value">{{ userInfo.user_on || '未设置' }}</text>
			</view>
			
			<view class="info-item">
				<text class="info-label">姓名</text>
				<text class="info-value">{{ userInfo.user_name || '未设置' }}</text>
			</view>
			
			<view class="info-item">
				<text class="info-label">学院</text>
				<text class="info-value">{{ userInfo.college_name || '未设置' }}</text>
			</view>
			
			<view class="info-item">
				<text class="info-label">教研室</text>
				<text class="info-value">{{ userInfo.research_room_name || '未设置' }}</text>
			</view>
			
			<view class="info-item">
				<text class="info-label">角色</text>
				<text class="info-value">{{ getUserRoleText() }}</text>
			</view>
		</view>
		
		<!-- 功能列表 -->
		<view class="function-section">
			<view class="function-item" @tap="navigateTo('/pages/password/change-password')">
				<text class="function-text">修改密码</text>
				<!-- 22300417陈俫坤开发：用样式绘制右箭头，避免出现“&gt;/%gt”实体字符 -->
				<text class="arrow"></text>
			</view>
			
			<view class="function-item" @tap="editProfile">
				<text class="function-text">编辑资料</text>
				<text class="arrow"></text>
			</view>
			
			<view class="function-item" @tap="aboutUs">
				<text class="function-text">关于我们</text>
				<text class="arrow"></text>
			</view>
			
			<view class="function-item" @tap="feedback">
				<text class="function-text">意见反馈</text>
				<text class="arrow"></text>
			</view>
		</view>
		
		<!-- 退出登录按钮 -->
		<button @tap="logout" class="logout-btn">
			退出登录
		</button>
		
		<!-- 编辑资料弹窗 -->
		<uni-popup ref="editPopup" type="center" :mask-click="false">
			<view class="popup-container">
				<view class="popup-header">
					<text class="popup-title">编辑资料</text>
					<text class="popup-close" @tap="closeEditPopup">×</text>
				</view>
				
				<view class="popup-content">
					<view class="form-item">
						<text class="form-label">姓名</text>
						<input 
							type="text" 
							class="form-input" 
							:value="editForm.user_name" 
							placeholder="请输入姓名" 
							@input="handleUserNameInput"
						/>
					</view>
					
					<view class="form-item">
						<text class="form-label">学院</text>
						<picker mode="selector" :range="collegePickerNames" :value="collegeIndex" @change="handleCollegeChange">
							<view class="form-input picker-input">{{ currentCollegeName }}</view>
						</picker>
					</view>
					
					<view class="form-item">
						<text class="form-label">教研室</text>
						<picker mode="selector" :range="researchRoomPickerNames" :value="researchRoomIndex" @change="handleResearchRoomChange">
							<view class="form-input picker-input">{{ currentResearchRoomName }}</view>
						</picker>
					</view>
					
					<view class="form-item">
						<text class="form-label">用户名</text>
						<input 
							type="text" 
							class="form-input" 
							:value="editForm.user_on" 
							placeholder="请输入用户名" 
							@input="handleUserOnInput"
						/>
					</view>
				</view>
				
				<view class="popup-footer">
					<button class="cancel-btn" @tap="closeEditPopup">取消</button>
					<button class="save-btn" @tap="saveProfile" :loading="loading">保存</button>
				</view>
			</view>
		</uni-popup>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	data() {
		return {
			logoUrl: '/static/logo.png',
			userInfo: {},
			editForm: {
				user_name: '',
				user_on: '',
				// 22300417陈俫坤开发：支持用户设置学院
				college_id: null,
				// 22300417陈俫坤开发：教师可同时属于学院与教研室
				research_room_id: null
			},
			// 22300417陈俫坤开发：学院列表（用于 picker）
			colleges: [],
			// 22300417陈俫坤开发：教研室列表（用于 picker）
			researchRooms: [],
			loading: false
		};
	},
	computed: {
		collegePickerNames() {
			const names = ['未设置'];
			(this.colleges || []).forEach(c => names.push(c.college_name));
			return names;
		},
		collegeIndex() {
			return this.getCollegeIndexById(this.editForm.college_id);
		},
		currentCollegeName() {
			return this.getCollegeNameById(this.editForm.college_id);
		},
		researchRoomPickerNames() {
			const names = ['未设置'];
			(this.researchRooms || []).forEach(r => names.push(r.room_name));
			return names;
		},
		researchRoomIndex() {
			return this.getResearchRoomIndexById(this.editForm.research_room_id);
		},
		currentResearchRoomName() {
			return this.getResearchRoomNameById(this.editForm.research_room_id);
		}
	},
	onLoad() {
		this.getUserInfo();
		this.loadColleges();
		this.loadResearchRooms();
	},
	onShow() {
		// 页面显示时刷新用户信息
		this.getUserInfo();
	},
	methods: {
		// 22300417陈俫坤开发：获取学院列表供用户选择
		async loadColleges() {
			try {
				const res = await request({
					url: '/org/colleges',
					method: 'GET',
					params: { skip: 0, limit: 200 }
				});
				this.colleges = (res && res.list) ? res.list : [];
			} catch (e) {
				this.colleges = [];
			}
		},
		// picker 当前选中 index（0=未设置，其余为 colleges+1）
		getCollegeIndexById(collegeId) {
			if (!collegeId) return 0;
			const idx = (this.colleges || []).findIndex(c => Number(c.id) === Number(collegeId));
			return idx >= 0 ? idx + 1 : 0;
		},
		getCollegeNameById(collegeId) {
			if (!collegeId) return '未设置';
			const c = (this.colleges || []).find(x => Number(x.id) === Number(collegeId));
			return c ? c.college_name : '未设置';
		},
		handleCollegeChange(e) {
			const index = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			if (index <= 0) {
				this.editForm.college_id = null;
				// 22300417陈俫坤开发：学院变更后，教研室选择也清空并刷新列表
				this.editForm.research_room_id = null;
				this.loadResearchRooms();
				return;
			}
			const c = (this.colleges || [])[index - 1];
			this.editForm.college_id = c ? c.id : null;
			// 22300417陈俫坤开发：学院变更后，教研室选择也清空并刷新列表
			this.editForm.research_room_id = null;
			this.loadResearchRooms();
		},

		// 22300417陈俫坤开发：获取教研室列表供用户选择（默认按本人学院过滤；传 college_id 可按学院筛选）
		async loadResearchRooms() {
			try {
				const params = {};
				if (this.editForm && this.editForm.college_id) {
					params.college_id = this.editForm.college_id;
				}
				const res = await request({
					url: '/user/research-rooms',
					method: 'GET',
					params
				});
				this.researchRooms = (res && res.list) ? res.list : [];
			} catch (e) {
				this.researchRooms = [];
			}
		},
		getResearchRoomIndexById(roomId) {
			if (!roomId) return 0;
			const idx = (this.researchRooms || []).findIndex(r => Number(r.id) === Number(roomId));
			return idx >= 0 ? idx + 1 : 0;
		},
		getResearchRoomNameById(roomId) {
			if (!roomId) return '未设置';
			const r = (this.researchRooms || []).find(x => Number(x.id) === Number(roomId));
			return r ? r.room_name : '未设置';
		},
		handleResearchRoomChange(e) {
			const index = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			if (index <= 0) {
				this.editForm.research_room_id = null;
				return;
			}
			const r = (this.researchRooms || [])[index - 1];
			this.editForm.research_room_id = r ? r.id : null;
		},

		// 兼容 web 和微信小程序的输入处理
		handleUserNameInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.editForm.user_name = value;
		},
		handleUserOnInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.editForm.user_on = value;
		},
		// 获取用户信息
		async getUserInfo() {
			try {
				// 调用接口获取最新信息
				const res = await request({
					url: '/user/me',
					method: 'GET'
				});
				// 提取用户信息，包括角色信息
				const userInfo = res.user || {};
				// 添加角色信息到userInfo中
				userInfo.roles_name = res.roles_name || [];
				userInfo.roles_code = res.roles_code || [];
				// 22300417陈俫坤开发：后端若未返回 college_name，则用学院列表做一次兜底映射
				if (!userInfo.college_name && userInfo.college_id) {
					userInfo.college_name = this.getCollegeNameById(userInfo.college_id);
				}
				// 保存到本地
				uni.setStorageSync('userInfo', userInfo);
				this.userInfo = userInfo;
				// 22300417陈俫坤开发：同步编辑表单默认值
				this.editForm.research_room_id = userInfo.research_room_id || null;
			} catch (error) {
				console.error('获取用户信息失败:', error);
				// 如果获取失败，可能是登录过期，跳转到登录页面
				if (error.code === 401) {
					this.logout();
				}
			}
		},
		
		// 获取用户角色文本
		getUserRoleText() {
			// 从roles_name数组中获取角色信息
			if (this.userInfo.roles_name && this.userInfo.roles_name.length > 0) {
				return this.userInfo.roles_name[0];
			}
			// 从roles_code数组中推断角色名称
			if (this.userInfo.roles_code && this.userInfo.roles_code.length > 0) {
				const roleCode = this.userInfo.roles_code[0];
				const roleMap = {
					'teacher': '教师',
					'supervisor': '督导老师',
					'college_admin': '学院管理员',
					'school_admin': '学校管理员'
				};
				return roleMap[roleCode] || '教师';
			}
			// 默认显示教师
			return '教师';
		},
		
		// 导航到指定页面
		navigateTo(url) {
			uni.navigateTo({
				url: url
			});
		},
		
		// 打开编辑资料弹窗
		editProfile() {
			// 初始化编辑表单数据
			this.editForm = {
				user_name: this.userInfo.user_name || '',
				user_on: this.userInfo.user_on || '',
				college_id: this.userInfo.college_id || null,
				research_room_id: this.userInfo.research_room_id || null
			};
			// 打开弹窗
			this.$refs.editPopup.open();
		},
		
		// 关闭编辑资料弹窗
		closeEditPopup() {
			this.$refs.editPopup.close();
		},
		
		// 保存个人信息
		async saveProfile() {
			// 表单验证
			if (!this.editForm.user_name) {
				uni.showToast({
					title: '请输入姓名',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			if (!this.editForm.user_on) {
				uni.showToast({
					title: '请输入用户名',
					icon: 'none',
					duration: 2000
				});
				return;
			}
			
			this.loading = true;
			
			try {
				// 调用更新接口
				const res = await request({
					url: '/user/update',
					method: 'PATCH',
					data: this.editForm
				});
				
				uni.showToast({
					title: '保存成功',
					icon: 'success',
					duration: 1500
				});
				
				// 更新本地用户信息
				this.userInfo = { ...this.userInfo, ...this.editForm };
				this.userInfo.college_name = this.getCollegeNameById(this.editForm.college_id);
				this.userInfo.research_room_name = this.getResearchRoomNameById(this.editForm.research_room_id);
				uni.setStorageSync('userInfo', this.userInfo);
				
				// 关闭弹窗
				this.closeEditPopup();
			} catch (error) {
				console.error('更新个人信息失败:', error);
				uni.showToast({
					title: error.msg || '保存失败，请重试',
					icon: 'none',
					duration: 2000
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 关于我们
		aboutUs() {
			uni.showModal({
				title: '关于我们',
				content: '南宁理工学院听课评教系统\n版本：1.0.0\n\n© 2025 南宁理工学院',
				showCancel: false
			});
		},
		
		// 意见反馈
		feedback() {
			uni.showToast({
				title: '功能开发中',
				icon: 'none',
				duration: 1500
			});
		},
		
		// 退出登录
		logout() {
			uni.showModal({
				title: '提示',
				content: '确定要退出登录吗？',
				success: (res) => {
					if (res.confirm) {
						// 清除本地存储
						uni.removeStorageSync('token');
						uni.removeStorageSync('userInfo');
						// 跳转到登录页面
						uni.redirectTo({
							url: '/pages/login/login'
						});
					}
				}
			});
		}
	}
};
</script>

<style scoped>
.profile-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding-bottom: 30rpx;
}

/* 个人信息卡片 */
.profile-card {
	background-color: #3E5C76;
	color: #FFFFFF;
	padding: 40rpx 30rpx;
}

.avatar-section {
	display: flex;
	align-items: center;
}

.avatar {
	width: 120rpx;
	height: 120rpx;
	border-radius: 60rpx;
	background-color: #FFFFFF;
	padding: 10rpx;
	margin-right: 30rpx;
}

.user-info {
	flex: 1;
}

.username {
	font-size: 36rpx;
	font-weight: bold;
	display: block;
	margin-bottom: 10rpx;
}

.user-role {
	font-size: 24rpx;
	opacity: 0.9;
}

/* 信息列表 */
.info-section {
	background-color: #FFFFFF;
	margin-top: 20rpx;
	padding: 0 30rpx;
}

.info-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	height: 100rpx;
	border-bottom: 2rpx solid #F5F7FA;
}

.info-item:last-child {
	border-bottom: none;
}

.info-label {
	font-size: 28rpx;
	color: #333333;
}

.info-value {
	font-size: 28rpx;
	color: #666666;
	text-align: right;
}

/* 功能列表 */
.function-section {
	background-color: #FFFFFF;
	margin-top: 20rpx;
	padding: 0 30rpx;
}

.function-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	height: 100rpx;
	border-bottom: 2rpx solid #F5F7FA;
}

.function-item:last-child {
	border-bottom: none;
}

.function-text {
	font-size: 28rpx;
	color: #333333;
}

.arrow {
	font-size: 32rpx;
	color: #C0C4CC;
}

.arrow::after {
	content: '>';
}

/* 退出登录按钮 */
.logout-btn {
	width: 90%;
	height: 88rpx;
	background-color: #FF6B6B;
	color: #FFFFFF;
	font-size: 32rpx;
	font-weight: bold;
	border-radius: 44rpx;
	margin-top: 60rpx;
	margin-left: 5%;
	margin-right: 5%;
}

.logout-btn::after {
	border: none;
}

.logout-btn:active {
	background-color: #FF5252;
}

/* 编辑资料弹窗样式 */
.popup-container {
	width: 600rpx;
	background-color: #FFFFFF;
	border-radius: 20rpx;
	overflow: hidden;
}

.popup-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	border-bottom: 2rpx solid #F5F7FA;
}

.popup-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.popup-close {
	font-size: 48rpx;
	color: #C0C4CC;
	font-weight: bold;
}

.popup-content {
	padding: 30rpx;
}

.form-item {
	margin-bottom: 30rpx;
}

.form-label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 10rpx;
	font-weight: 500;
}

.form-input {
	width: 100%;
	height: 80rpx;
	border: 2rpx solid #E4E7ED;
	border-radius: 10rpx;
	padding: 0 20rpx;
	box-sizing: border-box;
	background-color: #F5F7FA;
}

.popup-footer {
	display: flex;
	justify-content: flex-end;
	padding: 30rpx;
	border-top: 2rpx solid #F5F7FA;
	gap: 20rpx;
}

.cancel-btn {
	width: 160rpx;
	height: 72rpx;
	background-color: #F5F7FA;
	color: #606266;
	font-size: 28rpx;
	border-radius: 8rpx;
}

.cancel-btn::after {
	border: none;
}

.save-btn {
	width: 160rpx;
	height: 72rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 28rpx;
	border-radius: 8rpx;
}

.save-btn::after {
	border: none;
}

.save-btn:active {
	background-color: #2D4A63;
}
</style>