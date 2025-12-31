<template>
	<view class="pending-courses-container">
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
		
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">待评课程列表</text>
		</view>
		
		<!-- 搜索和筛选 -->
		<view class="search-section">
			<view class="search-input">
				<text class="search-icon">🔍</text>
				<input 
					v-model="searchKeyword" 
					placeholder="搜索课程名称" 
					class="input"
					placeholder-class="placeholder"
					@input="handleSearch"
				/>
			</view>
		</view>
		
		<!-- 课程列表 -->
		<view class="courses-section">
			<view v-if="courses.length > 0" class="courses-list">
				<view class="course-item" v-for="(course, index) in courses" :key="index" @tap="navigateToEvaluation(course)">
					<view class="item-header">
						<text class="course-name">{{ course.course_name }}</text>
						<text class="course-type">{{ course.course_type }}</text>
					</view>
					
					<view class="item-info">
						<text class="teacher-name">授课教师：{{ course.teacher_name || '未知教师' }}</text>
						<text class="class-name">授课班级：{{ course.class_name }}</text>
					</view>
					
					<view class="item-details">
						<text class="weekday">星期{{ course.weekday_text }}</text>
						<text class="period">{{ course.period }}</text>
						<text class="classroom">地点：{{ course.classroom }}</text>
					</view>
					
					<view class="item-academic">
						<text class="academic-info">{{ course.academic_year }} 第{{ course.semester }}学期</text>
					</view>
				</view>
			</view>
			
			<!-- 空状态 -->
			<view v-else class="empty-state">
				<text class="empty-icon">📝</text>
				<text class="empty-text">暂无待评课程</text>
				<text class="empty-hint">所有课程都已完成评教</text>
			</view>
		</view>
		
		<!-- 分页 -->
		<view class="pagination" v-if="courses.length > 0">
			<button @tap="prevPage" :disabled="currentPage <= 1" class="page-btn">上一页</button>
			<text class="page-info">{{ currentPage }}/{{ totalPages }}</text>
			<button @tap="nextPage" :disabled="currentPage >= totalPages" class="page-btn">下一页</button>
		</view>
	</view>
</template>

<script>
import { request } from '@/common/request.js';

export default {
	data() {
			return {
				// 当前导航项
				currentNav: 'pending',
				// 课程列表数据
				courses: [],
				// 搜索关键词
				searchKeyword: '',
				// 分页信息
				currentPage: 1,
				totalPages: 1,
				pageSize: 10,
				// 加载状态
				loading: false,
				// 教师信息映射（根据teacher_id获取教师姓名）
				teacherMap: {}
			};
	},
	onLoad() {
		this.getPendingCourses();
	},
	methods: {
		// 获取待评课程列表
		async getPendingCourses() {
			this.loading = true;
			try {
				const res = await request({
					url: '/eval/pending-courses',
					method: 'GET',
					params: {
						page: this.currentPage,
						page_size: this.pageSize,
						academic_year: '2025-2026', // 可以根据需要动态获取
						semester: 2 // 可以根据需要动态获取
					}
				});
				
				if (res && res.list) {
					this.courses = res.list;
					this.totalPages = Math.ceil(res.total / this.pageSize) || 1;
				}
			} catch (error) {
				console.error('获取待评课程失败:', error);
				uni.showToast({
					title: '获取待评课程失败，请重试',
					icon: 'none',
					duration: 2000
				});
				this.courses = [];
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
				this.getPendingCourses();
			}, 500);
		},
		
		// 上一页
		prevPage() {
			if (this.currentPage > 1) {
				this.currentPage--;
				this.getPendingCourses();
			}
		},
		
		// 下一页
		nextPage() {
			if (this.currentPage < this.totalPages) {
				this.currentPage++;
				this.getPendingCourses();
			}
		},
		
		// 切换导航项
		switchNav(nav) {
			this.currentNav = nav;
			// 根据导航项跳转到不同页面
			switch(nav) {
				case 'received':
					uni.navigateTo({
						url: '/pages/evaluation/received-evaluations'
					});
					break;
				case 'my':
					uni.navigateTo({
						url: '/pages/evaluation/my-evaluations'
					});
					break;
				case 'pending':
					// 已经在当前页面，不需要跳转
					break;
				case 'completed':
					uni.navigateTo({
						url: '/pages/evaluation/completed-courses'
					});
					break;
			}
		},
		
		// 跳转到评教页面
		navigateToEvaluation(course) {
			uni.navigateTo({
				url: `/pages/evaluation/submit?timetable_id=${course.id}&course_name=${encodeURIComponent(course.course_name)}&teacher_id=${course.teacher_id}`
			});
		}
	}
};
</script>

<style scoped>
.pending-courses-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding-bottom: 30rpx;
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

/* 页面标题 */
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

/* 搜索和筛选 */
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

/* 课程列表 */
.courses-section {
	padding: 0 30rpx;
	margin-top: 20rpx;
}

.courses-list {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

/* 课程项 */
.course-item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 25rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	transition: all 0.3s;
}

.course-item:last-child {
	margin-bottom: 0;
}

.course-item:active {
	background-color: #E9EDF2;
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

.course-type {
	font-size: 24rpx;
	font-weight: bold;
	color: #FFFFFF;
	background-color: #E6A23C;
	padding: 8rpx 16rpx;
	border-radius: 20rpx;
}

.item-info {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
	margin-bottom: 15rpx;
}

.teacher-name, .class-name {
	font-size: 26rpx;
	color: #666666;
}

.item-details {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
	margin-bottom: 15rpx;
	font-size: 26rpx;
	color: #666666;
}

.weekday, .period, .classroom {
	background-color: #FFFFFF;
	padding: 6rpx 12rpx;
	border-radius: 8rpx;
}

.item-academic {
	border-top: 2rpx solid #E4E7ED;
	padding-top: 15rpx;
}

.academic-info {
	font-size: 24rpx;
	color: #999999;
}

/* 空状态 */
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