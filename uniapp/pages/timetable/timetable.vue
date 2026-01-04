<template>
	<view class="timetable-container">
		<!-- 22300417陈俫坤开发：Tab切换 - 我的课表/听课课表 -->
		<view class="mode-tabs">
			<view class="mode-tab" :class="mode === 'my' ? 'active' : ''" @tap="switchMode('my')">我的课表</view>
			<view class="mode-tab" :class="mode === 'listen' ? 'active' : ''" @tap="switchMode('listen')">听课课表</view>
		</view>

		<!-- 听课课表筛选条件：校区-学院-教师 -->
		<view class="listen-filter-section" v-if="mode === 'listen'">
			<view class="filter-row">
				<view class="filter-item">
					<text class="filter-label">校区</text>
					<picker mode="selector" :range="campusNames" :value="campusIndex" @change="handleCampusChange">
						<view class="filter-picker">{{ campusNames[campusIndex] || '全部' }}</view>
					</picker>
				</view>
				<view class="filter-item">
					<text class="filter-label">学院</text>
					<picker mode="selector" :range="collegeNames" :value="collegeIndex" @change="handleCollegeChange">
						<view class="filter-picker">{{ collegeNames[collegeIndex] || '全部' }}</view>
					</picker>
				</view>
			</view>
			<view class="filter-row">
				<view class="filter-item" style="flex: 1;">
					<text class="filter-label">教师</text>
					<picker mode="selector" :range="teacherPickerNames" :value="teacherIndex" @change="handleTeacherChange">
						<view class="filter-picker">{{ currentTeacherName }}</view>
					</picker>
				</view>
			</view>
			<view class="listen-tip" v-if="!selectedTeacherId">
				<text class="tip-text">请选择教师查看课表</text>
			</view>
		</view>

		<!-- 周次切换 -->
		<view class="week-switcher">
			<text class="week-btn" @tap="prevWeek" :disabled="currentWeek <= 1">
				<text class="arrow">←</text> 上一周
			</text>
			<view class="current-week">
				<view class="week-center">
					<text class="week-text">第{{ currentWeek }}周</text>
					<text class="week-range">{{ weekRangeText }}</text>
					<!-- 22300417陈俫坤开发：可视化设置“第1周周一日期”，用于计算周次与表头日期 -->
					<picker mode="date" :value="termStartDate" @change="handleTermStartDateChange">
						<view class="term-setting">
							<text class="term-setting-btn">设置第1周周一</text>
							<text class="term-setting-date">{{ termStartDate }}</text>
						</view>
					</picker>
				</view>
			</view>
			<text class="week-btn" @tap="nextWeek" :disabled="currentWeek >= totalWeeks">
				下一周 <text class="arrow">→</text>
			</text>
		</view>
		
		<!-- 课表表格 -->
		<view class="timetable-scroll-container">
			<view class="timetable-section">
				<!-- 22300417陈俫坤开发：表头按参考图改为两行：星期行 + 日期行；左侧显示本周起始月 -->
				<view class="timetable-header">
					<view class="header-month">
						<text class="month-text">{{ weekStartMonthText }}</text>
					</view>
					<view class="header-weekday" v-for="day in days" :key="day.value">
						<text class="weekday-text">{{ day.label }}</text>
					</view>
					<view
						class="header-date"
						:class="{ today: isToday(day.value) }"
						v-for="day in days"
						:key="String(day.value) + '_date'"
					>
						<text class="date-text">{{ getHeaderDateText(day.value) }}</text>
					</view>
				</view>
				
				<view class="timetable-body">
					<!-- 每节课的行 -->
					<view class="timetable-row" v-for="(row, rowIndex) in rows" :key="rowIndex">
						<!-- 时间列 -->
						<view class="time-column">
							<view class="time-cell">
								<text class="time-no">{{ row.no }}</text>
								<view class="time-ranges">
									<text class="time-range" v-for="(t, idx) in row.ranges" :key="idx">{{ t }}</text>
								</view>
							</view>
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
						<text class="detail-label">上课人数：</text>
						<text class="detail-value">{{ (selectedCourse.student_count === 0 || selectedCourse.student_count) ? selectedCourse.student_count : '—' }}</text>
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
import { request } from '../../common/request.js';

