<!--
  22300417陈俫坤开发
  页面用途：系统管理-权限管理（权限增删改查）
  编写日期：2026-01-01
-->
<template>
	<view class="admin-container">
		<view class="page-header">
			<text class="page-title">权限管理</text>
		</view>

		<view class="toolbar">
			<button class="primary-btn" @tap="openCreatePermission">新增权限</button>
			<button class="ghost-btn" @tap="refresh">刷新</button>
		</view>

		<view class="list-section">
			<view v-if="permissions.length" class="list-card">
				<view class="perm-item" v-for="p in permissions" :key="p.id">
					<view class="item-header">
						<text class="item-title">{{ p.name || p.permission_name }}</text>
						<text class="item-sub">{{ p.code || p.permission_code }}</text>
					</view>
					<view class="item-info">
						<text class="info-text">类型：{{ p.type || p.permission_type }}</text>
						<text class="info-text">父ID：{{ p.parent_id ?? '-' }}</text>
					</view>
					<view class="item-actions">
						<button class="action-btn" @tap="openEditPermission(p)">编辑</button>
						<button class="action-btn danger" @tap="deletePermission(p)">删除</button>
					</view>
				</view>
			</view>
			<view v-else class="empty-state">
				<text class="empty-icon">🔐</text>
				<text class="empty-text">暂无权限</text>
				<text class="empty-hint">请确认你使用 school001 登录</text>
			</view>
		</view>

		<!-- 新增/编辑权限弹窗 -->
		<view class="modal" v-if="showModal" @tap="closeModals">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">{{ formMode === 'create' ? '新增权限' : '编辑权限' }}</text>
					<text class="modal-close" @tap="closeModals">×</text>
				</view>
				<view class="modal-body">
					<input :value="form.code" placeholder="权限编码（如 system:config）" class="modal-input" placeholder-class="placeholder" @input="onCodeInput" />
					<input :value="form.name" placeholder="权限名称" class="modal-input" placeholder-class="placeholder" @input="onNameInput" />
					<input :value="form.type" placeholder="权限类型(1-查看 2-操作 3-导出 4-配置)" class="modal-input" placeholder-class="placeholder" @input="onTypeInput" />
					<input :value="form.parent_id" placeholder="父权限ID（可空）" class="modal-input" placeholder-class="placeholder" @input="onParentIdInput" />
					<input :value="form.description" placeholder="描述（可选）" class="modal-input" placeholder-class="placeholder" @input="onDescInput" />
					<button class="submit-btn" @tap="submitPermission">保存</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
// 22300417陈俫坤开发
import { request } from '../../common/request.js';

export default {
	name: 'permission-management',
	data() {
		return {
			// 22300417陈俫坤开发
			permissions: [],
			showModal: false,
			formMode: 'create',
			form: {
				id: null,
				code: '',
				name: '',
				type: '1',
				parent_id: '',
				description: ''
			}
		};
	},
	onLoad() {
		this.refresh();
	},
	methods: {
		async refresh() {
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
		openCreatePermission() {
			this.formMode = 'create';
			this.form = { id: null, code: '', name: '', type: '1', parent_id: '', description: '' };
			this.showModal = true;
		},
		openEditPermission(p) {
			this.formMode = 'edit';
			this.form = {
				id: p.id,
				code: p.permission_code || p.code || '',
				name: p.permission_name || p.name || '',
				type: String(p.permission_type ?? p.type ?? '1'),
				parent_id: (p.parent_id === null || p.parent_id === undefined) ? '' : String(p.parent_id),
				description: p.permission_description || p.description || ''
			};
			this.showModal = true;
		},
		onCodeInput(e) {
			this.form.code = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onNameInput(e) {
			this.form.name = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onTypeInput(e) {
			this.form.type = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '1';
		},
		onParentIdInput(e) {
			this.form.parent_id = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onDescInput(e) {
			this.form.description = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		async submitPermission() {
			const code = (this.form.code || '').trim();
			const name = (this.form.name || '').trim();
			const type = parseInt(this.form.type, 10);
			const parentId = (this.form.parent_id || '').trim();
			if (!code || !name || Number.isNaN(type)) {
				uni.showToast({ title: '请填写编码/名称/类型', icon: 'none' });
				return;
			}
			try {
				if (this.formMode === 'create') {
					await request({
						url: '/auth/permission',
						method: 'POST',
						params: {
							code,
							name,
							type,
							parent_id: parentId ? parseInt(parentId, 10) : null,
							description: this.form.description || '',
							sort: 0
						}
					});
				} else {
					await request({
						url: `/auth/permission/${this.form.id}`,
						method: 'PUT',
						params: {
							name,
							type,
							parent_id: parentId ? parseInt(parentId, 10) : null,
							sort: 0,
							description: this.form.description || ''
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
		deletePermission(p) {
			uni.showModal({
				title: '确认删除',
				content: `确定删除权限 ${p.permission_name || p.name} 吗？`,
				success: async (res) => {
					if (!res.confirm) return;
					try {
						await request({ url: `/auth/permission/${p.id}`, method: 'DELETE' });
						uni.showToast({ title: '删除成功', icon: 'success' });
						this.refresh();
					} catch (e) {
						// request.js 已统一 toast
					}
				}
			});
		},
		closeModals() {
			this.showModal = false;
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

.perm-item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 25rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.perm-item:last-child {
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

.modal-input {
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

.submit-btn {
	height: 78rpx;
	line-height: 78rpx;
	border-radius: 12rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 28rpx;
}
</style>
