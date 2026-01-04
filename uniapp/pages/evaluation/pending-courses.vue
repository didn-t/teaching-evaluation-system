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
		<view class="search-section" v-if="!isSupervisor">
			<view class="search-input">
				<text class="search-icon">🔍</text>
				<input 
					:value="searchKeyword" 
					placeholder="搜索课程名/教师名" 
					class="input"
					placeholder-class="placeholder"
					@input="handleSearchKeywordInput"
				/>
			</view>
		</view>
		
		<!-- 22300417陈俫坤开发：督导待评筛选（两种模式） -->
		<view class="filter-section" v-else>
			<view class="filter-mode-tabs">
				<view class="filter-mode-tab" :class="filterMode === 'level' ? 'active' : ''" @tap="switchFilterMode('level')">分级筛选</view>
				<view class="filter-mode-tab" :class="filterMode === 'time' ? 'active' : ''" @tap="switchFilterMode('time')">按时间筛选</view>
			</view>
			
			<view class="filter-grid">
				<view class="filter-item" v-if="filterMode === 'level'">
					<text class="filter-label">校区</text>
					<picker mode="selector" :range="campusPickerNames" :value="campusIndex" @change="handleCampusChange">
						<view class="filter-input">{{ currentCampusName }}</view>
					</picker>
				</view>
				
				<view class="filter-item">
					<text class="filter-label">学院</text>
					<picker mode="selector" :range="collegePickerNames" :value="collegeIndex" @change="handleCollegeChange">
						<view class="filter-input">{{ currentCollegeName }}</view>
					</picker>
				</view>
				
				<view class="filter-item">
					<text class="filter-label">周次</text>
					<picker mode="selector" :range="weekPickerNames" :value="weekIndex" @change="handleWeekChange">
						<view class="filter-input">{{ currentWeekName }}</view>
					</picker>
				</view>
				
				<view class="filter-item" v-if="filterMode === 'time'">
					<text class="filter-label">星期</text>
					<picker mode="selector" :range="weekdayPickerNames" :value="weekdayIndex" @change="handleWeekdayChange">
						<view class="filter-input">{{ currentWeekdayName }}</view>
					</picker>
				</view>
				
				<view class="filter-item">
					<text class="filter-label">教师</text>
					<picker mode="selector" :range="teacherPickerNames" :value="teacherIndex" @change="handleTeacherChange">
						<view class="filter-input">{{ currentTeacherName }}</view>
					</picker>
				</view>
			</view>
			
			<view class="filter-actions">
				<button class="filter-btn" @tap="applySupervisorFilters" :loading="loading">查询</button>
				<button class="filter-btn secondary" @tap="resetSupervisorFilters" :disabled="loading">重置</button>
			</view>
		</view>
		
		<!-- 课程列表 -->
		<view class="courses-section">
			<view v-if="courses.length > 0" class="courses-list">
				<view class="course-item" v-for="(course, index) in courses" :key="index" @tap="navigateToEvaluation(course)">
					<view class="item-header">
						<text class="course-name">{{ course.course_name }}</text>
						<!-- 22300417陈俫坤开发：course_type 为空时会出现“橙色点”，这里给待评课程默认显示“待评” -->
						<text class="course-type">{{ (course.course_type !== undefined && course.course_type !== null && String(course.course_type).trim()) ? String(course.course_type).trim() : '待评' }}</text>
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
import { request } from '../../common/request.js';

	export default {
	data() {
			return {
				// 当前导航项
				currentNav: 'pending',
				// 22300417陈俫坤开发：是否督导（决定待评课程筛选样式）
				isSupervisor: false,
				// 22300417陈俫坤开发：督导筛选模式 level=分级筛选 time=按时间筛选
				filterMode: 'level',
				// 课程列表数据
				courses: [],
				// 搜索关键词
				searchKeyword: '',
				// 22300417陈俫坤开发：督导筛选条件
				campusId: 1,
				collegeId: null,
				// 22300417陈俫坤开发：week 为空表示“全部周次”
				week: null,
				weekday: null,
				teacherId: null,
				colleges: [],
				pendingTeachers: [],
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
		this.initRoleFlags();
		this.loadColleges();
		this.getPendingCourses();
	},
	computed: {
		campusPickerNames() {
			return ['南宁', '桂林'];
		},
		campusIndex() {
			return this.campusId === 2 ? 1 : 0;
		},
		currentCampusName() {
			return this.campusId === 2 ? '桂林' : '南宁';
		},
		collegePickerNames() {
			const names = ['请选择'];
			(this.filteredColleges || []).forEach(c => names.push(c.college_name));
			return names;
		},
		filteredColleges() {
			const list = this.colleges || [];
			if (!this.isSupervisor) return list;
			if (this.filterMode !== 'level') return list;
			// 22300417陈俫坤开发：若学院未配置 campus_id，则默认视为南宁(1)，避免下拉无数据
			return list.filter(c => {
				const cid = (c && c.campus_id !== undefined && c.campus_id !== null) ? Number(c.campus_id) : 1;
				return cid === Number(this.campusId || 1);
			});
		},
		collegeIndex() {
			if (!this.collegeId) return 0;
			const idx = (this.filteredColleges || []).findIndex(c => Number(c.id) === Number(this.collegeId));
			return idx >= 0 ? idx + 1 : 0;
		},
		currentCollegeName() {
			if (!this.collegeId) return '请选择';
			const c = (this.colleges || []).find(x => Number(x.id) === Number(this.collegeId));
			return c ? c.college_name : '请选择';
		},
		weekPickerNames() {
			const names = ['全部'];
			for (let i = 1; i <= 30; i++) names.push(`第${i}周`);
			return names;
		},
		weekIndex() {
			if (!this.week) return 0;
			const w = Number(this.week);
			if (w < 1 || w > 30) return 0;
			return w;
		},
		currentWeekName() {
			return this.week ? `第${this.week}周` : '全部';
		},
		weekdayPickerNames() {
			return ['请选择', '周一', '周二', '周三', '周四', '周五', '周六', '周日'];
		},
		weekdayIndex() {
			if (!this.weekday) return 0;
			const d = Number(this.weekday);
			if (d < 1 || d > 7) return 0;
			return d;
		},
		currentWeekdayName() {
			return this.weekday ? this.weekdayPickerNames[this.weekday] : '请选择';
		},
		teacherPickerNames() {
			const names = ['请选择'];
			(this.pendingTeachers || []).forEach(t => names.push(t.teacher_name || String(t.teacher_id)));
			return names;
		},
		teacherIndex() {
			if (!this.teacherId) return 0;
			const idx = (this.pendingTeachers || []).findIndex(t => Number(t.teacher_id) === Number(this.teacherId));
			return idx >= 0 ? idx + 1 : 0;
		},
		currentTeacherName() {
			if (!this.teacherId) return '请选择';
			const t = (this.pendingTeachers || []).find(x => Number(x.teacher_id) === Number(this.teacherId));
			return t ? (t.teacher_name || String(t.teacher_id)) : '请选择';
		}
	},
	methods: {
		// 22300417陈俫坤开发：从本地 userInfo 判断是否督导
		initRoleFlags() {
			try {
				const userInfo = uni.getStorageSync('userInfo') || {};
				const roles = userInfo.roles_code || [];
				this.isSupervisor = Array.isArray(roles) && roles.includes('supervisor');
				if (this.isSupervisor) {
					this.collegeId = userInfo.college_id || null;
				}
			} catch (e) {
				this.isSupervisor = false;
			}
		},
		// 22300417陈俫坤开发：加载学院列表（含 campus_id）
		async loadColleges() {
			try {
				const res = await request({
					url: '/org/colleges',
					method: 'GET',
					params: { skip: 0, limit: 200 }
				});
				this.colleges = (res && res.list) ? res.list : [];
				if (this.isSupervisor && this.collegeId) {
					const c = (this.colleges || []).find(x => Number(x.id) === Number(this.collegeId));
					if (c && c.campus_id) this.campusId = Number(c.campus_id);
				}
				// 22300417陈俫坤开发：学院加载完成后，若已具备筛选条件则预加载教师下拉
				if (this.isSupervisor && this.collegeId && this.week) {
					this.loadPendingTeachers();
				}
			} catch (e) {
				this.colleges = [];
				uni.showToast({
					title: '学院列表加载失败',
					icon: 'none',
					duration: 2000
				});
			}
		},
		switchFilterMode(mode) {
			this.filterMode = mode;
			this.teacherId = null;
			this.pendingTeachers = [];
			this.courses = [];
			// 22300417陈俫坤开发：切换模式后刷新可选教师列表
			if (this.isSupervisor) {
				this.loadPendingTeachers();
			}
		},
		handleCampusChange(e) {
			const idx = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			this.campusId = idx === 1 ? 2 : 1;
			this.collegeId = null;
			this.teacherId = null;
			this.pendingTeachers = [];
		},
		handleCollegeChange(e) {
			const index = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			if (index <= 0) {
				this.collegeId = null;
				this.teacherId = null;
				this.pendingTeachers = [];
				return;
			}
			const c = (this.filteredColleges || [])[index - 1];
			this.collegeId = c ? c.id : null;
			this.teacherId = null;
			this.pendingTeachers = [];
			// 22300417陈俫坤开发：学院变更后刷新可选教师列表
			this.loadPendingTeachers();
		},
		handleWeekChange(e) {
			const index = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			this.week = index <= 0 ? null : index;
			this.teacherId = null;
			this.pendingTeachers = [];
			// 22300417陈俫坤开发：周次变更后刷新可选教师列表
			this.loadPendingTeachers();
		},
		handleWeekdayChange(e) {
			const index = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			this.weekday = index <= 0 ? null : index;
			this.teacherId = null;
			this.pendingTeachers = [];
			// 22300417陈俫坤开发：星期变更后刷新可选教师列表
			this.loadPendingTeachers();
		},
		handleTeacherChange(e) {
			const index = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			if (index <= 0) {
				this.teacherId = null;
				return;
			}
			const t = (this.pendingTeachers || [])[index - 1];
			this.teacherId = t ? t.teacher_id : null;
		},
		// 22300417陈俫坤开发：获取待评教师列表（用于督导筛选）
		async loadPendingTeachers() {
			if (!this.collegeId) {
				this.pendingTeachers = [];
				return;
			}
			if (this.filterMode === 'time' && !this.weekday) {
				this.pendingTeachers = [];
				return;
			}
			try {
				const res = await request({
					url: '/eval/pending-teachers',
					method: 'GET',
					params: {
						campus_id: this.filterMode === 'level' ? this.campusId : undefined,
						college_id: this.collegeId,
						week: this.week || undefined,
						weekday: this.filterMode === 'time' ? this.weekday : undefined
					}
				});
				this.pendingTeachers = (res && res.list) ? res.list : [];
			} catch (e) {
				this.pendingTeachers = [];
				uni.showToast({
					title: '教师列表加载失败',
					icon: 'none',
					duration: 2000
				});
			}
		},
		applySupervisorFilters() {
			this.currentPage = 1;
			this.handleSearchTimerCleanup();
			this.getPendingCourses();
		},
		resetSupervisorFilters() {
			const userInfo = uni.getStorageSync('userInfo') || {};
			this.filterMode = 'level';
			this.campusId = 1;
			this.collegeId = userInfo.college_id || null;
			this.week = 1;
			this.weekday = null;
			this.teacherId = null;
			this.pendingTeachers = [];
			this.courses = [];
		},
		handleSearchTimerCleanup() {
			if (this.searchTimer) {
				clearTimeout(this.searchTimer);
				this.searchTimer = null;
			}
		},
		// 兼容 web 和微信小程序的输入处理
		handleSearchKeywordInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.searchKeyword = value;
			// 22300417陈俫坤开发：输入即触发搜索（防抖由 handleSearch 统一处理）
			this.handleSearch();
		},
		// 获取待评课程列表
		async getPendingCourses() {
			this.loading = true;
			try {
				if (this.isSupervisor) {
					await this.loadPendingTeachers();
					if (!this.collegeId) {
						this.courses = [];
						this.totalPages = 1;
						return;
					}
					if (this.filterMode === 'time' && !this.weekday) {
						this.courses = [];
						this.totalPages = 1;
						return;
					}
					if (!this.teacherId) {
						this.courses = [];
						this.totalPages = 1;
						return;
					}
				}

				const res = await request({
					url: '/eval/pending-courses',
					method: 'GET',
					params: {
						page: this.currentPage,
						page_size: this.pageSize,
						// 22300417陈俫坤开发：关键词模糊搜索（课程名/教师名）；兼容旧参数 course_name
						keyword: this.searchKeyword,
						course_name: this.searchKeyword,
						// 22300417陈俫坤开发：督导待评筛选参数
						campus_id: this.isSupervisor && this.filterMode === 'level' ? this.campusId : undefined,
						college_id: this.isSupervisor ? this.collegeId : undefined,
						week: this.isSupervisor ? (this.week || undefined) : undefined,
						weekday: this.isSupervisor && this.filterMode === 'time' ? this.weekday : undefined,
						teacher_id: this.isSupervisor ? this.teacherId : undefined
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
					// 22300417陈俫坤开发：修复导航错误 - tabBar页面使用switchTab
					uni.switchTab({
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

 .filter-section {
	padding: 20rpx 30rpx;
	background-color: #FFFFFF;
 }

 .filter-mode-tabs {
	display: flex;
	background-color: #F5F7FA;
	border-radius: 12rpx;
	overflow: hidden;
	margin-bottom: 20rpx;
 }

 .filter-mode-tab {
	flex: 1;
	text-align: center;
	padding: 18rpx 10rpx;
	font-size: 26rpx;
	color: #666666;
 }

 .filter-mode-tab.active {
	color: #FFFFFF;
	background-color: #3E5C76;
	font-weight: 600;
 }

 .filter-grid {
	display: grid;
	grid-template-columns: repeat(2, 1fr);
	gap: 20rpx;
 }

 .filter-item {
	background-color: #F5F7FA;
	border-radius: 12rpx;
	padding: 18rpx;
 }

 .filter-label {
	display: block;
	font-size: 24rpx;
	color: #666666;
	margin-bottom: 10rpx;
 }

 .filter-input {
	background-color: #FFFFFF;
	border-radius: 10rpx;
	padding: 16rpx 18rpx;
	font-size: 26rpx;
	color: #333333;
 }

 .filter-actions {
	display: flex;
	gap: 20rpx;
	margin-top: 20rpx;
 }

 .filter-btn {
	flex: 1;
	height: 72rpx;
	line-height: 72rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 28rpx;
	border-radius: 36rpx;
 }

 .filter-btn.secondary {
	background-color: #FFFFFF;
	color: #3E5C76;
	border: 2rpx solid #3E5C76;
 }

 .filter-btn::after {
	border: none;
 }
</style>