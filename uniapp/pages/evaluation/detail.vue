<template>
	<view class="evaluation-detail-container">
		<!-- 课程信息 -->
		<view class="course-info">
			<text class="course-name">{{ evaluationInfo.timetable?.course_name }}</text>
			<text class="status" :class="getStatusClass(evaluationInfo.status)">
				{{ getStatusText(evaluationInfo.status) }}
			</text>
		</view>
		
		<!-- 基本信息 -->
		<view class="basic-info">
			<view class="info-row">
				<text class="info-label">授课教师</text>
				<text class="info-value">{{ evaluationInfo.teach_teacher_name || evaluationInfo.teach_teacher_id }}</text>
			</view>
			
			<view class="info-row">
				<text class="info-label">上课地点</text>
				<text class="info-value">{{ evaluationInfo.timetable?.classroom || evaluationInfo.listen_location }}</text>
			</view>
			
			<view class="info-row">
				<text class="info-label">上课时间</text>
				<text class="info-value">{{ evaluationInfo.timetable?.weekday_text }} {{ evaluationInfo.timetable?.period }}</text>
			</view>
			
			<view class="info-row">
				<text class="info-label">评教日期</text>
				<text class="info-value">{{ evaluationInfo.listen_date }}</text>
			</view>
			
			<view class="info-row">
				<text class="info-label">评教时间</text>
				<text class="info-value">{{ evaluationInfo.submit_time }}</text>
			</view>
			
			<view class="info-row">
				<text class="info-label">听课时长</text>
				<text class="info-value">{{ evaluationInfo.listen_duration }}分钟</text>
			</view>
			
			<view class="info-row">
				<text class="info-label">是否匿名</text>
				<text class="info-value">{{ evaluationInfo.is_anonymous ? '是' : '否' }}</text>
			</view>
			
			<view class="info-row">
				<text class="info-label">评教教师</text>
				<text class="info-value">{{ evaluationInfo.listen_teacher_name || evaluationInfo.listen_teacher_id }}</text>
			</view>
			
			<view class="info-row">
				<text class="info-label">综合评分</text>
				<text class="info-value score">{{ evaluationInfo.total_score }}分 ({{ evaluationInfo.score_level }})</text>
			</view>
		</view>
		
		<!-- 评分详情 -->
		<view class="score-detail">
			<text class="section-title">评分详情</text>
			
			<view class="dimension-score" v-for="(score, key) in evaluationInfo.dimension_scores" :key="key">
				<text class="dimension-name">{{ getDimensionName(key) }}</text>
				<text class="dimension-score-value">{{ score }}分</text>
			</view>
		</view>
		
		<!-- 评价内容 -->
		<view class="evaluation-content">
			<text class="section-title">评价内容</text>
			
			<view class="content-item">
				<text class="content-label">优点</text>
				<text class="content-text">{{ evaluationInfo.advantage_content || '无' }}</text>
			</view>
			
			<view class="content-item">
				<text class="content-label">问题</text>
				<text class="content-text">{{ evaluationInfo.problem_content || '无' }}</text>
			</view>
			
			<view class="content-item">
				<text class="content-label">改进建议</text>
				<text class="content-text">{{ evaluationInfo.improve_suggestion || '无' }}</text>
			</view>
		</view>
		
		<!-- 操作按钮 -->
		<view class="action-buttons" v-if="canDelete">
			<button @tap="deleteEvaluation" class="delete-btn">
				删除评教
			</button>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	name: 'evaluation-detail',
	data() {
		return {
			// 评教详情信息
			evaluationInfo: {},
			// 评教ID
			evaluationId: '',
			// 是否可以删除
			canDelete: true,
			// 加载状态
			loading: false
		};
	},
	onLoad(options) {
		// 获取评教ID
		this.evaluationId = options.evaluation_id || '';
		if (this.evaluationId) {
			// 获取评教详情
			this.getEvaluationDetail();
		} else {
			uni.showToast({
				title: '缺少评教信息',
				icon: 'none',
				duration: 2000
			});
			// 跳回上一页
			setTimeout(() => {
				uni.navigateBack();
			}, 1500);
		}
	},
	methods: {
		// 获取评教详情
		async getEvaluationDetail() {
			this.loading = true;
			try {
				const res = await request({
					url: `/eval/detail/${this.evaluationId}`,
					method: 'GET'
				});
				this.evaluationInfo = res || {};
				// 判断是否可以删除（只有待审核状态可以删除）
				this.canDelete = this.evaluationInfo.status === 2;
			} catch (error) {
				console.error('获取评教详情失败:', error);
				uni.showToast({
					title: '获取评教详情失败，请重试',
					icon: 'none',
					duration: 2000
				});
				// 跳回上一页
				setTimeout(() => {
					uni.navigateBack();
				}, 1500);
			} finally {
				this.loading = false;
			}
		},
		
		// 获取状态文本
		getStatusText(status) {
			const statusMap = {
				0: '作废',
				1: '有效',
				2: '待审核',
				3: '驳回'
			};
			return statusMap[status] || '未知';
		},
		
		// 获取状态样式类
		getStatusClass(status) {
			const classMap = {
				0: 'status-invalid',
				1: 'status-valid',
				2: 'status-pending',
				3: 'status-rejected'
			};
			return classMap[status] || '';
		},
		
		// 获取维度中文名称
		getDimensionName(key) {
			const nameMap = {
				teachingAttitude: '教学态度',
				content: '教学内容',
				method: '教学方法与手段',
				effect: '教学效果'
			};
			return nameMap[key] || key;
		},
		
		// 删除评教
		async deleteEvaluation() {
			uni.showModal({
				title: '提示',
				content: '确定要删除这条评教记录吗？',
				success: async (res) => {
					if (res.confirm) {
						try {
							const res = await request({
								url: `/eval/${this.evaluationId}`,
								method: 'DELETE'
							});
							
							uni.showToast({
								title: '删除成功',
								icon: 'success',
								duration: 1500
							});
							
							// 跳回上一页
							setTimeout(() => {
								uni.navigateBack();
							}, 1500);
						} catch (error) {
							console.error('删除评教失败:', error);
							uni.showToast({
								title: error.msg || '删除评教失败，请重试',
								icon: 'none',
								duration: 2000
							});
						}
					}
				}
			});
		}
	}
};
</script>