export default {
	computed: {
		// 22300417陈俫坤开发：校区名称列表
		campusNames() {
			const names = ['全部校区'];
			(this.campusList || []).forEach(c => names.push(c.campus_name || ''));
			return names;
		},
		// 22300417陈俫坤开发：学院名称列表（根据校区筛选）
		collegeNames() {
			const names = ['全部学院'];
			(this.filteredCollegeList || []).forEach(c => names.push(c.college_name || ''));
			return names;
		},
		teacherPickerNames() {
			const names = ['全部教师'];
			(this.teacherList || []).forEach(t => names.push(`${t.user_name || ''}${t.user_on ? '(' + t.user_on + ')' : ''}`));
			return names;
		},
		teacherIndex() {
			if (!this.selectedTeacherId) return 0;
			const idx = (this.teacherList || []).findIndex(t => Number(t.id) === Number(this.selectedTeacherId));
			return idx >= 0 ? idx + 1 : 0;
		},
		currentTeacherName() {
			if (!this.selectedTeacherId) return '全部教师';
			const t = (this.teacherList || []).find(x => Number(x.id) === Number(this.selectedTeacherId));
			return t ? `${t.user_name || ''}${t.user_on ? '(' + t.user_on + ')' : ''}` : '全部教师';
		},
		// 22300417陈俫坤开发：当前周日期范围展示（年月日）
		weekRangeText() {
			if (!this.weekDates || this.weekDates.length === 0) return '';
			const first = this.weekDates[0] ? this.weekDates[0].date : null;
			const lastItem = this.weekDates[this.weekDates.length - 1];
			const last = lastItem ? lastItem.date : null;
			if (!first || !last) return '';
			return `${this.formatYmd(first)} 至 ${this.formatYmd(last)}`;
		},
		// 22300417陈俫坤开发：左侧月份显示本周周一所在月份（参考图：12月）
		weekStartMonthText() {
			if (!this.weekDates || this.weekDates.length === 0) return '';
			const first = this.weekDates[0] ? this.weekDates[0].date : null;
			if (!first) return '';
			return `${first.getMonth() + 1}月`;
		}
	},
	data() {
			return {
				// 22300417陈俫坤开发：Tab模式 my=我的课表, listen=听课课表
				mode: 'my',
				// 当前周次
				currentWeek: 1,
				// 总周数
				totalWeeks: 20,
				// 22300417陈俫坤开发：学期第1周周一日期（用于计算每周的年月日显示，可按实际校历调整）
				// 为空则自动设置为本周周一
				termStartDate: '',
				// 星期列表
				days: [
					// 22300417陈俫坤开发：表头不展示"周"字，仅展示一至日
					{ label: '一', value: 1 },
					{ label: '二', value: 2 },
					{ label: '三', value: 3 },
					{ label: '四', value: 4 },
					{ label: '五', value: 5 },
					{ label: '六', value: 6 },
					{ label: '日', value: 7 }
				],
				// 22300417陈俫坤开发：节次轴改为数字 + 具体时间段（可按你学校作息修改 ranges）
				rows: [
					{ no: 1, ranges: ['08:30-09:15', '09:20-10:05'] },
					{ no: 2, ranges: ['10:25-11:10', '11:15-12:00'] },
					{ no: 3, ranges: ['14:00-14:45', '14:50-15:35'] },
					{ no: 4, ranges: ['15:55-16:40', '16:45-17:30'] },
					{ no: 5, ranges: ['19:00-19:45', '19:50-20:35'] },
					{ no: 6, ranges: ['20:45-21:30', '21:35-22:20'] }
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
				// 22300417陈俫坤开发：学院管理员查看本学院教师课表（显示筛选栏）
				isCollegeAdmin: false,
				showSearchBar: false,
				// 22300417陈俫坤开发：缓存当周日期（用于表头展示月/日）
				weekDates: [],
				// 22300417陈俫坤开发：学院管理员选择教师
				teacherList: [],
				selectedTeacherId: null,
				// 课程类型选项
				courseTypeOptions: [
					{ label: '空', value: '' },
					{ label: '待评', value: '待评' },
					{ label: '已评', value: '已评' }
				],
				// 22300417陈俫坤开发：听课课表筛选 - 校区/学院列表
				campusList: [],
				collegeList: [],
				filteredCollegeList: [],
				campusIndex: 0,
				collegeIndex: 0,
				selectedCampusId: null,
				selectedCollegeId: null
				};
		},
	onLoad() {
		this.initRoleFlags();
		this.initTimetableUi();
		this.loadCampusList();
		this.loadCollegeList();
		this.getTimetable();
	},
	methods: {
		// 22300417陈俫坤开发：Tab切换
		switchMode(mode) {
			this.mode = mode;
			this.courses = [];
			if (mode === 'listen') {
				this.loadTeachersByCollege();
			}
			this.getTimetable();
		},
		// 22300417陈俫坤开发：加载校区列表
		async loadCampusList() {
			try {
				const res = await request({ url: '/org/campuses', method: 'GET' });
				this.campusList = (res && res.list) ? res.list : [];
			} catch (e) {
				this.campusList = [];
			}
		},
		// 22300417陈俫坤开发：加载学院列表
		async loadCollegeList() {
			try {
				const res = await request({ url: '/org/colleges', method: 'GET' });
				this.collegeList = (res && res.list) ? res.list : [];
				this.filteredCollegeList = this.collegeList;
			} catch (e) {
				this.collegeList = [];
				this.filteredCollegeList = [];
			}
		},
		// 22300417陈俫坤开发：校区选择变化
		handleCampusChange(e) {
			const index = Number(e.detail.value) || 0;
			this.campusIndex = index;
			if (index <= 0) {
				this.selectedCampusId = null;
				this.filteredCollegeList = this.collegeList;
			} else {
				const campus = this.campusList[index - 1];
				this.selectedCampusId = campus ? campus.id : null;
				this.filteredCollegeList = this.collegeList.filter(c => c.campus_id === this.selectedCampusId);
			}
			this.collegeIndex = 0;
			this.selectedCollegeId = null;
			this.loadTeachersByCollege();
			this.getTimetable();
		},
		// 22300417陈俫坤开发：学院选择变化
		handleCollegeChange(e) {
			const index = Number(e.detail.value) || 0;
			this.collegeIndex = index;
			if (index <= 0) {
				this.selectedCollegeId = null;
			} else {
				const college = this.filteredCollegeList[index - 1];
				this.selectedCollegeId = college ? college.id : null;
			}
			this.loadTeachersByCollege();
			this.getTimetable();
		},
		// 22300417陈俫坤开发：根据学院加载教师列表
		async loadTeachersByCollege() {
			try {
				const params = { skip: 0, limit: 200 };
				if (this.selectedCollegeId) params.college_id = this.selectedCollegeId;
				if (this.searchKeyword) params.keyword = this.searchKeyword;
				const res = await request({ url: '/org/teachers', method: 'GET', params });
				this.teacherList = (res && res.list) ? res.list : [];
			} catch (e) {
				this.teacherList = [];
			}
		},
		initRoleFlags() {
			try {
				const userInfo = uni.getStorageSync('userInfo') || {};
				const roles = userInfo.roles_code || [];
				this.isCollegeAdmin = Array.isArray(roles) && roles.includes('college_admin');
			} catch (e) {
				this.isCollegeAdmin = false;
			}
		},
		// 22300417陈俫坤开发：初始化课表UI（搜索栏权限 + 周次日期显示）
		initTimetableUi() {
			// 22300417陈俫坤开发：学院管理员可查看本学院课表并筛选教师；其他角色仅看我的课表
			this.showSearchBar = !!this.isCollegeAdmin;
			this.loadTermStartDate();
			this.ensureTermStartDate();
			this.initWeekFromToday();
			this.updateWeekDates();
		},
		// 22300417陈俫坤开发：加载本学院教师列表供学院管理员选择
		async loadCollegeTeachers() {
			try {
				const res = await request({
					url: '/org/teachers',
					method: 'GET',
					params: {
						keyword: this.searchKeyword || undefined,
						skip: 0,
						limit: 200
					}
				});
				this.teacherList = (res && res.list) ? res.list : [];
			} catch (e) {
				this.teacherList = [];
				uni.showToast({
					title: '教师列表获取失败',
					icon: 'none',
					duration: 2000
				});
			}
		},
		handleTeacherChange(e) {
			const index = (e && e.detail && e.detail.value !== undefined) ? Number(e.detail.value) : 0;
			if (index <= 0) {
				this.selectedTeacherId = null;
				this.getTimetable();
				return;
			}
			const t = (this.teacherList || [])[index - 1];
			this.selectedTeacherId = t ? t.id : null;
			this.getTimetable();
		},
		// 22300417陈俫坤开发：读取本地缓存的“第1周周一日期”
		loadTermStartDate() {
			try {
				const val = uni.getStorageSync('timetable_termStartDate');
				if (val) this.termStartDate = String(val);
			} catch (e) {
				// ignore
			}
		},
		// 22300417陈俫坤开发：若未配置学期第1周周一日期，则自动使用本周周一
		ensureTermStartDate() {
			if (this.termStartDate && String(this.termStartDate).trim()) return;
			const today = new Date();
			const day = today.getDay();
			const diff = day === 0 ? 6 : (day - 1);
			const monday = new Date(today.getFullYear(), today.getMonth(), today.getDate() - diff);
			this.termStartDate = this.formatYmd(monday);
		},
		// 22300417陈俫坤开发：手动设置“第1周周一日期”，并立即重算周次与表头
		handleTermStartDateChange(e) {
			const value = e && e.detail ? e.detail.value : '';
			if (!value) return;
			this.termStartDate = value;
			try {
				uni.setStorageSync('timetable_termStartDate', value);
			} catch (err) {
				// ignore
			}
			this.initWeekFromToday();
			this.updateWeekDates();
		},
		// 22300417陈俫坤开发：根据 termStartDate 计算今天对应的周次（用于默认显示第几周）
		initWeekFromToday() {
			try {
				const start = this.parseDate(this.termStartDate);
				const today = new Date();
				const diffDays = Math.floor((today.getTime() - start.getTime()) / (24 * 3600 * 1000));
				const week = Math.floor(diffDays / 7) + 1;
				if (week >= 1 && week <= this.totalWeeks) {
					this.currentWeek = week;
				}
			} catch (e) {
				// ignore
			}
		},
		// 22300417陈俫坤开发：解析 YYYY-MM-DD
		parseDate(dateStr) {
			const parts = String(dateStr || '').split('-');
			if (parts.length !== 3) return new Date();
			const y = parseInt(parts[0]);
			const m = parseInt(parts[1]);
			const d = parseInt(parts[2]);
			return new Date(y, m - 1, d);
		},
		// 22300417陈俫坤开发：格式化年月日
		formatYmd(date) {
			const y = date.getFullYear();
			const m = String(date.getMonth() + 1).padStart(2, '0');
			const d = String(date.getDate()).padStart(2, '0');
			return `${y}-${m}-${d}`;
		},
		// 22300417陈俫坤开发：格式化月/日
		formatMd(date) {
			const m = date.getMonth() + 1;
			const d = date.getDate();
			return `${m}/${d}`;
		},
		// 22300417陈俫坤开发：更新当前周的日期数组（周一到周日）
		updateWeekDates() {
			const start = this.parseDate(this.termStartDate);
			const weekStart = new Date(start.getTime() + (this.currentWeek - 1) * 7 * 24 * 3600 * 1000);
			this.weekDates = this.days.map((day) => {
				const dt = new Date(weekStart.getTime() + (day.value - 1) * 24 * 3600 * 1000);
				return { value: day.value, date: dt };
			});
		},
		// 22300417陈俫坤开发：日期行显示规则：跨月时当月1号显示“X月”，其余显示日（参考图：1月）
		getHeaderDateText(dayValue) {
			const hit = (this.weekDates || []).find((x) => x.value === dayValue);
			if (!hit || !hit.date) return '';
			const m = hit.date.getMonth() + 1;
			const d = hit.date.getDate();
			if (d === 1) return `${m}月`;
			return `${d}`;
		},
		// 22300417陈俫坤开发：高亮今天日期（参考图：黑底）
		isToday(dayValue) {
			const hit = (this.weekDates || []).find((x) => x.value === dayValue);
			if (!hit || !hit.date) return false;
			const today = new Date();
			return this.formatYmd(hit.date) === this.formatYmd(today);
		},
		// 兼容 web 和微信小程序的输入处理
		handleSearchKeywordInput(e) {
			const value = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e && e.target ? e.target.value : '');
			this.searchKeyword = value;
		},
		// 获取课表数据
		async getTimetable() {
			try {
				const userInfo = uni.getStorageSync('userInfo') || {};
				
				// 22300417陈俫坤开发：听课课表必须选择教师才显示
				if (this.mode === 'listen' && !this.selectedTeacherId) {
					this.courses = [];
					return;
				}
				
				// 构造请求参数
				const params = {
					academic_year: this.currentAcademicYear,
					semester: this.currentSemester,
					skip: 0,
					limit: 100
				};
				
				// 22300417陈俫坤开发：根据Tab模式决定查询参数
				if (this.mode === 'my') {
					// 我的课表：只查当前用户的课表
					params.teacher_id = userInfo.id || '';
				} else {
					// 听课课表：必须选择教师
					params.teacher_id = this.selectedTeacherId;
				}
				
				// 22300417陈俫坤开发：后端路由为 /api/v1/teaching-eval/org/timetables
				// request.js 会自动拼 baseUrl，这里只写相对路径 /org/timetables
				// 调用课表接口，包含所有必要的查询参数
				const res = await request({
					url: '/org/timetables',
					method: 'GET',
					params: params
				});
				if (res && res.list) {
					// 将API返回的数据转换为课程数组
					this.courses = res.list.map(course => {
						// 22300417陈俫坤开发：将 period 转换为 time_slot（与 rows 的下标对应）
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
							// 22300417陈俫坤开发：上课人数（后端字段 student_count）
							student_count: course.student_count,
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
				// 22300417陈俫坤开发：学院管理员搜索时同时刷新教师列表（按关键词过滤）
				if (this.isCollegeAdmin) {
					this.loadCollegeTeachers();
				}
				// 无论搜索关键词是否为空，都重新获取课表
				this.getTimetable();
			},
		
		// 上一周
		prevWeek() {
			if (this.currentWeek > 1) {
				this.currentWeek--;
				// 22300417陈俫坤开发：周次切换后更新日期显示
				this.updateWeekDates();
				// 周次切换暂时不重新获取数据，因为API不支持按周次过滤
			}
		},
		
		// 下一周
		nextWeek() {
			if (this.currentWeek < this.totalWeeks) {
				this.currentWeek++;
				// 22300417陈俫坤开发：周次切换后更新日期显示
				this.updateWeekDates();
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

/* 22300417陈俫坤开发：统一盒模型 */
.timetable-container,
.timetable-container view,
.timetable-container text,
.timetable-container button,
.timetable-container input {
	box-sizing: border-box;
}

/* 22300417陈俫坤开发：Tab切换样式 */
.mode-tabs {
	display: flex;
	background-color: #FFFFFF;
	border-radius: 12rpx;
	overflow: hidden;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}
.mode-tab {
	flex: 1;
	text-align: center;
	padding: 22rpx 10rpx;
	font-size: 28rpx;
	color: #666666;
	background-color: #FFFFFF;
}
.mode-tab.active {
	color: #FFFFFF;
	background-color: #3E5C76;
	font-weight: 600;
}

/* 22300417陈俫坤开发：听课课表筛选区域 */
.listen-filter-section {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	padding: 20rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}
.filter-row {
	display: flex;
	gap: 20rpx;
	margin-bottom: 20rpx;
}
.filter-row:last-child {
	margin-bottom: 0;
}
.filter-item {
	flex: 1;
}
.filter-label {
	display: block;
	font-size: 26rpx;
	color: #333333;
	margin-bottom: 10rpx;
}
.filter-picker {
	height: 70rpx;
	line-height: 70rpx;
	border: 2rpx solid #E4E7ED;
	border-radius: 8rpx;
	padding: 0 20rpx;
	font-size: 26rpx;
	color: #333333;
	background-color: #F5F7FA;
}
.search-item {
	display: flex;
	align-items: flex-end;
	gap: 10rpx;
}
.search-input-box {
	flex: 1;
	height: 70rpx;
	border: 2rpx solid #E4E7ED;
	border-radius: 8rpx;
	padding: 0 20rpx;
	font-size: 26rpx;
	background-color: #F5F7FA;
}
.search-btn-small {
	height: 70rpx;
	line-height: 70rpx;
	padding: 0 30rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 26rpx;
	border-radius: 8rpx;
}

/* 22300417陈俫坤开发：听课课表提示 */
.listen-tip {
	text-align: center;
	padding: 20rpx;
	margin-top: 10rpx;
}
.tip-text {
	font-size: 26rpx;
	color: #999999;
}

/* 搜索和筛选 */
.search-filter-section {
	display: flex;
	flex-wrap: wrap;
	justify-content: space-between;
	align-items: center;
	background-color: #FFFFFF;
	padding: 20rpx;
	border-radius: 12rpx;
	margin-bottom: 20rpx;
	box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	gap: 20rpx;
}

/* 22300417陈俫坤开发：学院管理员教师选择器 */
.teacher-picker {
	display: flex;
	align-items: center;
	gap: 16rpx;
	width: 100%;
	margin-bottom: 10rpx;
}

.picker-label {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
	white-space: nowrap;
}

.teacher-picker .picker-input {
	flex: 1;
	height: 72rpx;
	line-height: 72rpx;
	background-color: #F5F7FA;
	border-radius: 8rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #333333;
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

.week-center {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 6rpx;
}

.week-range {
	font-size: 22rpx;
	color: rgba(51, 51, 51, 0.75);
}

.term-setting {
	display: flex;
	align-items: center;
	gap: 10rpx;
	padding: 8rpx 14rpx;
	border-radius: 999rpx;
	background-color: #F5F7FA;
}

.term-setting-btn {
	font-size: 22rpx;
	color: #3E5C76;
	font-weight: 600;
}

.term-setting-date {
	font-size: 22rpx;
	color: #666666;
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
	font-size: 30rpx;
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
	/* 22300417陈俫坤开发：统一表头/表格列宽定义，保证严格对齐 */
	--time-col-width: 130rpx;
	--day-col-width: minmax(90rpx, 1fr);
}

.timetable-header {
	/* 22300417陈俫坤开发：两行表头（星期行+日期行），左侧月份占两行 */
	display: grid;
	/* 左侧列宽必须与课表内容的 time-column 一致，避免错位 */
	grid-template-columns: var(--time-col-width) repeat(7, var(--day-col-width));
	grid-template-rows: 56rpx 56rpx;
	background-color: #FFFFFF;
	border-bottom: 1rpx solid #E4E7ED;
}

/* 22300417陈俫坤开发：所有表格单元统一盒模型，避免 border/padding 导致的对齐偏差 */
.header-month,
.header-weekday,
.header-date,
.time-column,
.course-column {
	box-sizing: border-box;
}

.header-month {
	grid-column: 1;
	grid-row: 1 / 3;
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: #E9EDF2;
	border-right: 1rpx solid #E4E7ED;
}

.month-text {
	font-size: 22rpx;
	font-weight: 700;
	color: #3E5C76;
}

.header-weekday {
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: #3E5C76;
	color: #FFFFFF;
	border-right: 1rpx solid rgba(255, 255, 255, 0.25);
}

.header-weekday:nth-child(8) {
	border-right: none;
}

.weekday-text {
	font-size: 22rpx;
	font-weight: 700;
}

.header-date {
	display: flex;
	justify-content: center;
	align-items: center;
	background-color: #FFFFFF;
	color: #666666;
	border-right: 1rpx solid #E4E7ED;
	border-top: 1rpx solid #E4E7ED;
}

.header-date:nth-child(15) {
	border-right: none;
}

.date-text {
	font-size: 22rpx;
	font-weight: 600;
}

.header-date.today {
	background-color: #111111;
	color: #FFFFFF;
}

.header-date.today .date-text {
	color: #FFFFFF;
}

.timetable-body {
	display: flex;
	flex-direction: column;
}

.timetable-row {
	/* 22300417陈俫坤开发：内容行使用与表头相同的 grid 列定义，保证严格对齐 */
	display: grid;
	grid-template-columns: var(--time-col-width) repeat(7, var(--day-col-width));
	border-bottom: 1rpx solid #E4E7ED;
}

.timetable-row:last-child {
	border-bottom: none;
}


.time-cell {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	gap: 6rpx;
	padding: 8rpx 4rpx;
	width: 100%;
}

.time-no {
	font-size: 24rpx;
	font-weight: bold;
	color: #333333;
	line-height: 1;
}

.time-ranges {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 2rpx;
}

.time-range {
	font-size: 18rpx;
	color: #666666;
	line-height: 1.1;
}

.course-column {
	/* 22300417陈俫坤开发：由 grid 控制宽度，这里不再写 width/calc，避免错位 */
	min-height: 160rpx;
	min-width: 0;
	border-right: 1rpx solid #E4E7ED;
	padding: 8rpx 6rpx;
	display: flex;
	flex-direction: column;
	align-items: stretch;
	justify-content: flex-start;
	gap: 8rpx;
	background-color: #FFFFFF;
}

.course-column:last-child {
	border-right: none;
}

/* 课程卡片 */
.course-card {
	background-color: #E8F4F8;
	border: 2rpx solid #3E5C76;
	border-radius: 8rpx;
	padding: 10rpx;
	margin-bottom: 10rpx;
	width: 100%;
	min-height: 110rpx;
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
	font-size: 22rpx;
	font-weight: bold;
	color: #333333;
	margin-bottom: 6rpx;
	line-height: 1.2;
	max-height: 70rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	display: -webkit-box;
	line-clamp: 2;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
}

.course-teacher {
	display: block;
	font-size: 20rpx;
	color: #666666;
	margin-bottom: 4rpx;
	line-height: 1.2;
}

.course-room {
	display: block;
	font-size: 20rpx;
	color: #999999;
	line-height: 1.2;
	max-height: 50rpx;
	overflow: hidden;
	text-overflow: ellipsis;
	display: -webkit-box;
	line-clamp: 2;
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
	font-size: 22rpx;
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

/* 22300417陈俫坤开发：修复样式嵌套导致的解析异常（uniapp scoped style 不支持嵌套） */
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