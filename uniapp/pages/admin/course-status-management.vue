<template>
	<view class="course-status-management-container">
		<!-- 页面标题 -->
		<view class="page-header">
			<text class="page-title">课程评价状态管理</text>
		</view>
		
		<!-- 筛选条件 -->
		<view class="filter-section">
			<view class="filter-row">
				<view class="filter-item">
					<text class="filter-label">学年：</text>
					<input 
						:value="filters.academic_year" 
						placeholder="2025-2026" 
						class="filter-input"
						placeholder-class="placeholder"
						@input="handleAcademicYearInput"
					/>
				</view>
				<view class="filter-item">
					<text class="filter-label">学期：</text>
					<picker mode="selector" :range="[1, 2]" :value="getSemesterIndex()" @change="onSemesterChange">
						<view class="picker">
							{{ filters.semester || '请选择' }}
						</view>
					</picker>
				</view>
			</view>
			<view class="filter-row">
				<view class="filter-item">
					<text class="filter-label">评价状态：</text>
					<picker mode="selector" :range="['全部', '待评', '已评']" :value="getCourseTypeIndex()" @change="onCourseTypeChange">
						<view class="picker">
							{{ filters.course_type || '全部' }}
						</view>
					</picker>
				</view>
				<view class="filter-item">
					<text class="filter-label">课程名称：</text>
					<input 
						:value="filters.course_name" 
						placeholder="输入课程名称" 
						class="filter-input"
						placeholder-class="placeholder"
						@input="handleCourseNameInput"
					/>
				</view>
			</view>
			<view class="filter-actions">
				<button @tap="resetFilters" class="reset-btn">重置</button>
				<button @tap="getCourses" class="search-btn">查询</button>
			</view>
		</view>
		
		<!-- 课程列表 -->
		<view class="courses-section">
			<view v-if="courses.length > 0" class="courses-list">
				<view class="course-item" v-for="(course, index) in courses" :key="index">
					<view class="item-header">
						<text class="course-name">{{ course.course_name }}</text>
						<text class="course-type" :class="course.course_type === '待评' ? 'pending' : 'completed'">
							{{ course.course_type || '未设置' }}
						</text>
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
					
					<view class="item-actions">
						<button 
							v-if="course.course_type !== '待评'" 
							@tap="updateCourseStatus(course.id, '待评')" 
							class="action-btn pending-btn"
						>
							标记为待评
						</button>
						<button 
							v-if="course.course_type !== '已评'" 
							@tap="updateCourseStatus(course.id, '已评')" 
							class="action-btn completed-btn"
						>
							标记为已评
						</button>
					</view>
				</view>
			</view>
			
			<!-- 空状态 -->
			<view v-else class="empty-state">
				<text class="empty-icon">📝</text>
				<text class="empty-text">暂无课程数据</text>
				<text class="empty-hint">请调整筛选条件后重试</text>
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
import { request } from '../../common/request.js';

