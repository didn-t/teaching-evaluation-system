<template>
	<view class="timetable-container">
		<!-- 搜索和筛选 -->
		<view class="search-filter-section">
			<view class="search-input">
				<text class="search-icon">🔍</text>
				<input 
					v-model="searchKeyword" 
					placeholder="搜索教师ID" 
					class="input"
					placeholder-class="placeholder"
				/>
			</view>
			<button @tap="handleSearch" class="search-btn">
				搜索
			</button>
		</view>
		
		<!-- 周次切换 -->
		<view class="week-switcher">
			<text class="week-btn" @tap="prevWeek" :disabled="currentWeek <= 1">
				<text class="arrow">←</text> 上一周
			</text>
			<view class="current-week">
				<text class="week-text">第{{ currentWeek }}周</text>
			</view>
			<text class="week-btn" @tap="nextWeek" :disabled="currentWeek >= totalWeeks">
				下一周 <text class="arrow">→</text>
			</text>
		</view>
		
		<!-- 课表表格 -->
		<view class="timetable-scroll-container">
			<view class="timetable-section">
				<view class="timetable-header">
					<view class="time-column"></view>
					<view class="day-column" v-for="day in days" :key="day.value">
						<text class="day-text">{{ day.label }}</text>
					</view>
				</view>
				
				<view class="timetable-body">
					<!-- 每节课的行 -->
					<view class="timetable-row" v-for="(row, rowIndex) in rows" :key="rowIndex">
						<!-- 时间列 -->
						<view class="time-column">
							<text class="time-text">{{ row.time }}</text>
						</view>
						
						<!-- 每天的课程列 -->
						<view class="course-column" 
							v-for="(day, dayIndex) in days" 
							:key="dayIndex"
						>
							<!-- 课程卡片 -->
							<view class="course-card" 
							v-for="course in getCoursesByTime(rowIndex, dayIndex)" 
							:key="course.id"
							@tap="showCourseDetail(course)"
						>
								<text class="course-name">{{ course.course_name }}</text>
								<text class="course-teacher" v-if="course.teacher_name && course.teacher_name !== '未知教师'">{{ course.teacher_name }}</text>
								<text class="course-room">{{ course.classroom }}</text>
							</view>
							<!-- 空课程占位 -->
							<view class="empty-course" v-if="getCoursesByTime(rowIndex, dayIndex).length === 0">
								<text class="empty-text">无</text>
							</view>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 课程详情弹窗 -->
		<view class="detail-modal" v-if="showDetailModal">
			<view class="modal-content">
				<view class="modal-header">
					<text class="modal-title">课程详情</text>
					<text class="modal-close" @tap="closeModal">×</text>
				</view>
				<view class="modal-body">
					<view class="detail-item">
						<text class="detail-label">课程名称：</text>
						<text class="detail-value">{{ selectedCourse.course_name || '' }}</text>
					</view>
					<view class="detail-item">
						<text class="detail-label">上课班级：</text>
						<text class="detail-value">{{ selectedCourse.class_name || '' }}</text>
					</view>
					<view class="detail-item">
						<text class="detail-label">上课时间：</text>
						<text class="detail-value">{{ selectedCourse.weekday_text || '' }} {{ selectedCourse.period || '' }}</text>
					</view>
					<view class="detail-item">
						<text class="detail-label">上课周次：</text>
						<text class="detail-value">{{ selectedCourse.week_info || '' }}</text>
					</view>
					<view class="detail-item">
						<text class="detail-label">上课地点：</text>
						<text class="detail-value">{{ selectedCourse.classroom || '' }}</text>
					</view>
					<view class="detail-item">
						<text class="detail-label">课程代码：</text>
						<text class="detail-value">{{ selectedCourse.course_code || '' }}</text>
					</view>
					<view class="detail-item">
						<text class="detail-label">学年学期：</text>
						<text class="detail-value">{{ selectedCourse.academic_year || '' }} 第{{ selectedCourse.semester || '' }}学期</text>
					</view>
					<view class="detail-item">
						<text class="detail-label">评教状态：</text>
						<view class="course-type-selector">
							<button 
								v-for="type in courseTypeOptions" 
								:key="type.value" 
								@tap="updateCourseType(type.value)"
								:class="['course-type-btn', { active: selectedCourse.course_type === type.value }]"
							>
								{{ type.label }}
							</button>
						</view>
					</view>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '@/common/request.js';

