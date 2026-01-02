<!--
  22300417陈俫坤开发
  页面用途：系统管理-系统配置（查看/新增/修改/删除系统配置项）
  编写日期：2026-01-01
-->
<template>
	<view class="admin-container">
		<view class="page-header">
			<text class="page-title">系统配置</text>
		</view>

		<view class="toolbar">
			<button class="primary-btn" @tap="openCreate">新增配置</button>
			<button class="ghost-btn" @tap="refresh">刷新</button>
		</view>

		<view class="list-section">
			<view v-if="items.length" class="list-card">
				<view class="cfg-item" v-for="c in items" :key="c.key">
					<view class="item-header">
						<text class="item-title">{{ c.key }}</text>
						<text class="item-sub">{{ c.type }}</text>
					</view>
					<view class="item-info">
						<text class="info-text">描述：{{ c.desc || '-' }}</text>
						<text class="info-text">公开：{{ c.is_public ? '是' : '否' }}</text>
					</view>
					<view class="value-box">
						<text class="value-text">{{ c.valueText }}</text>
					</view>
					<view class="item-actions">
						<button class="action-btn" @tap="openEdit(c)">编辑</button>
						<button class="action-btn danger" @tap="deleteConfig(c)">删除</button>
					</view>
				</view>
			</view>
			<view v-else class="empty-state">
				<text class="empty-icon">⚙️</text>
				<text class="empty-text">暂无配置</text>
				<text class="empty-hint">请确认你使用 school001 登录</text>
			</view>
		</view>

		<!-- 新增/编辑弹窗 -->
		<view class="modal" v-if="showModal" @tap="closeModals">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">{{ formMode === 'create' ? '新增配置' : '编辑配置' }}</text>
					<text class="modal-close" @tap="closeModals">×</text>
				</view>
				<view class="modal-body">
					<input :disabled="formMode !== 'create'" :value="form.key" placeholder="配置Key（如 current_academic_year）" class="modal-input" placeholder-class="placeholder" @input="onKeyInput" />
					<picker mode="selector" :range="['string','number','boolean','json']" :value="typeIndex" @change="onTypeChange">
						<view class="picker">类型：{{ form.type }}</view>
					</picker>
					<input :value="form.desc" placeholder="描述（可选）" class="modal-input" placeholder-class="placeholder" @input="onDescInput" />
					<view class="switch-row">
						<text class="switch-label">是否公开</text>
						<switch :checked="form.is_public" @change="onPublicChange" />
					</view>
					<textarea :value="form.valueRaw" placeholder="配置值（根据类型填写，json请填JSON字符串）" class="modal-textarea" placeholder-class="placeholder" @input="onValueInput" />
					<button class="submit-btn" @tap="submit">保存</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
// 22300417陈俫坤开发
import { request } from '../../common/request.js';

export default {
	name: 'system-config',
	data() {
		return {
			// 22300417陈俫坤开发
			items: [],
			showModal: false,
			formMode: 'create',
			form: {
				key: '',
				type: 'string',
				desc: '',
				is_public: false,
				valueRaw: ''
			}
		};
	},
	computed: {
		typeIndex() {
			const types = ['string', 'number', 'boolean', 'json'];
			const idx = types.indexOf(this.form.type);
			return idx >= 0 ? idx : 0;
		}
	},
	onLoad() {
		this.refresh();
	},
	methods: {
		async refresh() {
			try {
				const res = await request({ url: '/config/', method: 'GET' });
				this.items = this.mapConfigObjectToList(res || {});
			} catch (e) {
				this.items = [];
			}
		},
		mapConfigObjectToList(obj) {
			return Object.keys(obj).map((k) => {
				const v = obj[k] || {};
				return {
					key: k,
					value: v.value,
					type: v.type || 'string',
					desc: v.desc || '',
					is_public: !!v.is_public,
					valueText: this.formatValue(v.value)
				};
			});
		},
		formatValue(v) {
			try {
				if (typeof v === 'string') return v;
				return JSON.stringify(v);
			} catch (e) {
				return String(v);
			}
		},
		openCreate() {
			this.formMode = 'create';
			this.form = { key: '', type: 'string', desc: '', is_public: false, valueRaw: '' };
			this.showModal = true;
		},
		openEdit(c) {
			this.formMode = 'edit';
			this.form = {
				key: c.key,
				type: c.type || 'string',
				desc: c.desc || '',
				is_public: !!c.is_public,
				valueRaw: this.formatValue(c.value)
			};
			this.showModal = true;
		},
		onKeyInput(e) {
			this.form.key = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onTypeChange(e) {
			const idx = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			this.form.type = ['string', 'number', 'boolean', 'json'][idx] || 'string';
		},
		onDescInput(e) {
			this.form.desc = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		onPublicChange(e) {
			this.form.is_public = !!(e && e.detail && e.detail.value);
		},
		onValueInput(e) {
			this.form.valueRaw = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		parseValueByType() {
			const raw = this.form.valueRaw;
			if (this.form.type === 'number') {
				const n = Number(raw);
				if (Number.isNaN(n)) throw new Error('number');
				return n;
			}
			if (this.form.type === 'boolean') {
				if (raw === 'true' || raw === '1') return true;
				if (raw === 'false' || raw === '0') return false;
				throw new Error('boolean');
			}
			if (this.form.type === 'json') {
				return raw ? JSON.parse(raw) : {};
			}
			return raw;
		},
		async submit() {
			const key = (this.form.key || '').trim();
			if (!key) {
				uni.showToast({ title: '请输入配置Key', icon: 'none' });
				return;
			}
			let value;
			try {
				value = this.parseValueByType();
			} catch (e) {
				uni.showToast({ title: '配置值格式不正确', icon: 'none' });
				return;
			}
			try {
				await request({
					url: '/config/',
					method: 'POST',
					params: {
						config_key: key,
						config_type: this.form.type,
						config_desc: this.form.desc || '',
						is_public: this.form.is_public
					},
					data: value
				});
				uni.showToast({ title: '保存成功', icon: 'success' });
				this.closeModals();
				this.refresh();
			} catch (e) {
				// request.js 已统一 toast
			}
		},
		deleteConfig(c) {
			uni.showModal({
				title: '确认删除',
				content: `确定删除配置 ${c.key} 吗？`,
				success: async (res) => {
					if (!res.confirm) return;
					try {
						await request({ url: `/config/${encodeURIComponent(c.key)}`, method: 'DELETE' });
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

.cfg-item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 25rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.cfg-item:last-child {
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

.value-box {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 16rpx;
	margin-bottom: 16rpx;
}

.value-text {
	font-size: 26rpx;
	color: #333333;
	word-break: break-all;
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

.modal-textarea {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 20rpx;
	min-height: 180rpx;
}

.picker {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 20rpx;
}

.switch-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.switch-label {
	font-size: 28rpx;
	color: #333333;
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