export default {
	data() {
		return {
			// 课程列表数据
			courses: [],
			// 筛选条件
			filters: {
				academic_year: '',
				semester: '',
				course_type: '全部',
				course_type_index: 0,
				course_name: ''
			},
			// 分页信息
			currentPage: 1,
			totalPages: 1,
			pageSize: 10,
			// 加载状态
			loading: false,
			// 教师信息映射
			teacherMap: {}
		};
	},
	onLoad() {
		this.getCourses();
	},
	methods: {
		// 兼容 web 和微信小程序的输入处理
		handleAcademicYearInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.filters.academic_year = value;
		},
		handleCourseNameInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.filters.course_name = value;
		},
		getSemesterIndex() {
			if (this.filters.semester === 1) return 0;
			if (this.filters.semester === 2) return 1;
			return 0;
		},
		getCourseTypeIndex() {
			const types = ['全部', '待评', '已评'];
			const index = types.indexOf(this.filters.course_type);
			return index >= 0 ? index : 0;
		},
		// 获取课程列表
		async getCourses() {
			this.loading = true;
			try {
				// 构建查询参数
				const params = {
					page: this.currentPage,
					page_size: this.pageSize
				};
				
				// 添加筛选条件
				if (this.filters.academic_year) {
					params.academic_year = this.filters.academic_year;
				}
				if (this.filters.semester) {
					params.semester = this.filters.semester;
				}
				if (this.filters.course_type && this.filters.course_type !== '全部') {
					// 根据course_type调用不同的接口
					const res = await request({
						url: this.filters.course_type === '待评' ? '/eval/pending-courses' : '/eval/completed-courses',
						method: 'GET',
						params: params
					});
					this.courses = res.list || [];
					this.totalPages = Math.ceil(res.total / this.pageSize) || 1;
				} else {
					// 这里需要一个获取所有课程的接口，暂时使用待评课程接口作为示例
					const res = await request({
						url: '/eval/pending-courses',
						method: 'GET',
						params: params
					});
					this.courses = res.list || [];
					this.totalPages = Math.ceil(res.total / this.pageSize) || 1;
				}
			} catch (error) {
				console.error('获取课程列表失败:', error);
				uni.showToast({
					title: '获取课程列表失败，请重试',
					icon: 'none',
					duration: 2000
				});
				this.courses = [];
			} finally {
				this.loading = false;
			}
		},
		
		// 学期选择器变化
		onSemesterChange(e) {
			// 兼容 web 和微信小程序
			const index = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e ? e : 0);
			this.filters.semester = index + 1;
			this.currentPage = 1;
			this.getCourses();
		},
		
		// 课程类型选择器变化
		onCourseTypeChange(e) {
			// 兼容 web 和微信小程序
			const types = ['全部', '待评', '已评'];
			const index = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e ? e : 0);
			this.filters.course_type_index = index;
			this.filters.course_type = types[index] || '全部';
			this.currentPage = 1;
			this.getCourses();
		},
		
		// 重置筛选条件
		resetFilters() {
			this.filters = {
				academic_year: '',
				semester: '',
				course_type: '全部',
				course_type_index: 0,
				course_name: ''
			};
			this.currentPage = 1;
			this.getCourses();
		},
		
		// 上一页
		prevPage() {
			if (this.currentPage > 1) {
				this.currentPage--;
				this.getCourses();
			}
		},
		
		// 下一页
		nextPage() {
			if (this.currentPage < this.totalPages) {
				this.currentPage++;
				this.getCourses();
			}
		},
		
		// 更新课程评价状态
		async updateCourseStatus(timetableId, courseType) {
			try {
				await request({
					url: `/courses/${timetableId}/course-type`,
					method: 'PUT',
					params: {
						course_type: courseType
					}
				});
				
				// 更新成功，刷新列表
				uni.showToast({
					title: `成功标记为${courseType}`,
					icon: 'success',
					duration: 2000
				});
				this.getCourses();
			} catch (error) {
				console.error('更新课程评价状态失败:', error);
				uni.showToast({
					title: '更新失败，请重试',
					icon: 'none',
					duration: 2000
				});
			}
		}
	}
};
</script>

<style scoped>
.course-status-management-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding-bottom: 30rpx;
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

/* 筛选条件 */
.filter-section {
	padding: 20rpx 30rpx;
	background-color: #FFFFFF;
}

.filter-row {
	display: flex;
	gap: 20rpx;
	margin-bottom: 20rpx;
}

.filter-item {
	display: flex;
	align-items: center;
	flex: 1;
}

.filter-label {
	font-size: 26rpx;
	color: #333333;
	margin-right: 15rpx;
	white-space: nowrap;
}

.filter-input {
	flex: 1;
	height: 80rpx;
	font-size: 26rpx;
	color: #333333;
	background-color: #F5F7FA;
	border-radius: 10rpx;
	padding: 0 20rpx;
}

.placeholder {
	color: #C0C4CC;
}

.picker {
	flex: 1;
	height: 80rpx;
	font-size: 26rpx;
	color: #333333;
	background-color: #F5F7FA;
	border-radius: 10rpx;
	padding: 0 20rpx;
	display: flex;
	align-items: center;
}

.filter-actions {
	display: flex;
	gap: 20rpx;
	justify-content: flex-end;
}

.reset-btn, .search-btn {
	height: 80rpx;
	font-size: 26rpx;
	border-radius: 10rpx;
	padding: 0 40rpx;
}

.reset-btn {
	background-color: #FFFFFF;
	color: #3E5C76;
	border: 2rpx solid #3E5C76;
}

.search-btn {
	background-color: #3E5C76;
	color: #FFFFFF;
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
	padding: 8rpx 16rpx;
	border-radius: 20rpx;
}

.course-type.pending {
	background-color: #E6A23C;
}

.course-type.completed {
	background-color: #67C23A;
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
	margin-bottom: 20rpx;
}

.academic-info {
	font-size: 24rpx;
	color: #999999;
}

/* 操作按钮 */
.item-actions {
	display: flex;
	gap: 20rpx;
	justify-content: flex-end;
}

.action-btn {
	height: 70rpx;
	font-size: 24rpx;
	border-radius: 10rpx;
	padding: 0 30rpx;
}

.pending-btn {
	background-color: #E6A23C;
	color: #FFFFFF;
}

.completed-btn {
	background-color: #67C23A;
	color: #FFFFFF;
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