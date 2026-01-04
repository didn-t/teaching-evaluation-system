<template>
	<view class="admin-container">
		<view class="page-header">
			<text class="page-title">用户管理</text>
		</view>

		<view class="search-section">
			<view class="search-input">
				<text class="search-icon">🔍</text>
				<input
					:value="keyword"
					placeholder="搜索账号/姓名"
					class="input"
					placeholder-class="placeholder"
					@input="handleKeywordInput"
				/>
			</view>
			<view class="filter-actions">
				<button class="search-btn" @tap="refresh">查询</button>
				<button class="reset-btn" @tap="reset">重置</button>
			</view>
		</view>

		<view class="list-section">
			<view v-if="users.length" class="list-card">
				<view class="user-item" v-for="u in users" :key="u.id">
					<view class="item-header">
						<text class="user-name">{{ u.user_name }}</text>
						<text class="user-on">{{ u.user_on }}</text>
					</view>
					<view class="item-info">
						<text class="info-text">学院ID：{{ u.college_id ?? '-' }}</text>
						<text class="info-text">状态：{{ u.status === 1 ? '启用' : '禁用' }}</text>
					</view>
					<view class="roles-row">
						<text class="roles-label">角色：</text>
						<text class="roles-value">{{ (u.roles && u.roles.length) ? u.roles.join('、') : '无' }}</text>
					</view>
					<view class="item-actions">
						<button class="action-btn" @tap="openResetPassword(u)">重置密码</button>
						<button class="action-btn primary" @tap="openAssignRoles(u)">分配角色</button>
						<!-- 22300417陈俫坤开发：学校管理员可给督导配置负责范围（多学院/教研组） -->
						<button
							v-if="isSchoolAdmin && isSupervisorUser(u)"
							class="action-btn"
							@tap="openScopeModal(u)"
						>
							配置范围
						</button>
					</view>
				</view>
			</view>

			<view v-else class="empty-state">
				<text class="empty-icon">👥</text>
				<text class="empty-text">暂无用户数据</text>
				<text class="empty-hint">请确认你使用 school001 登录，并已初始化权限</text>
			</view>
		</view>

		<view class="pagination" v-if="users.length">
			<button class="page-btn" :disabled="page <= 0" @tap="prevPage">上一页</button>
			<text class="page-info">{{ page + 1 }}</text>
			<button class="page-btn" :disabled="users.length < limit" @tap="nextPage">下一页</button>
		</view>

		<!-- 重置密码弹窗 -->
		<view class="modal" v-if="showResetModal" @tap="closeModals">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">重置密码</text>
					<text class="modal-close" @tap="closeModals">×</text>
				</view>
				<view class="modal-body">
					<text class="modal-tip">账号：{{ currentUser?.user_on }}</text>
					<input
						:value="newPassword"
						password
						placeholder="输入新密码"
						class="modal-input"
						placeholder-class="placeholder"
						@input="handleNewPasswordInput"
					/>
					<button class="submit-btn" @tap="submitResetPassword">确认重置</button>
				</view>
			</view>
		</view>

		<!-- 分配角色弹窗 -->
		<view class="modal" v-if="showRoleModal" @tap="closeModals">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">分配角色</text>
					<text class="modal-close" @tap="closeModals">×</text>
				</view>
				<view class="modal-body">
					<text class="modal-tip">用户：{{ currentUser?.user_name }}（{{ currentUser?.user_on }}）</text>
					<view class="checkbox-list">
						<checkbox-group @change="onRoleCheckboxChange">
							<label class="checkbox-item" v-for="r in roles" :key="r.id">
								<checkbox :value="String(r.id)" :checked="selectedRoleIds.includes(r.id)" />
								<!-- 22300417陈俫坤开发：兼容后端字段 name/code 与 role_name/role_code -->
								<text class="checkbox-text">{{ (r.role_name || r.name) }}（{{ (r.role_code || r.code) }}）</text>
							</label>
						</checkbox-group>
					</view>
					<button class="submit-btn" @tap="submitAssignRoles">保存角色</button>
				</view>
			</view>
		</view>

		<!-- 配置督导范围弹窗 -->
		<view class="modal" v-if="showScopeModal" @tap="closeModals">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">配置督导范围</text>
					<text class="modal-close" @tap="closeModals">×</text>
				</view>
				<view class="modal-body">
					<text class="modal-tip">督导：{{ currentUser?.user_name }}（{{ currentUser?.user_on }}）</text>

					<view class="roles-row" style="margin-top: 16rpx;">
						<text class="roles-label">负责学院：</text>
					</view>
					<view class="checkbox-list">
						<checkbox-group @change="onScopeCollegeChange">
							<label class="checkbox-item" v-for="c in colleges" :key="c.id">
								<checkbox :value="String(c.id)" :checked="selectedCollegeIds.includes(c.id)" />
								<text class="checkbox-text">{{ c.college_name }}</text>
							</label>
						</checkbox-group>
					</view>

					<view class="roles-row" style="margin-top: 16rpx;">
						<text class="roles-label">负责教研组：</text>
					</view>
					<view class="checkbox-list">
						<checkbox-group @change="onScopeRoomChange">
							<label class="checkbox-item" v-for="r in researchRooms" :key="r.id">
								<checkbox :value="String(r.id)" :checked="selectedRoomIds.includes(r.id)" />
								<text class="checkbox-text">{{ r.room_name }}</text>
							</label>
						</checkbox-group>
					</view>

					<button class="submit-btn" @tap="submitScope">保存范围</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'user-management',
	data() {
		return {
			// 22300417陈俫坤开发
			keyword: '',
			page: 0,
			limit: 20,
			users: [],
			roles: [],
			loading: false,

			showResetModal: false,
			showRoleModal: false,
			showScopeModal: false,
			currentUser: null,
			newPassword: '',
			selectedRoleIds: [],
			// 22300417陈俫坤开发：督导范围配置数据
			colleges: [],
			researchRooms: [],
			selectedCollegeIds: [],
			selectedRoomIds: [],
			isSchoolAdmin: false
		};
	},
	onLoad() {
		this.refresh();
		this.loadRoles();
		this.loadMeRole();
	},
	methods: {
		async loadMeRole() {
			try {
				const me = uni.getStorageSync('userInfo') || {};
				this.isSchoolAdmin = Array.isArray(me.roles_code) && me.roles_code.includes('school_admin');
			} catch (e) {
				this.isSchoolAdmin = false;
			}
		},
		isSupervisorUser(u) {
			const codes = (u && u.role_codes) ? u.role_codes : [];
			return Array.isArray(codes) && codes.includes('supervisor');
		},
		async openScopeModal(u) {
			this.currentUser = u;
			this.showScopeModal = true;
			await this.loadColleges();
			await this.loadResearchRooms();
			await this.loadScope(u);
		},
		async loadColleges() {
			try {
				const res = await request({ url: '/org/colleges', method: 'GET', params: { skip: 0, limit: 200 } });
				this.colleges = (res && res.list) ? res.list : [];
			} catch (e) {
				this.colleges = [];
			}
		},
		async loadResearchRooms() {
			try {
				const res = await request({ url: '/org/research-rooms', method: 'GET', params: { skip: 0, limit: 200 } });
				this.researchRooms = (res && res.list) ? res.list : [];
			} catch (e) {
				this.researchRooms = [];
			}
		},
		async loadScope(u) {
			try {
				const res = await request({ url: `/user/supervisor/${u.id}/scope`, method: 'GET' });
				this.selectedCollegeIds = Array.isArray(res.college_ids) ? res.college_ids : [];
				this.selectedRoomIds = Array.isArray(res.research_room_ids) ? res.research_room_ids : [];
			} catch (e) {
				this.selectedCollegeIds = [];
				this.selectedRoomIds = [];
			}
		},
		onScopeCollegeChange(e) {
			const values = (e && e.detail && e.detail.value) ? e.detail.value : [];
			this.selectedCollegeIds = values.map(v => parseInt(v, 10)).filter(n => !Number.isNaN(n));
		},
		onScopeRoomChange(e) {
			const values = (e && e.detail && e.detail.value) ? e.detail.value : [];
			this.selectedRoomIds = values.map(v => parseInt(v, 10)).filter(n => !Number.isNaN(n));
		},
		async submitScope() {
			if (!this.currentUser) return;
			try {
				await request({
					url: `/user/supervisor/${this.currentUser.id}/scope`,
					method: 'PUT',
					data: {
						college_ids: this.selectedCollegeIds,
						research_room_ids: this.selectedRoomIds
					}
				});
				uni.showToast({ title: '保存成功', icon: 'success' });
				this.closeModals();
			} catch (e) {
				// request.js 已统一 toast
			}
		},
		// 22300417陈俫坤开发：用户管理（列表/重置密码/分配角色）功能
		handleKeywordInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.keyword = value;
		},
		reset() {
			this.keyword = '';
			this.page = 0;
			this.refresh();
		},
		async refresh() {
			this.loading = true;
			try {
				// 22300417陈俫坤开发：拉取用户列表
				const res = await request({
					url: '/user/list',
					method: 'GET',
					params: {
						skip: this.page * this.limit,
						limit: this.limit
					}
				});
				const items = res && res.items ? res.items : [];
				this.users = this.applyKeywordFilter(items);
			} catch (e) {
				this.users = [];
			} finally {
				this.loading = false;
			}
		},
		applyKeywordFilter(items) {
			const kw = (this.keyword || '').trim();
			if (!kw) return items;
			return items.filter(u => {
				const on = String(u.user_on || '');
				const name = String(u.user_name || '');
				return on.includes(kw) || name.includes(kw);
			});
		},
		prevPage() {
			if (this.page <= 0) return;
			this.page -= 1;
			this.refresh();
		},
		nextPage() {
			this.page += 1;
			this.refresh();
		},
		async loadRoles() {
			try {
				// 22300417陈俫坤开发：拉取角色列表（用于分配角色）
				const res = await request({
					url: '/auth/roles',
					method: 'GET',
					params: { skip: 0, limit: 200 }
				});
				this.roles = (res && res.list) ? res.list : [];
			} catch (e) {
				this.roles = [];
			}
		},
		openResetPassword(u) {
			this.currentUser = u;
			this.newPassword = '';
			this.showResetModal = true;
		},
		openAssignRoles(u) {
			this.currentUser = u;
			// 22300417陈俫坤开发：后端 /user/list 已返回 role_ids，支持自动回显
			this.selectedRoleIds = Array.isArray(u.role_ids) ? u.role_ids : this.guessSelectedRoleIds(u);
			this.showRoleModal = true;
		},
		guessSelectedRoleIds(u) {
			// 后端 /user/list 返回的是角色名称数组（roles），这里无法直接映射 role_id。
			// 默认不预选，用户手动选择后保存。
			return [];
		},
		handleNewPasswordInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.newPassword = value;
		},
		async submitResetPassword() {
			if (!this.currentUser) return;
			const pwd = (this.newPassword || '').trim();
			if (!pwd) {
				uni.showToast({ title: '请输入新密码', icon: 'none' });
				return;
			}
			try {
				// 22300417陈俫坤开发：重置用户密码
				await request({
					url: '/user/reset-password',
					method: 'POST',
					params: { user_id: this.currentUser.id, new_password: pwd }
				});
				uni.showToast({ title: '重置成功', icon: 'success' });
				this.closeModals();
			} catch (e) {
				// request.js 已统一 toast
			}
		},
		onRoleCheckboxChange(e) {
			const values = (e && e.detail && e.detail.value) ? e.detail.value : [];
			this.selectedRoleIds = values.map(v => parseInt(v, 10)).filter(n => !Number.isNaN(n));
		},
		async submitAssignRoles() {
			if (!this.currentUser) return;
			try {
				// 22300417陈俫坤开发：给用户分配角色
				await request({
					url: `/auth/user/${this.currentUser.id}/roles`,
					method: 'POST',
					data: this.selectedRoleIds
				});
				uni.showToast({ title: '保存成功', icon: 'success' });
				this.closeModals();
				this.refresh();
			} catch (e) {
				// request.js 已统一 toast
			}
		},
		closeModals() {
			this.showResetModal = false;
			this.showRoleModal = false;
			this.showScopeModal = false;
			this.currentUser = null;
			this.newPassword = '';
			this.selectedRoleIds = [];
			this.selectedCollegeIds = [];
			this.selectedRoomIds = [];
		}
	}
};
</script>

