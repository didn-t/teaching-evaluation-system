<!--
  22300417陈俫坤开发
  页面用途：系统管理-角色管理（角色增删改查、分配权限）
  编写日期：2026-01-01
-->
<template>
	<view class="admin-container">
		<view class="page-header">
			<text class="page-title">角色管理</text>
		</view>

		<view class="toolbar">
			<button class="primary-btn" @tap="openCreateRole">新增角色</button>
			<button class="ghost-btn" @tap="refresh">刷新</button>
		</view>

		<view class="list-section">
			<view v-if="roles.length" class="list-card">
				<view class="role-item" v-for="r in roles" :key="r.id">
					<view class="item-header">
						<text class="item-title">{{ r.name || r.role_name }}</text>
						<text class="item-sub">{{ r.code || r.role_code }}</text>
					</view>
					<view class="item-info">
						<text class="info-text">状态：{{ (r.status === 1 || r.status === '1') ? '启用' : '禁用' }}</text>
						<text class="info-text">描述：{{ r.description || '-' }}</text>
					</view>
					<view class="item-actions">
						<button class="action-btn" @tap="openEditRole(r)">编辑</button>
						<button class="action-btn" @tap="openAssignPermissions(r)">分配权限</button>
						<button class="action-btn danger" @tap="deleteRole(r)">删除</button>
					</view>
				</view>
			</view>
			<view v-else class="empty-state">
				<text class="empty-icon">🧩</text>
				<text class="empty-text">暂无角色</text>
				<text class="empty-hint">请确认你使用 school001 登录</text>
			</view>
		</view>

		<!-- 新增/编辑角色弹窗 -->
		<view class="modal" v-if="showRoleModal" @tap="closeModals">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">{{ roleFormMode === 'create' ? '新增角色' : '编辑角色' }}</text>
					<text class="modal-close" @tap="closeModals">×</text>
				</view>
				<view class="modal-body">
					<input :value="roleForm.name" placeholder="角色名称" class="modal-input" placeholder-class="placeholder" @input="onRoleNameInput" />
					<input :value="roleForm.code" placeholder="角色编码（如 teacher）" class="modal-input" placeholder-class="placeholder" @input="onRoleCodeInput" />
					<input :value="roleForm.description" placeholder="描述（可选）" class="modal-input" placeholder-class="placeholder" @input="onRoleDescInput" />
					<picker mode="selector" :range="['启用', '禁用']" :value="roleForm.status === 1 ? 0 : 1" @change="onRoleStatusChange">
						<view class="picker">状态：{{ roleForm.status === 1 ? '启用' : '禁用' }}</view>
					</picker>
					<button class="submit-btn" @tap="submitRole">保存</button>
				</view>
			</view>
		</view>

		<!-- 分配权限弹窗 -->
		<view class="modal" v-if="showPermModal" @tap="closeModals">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">分配权限</text>
					<text class="modal-close" @tap="closeModals">×</text>
				</view>
				<view class="modal-body">
					<text class="modal-tip">角色：{{ currentRole?.role_name || currentRole?.name }}（{{ currentRole?.role_code || currentRole?.code }}）</text>
					<!-- 22300417陈俫坤开发：权限搜索 + 分组全选/清空，便于细化分配 -->
					<view class="perm-toolbar">
						<view class="perm-search">
							<text class="search-icon">🔍</text>
							<input
								:value="permSearch"
								placeholder="搜索权限码/名称"
								class="perm-search-input"
								placeholder-class="placeholder"
								@input="onPermSearchInput"
							/>
						</view>
						<view class="perm-toolbar-actions">
							<button class="perm-action-btn" @tap="selectAllVisible">全选</button>
							<button class="perm-action-btn ghost" @tap="clearAll">清空</button>
						</view>
					</view>
					<view class="checkbox-list">
						<checkbox-group @change="onPermCheckboxChange">
							<view class="perm-group" v-for="g in permissionGroups" :key="g.key">
								<view class="perm-group-header">
									<text class="perm-group-title">{{ g.title }}（{{ g.items.length }}）</text>
									<view class="perm-group-actions">
										<button class="perm-action-btn" @tap.stop="selectGroup(g.key)">全选</button>
										<button class="perm-action-btn ghost" @tap.stop="clearGroup(g.key)">清空</button>
									</view>
								</view>
								<label class="checkbox-item" v-for="p in g.items" :key="p.id">
									<checkbox :value="String(p.id)" :checked="selectedPermissionIds.includes(p.id)" />
									<text class="checkbox-text">{{ p.name || p.permission_name }}（{{ p.code || p.permission_code }}）</text>
								</label>
							</view>
						</checkbox-group>
					</view>
					<button class="submit-btn" @tap="submitAssignPermissions">保存权限</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
// 22300417陈俫坤开发
import { request } from '../../common/request.js';