export default {
	data() {
			return {
				// 当前周次
				currentWeek: 1,
				// 总周数
				totalWeeks: 20,
				// 星期列表
				days: [
					{ label: '周一', value: 1 },
					{ label: '周二', value: 2 },
					{ label: '周三', value: 3 },
					{ label: '周四', value: 4 },
					{ label: '周五', value: 5 },
					{ label: '周六', value: 6 },
					{ label: '周日', value: 7 }
				],
				// 每节课的时间（6个大节）
				rows: [
					{ time: '第一大节' },
					{ time: '第二大节' },
					{ time: '第三大节' },
					{ time: '第四大节' },
					{ time: '第五大节' },
					{ time: '第六大节' }
				],
				// 课程数据
				courses: [],
				// 当前学年学期
				currentAcademicYear: '2025-2026',
				currentSemester: 2,
				// 课程详情弹窗
				showDetailModal: false,
				selectedCourse: {},
				// 搜索相关
				searchKeyword: '',
				// 当前搜索的教师ID
				currentTeacherId: null,
				// 课程类型选项
				courseTypeOptions: [
					{ label: '空', value: '' },
					{ label: '待评', value: '待评' },
					{ label: '已评', value: '已评' }
				]
				};
		},
	onLoad() {
		this.getTimetable();
	},
	methods: {
		// 获取课表数据
		async getTimetable() {
			try {
				// 构造请求参数
				const params = {
					academic_year: this.currentAcademicYear,
					semester: this.currentSemester,
					skip: 0,
					limit: 50
				};
				
				// 获取当前登录用户信息
				const userInfo = uni.getStorageSync('userInfo') || {};
				
				// 只使用teacher_id参数，不使用user_on参数
				if (this.searchKeyword.trim()) {
					// 如果有搜索关键词，使用关键词作为teacher_id
					params.teacher_id = this.searchKeyword.trim();
				} else {
					// 如果没有搜索关键词，使用当前登录用户的id
					params.teacher_id = userInfo.id || '';
				}
				
				// 调用课表接口，包含所有必要的查询参数
				const res = await request({
					url: '/org/org/timetables',
					method: 'GET',
					params: params
				});
				if (res && res.list) {
					// 将API返回的数据转换为课程数组
					this.courses = res.list.map(course => {
						// 将period转换为time_slot
						let time_slot = 0;
						if (course.period.includes('第一')) time_slot = 0;
						else if (course.period.includes('第二')) time_slot = 1;
						else if (course.period.includes('第三')) time_slot = 2;
						else if (course.period.includes('第四')) time_slot = 3;
						else if (course.period.includes('第五')) time_slot = 4;
						else if (course.period.includes('第六')) time_slot = 5;
						
						return {
							id: course.id,
							course_name: course.course_name,
							teacher_name: course.teacher_name || '未知教师',
							classroom: course.classroom,
							day: course.weekday, // API返回的是weekday，映射为day
							time_slot: time_slot,
							course_type: course.course_type || '',
							credit: course.credit || 0,
							timetable_id: course.id, // 使用课程id作为timetable_id
							week_info: course.week_info, // 保存周次信息，用于过滤当前周课程
							// 保存完整课程信息，用于详情展示
							class_name: course.class_name,
							weekday_text: course.weekday_text,
							period: course.period,
							course_code: course.course_code,
							academic_year: course.academic_year,
							semester: course.semester
						};
					});
				}
			} catch (error) {
				console.error('获取课表失败:', error);
				uni.showToast({
					title: '获取课表失败',
					icon: 'none',
					duration: 2000
				});
			}
		},
			
			// 搜索处理
			handleSearch() {
				// 无论搜索关键词是否为空，都重新获取课表
				this.getTimetable();
			},
		
		// 上一周
		prevWeek() {
			if (this.currentWeek > 1) {
				this.currentWeek--;
				// 周次切换暂时不重新获取数据，因为API不支持按周次过滤
			}
		},
		
		// 下一周
		nextWeek() {
			if (this.currentWeek < this.totalWeeks) {
				this.currentWeek++;
				// 周次切换暂时不重新获取数据，因为API不支持按周次过滤
			}
		},
		
		// 根据时间槽和星期获取课程
		getCoursesByTime(timeSlot, dayIndex) {
			const day = this.days[dayIndex].value;
			return this.courses.filter(course => {
				// 过滤时间槽和星期
				const matchTimeAndDay = course.time_slot === timeSlot && course.day === day;
				
				// 过滤当前周是否有课
				// week_info是逗号分隔的周次字符串，如"1,2,3,4,5,6,7"
				const weekInfo = course.week_info || '';
				const weekList = weekInfo.split(',').map(w => parseInt(w));
				const currentWeek = this.currentWeek;
				const matchWeek = weekList.includes(currentWeek);
				
				return matchTimeAndDay && matchWeek;
			});
		},
		
		// 显示课程详情
		showCourseDetail(course) {
			this.selectedCourse = course;
			this.showDetailModal = true;
		},
		
		// 关闭弹窗
			closeModal() {
				this.showDetailModal = false;
				this.selectedCourse = {};
			},
			
			// 更新课程评教状态
		async updateCourseType(courseType) {
			if (!this.selectedCourse.id) return;
			
			try {
				// 调用更新课程类型API，使用JSON请求体
				const res = await request({
					url: `/eval/courses/${this.selectedCourse.id}/course-type`,
					method: 'PUT',
					data: {
						course_type: courseType
					}
				});
				
				if (res) {
					// 更新本地课程数据
					this.selectedCourse.course_type = courseType;
					// 更新课程列表中的对应课程
					const index = this.courses.findIndex(course => course.id === this.selectedCourse.id);
					if (index !== -1) {
						this.courses[index].course_type = courseType;
					}
					uni.showToast({
						title: '更新成功',
						icon: 'success',
						duration: 1500
					});
				}
			} catch (error) {
				console.error('更新课程评教状态失败:', error);
				// 显示更详细的错误信息
				const errorMsg = error.msg || '更新失败，请重试';
				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 2000
				});
			}
		}
	}
};
</script>