<style scoped>
.admin-container {
	background-color: #F5F7FA;
	min-height: 100vh;
}

.page-header {
	background-color: #3E5C76;
	color: #FFFFFF;
	padding: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.page-title {
	font-size: 36rpx;
	font-weight: bold;
}

.search-section {
	padding: 20rpx 30rpx;
	background-color: #FFFFFF;
}

.search-input {
	display: flex;
	align-items: center;
	background-color: #F5F7FA;
	border-radius: 40rpx;
	padding: 0 20rpx;
}

.search-icon {
	font-size: 28rpx;
	color: #999999;
	margin-right: 15rpx;
}

.input {
	flex: 1;
	height: 80rpx;
	font-size: 28rpx;
	color: #333333;
}

.placeholder {
	color: #C0C4CC;
}

.filter-actions {
	display: flex;
	gap: 20rpx;
	margin-top: 16rpx;
}

.search-btn,
.reset-btn {
	flex: 1;
	height: 72rpx;
	line-height: 72rpx;
	border-radius: 36rpx;
	font-size: 28rpx;
}

.search-btn {
	background-color: #3E5C76;
	color: #FFFFFF;
}

.reset-btn {
	background-color: #FFFFFF;
	color: #3E5C76;
	border: 2rpx solid #3E5C76;
}

.search-btn::after,
.reset-btn::after {
	border: none;
}

.list-section {
	padding: 0 30rpx;
	margin-top: 20rpx;
}

.list-card {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.user-item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 25rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.user-item:last-child {
	margin-bottom: 0;
}

.item-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12rpx;
}

.user-name {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
}

.user-on {
	font-size: 24rpx;
	color: #666666;
}

.item-info {
	display: flex;
	gap: 20rpx;
	flex-wrap: wrap;
	margin-bottom: 12rpx;
}

.info-text {
	font-size: 26rpx;
	color: #666666;
}

.roles-row {
	display: flex;
	flex-wrap: wrap;
	gap: 10rpx;
	margin-bottom: 16rpx;
}

.roles-label {
	font-size: 26rpx;
	color: #666666;
}

.roles-value {
	font-size: 26rpx;
	color: #333333;
}

.item-actions {
	display: flex;
	gap: 16rpx;
}

.action-btn {
	flex: 1;
	height: 70rpx;
	line-height: 70rpx;
	border-radius: 10rpx;
	font-size: 26rpx;
	background-color: #FFFFFF;
	color: #3E5C76;
}

.action-btn.primary {
	background-color: #3E5C76;
	color: #FFFFFF;
}

.action-btn::after {
	border: none;
}

.empty-state {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 100rpx 0;
	text-align: center;
	color: #999999;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.empty-icon {
	font-size: 80rpx;
	margin-bottom: 20rpx;
}

.empty-text {
	font-size: 32rpx;
	margin-bottom: 10rpx;
}

.empty-hint {
	font-size: 26rpx;
}

.pagination {
	display: flex;
	justify-content: center;
	align-items: center;
	margin: 30rpx 0;
	gap: 30rpx;
}

.page-btn {
	height: 72rpx;
	background-color: #FFFFFF;
	color: #3E5C76;
	font-size: 28rpx;
	border-radius: 36rpx;
	padding: 0 40rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.page-btn::after {
	border: none;
}

.page-btn:disabled {
	color: #C0C4CC;
	background-color: #F5F7FA;
}

.page-info {
	font-size: 28rpx;
	color: #666666;
}

.modal {
	position: fixed;
	top: 0;
	left: 0;
	width: 100%;
	height: 100%;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
	z-index: 9999;
}

.modal-content {
	background-color: #FFFFFF;
	border-radius: 20rpx;
	width: 86%;
	max-width: 560rpx;
	box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.2);
}

.modal-header {
	padding: 25rpx 30rpx;
	border-bottom: 2rpx solid #F5F7FA;
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.modal-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.modal-close {
	font-size: 40rpx;
	color: #C0C4CC;
	padding: 8rpx;
}

.modal-body {
	padding: 24rpx 30rpx 30rpx;
}

.modal-tip {
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 16rpx;
}

.modal-input {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 20rpx;
}

.checkbox-list {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 16rpx;
	max-height: 520rpx;
	overflow: auto;
	margin-bottom: 20rpx;
}

.checkbox-item {
	display: flex;
	align-items: center;
	gap: 14rpx;
	padding: 14rpx 10rpx;
}

.checkbox-text {
	font-size: 26rpx;
	color: #333333;
}

.submit-btn {
	height: 78rpx;
	line-height: 78rpx;
	border-radius: 12rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 28rpx;
}

.submit-btn::after {
	border: none;
}
</style>