export default {
	name: 'role-management',
	data() {
		return {
			// 22300417陈俫坤开发
			roles: [],
			permissions: [],
			loading: false,

			showRoleModal: false,
			roleFormMode: 'create',
			roleForm: {
				id: null,
				name: '',
				code: '',
				description: '',
				status: 1
			},

			showPermModal: false,
			currentRole: null,
			selectedPermissionIds: [],
			permSearch: ''
		};
	},
	computed: {
		permissionGroups() {
			// 22300417陈俫坤开发：按权限码前缀分组（如 auth/org/evaluation/system），并支持搜索过滤
			const kw = String(this.permSearch || '').trim().toLowerCase();
			const list = (this.permissions || []).filter(p => {
				if (!kw) return true;
				const code = String(p.code || p.permission_code || '').toLowerCase();
				const name = String(p.name || p.permission_name || '').toLowerCase();
				return code.includes(kw) || name.includes(kw);
			});

			const map = {};
			list.forEach(p => {
				const code = String(p.code || p.permission_code || '');
				const key = code.includes(':') ? code.split(':')[0] : 'other';
				if (!map[key]) map[key] = [];
				map[key].push(p);
			});

			const keys = Object.keys(map).sort();
			return keys.map(k => ({
				key: k,
				title: k === 'other' ? '其他' : k,
				items: map[k].sort((a, b) => {
					const ac = String(a.code || a.permission_code || '');
					const bc = String(b.code || b.permission_code || '');
					return ac.localeCompare(bc);
				})
			}));
		}
	},
	onLoad() {
		this.refresh();
		this.loadPermissions();
	},
	methods: {
		async refresh() {
			this.loading = true;
			try {
				const res = await request({
					url: '/auth/roles',
					method: 'GET',
					params: { skip: 0, limit: 200 }
				});
				this.roles = (res && res.list) ? res.list : [];
			} catch (e) {
				this.roles = [];
			} finally {
				this.loading = false;
			}
		},
		async loadPermissions() {
			try {
				const res = await request({
					url: '/auth/permissions',
					method: 'GET',
					params: { skip: 0, limit: 500 }
				});
				this.permissions = (res && res.list) ? res.list : [];
			} catch (e) {
				this.permissions = [];
			}
		},
		openCreateRole() {
			this.roleFormMode = 'create';
			this.roleForm = { id: null, name: '', code: '', description: '', status: 1 };
			this.showRoleModal = true;
		},
		openEditRole(r) {
			this.roleFormMode = 'edit';
			this.roleForm = {
				id: r.id,
				name: r.role_name || r.name || '',
				code: r.role_code || r.code || '',
				description: r.description || '',
				status: (r.status === undefined || r.status === null) ? 1 : r.status
			};
			this.showRoleModal = true;
		},
		onRoleNameInput(e) {
			this.roleForm.name = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onRoleCodeInput(e) {
			this.roleForm.code = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onRoleDescInput(e) {
			this.roleForm.description = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onRoleStatusChange(e) {
			const idx = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			this.roleForm.status = idx === 0 ? 1 : 0;
		},
		async submitRole() {
			const name = (this.roleForm.name || '').trim();
			const code = (this.roleForm.code || '').trim();
			if (!name || !code) {
				uni.showToast({ title: '请填写名称和编码', icon: 'none' });
				return;
			}
			try {
				if (this.roleFormMode === 'create') {
					await request({
						url: '/auth/role',
						method: 'POST',
						params: {
							name,
							code,
							description: this.roleForm.description || '',
							status: this.roleForm.status
						}
					});
				} else {
					await request({
						url: `/auth/role/${this.roleForm.id}`,
						method: 'PUT',
						params: {
							name,
							description: this.roleForm.description || '',
							status: this.roleForm.status
						}
					});
				}
				uni.showToast({ title: '保存成功', icon: 'success' });
				this.closeModals();
				this.refresh();
			} catch (e) {
				// request.js 已统一 toast
			}
		},
		deleteRole(r) {
			uni.showModal({
				title: '确认删除',
				content: `确定删除角色 ${r.role_name || r.name} 吗？`,
				success: async (res) => {
					if (!res.confirm) return;
					try {
						await request({ url: `/auth/role/${r.id}`, method: 'DELETE' });
						uni.showToast({ title: '删除成功', icon: 'success' });
						this.refresh();
					} catch (e) {
						// request.js 已统一 toast
					}
				}
			});
		},
		async openAssignPermissions(r) {
			this.currentRole = r;
			this.selectedPermissionIds = [];
			this.permSearch = '';
			this.showPermModal = true;
			if (!this.permissions.length) {
				await this.loadPermissions();
			}
			try {
				const res = await request({
					url: `/auth/role/${r.id}/permissions`,
					method: 'GET'
				});
				const permList = Array.isArray(res) ? res : (res && res.list ? res.list : res);
				const ids = Array.isArray(permList) ? permList.map(p => p.id).filter(Boolean) : [];
				this.selectedPermissionIds = ids;
			} catch (e) {
				this.selectedPermissionIds = [];
			}
		},
		onPermCheckboxChange(e) {
			const values = (e && e.detail && e.detail.value) ? e.detail.value : [];
			this.selectedPermissionIds = values.map(v => parseInt(v, 10)).filter(n => !Number.isNaN(n));
		},
		onPermSearchInput(e) {
			this.permSearch = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		selectAllVisible() {
			// 22300417陈俫坤开发：全选当前搜索结果范围内的权限
			const ids = [];
			this.permissionGroups.forEach(g => g.items.forEach(p => ids.push(p.id)));
			this.selectedPermissionIds = Array.from(new Set(ids));
		},
		clearAll() {
			this.selectedPermissionIds = [];
		},
		selectGroup(groupKey) {
			// 22300417陈俫坤开发：分组全选（只作用于当前搜索过滤后的分组）
			const g = this.permissionGroups.find(x => x.key === groupKey);
			if (!g) return;
			const set = new Set(this.selectedPermissionIds);
			g.items.forEach(p => set.add(p.id));
			this.selectedPermissionIds = Array.from(set);
		},
		clearGroup(groupKey) {
			// 22300417陈俫坤开发：分组清空（只作用于当前搜索过滤后的分组）
			const g = this.permissionGroups.find(x => x.key === groupKey);
			if (!g) return;
			const remove = new Set(g.items.map(p => p.id));
			this.selectedPermissionIds = this.selectedPermissionIds.filter(id => !remove.has(id));
		},
		async submitAssignPermissions() {
			if (!this.currentRole) return;
			try {
				await request({
					url: `/auth/role/${this.currentRole.id}/permissions`,
					method: 'POST',
					data: this.selectedPermissionIds
				});
				uni.showToast({ title: '保存成功', icon: 'success' });
				this.closeModals();
			} catch (e) {
				// request.js 已统一 toast
			}
		},
		closeModals() {
			this.showRoleModal = false;
			this.showPermModal = false;
			this.currentRole = null;
			this.selectedPermissionIds = [];
			this.permSearch = '';
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

.toolbar {
	padding: 20rpx 30rpx;
	background-color: #FFFFFF;
	display: flex;
	gap: 20rpx;
}

.primary-btn,
.ghost-btn {
	flex: 1;
	height: 72rpx;
	line-height: 72rpx;
	border-radius: 36rpx;
	font-size: 28rpx;
}

.primary-btn {
	background-color: #3E5C76;
	color: #FFFFFF;
}

.ghost-btn {
	background-color: #FFFFFF;
	color: #3E5C76;
	border: 2rpx solid #3E5C76;
}

.primary-btn::after,
.ghost-btn::after,
.action-btn::after,
.submit-btn::after {
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

.role-item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 25rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.role-item:last-child {
	margin-bottom: 0;
}

.item-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12rpx;
}

.item-title {
	font-size: 30rpx;
	font-weight: bold;
	color: #333333;
}

.item-sub {
	font-size: 24rpx;
	color: #666666;
}

.item-info {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
	margin-bottom: 16rpx;
}

.info-text {
	font-size: 26rpx;
	color: #666666;
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

.action-btn.danger {
	color: #F56C6C;
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

.picker {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 20rpx;
}

.placeholder {
	color: #C0C4CC;
}

.checkbox-list {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 16rpx;
	max-height: 520rpx;
	overflow: auto;
	margin-bottom: 20rpx;
}

.perm-toolbar {
	margin-top: 16rpx;
	margin-bottom: 16rpx;
}

.perm-search {
	display: flex;
	align-items: center;
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 0 16rpx;
	margin-bottom: 12rpx;
}

.search-icon {
	font-size: 26rpx;
	color: #999999;
	margin-right: 10rpx;
}

.perm-search-input {
	flex: 1;
	height: 72rpx;
	font-size: 26rpx;
	color: #333333;
}

.perm-toolbar-actions {
	display: flex;
	gap: 16rpx;
}

.perm-action-btn {
	flex: 1;
	height: 64rpx;
	line-height: 64rpx;
	border-radius: 10rpx;
	font-size: 24rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
}

.perm-action-btn.ghost {
	background-color: #FFFFFF;
	color: #3E5C76;
	border: 2rpx solid #3E5C76;
}

.perm-action-btn::after {
	border: none;
}

.perm-group {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 14rpx;
	margin-bottom: 16rpx;
}

.perm-group:last-child {
	margin-bottom: 0;
}

.perm-group-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 10rpx;
}

.perm-group-title {
	font-size: 26rpx;
	font-weight: bold;
	color: #333333;
}

.perm-group-actions {
	display: flex;
	gap: 12rpx;
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
</style>