<style scoped>
.timetable-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding: 20rpx;
}

/* 搜索和筛选 */
.search-filter-section {
				display: flex;
				justify-content: space-between;
				align-items: center;
				background-color: #FFFFFF;
				padding: 20rpx;
				border-radius: 12rpx;
				margin-bottom: 20rpx;
				box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
				gap: 20rpx;
			}
			
			.search-input {
				flex: 1;
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
				background-color: transparent;
			}
			
			.placeholder {
				color: #C0C4CC;
			}
			
			.search-btn {
				height: 80rpx;
				background-color: #3E5C76;
				color: #FFFFFF;
				font-size: 28rpx;
				border-radius: 40rpx;
				padding: 0 30rpx;
			}
			
			.search-btn::after {
				border: none;
			}
			
			/* 周次切换 */
			.week-switcher {
				display: flex;
				justify-content: space-between;
				align-items: center;
				background-color: #FFFFFF;
				padding: 20rpx;
				border-radius: 12rpx;
				margin-bottom: 20rpx;
				box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
			}

.week-btn {
	font-size: 28rpx;
	color: #3E5C76;
	font-weight: 500;
	padding: 10rpx 20rpx;
}

.week-btn[disabled] {
	color: #C0C4CC;
}

.arrow {
	font-size: 32rpx;
	margin: 0 10rpx;
}

.current-week {
	display: flex;
	align-items: center;
}

