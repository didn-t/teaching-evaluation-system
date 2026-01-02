<template>
	<view class="admin-container">
		<view class="page-header">
			<text class="page-title">学院管理</text>
		</view>

		<view class="toolbar">
			<button class="primary-btn" :disabled="!canEdit" @tap="openCreate">新增学院</button>
			<button class="ghost-btn" @tap="refresh">刷新</button>
		</view>

		<view class="list-section">
			<view v-if="list.length" class="list-card">
				<view class="item" v-for="c in list" :key="c.id">
					<view class="item-header">
						<text class="item-title">{{ c.college_name }}</text>
						<text class="item-sub">{{ c.college_code }}</text>
					</view>
					<view class="item-info">
						<text class="info-text">简称：{{ c.short_name || '-' }}</text>
						<text class="info-text">排序：{{ c.sort_order ?? 0 }}</text>
					</view>
					<view class="item-actions" v-if="canEdit">
						<button class="action-btn" @tap="openEdit(c)">编辑</button>
						<button class="action-btn danger" @tap="deleteCollege(c)">删除</button>
					</view>
				</view>
			</view>

			<view v-else class="empty-state">
				<text class="empty-icon">🏫</text>
				<text class="empty-text">暂无学院数据</text>
				<text class="empty-hint">如提示无权限，请使用 school_admin 账号</text>
			</view>
		</view>

		<!-- 新增/编辑弹窗 -->
		<view class="modal" v-if="showModal" @tap="closeModal">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">{{ formMode === 'create' ? '新增学院' : '编辑学院' }}</text>
					<text class="modal-close" @tap="closeModal">×</text>
				</view>
				<view class="modal-body">
					<input :disabled="formMode !== 'create'" :value="form.college_code" placeholder="学院编码（如 CS）" class="modal-input" placeholder-class="placeholder" @input="onCodeInput" />
					<input :value="form.college_name" placeholder="学院名称" class="modal-input" placeholder-class="placeholder" @input="onNameInput" />
					<input :value="form.short_name" placeholder="简称（可选）" class="modal-input" placeholder-class="placeholder" @input="onShortInput" />
					<input :value="String(form.sort_order)" placeholder="排序（数字）" class="modal-input" placeholder-class="placeholder" @input="onSortInput" />
					<button class="submit-btn" @tap="submit">保存</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'college-management',
	data() {
		return {
			// 22300417陈俫坤开发：学院管理页数据
			me: null,
			list: [],
			loading: false,
			showModal: false,
			formMode: 'create',
			form: {
				id: null,
				college_code: '',
				college_name: '',
				short_name: '',
				sort_order: 0
			}
		};
	},
	onLoad() {
		this.init();
	},
	computed: {
		canEdit() {
			const codes = (this.me && this.me.roles_code) ? this.me.roles_code : [];
			return codes.includes('school_admin');
		}
	},
	methods: {
		async init() {
			await this.loadMe();
			await this.refresh();
		},
		async loadMe() {
			try {
				this.me = await request({ url: '/user/me', method: 'GET' });
			} catch (e) {
				this.me = null;
			}
		},
		async refresh() {
			this.loading = true;
			try {
				// 22300417陈俫坤开发：拉取学院列表
				const res = await request({ url: '/org/colleges', method: 'GET', params: { skip: 0, limit: 200 } });
				this.list = (res && res.list) ? res.list : [];
			} catch (e) {
				this.list = [];
			} finally {
				this.loading = false;
			}
		},
		openCreate() {
			this.formMode = 'create';
			this.form = { id: null, college_code: '', college_name: '', short_name: '', sort_order: 0 };
			this.showModal = true;
		},
		openEdit(c) {
			this.formMode = 'edit';
			this.form = {
				id: c.id,
				college_code: c.college_code,
				college_name: c.college_name,
				short_name: c.short_name || '',
				sort_order: c.sort_order ?? 0
			};
			this.showModal = true;
		},
		closeModal() {
			this.showModal = false;
		},
		onCodeInput(e) {
			this.form.college_code = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onNameInput(e) {
			this.form.college_name = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onShortInput(e) {
			this.form.short_name = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onSortInput(e) {
			const v = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '0';
			const n = Number(v);
			this.form.sort_order = Number.isNaN(n) ? 0 : n;
		},
		async submit() {
			if (!this.canEdit) return;
			const code = (this.form.college_code || '').trim();
			const name = (this.form.college_name || '').trim();
			if (!code || !name) {
				uni.showToast({ title: '请填写学院编码和名称', icon: 'none' });
				return;
			}
			try {
				if (this.formMode === 'create') {
					// 22300417陈俫坤开发：新增学院
					await request({
						url: '/org/college',
						method: 'POST',
						data: {
							college_code: code,
							college_name: name,
							short_name: this.form.short_name || null,
							sort_order: this.form.sort_order || 0
						}
					});
				} else {
					// 22300417陈俫坤开发：编辑学院
					await request({
						url: `/org/college/${this.form.id}`,
						method: 'PUT',
						data: {
							college_name: name,
							short_name: this.form.short_name || null,
							sort_order: this.form.sort_order || 0
						}
					});
				}
				uni.showToast({ title: '保存成功', icon: 'success' });
				this.closeModal();
				this.refresh();
			} catch (e) {
				// request.js 已统一 toast
			}
		},
		deleteCollege(c) {
			if (!this.canEdit) return;
			uni.showModal({
				title: '确认删除',
				content: `确定删除学院 ${c.college_name} 吗？`,
				success: async (res) => {
					if (!res.confirm) return;
					try {
						// 22300417陈俫坤开发：删除学院
						await request({ url: `/org/college/${c.id}`, method: 'DELETE' });
						uni.showToast({ title: '删除成功', icon: 'success' });
						this.refresh();
					} catch (e) {
						// request.js 已统一 toast
					}
				}
			});
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

.primary-btn:disabled {
	background-color: #C0C4CC;
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

.item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 25rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.item:last-child {
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
	background-color: #3E5C76;
	color: #FFFFFF;
}

.action-btn.danger {
	background-color: #F56C6C;
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