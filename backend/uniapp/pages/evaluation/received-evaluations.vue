<template>
	<view class="received-evaluations-container">
		<!-- 导航菜单 -->
		<view class="nav-menu">
			<view 
				class="nav-item" 
				:class="{ active: currentNav === 'received' }" 
				@tap="switchNav('received')"
			>
				收到的评教
			</view>
			<view 
				class="nav-item" 
				:class="{ active: currentNav === 'my' }" 
				@tap="switchNav('my')"
			>
				我的评教
			</view>
			<view 
				class="nav-item" 
				:class="{ active: currentNav === 'pending' }" 
				@tap="switchNav('pending')"
			>
				待评课程
			</view>
			<view 
				class="nav-item" 
				:class="{ active: currentNav === 'completed' }" 
				@tap="switchNav('completed')"
			>
				已评课程
			</view>
		</view>
		
		<!-- 搜索和筛选 -->
		<view class="search-section">
			<view class="search-input">
				<text class="search-icon">🔍</text>
				<input 
					:value="searchKeyword" 
					placeholder="搜索课程或评教教师" 
					class="input"
					placeholder-class="placeholder"
					@input="handleSearchKeywordInput"
				/>
			</view>
			
			<!-- 筛选按钮 -->
			<button @tap="showFilter" class="filter-btn">
				筛选
			</button>
		</view>
		
		<!-- 评教列表 -->
		<view class="evaluations-section">
			<text class="section-title">收到的评教</text>
			
			<!-- 列表内容 -->
			<view class="evaluations-list" v-if="evaluations.length > 0">
				<view class="evaluation-item" v-for="(item, index) in evaluations" :key="index" @tap="viewDetail(item.id)">
					<view class="item-header">
						<text class="course-name">{{ item.timetable?.course_name || 'N/A' }}</text>
						<text class="status" :class="getStatusClass(item.status)">
							{{ getStatusText(item.status) }}
						</text>
					</view>
					
					<view class="item-info">
						<text class="evaluator-name">评教教师：{{ item.listen_teacher_name || (item.is_anonymous ? '匿名' : 'N/A') }}</text>
						<text class="evaluate-date">评教时间：{{ item.submit_time ? new Date(item.submit_time).toLocaleString() : 'N/A' }}</text>
					</view>
					
					<view class="item-score">
						<text class="score-label">综合评分：</text>
						<text class="score-value">{{ item.total_score }}分</text>
					</view>
					
					<view class="item-preview">
						<text class="preview-label">评价预览：</text>
						<text class="preview-text">{{ item.advantage_content || '无评价内容' }}</text>
					</view>
				</view>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-else>
				<text class="empty-icon">📝</text>
				<text class="empty-text">暂无收到的评教</text>
				<text class="empty-hint">耐心等待评教反馈吧</text>
			</view>
		</view>
		
		<!-- 分页 -->
		<view class="pagination" v-if="evaluations.length > 0">
			<button @tap="prevPage" :disabled="currentPage <= 1" class="page-btn">上一页</button>
			<text class="page-info">{{ currentPage }}/{{ totalPages }}</text>
			<button @tap="nextPage" :disabled="currentPage >= totalPages" class="page-btn">下一页</button>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	data() {
			return {
				// 当前导航项
				currentNav: 'received',
				// 评教列表数据
				evaluations: [],
				// 搜索关键词
				searchKeyword: '',
				// 筛选条件
				filter: {
					status: null,
					score_level: null,
					startDate: '',
					endDate: '',
					academic_year: '',
					semester: null
				},
			// 状态选项
			statusOptions: [
				{ label: '全部', value: null },
				{ label: '有效', value: 1 },
				{ label: '待审核', value: 2 },
				{ label: '驳回', value: 3 },
				{ label: '作废', value: 0 }
			],
			// 评分等级选项
			levelOptions: [
				{ label: '全部', value: null },
				{ label: '优秀', value: 'excellent' },
				{ label: '良好', value: 'good' },
				{ label: '中等', value: 'medium' },
				{ label: '及格', value: 'pass' },
				{ label: '不及格', value: 'fail' }
			],
			// 学期选项
			semesterOptions: [
				{ label: '全部', value: null },
				{ label: '春季', value: 1 },
				{ label: '秋季', value: 2 }
			],
			// 分页信息
			currentPage: 1,
			totalPages: 1,
			pageSize: 10,
			// 加载状态
			loading: false
		};
	},
	onLoad() {
		this.getReceivedEvaluations();
	},
	onShow() {
		// 页面显示时刷新数据
		this.getReceivedEvaluations();
	},
	methods: {
		// 兼容 web 和微信小程序的输入处理
		handleSearchKeywordInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.searchKeyword = value;
		},
		// 获取收到的评教记录
		async getReceivedEvaluations() {
			this.loading = true;
			try {
				// 构造请求参数，只包含后端接口定义的参数
				const params = {
					page: this.currentPage,
					page_size: this.pageSize,
					status: this.filter.status,
					score_level: this.filter.score_level,
					academic_year: this.filter.academic_year,
					semester: this.filter.semester
				};
				
				// 只在有值时添加日期参数，避免发送空字符串
				if (this.filter.startDate) {
					params.start_date = this.filter.startDate;
				}
				if (this.filter.endDate) {
					params.end_date = this.filter.endDate;
				}
				
				const res = await request({
					url: '/eval/received',
					method: 'GET',
					params: params
				});
				
				if (res) {
					this.evaluations = res.list || [];
					this.totalPages = Math.ceil((res.total || 0) / this.pageSize) || 1;
				}
			} catch (error) {
				console.error('获取收到的评教失败:', error);
				uni.showToast({
					title: '获取收到的评教失败，请重试',
					icon: 'none',
					duration: 2000
				});
				this.evaluations = [];
			} finally {
				this.loading = false;
			}
		},
		
		// 搜索处理
		handleSearch() {
			// 重置页码
			this.currentPage = 1;
			// 防抖处理，延迟执行搜索
			if (this.searchTimer) {
				clearTimeout(this.searchTimer);
			}
			this.searchTimer = setTimeout(() => {
				this.getReceivedEvaluations();
			}, 500);
		},
		
		// 简化的筛选处理（移除了弹窗）
		showFilter() {
			// 重置页码
			this.currentPage = 1;
			// 重新获取数据
			this.getReceivedEvaluations();
		},
		
		// 显示日期选择器
		showDatePicker(type) {
			uni.showDatePicker({
				success: (res) => {
					const date = res.year + '-' + res.month + '-' + res.day;
					if (type === 'start') {
						this.filter.startDate = date;
					} else {
						this.filter.endDate = date;
					}
				}
			});
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
		
		// 查看详情
		viewDetail(id) {
			uni.navigateTo({
				url: `/pages/evaluation/detail?evaluation_id=${id}`
			});
		},
		
		// 切换导航项
			switchNav(nav) {
				this.currentNav = nav;
				// 根据导航项跳转到不同页面
				switch(nav) {
					case 'received':
						// 已经在当前页面，不需要跳转
						break;
					case 'my':
						// 22300417陈俫坤开发：修复导航错误 - tabBar页面使用switchTab
						uni.switchTab({
							url: '/pages/evaluation/my-evaluations'
						});
						break;
					case 'pending':
						uni.navigateTo({
							url: '/pages/evaluation/pending-courses'
						});
						break;
					case 'completed':
						uni.navigateTo({
							url: '/pages/evaluation/completed-courses'
						});
						break;
				}
			},
			
			// 上一页
			prevPage() {
				if (this.currentPage > 1) {
					this.currentPage--;
					this.getReceivedEvaluations();
				}
			},
			
			// 下一页
			nextPage() {
				if (this.currentPage < this.totalPages) {
					this.currentPage++;
					this.getReceivedEvaluations();
				}
			}
		}
};
</script>

