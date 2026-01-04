<template>
	<view class="admin-container">
		<view class="page-header">
			<text class="page-title">组织架构管理</text>
		</view>

		<!-- Tab导航 -->
		<view class="tabs">
			<view class="tab" :class="{ active: activeTab === 'campus' }" @tap="switchTab('campus')">校区管理</view>
			<view class="tab" :class="{ active: activeTab === 'college' }" @tap="switchTab('college')">学院管理</view>
			<view class="tab" :class="{ active: activeTab === 'room' }" @tap="switchTab('room')">教研室管理</view>
			<view class="tab" :class="{ active: activeTab === 'teacher' }" @tap="switchTab('teacher')">教师归属</view>
		</view>

		<!-- 校区管理 -->
		<view v-if="activeTab === 'campus'" class="content-section">
			<view class="toolbar">
				<button class="primary-btn" @tap="openCampusCreate">新增校区</button>
				<button class="ghost-btn" @tap="loadCampuses">刷新</button>
			</view>
			<view class="list-card" v-if="campuses.length">
				<view class="item" v-for="c in campuses" :key="c.id">
					<view class="item-header">
						<text class="item-title">{{ c.campus_name }}</text>
						<text class="item-sub">ID: {{ c.id }}</text>
					</view>
					<view class="item-actions">
						<button class="action-btn" @tap="openCampusEdit(c)">编辑</button>
						<button class="action-btn danger" @tap="deleteCampus(c)">删除</button>
					</view>
				</view>
			</view>
			<view v-else class="empty-state">
				<text class="empty-text">暂无校区数据</text>
			</view>
		</view>

		<!-- 学院管理 -->
		<view v-if="activeTab === 'college'" class="content-section">
			<view class="toolbar">
				<view class="filter-item">
					<picker mode="selector" :range="campusPickerNames" :value="collegeFilterCampusIndex" @change="handleCollegeFilterCampusChange">
						<view class="picker-btn">{{ currentCollegeFilterCampusName }}</view>
					</picker>
				</view>
				<button class="primary-btn" @tap="openCollegeCreate">新增学院</button>
				<button class="ghost-btn" @tap="loadColleges">刷新</button>
			</view>
			<view class="list-card" v-if="colleges.length">
				<view class="item" v-for="c in colleges" :key="c.id">
					<view class="item-header">
						<text class="item-title">{{ c.college_name }}</text>
						<text class="item-sub">{{ c.college_code }}</text>
					</view>
					<view class="item-info">
						<text class="info-text">校区：{{ getCampusName(c.campus_id) || '未设置' }}</text>
					</view>
					<view class="item-actions">
						<button class="action-btn" @tap="openCollegeEdit(c)">编辑</button>
						<button class="action-btn danger" @tap="deleteCollege(c)">删除</button>
					</view>
				</view>
			</view>
			<view v-else class="empty-state">
				<text class="empty-text">暂无学院数据</text>
			</view>
		</view>

		<!-- 教研室管理 -->
		<view v-if="activeTab === 'room'" class="content-section">
			<view class="toolbar">
				<view class="filter-item">
					<picker mode="selector" :range="collegePickerNames" :value="roomCollegeIndex" @change="handleRoomCollegeChange">
						<view class="picker-btn">{{ currentRoomCollegeName }}</view>
					</picker>
				</view>
				<button class="primary-btn" @tap="openRoomCreate">新增教研室</button>
				<button class="ghost-btn" @tap="loadRooms">刷新</button>
			</view>
			<view class="list-card" v-if="rooms.length">
				<view class="item" v-for="r in rooms" :key="r.id">
					<view class="item-header">
						<text class="item-title">{{ r.room_name }}</text>
						<text class="item-sub">{{ r.room_code }}</text>
					</view>
					<view class="item-info">
						<text class="info-text">所属学院：{{ getCollegeName(r.college_id) }}</text>
					</view>
					<view class="item-actions">
						<button class="action-btn" @tap="openRoomEdit(r)">编辑</button>
						<button class="action-btn danger" @tap="deleteRoom(r)">删除</button>
					</view>
				</view>
			</view>
			<view v-else class="empty-state">
				<text class="empty-text">暂无教研室数据</text>
			</view>
		</view>

		<!-- 教师归属管理 -->
		<view v-if="activeTab === 'teacher'" class="content-section">
			<view class="toolbar">
				<view class="filter-item">
					<picker mode="selector" :range="collegePickerNames" :value="teacherCollegeIndex" @change="handleTeacherCollegeChange">
						<view class="picker-btn">{{ currentTeacherCollegeName }}</view>
					</picker>
				</view>
				<button class="ghost-btn" @tap="loadTeachers">刷新</button>
			</view>
			<view class="list-card" v-if="teachers.length">
				<view class="item" v-for="t in teachers" :key="t.id">
					<view class="item-header">
						<text class="item-title">{{ t.user_name }}</text>
						<text class="item-sub">{{ t.user_on }}</text>
					</view>
					<view class="item-info">
						<text class="info-text">学院：{{ getCollegeName(t.college_id) || '未设置' }}</text>
						<text class="info-text">教研室：{{ getRoomName(t.research_room_id) || '未设置' }}</text>
					</view>
					<view class="item-actions">
						<button class="action-btn" @tap="openTeacherEdit(t)">设置归属</button>
					</view>
				</view>
			</view>
			<view v-else class="empty-state">
				<text class="empty-text">暂无教师数据</text>
			</view>
		</view>

		<!-- 校区编辑弹窗 -->
		<view class="modal" v-if="showCampusModal" @tap="closeCampusModal">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">{{ campusFormMode === 'create' ? '新增校区' : '编辑校区' }}</text>
					<text class="modal-close" @tap="closeCampusModal">×</text>
				</view>
				<view class="modal-body">
					<view class="form-item">
						<text class="form-label">校区名称</text>
						<input :value="campusForm.campus_name" placeholder="如 南宁校区、桂林校区" class="form-input" @input="e => campusForm.campus_name = e.detail.value" />
					</view>
					<button class="submit-btn" @tap="submitCampus">保存</button>
				</view>
			</view>
		</view>

		<!-- 学院编辑弹窗 -->
		<view class="modal" v-if="showCollegeModal" @tap="closeCollegeModal">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">{{ collegeFormMode === 'create' ? '新增学院' : '编辑学院' }}</text>
					<text class="modal-close" @tap="closeCollegeModal">×</text>
				</view>
				<view class="modal-body">
					<view class="form-item">
						<text class="form-label">所属校区</text>
						<picker mode="selector" :range="campusPickerNamesNoAll" :value="collegeFormCampusIndex" @change="handleCollegeFormCampusChange">
							<view class="form-picker">{{ collegeFormCampusName }}</view>
						</picker>
					</view>
					<view class="form-item">
						<text class="form-label">学院编码</text>
						<input :value="collegeForm.college_code" placeholder="如 CS、IE" class="form-input" @input="e => collegeForm.college_code = e.detail.value" />
					</view>
					<view class="form-item">
						<text class="form-label">学院名称</text>
						<input :value="collegeForm.college_name" placeholder="如 信息工程学院" class="form-input" @input="e => collegeForm.college_name = e.detail.value" />
					</view>
					<view class="form-item">
						<text class="form-label">简称</text>
						<input :value="collegeForm.short_name" placeholder="可选" class="form-input" @input="e => collegeForm.short_name = e.detail.value" />
					</view>
					<button class="submit-btn" @tap="submitCollege">保存</button>
				</view>
			</view>
		</view>

		<!-- 教研室编辑弹窗 -->
		<view class="modal" v-if="showRoomModal" @tap="closeRoomModal">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">{{ roomFormMode === 'create' ? '新增教研室' : '编辑教研室' }}</text>
					<text class="modal-close" @tap="closeRoomModal">×</text>
				</view>
				<view class="modal-body">
					<view class="form-item">
						<text class="form-label">所属学院</text>
						<picker mode="selector" :range="collegePickerNamesNoAll" :value="roomFormCollegeIndex" @change="handleRoomFormCollegeChange">
							<view class="form-picker">{{ roomFormCollegeName }}</view>
						</picker>
					</view>
					<view class="form-item">
						<text class="form-label">教研室编码</text>
						<input :value="roomForm.room_code" placeholder="如 SE、AI" class="form-input" @input="e => roomForm.room_code = e.detail.value" />
					</view>
					<view class="form-item">
						<text class="form-label">教研室名称</text>
						<input :value="roomForm.room_name" placeholder="如 软件工程教研室" class="form-input" @input="e => roomForm.room_name = e.detail.value" />
					</view>
					<button class="submit-btn" @tap="submitRoom">保存</button>
				</view>
			</view>
		</view>

		<!-- 教师归属编辑弹窗 -->
		<view class="modal" v-if="showTeacherModal" @tap="closeTeacherModal">
			<view class="modal-content" @tap.stop>
				<view class="modal-header">
					<text class="modal-title">设置教师归属</text>
					<text class="modal-close" @tap="closeTeacherModal">×</text>
				</view>
				<view class="modal-body">
					<view class="form-item">
						<text class="form-label">教师</text>
						<text class="form-value">{{ teacherForm.user_name }} ({{ teacherForm.user_on }})</text>
					</view>
					<view class="form-item">
						<text class="form-label">所属学院</text>
						<picker mode="selector" :range="collegePickerNamesNoAll" :value="teacherFormCollegeIndex" @change="handleTeacherFormCollegeChange">
							<view class="form-picker">{{ teacherFormCollegeName }}</view>
						</picker>
					</view>
					<view class="form-item">
						<text class="form-label">所属教研室</text>
						<picker mode="selector" :range="teacherFormRoomPickerNames" :value="teacherFormRoomIndex" @change="handleTeacherFormRoomChange">
							<view class="form-picker">{{ teacherFormRoomName }}</view>
						</picker>
					</view>
					<button class="submit-btn" @tap="submitTeacher">保存</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