.week-text {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

/* 课表滚动容器 */
.timetable-scroll-container {
	width: 100%;
	overflow-x: auto;
	overflow-y: hidden;
	white-space: nowrap;
	background-color: #FFFFFF;
	border-radius: 12rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	margin: 0 auto;
}

/* 课表表格 */
.timetable-section {
	display: inline-block;
	min-width: 100%;
	overflow: hidden;
}

.timetable-header {
	display: flex;
	background-color: #3E5C76;
	color: #FFFFFF;
}

.time-column {
	width: 70rpx;
	min-height: 80rpx;
	border-right: 1rpx solid #E4E7ED;
	display: flex;
	justify-content: center;
	align-items: center;
}

.day-column {
	flex: 1;
	min-height: 80rpx;
	border-right: 1rpx solid #E4E7ED;
	display: flex;
	justify-content: center;
	align-items: center;
}

.day-column:last-child {
	border-right: none;
}

.day-text {
	font-size: 26rpx;
	font-weight: bold;
}

.timetable-body {
	/* 课表内容 */
}

.timetable-row {
	display: flex;
	border-bottom: 1rpx solid #E4E7ED;
}

.timetable-row:last-child {
	border-bottom: none;
}

.time-text {
	font-size: 24rpx;
	color: #666666;
	text-align: center;
}

.course-column {
	flex: 1;
	min-height: 160rpx;
	min-width: 50rpx;
	width: calc(100% / 7);
	border-right: 1rpx solid #E4E7ED;
	padding: 10rpx;
	display: flex;
	flex-direction: column;
	align-items: stretch;
	justify-content: flex-start;
	gap: 10rpx;
	flex-shrink: 0;
}

.course-column:last-child {
	border-right: none;
}

/* 课程卡片 */
.course-card {
	background-color: #E8F4F8;
	border: 2rpx solid #3E5C76;
	border-radius: 8rpx;
	padding: 15rpx;
	margin-bottom: 10rpx;
	width: 100%;
	min-height: 120rpx;
	height: auto;
	box-sizing: border-box;
	word-break: break-all;
	white-space: normal;
	overflow: hidden;
	flex-shrink: 0;
}

.course-card:active {
	background-color: #D4E6F1;
}

.course-name {
	display: block;
	font-size: 26rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 6rpx;
	line-height: 1.2;
	max-height: 70rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
}

.course-teacher {
	display: block;
	font-size: 22rpx;
	color: #666666;
	margin-bottom: 4rpx;
	line-height: 1.2;
}

.course-room {
	display: block;
	font-size: 22rpx;
	color: #999999;
	line-height: 1.2;
	max-height: 50rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
}

/* 空课程 */
.empty-course {
	height: 140rpx;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: #F5F7FA;
	border-radius: 8rpx;
}

.empty-text {
	font-size: 24rpx;
	color: #C0C4CC;
}

/* 课程详情弹窗 */
.detail-modal {
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
	border-radius: 16rpx;
	width: 90%;
	max-width: 600rpx;
	max-height: 80%;
	overflow-y: auto;
}

.modal-header {
	padding: 20rpx 24rpx;
	border-bottom: 2rpx solid #E4E7ED;
	display: flex;
	justify-content: space-between;
	align-items: center;
	background-color: #3E5C76;
	color: #FFFFFF;
	border-radius: 16rpx 16rpx 0 0;
}

.modal-title {
	font-size: 32rpx;
	font-weight: bold;
}

.modal-close {
	font-size: 40rpx;
	color: #FFFFFF;
	padding: 8rpx;
}

.modal-body {
	padding: 30rpx 24rpx;
}

.detail-item {
	margin-bottom: 24rpx;
	padding: 16rpx;
	background-color: #F5F7FA;
	border-radius: 8rpx;
}

.detail-label {
	font-size: 26rpx;
	font-weight: bold;
	color: #333333;
	margin-right: 10rpx;
}

.detail-value {
	font-size: 26rpx;
	color: #666666;
	word-break: break-all;
	line-height: 1.4;
}

/* 课程类型选择器 */
.course-type-selector {
	display: flex;
	gap: 15rpx;
	margin-top: 10rpx;
}

.course-type-btn {
	height: 72rpx;
	background-color: #FFFFFF;
	color: #3E5C76;
	font-size: 28rpx;
	border-radius: 36rpx;
	padding: 0 30rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	flex: 1;
	min-width: 100rpx;
}

.course-type-btn::after {
	border: none;
}

.course-type-btn.active {
	background-color: #3E5C76;
	color: #FFFFFF;
}

.course-type-btn:active {
	background-color: #2D455A;
	color: #FFFFFF;
}
</style>