<style scoped>
.received-evaluations-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding: 0;
}

/* 导航菜单 */
.nav-menu {
	display: flex;
	background-color: #FFFFFF;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	position: sticky;
	top: 0;
	z-index: 100;
}

.nav-item {
	flex: 1;
	text-align: center;
	padding: 25rpx 0;
	font-size: 28rpx;
	color: #666666;
	position: relative;
}

.nav-item.active {
	color: #3E5C76;
	font-weight: bold;
}

.nav-item.active::after {
	content: '';
	position: absolute;
	bottom: 0;
	left: 50%;
	transform: translateX(-50%);
	width: 60rpx;
	height: 6rpx;
	background-color: #3E5C76;
	border-radius: 3rpx;
}

/* 搜索和筛选 */
.search-section {
	padding: 20rpx 30rpx;
	background-color: #FFFFFF;
	margin-bottom: 20rpx;
}

/* 搜索和筛选 */
.search-section {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
	gap: 20rpx;
}

.search-input {
	flex: 1;
	display: flex;
	align-items: center;
	background-color: #FFFFFF;
	border-radius: 40rpx;
	padding: 0 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
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

.filter-btn {
	height: 80rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 28rpx;
	border-radius: 40rpx;
	padding: 0 30rpx;
}

.filter-btn::after {
	border: none;
}

/* 评教列表 */
.evaluations-section {
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

/* 评教项 */
.evaluation-item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 30rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.evaluation-item:last-child {
	margin-bottom: 0;
}

.item-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.course-name {
	font-size: 30rpx;
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

.item-info {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.evaluator-name, .evaluate-date {
	font-size: 26rpx;
	color: #666666;
}

.item-score {
	margin-bottom: 20rpx;
}

.score-label {
	font-size: 28rpx;
	color: #666666;
}

.score-value {
	font-size: 32rpx;
	font-weight: bold;
	color: #3E5C76;
}

.item-preview {
	margin-top: 20rpx;
	padding-top: 20rpx;
	border-top: 2rpx solid #E4E7ED;
}

.preview-label {
	font-size: 26rpx;
	color: #666666;
	font-weight: 500;
}

.preview-text {
	font-size: 26rpx;
	color: #999999;
	margin-left: 10rpx;
	line-height: 1.4;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: center;
	padding: 100rpx 0;
	color: #999999;
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

/* 分页 */
.pagination {
	display: flex;
	justify-content: center;
	align-items: center;
	margin-top: 30rpx;
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
</style>