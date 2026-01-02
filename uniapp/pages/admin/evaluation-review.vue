<template>
	<view class="admin-container">
		<view class="page-header">
			<text class="page-title">评教审核</text>
		</view>

		<view class="toolbar">
			<button class="primary-btn" @tap="refresh">刷新</button>
			<button class="ghost-btn" @tap="reset">重置</button>
		</view>

		<view class="list-section">
			<view v-if="list.length" class="list-card">
				<view class="item" v-for="ev in list" :key="ev.id">
					<view class="item-header">
						<text class="item-title">{{ ev.timetable?.course_name || '未知课程' }}</text>
						<text class="item-tag">待审核</text>
					</view>
					<view class="item-info">
						<text class="info-text">评教编号：{{ ev.evaluation_no }}</text>
						<text class="info-text">授课教师：{{ ev.teach_teacher_name || '-' }}</text>
						<text class="info-text">听课教师：{{ ev.listen_teacher_name || '-' }}</text>
						<text class="info-text">听课日期：{{ ev.listen_date || '-' }}</text>
						<text class="info-text">总分：{{ ev.total_score }}</text>
					</view>
					<view class="item-actions">
						<button class="action-btn" @tap="openReview(ev, 1)">通过</button>
						<button class="action-btn danger" @tap="openReview(ev, 0)">作废</button>
					</view>
				</view>
			</view>

			<view v-else class="empty-state">
				<text class="empty-icon">🧾</text>
				<text class="empty-text">暂无待审核评教</text>
				<text class="empty-hint">如提示无权限，请用 school_admin/college_admin 账号登录并初始化权限</text>
			</view>
		</view>

		<view class="pagination" v-if="list.length">
			<button class="page-btn" :disabled="page <= 1" @tap="prevPage">上一页</button>
			<text class="page-info">{{ page }}</text>
			<button class="page-btn" :disabled="list.length < pageSize" @tap="nextPage">下一页</button>
		</view>

		<!-- 审核弹窗 -->
		<view class="modal" v-if="showModal" @tap="closeModal">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">{{ reviewStatus === 1 ? '通过评教' : '作废评教' }}</text>
					<text class="modal-close" @tap="closeModal">×</text>
				</view>
				<view class="modal-body">
					<text class="modal-tip">课程：{{ current?.timetable?.course_name || '-' }}</text>
					<textarea
						:value="reviewComment"
						placeholder="审核意见（可选）"
						class="modal-textarea"
						placeholder-class="placeholder"
						@input="onCommentInput"
					/>
					<button class="submit-btn" @tap="submitReview">确认提交</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'evaluation-review',
	data() {
		return {
			// 22300417陈俫坤开发：评教审核页数据
			list: [],
			page: 1,
			pageSize: 10,
			loading: false,

			showModal: false,
			current: null,
			reviewStatus: 1,
			reviewComment: ''
		};
	},
	onLoad() {
		this.refresh();
	},
	methods: {
		reset() {
			this.page = 1;
			this.refresh();
		},
		async refresh() {
			this.loading = true;
			try {
				// 22300417陈俫坤开发：拉取待审核评教列表
				const res = await request({
					url: '/eval/review/pending',
					method: 'GET',
					params: { page: this.page, page_size: this.pageSize }
				});
				this.list = (res && res.list) ? res.list : [];
			} catch (e) {
				this.list = [];
			} finally {
				this.loading = false;
			}
		},
		prevPage() {
			if (this.page <= 1) return;
			this.page -= 1;
			this.refresh();
		},
		nextPage() {
			this.page += 1;
			this.refresh();
		},
		openReview(ev, status) {
			this.current = ev;
			this.reviewStatus = status;
			this.reviewComment = '';
			this.showModal = true;
		},
		closeModal() {
			this.showModal = false;
			this.current = null;
			this.reviewComment = '';
		},
		onCommentInput(e) {
			this.reviewComment = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : '';
		},
		async submitReview() {
			if (!this.current) return;
			try {
				// 22300417陈俫坤开发：提交审核结果（status: 1通过 / 0驳回）
				await request({
					url: `/eval/${this.current.id}/review`,
					method: 'PUT',
					data: {
						status: this.reviewStatus,
						review_comment: (this.reviewComment || '').trim() || null
					}
				});
				uni.showToast({ title: '提交成功', icon: 'success' });
				this.closeModal();
				this.refresh();
			} catch (e) {
				// request.js 已统一 toast
			}
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
.page-btn::after,
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

.item-tag {
	font-size: 24rpx;
	color: #FFFFFF;
	background-color: #E6A23C;
	padding: 6rpx 14rpx;
	border-radius: 20rpx;
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

.modal-textarea {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 20rpx;
	min-height: 180rpx;
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