<style scoped>
.evaluation-detail-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding: 30rpx;
}

/* 课程信息 */
.course-info {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.course-name {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	flex: 1;
	margin-right: 20rpx;
}

.status {
	font-size: 24rpx;
	font-weight: bold;
	padding: 8rpx 16rpx;
	border-radius: 20rpx;
}

.status-valid {
	color: #FFFFFF;
	background-color: #67C23A;
}

.status-pending {
	color: #FFFFFF;
	background-color: #E6A23C;
}

.status-rejected {
	color: #FFFFFF;
	background-color: #F56C6C;
}

.status-invalid {
	color: #FFFFFF;
	background-color: #909399;
}

/* 基本信息 */
.basic-info {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.info-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 2rpx solid #F5F7FA;
}

.info-row:last-child {
	border-bottom: none;
}

.info-label {
	font-size: 28rpx;
	color: #666666;
	font-weight: 500;
}

.info-value {
	font-size: 28rpx;
	color: #333333;
	text-align: right;
	flex: 1;
	margin-left: 20rpx;
}

.score {
	font-size: 32rpx;
	font-weight: bold;
	color: #3E5C76;
}

/* 评分详情 */
.score-detail {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 30rpx;
	display: block;
}

.dimension-score {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 2rpx solid #F5F7FA;
}

.dimension-score:last-child {
	border-bottom: none;
}

.dimension-name {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
}

.dimension-score-value {
	font-size: 30rpx;
	font-weight: bold;
	color: #3E5C76;
}

/* 评价内容 */
.evaluation-content {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.content-item {
	margin-bottom: 30rpx;
}

.content-item:last-child {
	margin-bottom: 0;
}

.content-label {
	display: block;
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
	margin-bottom: 15rpx;
}

.content-text {
	display: block;
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
	background-color: #F5F7FA;
	padding: 20rpx;
	border-radius: 8rpx;
}

/* 审核信息 */
.review-info {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.review-comment {
	background-color: #FFF3CD;
	color: #856404;
	padding: 20rpx;
	border-radius: 8rpx;
	line-height: 1.6;
}

/* 操作按钮 */
.action-buttons {
	margin-top: 30rpx;
}

.delete-btn {
	width: 100%;
	height: 88rpx;
	background-color: #FF6B6B;
	color: #FFFFFF;
	font-size: 32rpx;
	font-weight: bold;
	border-radius: 44rpx;
}

.delete-btn::after {
	border: none;
}

.delete-btn:active {
	background-color: #FF5252;
}
</style>