import { request } from '../../common/request.js';

export default {
	data() {
		return {
			activeTab: 'campus',
			// 校区数据
			campuses: [],
			showCampusModal: false,
			campusFormMode: 'create',
			campusForm: { id: null, campus_name: '' },
			// 学院数据
			colleges: [],
			allColleges: [],
			collegeFilterCampusId: null,
			showCollegeModal: false,
			collegeFormMode: 'create',
			collegeForm: { id: null, campus_id: null, college_code: '', college_name: '', short_name: '' },
			// 教研室数据
			rooms: [],
			allRooms: [],
			roomCollegeId: null,
			showRoomModal: false,
			roomFormMode: 'create',
			roomForm: { id: null, college_id: null, room_code: '', room_name: '' },
			// 教师数据
			teachers: [],
			teacherCollegeId: null,
			showTeacherModal: false,
			teacherForm: { id: null, user_id: null, user_name: '', user_on: '', college_id: null, research_room_id: null },
			teacherFormRooms: []
		};
	},
	computed: {
		// 校区选择器
		campusPickerNames() {
			const names = ['全部校区'];
			this.campuses.forEach(c => names.push(c.campus_name));
			return names;
		},
		campusPickerNamesNoAll() {
			const names = ['请选择校区'];
			this.campuses.forEach(c => names.push(c.campus_name));
			return names;
		},
		collegeFilterCampusIndex() {
			if (!this.collegeFilterCampusId) return 0;
			const idx = this.campuses.findIndex(c => c.id === this.collegeFilterCampusId);
			return idx >= 0 ? idx + 1 : 0;
		},
		currentCollegeFilterCampusName() {
			if (!this.collegeFilterCampusId) return '全部校区';
			const c = this.campuses.find(x => x.id === this.collegeFilterCampusId);
			return c ? c.campus_name : '全部校区';
		},
		collegeFormCampusIndex() {
			if (!this.collegeForm.campus_id) return 0;
			const idx = this.campuses.findIndex(c => c.id === this.collegeForm.campus_id);
			return idx >= 0 ? idx + 1 : 0;
		},
		collegeFormCampusName() {
			if (!this.collegeForm.campus_id) return '请选择校区';
			const c = this.campuses.find(x => x.id === this.collegeForm.campus_id);
			return c ? c.campus_name : '请选择校区';
		},
		// 学院选择器
		collegePickerNames() {
			const names = ['全部学院'];
			this.allColleges.forEach(c => names.push(c.college_name));
			return names;
		},
		collegePickerNamesNoAll() {
			const names = ['请选择学院'];
			this.allColleges.forEach(c => names.push(c.college_name));
			return names;
		},
		roomCollegeIndex() {
			if (!this.roomCollegeId) return 0;
			const idx = this.colleges.findIndex(c => c.id === this.roomCollegeId);
			return idx >= 0 ? idx + 1 : 0;
		},
		currentRoomCollegeName() {
			if (!this.roomCollegeId) return '全部学院';
			const c = this.colleges.find(x => x.id === this.roomCollegeId);
			return c ? c.college_name : '全部学院';
		},
		teacherCollegeIndex() {
			if (!this.teacherCollegeId) return 0;
			const idx = this.colleges.findIndex(c => c.id === this.teacherCollegeId);
			return idx >= 0 ? idx + 1 : 0;
		},
		currentTeacherCollegeName() {
			if (!this.teacherCollegeId) return '全部学院';
			const c = this.colleges.find(x => x.id === this.teacherCollegeId);
			return c ? c.college_name : '全部学院';
		},
		roomFormCollegeIndex() {
			if (!this.roomForm.college_id) return 0;
			const idx = this.colleges.findIndex(c => c.id === this.roomForm.college_id);
			return idx >= 0 ? idx + 1 : 0;
		},
		roomFormCollegeName() {
			if (!this.roomForm.college_id) return '请选择学院';
			const c = this.colleges.find(x => x.id === this.roomForm.college_id);
			return c ? c.college_name : '请选择学院';
		},
		teacherFormCollegeIndex() {
			if (!this.teacherForm.college_id) return 0;
			const idx = this.colleges.findIndex(c => c.id === this.teacherForm.college_id);
			return idx >= 0 ? idx + 1 : 0;
		},
		teacherFormCollegeName() {
			if (!this.teacherForm.college_id) return '请选择学院';
			const c = this.colleges.find(x => x.id === this.teacherForm.college_id);
			return c ? c.college_name : '请选择学院';
		},
		teacherFormRoomPickerNames() {
			const names = ['请选择教研室'];
			this.teacherFormRooms.forEach(r => names.push(r.room_name));
			return names;
		},
		teacherFormRoomIndex() {
			if (!this.teacherForm.research_room_id) return 0;
			const idx = this.teacherFormRooms.findIndex(r => r.id === this.teacherForm.research_room_id);
			return idx >= 0 ? idx + 1 : 0;
		},
		teacherFormRoomName() {
			if (!this.teacherForm.research_room_id) return '请选择教研室';
			const r = this.teacherFormRooms.find(x => x.id === this.teacherForm.research_room_id);
			return r ? r.room_name : '请选择教研室';
		}
	},
	onLoad() {
		this.loadCampuses();
	},
	methods: {
		switchTab(tab) {
			this.activeTab = tab;
			if (tab === 'campus') this.loadCampuses();
			else if (tab === 'college') this.loadColleges();
			else if (tab === 'room') this.loadRooms();
			else if (tab === 'teacher') this.loadTeachers();
		},
		getCampusName(id) {
			if (!id) return '';
			const c = this.campuses.find(x => x.id === id);
			return c ? c.campus_name : '';
		},
		getCollegeName(id) {
			if (!id) return '';
			const c = this.allColleges.find(x => x.id === id);
			return c ? c.college_name : '';
		},
		getRoomName(id) {
			if (!id) return '';
			const r = this.allRooms.find(x => x.id === id);
			return r ? r.room_name : '';
		},
		// 校区管理
		async loadCampuses() {
			try {
				const res = await request({ url: '/org/campuses', method: 'GET', params: { skip: 0, limit: 100 } });
				this.campuses = (res && res.list) ? res.list : [];
			} catch (e) {
				this.campuses = [];
			}
		},
		openCampusCreate() {
			this.campusFormMode = 'create';
			this.campusForm = { id: null, campus_name: '' };
			this.showCampusModal = true;
		},
		openCampusEdit(c) {
			this.campusFormMode = 'edit';
			this.campusForm = { id: c.id, campus_name: c.campus_name };
			this.showCampusModal = true;
		},
		closeCampusModal() {
			this.showCampusModal = false;
		},
		async submitCampus() {
			const name = (this.campusForm.campus_name || '').trim();
			if (!name) {
				uni.showToast({ title: '请填写校区名称', icon: 'none' });
				return;
			}
			try {
				if (this.campusFormMode === 'create') {
					await request({ url: '/org/campuses', method: 'POST', data: this.campusForm });
					uni.showToast({ title: '创建成功', icon: 'success' });
				} else {
					await request({ url: `/org/campuses/${this.campusForm.id}`, method: 'PUT', data: this.campusForm });
					uni.showToast({ title: '更新成功', icon: 'success' });
				}
				this.closeCampusModal();
				this.loadCampuses();
			} catch (e) {
				uni.showToast({ title: '操作失败', icon: 'none' });
			}
		},
		async deleteCampus(c) {
			uni.showModal({
				title: '确认删除',
				content: `确定要删除校区“${c.campus_name}”吗？`,
				success: async (res) => {
					if (res.confirm) {
						try {
							await request({ url: `/org/campuses/${c.id}`, method: 'DELETE' });
							uni.showToast({ title: '删除成功', icon: 'success' });
							this.loadCampuses();
						} catch (e) {
							uni.showToast({ title: '删除失败', icon: 'none' });
						}
					}
				}
			});
		},
		// 学院管理
		handleCollegeFilterCampusChange(e) {
			const idx = Number(e.detail.value);
			this.collegeFilterCampusId = idx <= 0 ? null : (this.campuses[idx - 1]?.id || null);
			this.loadColleges();
		},
		handleCollegeFormCampusChange(e) {
			const idx = Number(e.detail.value);
			this.collegeForm.campus_id = idx <= 0 ? null : (this.campuses[idx - 1]?.id || null);
		},
		async loadColleges() {
			try {
				const params = { skip: 0, limit: 200 };
				if (this.collegeFilterCampusId) params.campus_id = this.collegeFilterCampusId;
				const res = await request({ url: '/org/colleges', method: 'GET', params });
				this.colleges = (res && res.list) ? res.list : [];
				// 同时加载所有学院用于其他选择器
				const allRes = await request({ url: '/org/colleges', method: 'GET', params: { skip: 0, limit: 500 } });
				this.allColleges = (allRes && allRes.list) ? allRes.list : [];
			} catch (e) {
				this.colleges = [];
			}
		},
		openCollegeCreate() {
			this.collegeFormMode = 'create';
			this.collegeForm = { id: null, campus_id: this.collegeFilterCampusId, college_code: '', college_name: '', short_name: '' };
			this.showCollegeModal = true;
		},
		openCollegeEdit(c) {
			this.collegeFormMode = 'edit';
			this.collegeForm = { id: c.id, campus_id: c.campus_id, college_code: c.college_code, college_name: c.college_name, short_name: c.short_name || '' };
			this.showCollegeModal = true;
		},
		closeCollegeModal() {
			this.showCollegeModal = false;
		},
		async submitCollege() {
			const code = (this.collegeForm.college_code || '').trim();
			const name = (this.collegeForm.college_name || '').trim();
			if (!code || !name) {
				uni.showToast({ title: '请填写学院编码和名称', icon: 'none' });
				return;
			}
			try {
				if (this.collegeFormMode === 'create') {
					await request({ url: '/org/college', method: 'POST', data: this.collegeForm });
					uni.showToast({ title: '创建成功', icon: 'success' });
				} else {
					await request({ url: `/org/college/${this.collegeForm.id}`, method: 'PUT', data: this.collegeForm });
					uni.showToast({ title: '更新成功', icon: 'success' });
				}
				this.closeCollegeModal();
				this.loadColleges();
			} catch (e) {
				uni.showToast({ title: '操作失败', icon: 'none' });
			}
		},
		async deleteCollege(c) {
			uni.showModal({
				title: '确认删除',
				content: `确定要删除学院"${c.college_name}"吗？`,
				success: async (res) => {
					if (res.confirm) {
						try {
							await request({ url: `/org/college/${c.id}`, method: 'DELETE' });
							uni.showToast({ title: '删除成功', icon: 'success' });
							this.loadColleges();
						} catch (e) {
							uni.showToast({ title: '删除失败', icon: 'none' });
						}
					}
				}
			});
		},
		// 教研室管理
		handleRoomCollegeChange(e) {
			const idx = Number(e.detail.value);
			this.roomCollegeId = idx <= 0 ? null : (this.colleges[idx - 1]?.id || null);
			this.loadRooms();
		},
		async loadRooms() {
			try {
				const params = { skip: 0, limit: 200 };
				if (this.roomCollegeId) params.college_id = this.roomCollegeId;
				const res = await request({ url: '/org/research-rooms', method: 'GET', params });
				this.rooms = (res && res.list) ? res.list : [];
				// 同时加载所有教研室用于显示名称
				const allRes = await request({ url: '/org/research-rooms', method: 'GET', params: { skip: 0, limit: 500 } });
				this.allRooms = (allRes && allRes.list) ? allRes.list : [];
			} catch (e) {
				this.rooms = [];
			}
		},
		openRoomCreate() {
			this.roomFormMode = 'create';
			this.roomForm = { id: null, college_id: this.roomCollegeId, room_code: '', room_name: '' };
			this.showRoomModal = true;
		},
		openRoomEdit(r) {
			this.roomFormMode = 'edit';
			this.roomForm = { id: r.id, college_id: r.college_id, room_code: r.room_code, room_name: r.room_name };
			this.showRoomModal = true;
		},
		closeRoomModal() {
			this.showRoomModal = false;
		},
		handleRoomFormCollegeChange(e) {
			const idx = Number(e.detail.value);
			this.roomForm.college_id = idx <= 0 ? null : (this.colleges[idx - 1]?.id || null);
		},
		async submitRoom() {
			const code = (this.roomForm.room_code || '').trim();
			const name = (this.roomForm.room_name || '').trim();
			if (!this.roomForm.college_id || !code || !name) {
				uni.showToast({ title: '请选择学院并填写教研室编码和名称', icon: 'none' });
				return;
			}
			try {
				if (this.roomFormMode === 'create') {
					await request({ url: '/org/research-rooms', method: 'POST', data: this.roomForm });
					uni.showToast({ title: '创建成功', icon: 'success' });
				} else {
					await request({ url: `/org/research-rooms/${this.roomForm.id}`, method: 'PUT', data: this.roomForm });
					uni.showToast({ title: '更新成功', icon: 'success' });
				}
				this.closeRoomModal();
				this.loadRooms();
			} catch (e) {
				uni.showToast({ title: '操作失败', icon: 'none' });
			}
		},
		async deleteRoom(r) {
			uni.showModal({
				title: '确认删除',
				content: `确定要删除教研室"${r.room_name}"吗？`,
				success: async (res) => {
					if (res.confirm) {
						try {
							await request({ url: `/org/research-rooms/${r.id}`, method: 'DELETE' });
							uni.showToast({ title: '删除成功', icon: 'success' });
							this.loadRooms();
						} catch (e) {
							uni.showToast({ title: '删除失败', icon: 'none' });
						}
					}
				}
			});
		},
		// 教师归属管理
		handleTeacherCollegeChange(e) {
			const idx = Number(e.detail.value);
			this.teacherCollegeId = idx <= 0 ? null : (this.colleges[idx - 1]?.id || null);
			this.loadTeachers();
		},
		async loadTeachers() {
			try {
				const params = { skip: 0, limit: 200 };
				if (this.teacherCollegeId) params.college_id = this.teacherCollegeId;
				const res = await request({ url: '/org/users', method: 'GET', params });
				this.teachers = (res && res.list) ? res.list : [];
			} catch (e) {
				this.teachers = [];
			}
		},
		openTeacherEdit(t) {
			this.teacherForm = {
				id: t.id,
				user_id: t.id,
				user_name: t.user_name,
				user_on: t.user_on,
				college_id: t.college_id,
				research_room_id: t.research_room_id
			};
			this.loadTeacherFormRooms();
			this.showTeacherModal = true;
		},
		closeTeacherModal() {
			this.showTeacherModal = false;
		},
		async handleTeacherFormCollegeChange(e) {
			const idx = Number(e.detail.value);
			this.teacherForm.college_id = idx <= 0 ? null : (this.colleges[idx - 1]?.id || null);
			this.teacherForm.research_room_id = null;
			await this.loadTeacherFormRooms();
		},
		async loadTeacherFormRooms() {
			if (!this.teacherForm.college_id) {
				this.teacherFormRooms = [];
				return;
			}
			try {
				const res = await request({ url: '/org/research-rooms', method: 'GET', params: { college_id: this.teacherForm.college_id, skip: 0, limit: 200 } });
				this.teacherFormRooms = (res && res.list) ? res.list : [];
			} catch (e) {
				this.teacherFormRooms = [];
			}
		},
		handleTeacherFormRoomChange(e) {
			const idx = Number(e.detail.value);
			this.teacherForm.research_room_id = idx <= 0 ? null : (this.teacherFormRooms[idx - 1]?.id || null);
		},
		async submitTeacher() {
			try {
				await request({
					url: `/org/users/${this.teacherForm.user_id}/affiliation`,
					method: 'PUT',
					data: {
						college_id: this.teacherForm.college_id,
						research_room_id: this.teacherForm.research_room_id
					}
				});
				uni.showToast({ title: '设置成功', icon: 'success' });
				this.closeTeacherModal();
				this.loadTeachers();
			} catch (e) {
				uni.showToast({ title: '设置失败', icon: 'none' });
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
}

.page-title {
	font-size: 36rpx;
	font-weight: bold;
}

.tabs {
	display: flex;
	background-color: #FFFFFF;
	padding: 0 20rpx;
}

.tab {
	flex: 1;
	text-align: center;
	padding: 24rpx 0;
	font-size: 28rpx;
	color: #666666;
	border-bottom: 4rpx solid transparent;
}

.tab.active {
	color: #3E5C76;
	font-weight: bold;
	border-bottom-color: #3E5C76;
}

.content-section {
	padding: 20rpx;
}

.toolbar {
	display: flex;
	gap: 20rpx;
	margin-bottom: 20rpx;
	flex-wrap: wrap;
}

.filter-item {
	flex: 1;
	min-width: 200rpx;
}

.picker-btn {
	height: 72rpx;
	line-height: 72rpx;
	background-color: #FFFFFF;
	border-radius: 8rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #333333;
}

.primary-btn {
	height: 72rpx;
	line-height: 72rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 28rpx;
	border-radius: 8rpx;
	padding: 0 30rpx;
}

.ghost-btn {
	height: 72rpx;
	line-height: 72rpx;
	background-color: #FFFFFF;
	color: #3E5C76;
	font-size: 28rpx;
	border-radius: 8rpx;
	padding: 0 30rpx;
	border: 2rpx solid #3E5C76;
}

.list-card {
	background-color: #FFFFFF;
	border-radius: 12rpx;
	overflow: hidden;
}

.item {
	padding: 24rpx;
	border-bottom: 1rpx solid #EEEEEE;
}

.item:last-child {
	border-bottom: none;
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
	color: #999999;
}

.item-info {
	display: flex;
	gap: 30rpx;
	margin-bottom: 12rpx;
}

.info-text {
	font-size: 24rpx;
	color: #666666;
}

.item-actions {
	display: flex;
	gap: 20rpx;
}

.action-btn {
	height: 56rpx;
	line-height: 56rpx;
	padding: 0 24rpx;
	font-size: 24rpx;
	background-color: #F5F7FA;
	color: #3E5C76;
	border-radius: 8rpx;
}

.action-btn.danger {
	color: #E74C3C;
}

.empty-state {
	padding: 100rpx 0;
	text-align: center;
}

.empty-text {
	font-size: 28rpx;
	color: #999999;
}

/* 弹窗样式 */
.modal {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	justify-content: center;
	align-items: center;
	z-index: 1000;
}

.modal-content {
	width: 90%;
	max-width: 600rpx;
	background-color: #FFFFFF;
	border-radius: 16rpx;
	overflow: hidden;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 30rpx;
	border-bottom: 1rpx solid #EEEEEE;
}

.modal-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.modal-close {
	font-size: 40rpx;
	color: #999999;
}

.modal-body {
	padding: 30rpx;
}

.form-item {
	margin-bottom: 24rpx;
}

.form-label {
	display: block;
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 12rpx;
}

.form-input {
	width: 100%;
	height: 80rpx;
	background-color: #F5F7FA;
	border-radius: 8rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #333333;
}

.form-picker {
	height: 80rpx;
	line-height: 80rpx;
	background-color: #F5F7FA;
	border-radius: 8rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #333333;
}

.form-value {
	font-size: 28rpx;
	color: #333333;
}

.submit-btn {
	width: 100%;
	height: 80rpx;
	line-height: 80rpx;
	background-color: #3E5C76;
	color: #FFFFFF;
	font-size: 30rpx;
	border-radius: 8rpx;
	margin-top: 20rpx;
}
</style>
