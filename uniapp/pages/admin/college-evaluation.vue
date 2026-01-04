<template>
	<view class="college-eval-container">
		<!-- 顶部导航 -->
		<view class="nav-section">
			<view 
				class="nav-item" 
				:class="{ active: currentTab === 'teacher_records' }"
				@tap="switchTab('teacher_records')"
			>
				<text class="nav-text">教师听课记录</text>
			</view>
			<view 
				class="nav-item" 
				:class="{ active: currentTab === 'received' }"
				@tap="switchTab('received')"
			>
				<text class="nav-text">收到的评教</text>
			</view>
			<view 
				class="nav-item" 
				:class="{ active: currentTab === 'pending' }"
				@tap="switchTab('pending')"
			>
				<text class="nav-text">待评课程</text>
			</view>
			<view 
				class="nav-item" 
				:class="{ active: currentTab === 'completed' }"
				@tap="switchTab('completed')"
			>
				<text class="nav-text">已评课程</text>
			</view>
		</view>

		<!-- 筛选区域 -->
		<view class="filter-section">
			<!-- 22300417陈俫坤开发：学校管理员可选择学院 -->
			<view class="filter-row" v-if="isSchoolAdmin">
				<view class="filter-item" style="flex: 1;">
					<text class="filter-label">学院</text>
					<picker mode="selector" :range="collegePickerNames" :value="collegeIndex" @change="handleCollegeChange">
						<view class="picker-input">{{ currentCollegeName }}</view>
					</picker>
				</view>
			</view>

			<!-- 筛选模式切换 -->
			<view class="filter-mode-tabs" v-if="currentTab === 'pending' || currentTab === 'completed'">
				<view 
					class="mode-tab" 
					:class="{ active: filterMode === 'teacher' }"
					@tap="switchFilterMode('teacher')"
				>
					<text>按教研室-教师</text>
				</view>
				<view 
					class="mode-tab" 
					:class="{ active: filterMode === 'time' }"
					@tap="switchFilterMode('time')"
				>
					<text>按周次-天次-节次</text>
				</view>
			</view>

			<!-- 按教研室-教师筛选 -->
			<view class="filter-row" v-if="filterMode === 'teacher' || currentTab === 'teacher_records' || currentTab === 'received'">
				<view class="filter-item">
					<text class="filter-label">教研室</text>
					<picker mode="selector" :range="researchRoomPickerNames" :value="researchRoomIndex" @change="handleResearchRoomChange">
						<view class="picker-input">{{ currentResearchRoomName }}</view>
					</picker>
				</view>
				<view class="filter-item">
					<text class="filter-label">教师</text>
					<picker mode="selector" :range="teacherPickerNames" :value="teacherIndex" @change="handleTeacherChange">
						<view class="picker-input">{{ currentTeacherName }}</view>
					</picker>
				</view>
			</view>

			<!-- 按周次-天次-节次筛选 -->
			<view class="filter-row" v-if="filterMode === 'time' && (currentTab === 'pending' || currentTab === 'completed')">
				<view class="filter-item">
					<text class="filter-label">周次</text>
					<picker mode="selector" :range="weekPickerNames" :value="weekIndex" @change="handleWeekChange">
						<view class="picker-input">{{ currentWeekName }}</view>
					</picker>
				</view>
				<view class="filter-item">
					<text class="filter-label">星期</text>
					<picker mode="selector" :range="weekdayPickerNames" :value="weekdayIndex" @change="handleWeekdayChange">
						<view class="picker-input">{{ currentWeekdayName }}</view>
					</picker>
				</view>
				<view class="filter-item">
					<text class="filter-label">节次</text>
					<picker mode="selector" :range="periodPickerNames" :value="periodIndex" @change="handlePeriodChange">
						<view class="picker-input">{{ currentPeriodName }}</view>
					</picker>
				</view>
			</view>

			<!-- 搜索和操作按钮 -->
			<view class="filter-actions">
				<button class="btn-search" @tap="handleSearch">查询</button>
				<button class="btn-reset" @tap="handleReset">重置</button>
			</view>
		</view>

		<!-- 列表区域 -->
		<view class="list-section">
			<!-- 教师听课记录 -->
			<view v-if="currentTab === 'teacher_records'" class="records-list">
				<view v-if="records.length === 0" class="empty-state">
					<text class="empty-text">暂无教师听课记录</text>
				</view>
				<view v-for="record in records" :key="record.id" class="record-item" @tap="viewDetail(record)">
					<view class="record-header">
						<text class="record-no">{{ record.evaluation_no }}</text>
						<text class="record-score">{{ record.total_score }}分</text>
					</view>
					<view class="record-info">
						<text class="info-label">听课教师：</text>
						<text class="info-value">{{ record.listen_teacher_name }}</text>
					</view>
					<view class="record-info">
						<text class="info-label">被评教师：</text>
						<text class="info-value">{{ record.teacher_name }}</text>
					</view>
					<view class="record-info">
						<text class="info-label">课程名称：</text>
						<text class="info-value">{{ record.course_name }}</text>
					</view>
					<view class="record-info">
						<text class="info-label">听课日期：</text>
						<text class="info-value">{{ formatDate(record.listen_date) }}</text>
					</view>
				</view>
			</view>

			<!-- 收到的评教 -->
			<view v-if="currentTab === 'received'" class="records-list">
				<view v-if="records.length === 0" class="empty-state">
					<text class="empty-text">暂无收到的评教记录</text>
				</view>
				<view v-for="record in records" :key="record.id" class="record-item" @tap="viewDetail(record)">
					<view class="record-header">
						<text class="record-no">{{ record.evaluation_no }}</text>
						<text class="record-score">{{ record.total_score }}分</text>
					</view>
					<view class="record-info">
						<text class="info-label">督导：</text>
						<text class="info-value">{{ record.listen_teacher_name }}</text>
					</view>
					<view class="record-info">
						<text class="info-label">被评教师：</text>
						<text class="info-value">{{ record.teacher_name }}</text>
					</view>
					<view class="record-info">
						<text class="info-label">课程名称：</text>
						<text class="info-value">{{ record.course_name }}</text>
					</view>
					<view class="record-info">
						<text class="info-label">听课日期：</text>
						<text class="info-value">{{ formatDate(record.listen_date) }}</text>
					</view>
				</view>
			</view>

			<!-- 待评课程 -->
			<view v-if="currentTab === 'pending'" class="courses-list">
				<view v-if="courses.length === 0" class="empty-state">
					<text class="empty-text">暂无待评课程</text>
				</view>
				<view v-for="course in courses" :key="course.id" class="course-item">
					<view class="course-header">
						<text class="course-name">{{ course.course_name }}</text>
					</view>
					<view class="course-info">
						<text class="info-label">授课教师：</text>
						<text class="info-value">{{ course.teacher_name }}</text>
					</view>
					<view class="course-info">
						<text class="info-label">上课时间：</text>
						<text class="info-value">{{ course.weekday_text }} {{ course.period }}</text>
					</view>
					<view class="course-info">
						<text class="info-label">上课地点：</text>
						<text class="info-value">{{ course.classroom }}</text>
					</view>
					<view class="course-info">
						<text class="info-label">周次：</text>
						<text class="info-value">{{ course.week_info }}</text>
					</view>
				</view>
			</view>

			<!-- 已评课程 -->
			<view v-if="currentTab === 'completed'" class="courses-list">
				<view v-if="courses.length === 0" class="empty-state">
					<text class="empty-text">暂无已评课程</text>
				</view>
				<view v-for="course in courses" :key="course.id" class="course-item">
					<view class="course-header">
						<text class="course-name">{{ course.course_name }}</text>
						<text class="course-score">{{ course.total_score }}分</text>
					</view>
					<view class="course-info">
						<text class="info-label">授课教师：</text>
						<text class="info-value">{{ course.teacher_name }}</text>
					</view>
					<view class="course-info">
						<text class="info-label">评教教师：</text>
						<text class="info-value">{{ course.listen_teacher_name }}</text>
					</view>
					<view class="course-info">
						<text class="info-label">评教日期：</text>
						<text class="info-value">{{ formatDate(course.listen_date) }}</text>
					</view>
				</view>
			</view>
		</view>

		<!-- 分页 -->
		<view class="pagination" v-if="totalPages > 1">
			<button class="page-btn" :disabled="currentPage <= 1" @tap="prevPage">上一页</button>
			<text class="page-info">{{ currentPage }} / {{ totalPages }}</text>
			<button class="page-btn" :disabled="currentPage >= totalPages" @tap="nextPage">下一页</button>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	data() {
		return {
			currentTab: 'teacher_records',
			filterMode: 'teacher',
			// 筛选条件
			collegeId: null,
			researchRoomId: null,
			teacherId: null,
			week: null,
			weekday: null,
			period: null,
			// 数据列表
			colleges: [],
			researchRooms: [],
			teachers: [],
			records: [],
			courses: [],
			// 分页
			currentPage: 1,
			totalPages: 1,
			pageSize: 10,
			loading: false,
			// 22300417陈俫坤开发：角色标记
			isSchoolAdmin: false,
			userInfo: null
		};
	},
	computed: {
		// 22300417陈俫坤开发：学院选择器
		collegePickerNames() {
			const names = ['请选择学院'];
			(this.colleges || []).forEach(c => names.push(c.college_name));
			return names;
		},
		collegeIndex() {
			if (!this.collegeId) return 0;
			const idx = (this.colleges || []).findIndex(c => Number(c.id) === Number(this.collegeId));
			return idx >= 0 ? idx + 1 : 0;
		},
		currentCollegeName() {
			if (!this.collegeId) return '请选择学院';
			const c = (this.colleges || []).find(x => Number(x.id) === Number(this.collegeId));
			return c ? c.college_name : '请选择学院';
		},
		researchRoomPickerNames() {
			const names = ['全部'];
			(this.researchRooms || []).forEach(r => names.push(r.room_name));
			return names;
		},
		researchRoomIndex() {
			if (!this.researchRoomId) return 0;
			const idx = (this.researchRooms || []).findIndex(r => Number(r.id) === Number(this.researchRoomId));
			return idx >= 0 ? idx + 1 : 0;
		},
		currentResearchRoomName() {
			if (!this.researchRoomId) return '全部';
			const r = (this.researchRooms || []).find(x => Number(x.id) === Number(this.researchRoomId));
			return r ? r.room_name : '全部';
		},
		teacherPickerNames() {
			const names = ['全部'];
			(this.teachers || []).forEach(t => names.push(`${t.user_name || ''}(${t.user_on || ''})`));
			return names;
		},
		teacherIndex() {
			if (!this.teacherId) return 0;
			const idx = (this.teachers || []).findIndex(t => Number(t.id) === Number(this.teacherId));
			return idx >= 0 ? idx + 1 : 0;
		},
		currentTeacherName() {
			if (!this.teacherId) return '全部';
			const t = (this.teachers || []).find(x => Number(x.id) === Number(this.teacherId));
			return t ? `${t.user_name || ''}(${t.user_on || ''})` : '全部';
		},
		weekPickerNames() {
			const names = ['全部'];
			for (let i = 1; i <= 30; i++) names.push(`第${i}周`);
			return names;
		},
		weekIndex() {
			if (!this.week) return 0;
			return Number(this.week);
		},
		currentWeekName() {
			return this.week ? `第${this.week}周` : '全部';
		},
		weekdayPickerNames() {
			return ['全部', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
		},
		weekdayIndex() {
			if (!this.weekday) return 0;
			return Number(this.weekday);
		},
		currentWeekdayName() {
			const names = ['全部', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
			return this.weekday ? names[this.weekday] : '全部';
		},
		periodPickerNames() {
			return ['全部', '第一大节', '第二大节', '第三大节', '第四大节', '第五大节', '第六大节'];
		},
		periodIndex() {
			if (!this.period) return 0;
			const periods = ['第一大节', '第二大节', '第三大节', '第四大节', '第五大节', '第六大节'];
			const idx = periods.indexOf(this.period);
			return idx >= 0 ? idx + 1 : 0;
		},
		currentPeriodName() {
			return this.period || '全部';
		}
	},
	async onLoad() {
		// 22300417陈俫坤开发：加载用户信息判断角色
		await this.loadUserInfo();
		if (this.isSchoolAdmin) {
			await this.loadColleges();
		}
		this.loadResearchRooms();
		this.loadTeachers();
		this.loadData();
	},
	methods: {
		async loadUserInfo() {
			try {
				const res = await request({ url: '/user/me', method: 'GET' });
				this.userInfo = res;
				const codes = (res && res.roles_code) ? res.roles_code : [];
				this.isSchoolAdmin = codes.includes('school_admin');
			} catch (e) {
				this.userInfo = null;
				this.isSchoolAdmin = false;
			}
		},
		async loadColleges() {
			try {
				const res = await request({ url: '/org/colleges', method: 'GET', params: { skip: 0, limit: 200 } });
				this.colleges = (res && res.list) ? res.list : [];
			} catch (e) {
				this.colleges = [];
			}
		},
		handleCollegeChange(e) {
			const index = Number(e.detail.value);
			this.collegeId = index <= 0 ? null : (this.colleges[index - 1]?.id || null);
			this.researchRoomId = null;
			this.teacherId = null;
			this.loadResearchRooms();
			this.loadTeachers();
		},
		switchTab(tab) {
			this.currentTab = tab;
			this.currentPage = 1;
			this.records = [];
			this.courses = [];
			this.loadData();
		},
		switchFilterMode(mode) {
			this.filterMode = mode;
		},
		handleResearchRoomChange(e) {
			const index = Number(e.detail.value);
			this.researchRoomId = index <= 0 ? null : (this.researchRooms[index - 1]?.id || null);
			this.loadTeachers();
		},
		handleTeacherChange(e) {
			const index = Number(e.detail.value);
			this.teacherId = index <= 0 ? null : (this.teachers[index - 1]?.id || null);
		},
		handleWeekChange(e) {
			const index = Number(e.detail.value);
			this.week = index <= 0 ? null : index;
		},
		handleWeekdayChange(e) {
			const index = Number(e.detail.value);
			this.weekday = index <= 0 ? null : index;
		},
		handlePeriodChange(e) {
			const index = Number(e.detail.value);
			const periods = ['第一大节', '第二大节', '第三大节', '第四大节', '第五大节', '第六大节'];
			this.period = index <= 0 ? null : periods[index - 1];
		},
		handleSearch() {
			this.currentPage = 1;
			this.loadData();
		},
		handleReset() {
			if (this.isSchoolAdmin) {
				this.collegeId = null;
			}
			this.researchRoomId = null;
			this.teacherId = null;
			this.week = null;
			this.weekday = null;
			this.period = null;
			this.currentPage = 1;
			this.loadTeachers();
			this.loadData();
		},
		async loadResearchRooms() {
			try {
				const res = await request({
					url: '/user/research-rooms',
					method: 'GET'
				});
				this.researchRooms = (res && res.list) ? res.list : [];
			} catch (e) {
				this.researchRooms = [];
			}
		},
		async loadTeachers() {
			try {
				const res = await request({
					url: '/org/teachers',
					method: 'GET',
					params: {
						research_room_id: this.researchRoomId || undefined
					}
				});
				this.teachers = (res && res.list) ? res.list : [];
			} catch (e) {
				this.teachers = [];
			}
		},
		async loadData() {
			// 22300417陈俫坤开发：school_admin必须先选择学院
			if (this.isSchoolAdmin && !this.collegeId) {
				this.records = [];
				this.courses = [];
				return;
			}
			this.loading = true;
			try {
				if (this.currentTab === 'teacher_records') {
					await this.loadTeacherRecords();
				} else if (this.currentTab === 'received') {
					await this.loadReceivedEvaluations();
				} else if (this.currentTab === 'pending') {
					await this.loadPendingCourses();
				} else if (this.currentTab === 'completed') {
					await this.loadCompletedCourses();
				}
			} finally {
				this.loading = false;
			}
		},
		async loadTeacherRecords() {
			try {
				const res = await request({
					url: '/eval/college/teacher-records',
					method: 'GET',
					params: {
						page: this.currentPage,
						page_size: this.pageSize,
						college_id: this.collegeId || undefined,
						research_room_id: this.researchRoomId || undefined,
						teacher_id: this.teacherId || undefined
					}
				});
				this.records = (res && res.list) ? res.list : [];
				this.totalPages = Math.ceil((res?.total || 0) / this.pageSize) || 1;
			} catch (e) {
				this.records = [];
				this.totalPages = 1;
				uni.showToast({ title: '加载失败', icon: 'none' });
			}
		},
		async loadReceivedEvaluations() {
			try {
				const res = await request({
					url: '/eval/college/received',
					method: 'GET',
					params: {
						page: this.currentPage,
						page_size: this.pageSize,
						college_id: this.collegeId || undefined,
						research_room_id: this.researchRoomId || undefined,
						teacher_id: this.teacherId || undefined
					}
				});
				this.records = (res && res.list) ? res.list : [];
				this.totalPages = Math.ceil((res?.total || 0) / this.pageSize) || 1;
			} catch (e) {
				this.records = [];
				this.totalPages = 1;
				uni.showToast({ title: '加载失败', icon: 'none' });
			}
		},
		async loadPendingCourses() {
			try {
				const params = {
					page: this.currentPage,
					page_size: this.pageSize,
					college_id: this.collegeId || undefined
				};
				if (this.filterMode === 'teacher') {
					params.research_room_id = this.researchRoomId || undefined;
					params.teacher_id = this.teacherId || undefined;
				} else {
					params.week = this.week || undefined;
					params.weekday = this.weekday || undefined;
					params.period = this.period || undefined;
				}
				const res = await request({
					url: '/eval/college/pending-courses',
					method: 'GET',
					params
				});
				this.courses = (res && res.list) ? res.list : [];
				this.totalPages = Math.ceil((res?.total || 0) / this.pageSize) || 1;
			} catch (e) {
				this.courses = [];
				this.totalPages = 1;
				uni.showToast({ title: '加载失败', icon: 'none' });
			}
		},
		async loadCompletedCourses() {
			try {
				const params = {
					page: this.currentPage,
					page_size: this.pageSize,
					college_id: this.collegeId || undefined
				};
				if (this.filterMode === 'teacher') {
					params.research_room_id = this.researchRoomId || undefined;
					params.teacher_id = this.teacherId || undefined;
				} else {
					params.week = this.week || undefined;
					params.weekday = this.weekday || undefined;
					params.period = this.period || undefined;
				}
				const res = await request({
					url: '/eval/college/completed-courses',
					method: 'GET',
					params
				});
				this.courses = (res && res.list) ? res.list : [];
				this.totalPages = Math.ceil((res?.total || 0) / this.pageSize) || 1;
			} catch (e) {
				this.courses = [];
				this.totalPages = 1;
				uni.showToast({ title: '加载失败', icon: 'none' });
			}
		},
		viewDetail(record) {
			uni.navigateTo({
				url: `/pages/evaluation/detail?id=${record.id}`
			});
		},
		formatDate(dateStr) {
			if (!dateStr) return '-';
			const d = new Date(dateStr);
			return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
		},
		prevPage() {
			if (this.currentPage > 1) {
				this.currentPage--;
				this.loadData();
			}
		},
		nextPage() {
			if (this.currentPage < this.totalPages) {
				this.currentPage++;
				this.loadData();
			}
		}
	}
};
</script>

<style scoped>
.college-eval-container {
	background-color: #F5F7FA;
	min-height: 100vh;
	padding: 20rpx;
}

/* 导航 */
.nav-section {
	display: flex;
	background-color: #FFFFFF;
	border-radius: 12rpx;
	margin-bottom: 20rpx;
	overflow: hidden;
}

.nav-item {
	flex: 1;
	text-align: center;
	padding: 24rpx 10rpx;
	font-size: 26rpx;
	color: #666666;
	border-bottom: 4rpx solid transparent;
}

.nav-item.active {
	color: #3E5C76;
	font-weight: bold;
	border-bottom-color: #3E5C76;
}

/* 筛选区域 */
.filter-section {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-bottom: 20rpx;
}

.filter-mode-tabs {
	display: flex;
	margin-bottom: 20rpx;
	gap: 20rpx;
}

.mode-tab {
	flex: 1;
	text-align: center;
	padding: 16rpx;
	background-color: #F5F7FA;
	border-radius: 8rpx;
	font-size: 26rpx;
	color: #666666;
}

.mode-tab.active {
	background-color: #3E5C76;
	color: #FFFFFF;
}

.filter-row {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
	margin-bottom: 20rpx;
}

.filter-item {
	flex: 1;
	min-width: 200rpx;
}

.filter-label {
	display: block;
	font-size: 24rpx;
	color: #999999;
	margin-bottom: 8rpx;
}

.picker-input {
	height: 72rpx;
	line-height: 72rpx;
	background-color: #F5F7FA;
	border-radius: 8rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #333333;
}

.filter-actions {
	display: flex;
	gap: 20rpx;
}

.btn-search {
	flex: 1;
	height: 72rpx;
	line-height: 72rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 28rpx;
	border-radius: 8rpx;
}

.btn-reset {
	flex: 1;
	height: 72rpx;
	line-height: 72rpx;
	background-color: #F5F7FA;
	color: #666666;
	font-size: 28rpx;
	border-radius: 8rpx;
}

/* 列表区域 */
.list-section {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 20rpx;
	min-height: 400rpx;
}

.empty-state {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 300rpx;
}

.empty-text {
	font-size: 28rpx;
	color: #999999;
}

.record-item,
.course-item {
	padding: 20rpx;
	border-bottom: 1rpx solid #EEEEEE;
}

.record-item:last-child,
.course-item:last-child {
	border-bottom: none;
}

.record-header,
.course-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.record-no {
	font-size: 26rpx;
	color: #333333;
	font-weight: bold;
}

.record-score,
.course-score {
	font-size: 32rpx;
	color: #3E5C76;
	font-weight: bold;
}

.course-name {
	font-size: 28rpx;
	color: #333333;
	font-weight: bold;
}

.record-info,
.course-info {
	display: flex;
	margin-bottom: 8rpx;
}

.info-label {
	font-size: 24rpx;
	color: #999999;
	width: 160rpx;
}

.info-value {
	font-size: 24rpx;
	color: #666666;
	flex: 1;
}

/* 分页 */
.pagination {
	display: flex;
	justify-content: center;
	align-items: center;
	padding: 30rpx;
	gap: 30rpx;
}

.page-btn {
	height: 64rpx;
	line-height: 64rpx;
	padding: 0 30rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 26rpx;
	border-radius: 8rpx;
}

.page-btn[disabled] {
	background-color: #CCCCCC;
}

.page-info {
	font-size: 26rpx;
	color: #666666;
}
</style>
