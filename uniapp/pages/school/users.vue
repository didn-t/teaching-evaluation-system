<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学校管理员</text>
        <text class="title">用户管理</text>
        <text class="desc">管理所有用户账号、角色分配及权限配置</text>
      </view>
      <view class="header-badges">
        <button @click="showAddModal = true" class="add-btn">+ 添加用户</button>
        <button @click="navigateBack" class="badge">返回</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">用户列表</text>
        <text class="panel-desc">全校所有用户</text>
      </view>
      
      <view class="filter-bar">
        <picker mode="selector" :range="collegeOptions" :range-key="'name'" @change="onCollegeFilter">
          <view class="filter-item">{{ selectedCollege || '全部学院' }}</view>
        </picker>
        <picker mode="selector" :range="roleOptions" :range-key="'label'" @change="onRoleFilter">
          <view class="filter-item">{{ selectedRole || '全部角色' }}</view>
        </picker>
      </view>
      
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">用户名</view>
          <view class="table-cell">姓名</view>
          <view class="table-cell">学院</view>
          <view class="table-cell">角色</view>
          <view class="table-cell">操作</view>
        </view>
        <view v-for="user in filteredUsers" :key="user.id" class="table-row">
          <view class="table-cell">{{ user.username }}</view>
          <view class="table-cell">{{ user.name }}</view>
          <view class="table-cell">{{ user.college || '-' }}</view>
          <view class="table-cell">
            <text class="role-badge" :class="getRoleClass(user.role)">{{ getRoleLabel(user.role) }}</text>
          </view>
          <view class="table-cell">
            <button @click="editUser(user)" class="action-btn edit">编辑</button>
            <button v-if="user.role === 'supervisor'" @click="viewSupervisorScope(user)" class="action-btn scope">负责范围</button>
            <button @click="resetPassword(user)" class="action-btn reset">重置密码</button>
            <button @click="deleteUser(user)" class="action-btn delete">删除</button>
          </view>
        </view>
        <view v-if="filteredUsers.length === 0" class="empty">暂无用户</view>
      </view>
    </view>

    <!-- 添加/编辑用户弹窗 -->
    <view v-if="showAddModal || editingUser" class="modal-overlay" @click="closeModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ editingUser ? '编辑用户' : '添加用户' }}</text>
          <button @click="closeModal" class="close-btn">×</button>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">用户名</text>
            <input class="form-input" v-model="formData.username" placeholder="请输入用户名" :disabled="!!editingUser" />
          </view>
          <view class="form-item">
            <text class="form-label">姓名</text>
            <input class="form-input" v-model="formData.name" placeholder="请输入姓名" />
          </view>
          <view class="form-item">
            <text class="form-label">密码</text>
            <input class="form-input" v-model="formData.password" type="password" placeholder="请输入密码" />
          </view>
          <view class="form-item">
            <text class="form-label">角色</text>
            <picker mode="selector" :range="roleOptions" :range-key="'label'" @change="onRoleChange">
              <view class="picker-view">{{ selectedRoleLabel }}</view>
            </picker>
          </view>
          <view class="form-item">
            <text class="form-label">所属学院</text>
            <picker mode="selector" :range="collegeOptions" :range-key="'name'" @change="onCollegeChange">
              <view class="picker-view">{{ selectedCollegeName || '请选择学院' }}</view>
            </picker>
          </view>
          <!-- 督导老师负责范围设置 -->
          <view v-if="formData.role === 'supervisor'" class="form-item supervisor-scope">
            <text class="form-label">负责学院</text>
            <view class="checkbox-group">
              <view v-for="college in allColleges" :key="college.id" class="checkbox-item" @click="toggleCollegeCheckbox(college.name)">
                <checkbox 
                  :value="college.name" 
                  :checked="formData.responsibleColleges.includes(college.name)"
                  @change="onResponsibleCollegeChange(college.name, $event)"
                />
                <text>{{ college.name }}</text>
              </view>
            </view>
          </view>
          <view v-if="formData.role === 'supervisor'" class="form-item supervisor-teachers">
            <text class="form-label">负责老师</text>
            <view class="teacher-select-container">
              <view class="teacher-filter">
                <input 
                  class="form-input search-input" 
                  v-model="teacherSearchKeyword" 
                  placeholder="搜索老师姓名或用户名" 
                  @input="filterTeachers"
                />
              </view>
              <view class="teacher-list">
                <view v-for="teacher in filteredTeacherList" :key="teacher.id" class="teacher-checkbox-item" @click="toggleTeacherCheckbox(teacher.id)">
                  <checkbox 
                    :value="teacher.id.toString()" 
                    :checked="formData.responsibleTeachers.includes(teacher.id)"
                    @change="onResponsibleTeacherChange(teacher.id, $event)"
                  />
                  <text class="teacher-name">{{ teacher.name }}</text>
                  <text class="teacher-info">{{ teacher.college || '' }}</text>
                </view>
                <view v-if="filteredTeacherList.length === 0" class="empty-teachers">暂无符合条件的老师</view>
              </view>
              <text class="form-hint">已选择 {{ formData.responsibleTeachers.length }} 位老师</text>
            </view>
          </view>
        </view>
        <view class="modal-footer">
          <button @click="closeModal" class="btn-cancel">取消</button>
          <button @click="saveUser" class="btn-save">保存</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { simpleStore } from '../../utils/simpleStore';

export default {
  data() {
    return {
      currentUser: {},
      allUsers: [],
      selectedCollege: '',
      selectedRole: '',
      showAddModal: false,
      editingUser: null,
      formData: {
        username: '',
        name: '',
        password: '',
        role: 'teacher',
        college: '',
        responsibleColleges: [],
        responsibleTeachers: []
      },
      allTeachers: [],
      teacherSearchKeyword: '',
      filteredTeacherList: [],
      roleOptions: [
        { label: '教师', value: 'teacher' },
        { label: '学院管理员', value: 'college_admin' },
        { label: '督导老师', value: 'supervisor' },
        { label: '学校管理员', value: 'school_admin' }
      ],
      selectedRoleLabel: '教师',
      selectedCollegeName: ''
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadUsers();
    this.loadColleges();
    this.loadTeachers();
  },
  computed: {
    collegeOptions() {
      return [{ id: '', name: '全部学院' }, ...simpleStore.getColleges()];
    },
    filteredUsers() {
      let users = [...this.allUsers];
      if (this.selectedCollege) {
        users = users.filter(u => u.college === this.selectedCollege);
      }
      if (this.selectedRole) {
        users = users.filter(u => u.role === this.selectedRole);
      }
      return users;
    }
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadUsers() {
      this.allUsers = simpleStore.getUsers();
    },
    loadColleges() {
      this.allColleges = simpleStore.getColleges();
    },
    loadTeachers() {
      // 加载所有教师用户
      this.allTeachers = simpleStore.state.users.filter(u => u.role === 'teacher') || [];
      this.filteredTeacherList = [...this.allTeachers];
    },
    filterTeachers() {
      const keyword = (this.teacherSearchKeyword || '').toLowerCase().trim();
      if (!keyword) {
        this.filteredTeacherList = [...this.allTeachers];
      } else {
        this.filteredTeacherList = this.allTeachers.filter(teacher => {
          const name = (teacher.name || '').toLowerCase();
          const username = (teacher.username || '').toLowerCase();
          return name.includes(keyword) || username.includes(keyword);
        });
      }
    },
    getRoleLabel(role) {
      const map = {
        'teacher': '教师',
        'college_admin': '学院管理员',
        'supervisor': '督导老师',
        'school_admin': '学校管理员'
      };
      return map[role] || role;
    },
    getRoleClass(role) {
      const map = {
        'teacher': 'role-teacher',
        'college_admin': 'role-admin',
        'supervisor': 'role-supervisor',
        'school_admin': 'role-school-admin'
      };
      return map[role] || '';
    },
    onCollegeFilter(e) {
      // 兼容 Web 和微信小程序的事件处理
      const index = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e ? e : 0);
      if (this.collegeOptions && this.collegeOptions[index]) {
        this.selectedCollege = this.collegeOptions[index].name === '全部学院' ? '' : this.collegeOptions[index].name;
      }
    },
    onRoleFilter(e) {
      // 兼容 Web 和微信小程序的事件处理
      const index = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e ? e : 0);
      if (this.roleOptions && this.roleOptions[index]) {
        this.selectedRole = this.roleOptions[index].label === '全部角色' ? '' : this.roleOptions[index].value;
      }
    },
    editUser(user) {
      this.editingUser = user;
      this.formData = {
        username: user.username,
        name: user.name,
        password: '',
        role: user.role,
        college: user.college || '',
        responsibleColleges: user.responsibleColleges || [],
        responsibleTeachers: user.responsibleTeachers || []
      };
      this.selectedRoleLabel = this.getRoleLabel(user.role);
      this.selectedCollegeName = user.college || '';
      // 重置搜索关键词
      this.teacherSearchKeyword = '';
      this.filterTeachers();
    },
    viewSupervisorScope(user) {
      // 查看或编辑督导老师的负责范围
      this.editUser(user);
    },
    resetPassword(user) {
      uni.showModal({
        title: '重置密码',
        content: `确定要重置用户"${user.name}"的密码吗？新密码将设置为：123456`,
        success: (res) => {
          if (res.confirm) {
            const userObj = simpleStore.state.users.find(u => u.id === user.id);
            if (userObj) {
              userObj.password = '123456';
              simpleStore.saveAllToStorage();
              uni.showToast({
                title: '密码重置成功',
                icon: 'success'
              });
            }
          }
        }
      });
    },
    deleteUser(user) {
      if (user.role === 'school_admin') {
        uni.showToast({
          title: '不能删除学校管理员',
          icon: 'none'
        });
        return;
      }
      if (user.id === this.currentUser.id) {
        uni.showToast({
          title: '不能删除自己的账号',
          icon: 'none'
        });
        return;
      }
      uni.showModal({
        title: '确认删除',
        content: `确定要删除用户"${user.name}"吗？此操作不可恢复！`,
        success: (res) => {
          if (res.confirm) {
            // ========== 后端接入点：删除用户 ==========
            // TODO: 后期接入后端接口时，可在此处调用API删除用户
            // 示例：
            // await uni.request({
            //   url: `/api/users/${user.id}`,
            //   method: 'DELETE'
            // });
            // ============================================
            
            const index = simpleStore.state.users.findIndex(u => u.id === user.id);
            if (index !== -1) {
              simpleStore.state.users.splice(index, 1);
              simpleStore.saveAllToStorage();
              this.loadUsers();
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              });
            }
          }
        }
      });
    },
    onRoleChange(e) {
      // 兼容 Web 和微信小程序的事件处理
      const index = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e ? e : 0);
      if (this.roleOptions && this.roleOptions[index]) {
        this.formData.role = this.roleOptions[index].value;
        this.selectedRoleLabel = this.roleOptions[index].label;
        // 如果切换到督导老师，初始化负责范围
        if (this.formData.role === 'supervisor' && this.formData.responsibleColleges.length === 0) {
          // 如果已选择学院，默认将该学院加入负责范围
          if (this.formData.college) {
            this.formData.responsibleColleges = [this.formData.college];
          }
        }
      }
    },
    onCollegeChange(e) {
      // 兼容 Web 和微信小程序的事件处理
      const index = (e && e.detail && e.detail.value !== undefined) ? e.detail.value : (e ? e : 0);
      if (this.collegeOptions && this.collegeOptions[index]) {
        this.formData.college = this.collegeOptions[index].name === '全部学院' ? '' : this.collegeOptions[index].name;
        this.selectedCollegeName = this.formData.college;
      }
    },
    toggleCollegeCheckbox(collegeName) {
      // 兼容 Web 和微信小程序的点击事件
      const index = this.formData.responsibleColleges.indexOf(collegeName);
      if (index > -1) {
        this.formData.responsibleColleges.splice(index, 1);
      } else {
        this.formData.responsibleColleges.push(collegeName);
      }
    },
    onResponsibleCollegeChange(collegeName, e) {
      // 兼容微信小程序和 Web 的事件处理
      let isChecked = false;
      if (e && e.detail) {
        // 微信小程序
        isChecked = e.detail.value && e.detail.value.length > 0;
      } else if (e && e.target) {
        // Web 端
        isChecked = e.target.checked;
      }
      
      if (isChecked) {
        if (!this.formData.responsibleColleges.includes(collegeName)) {
          this.formData.responsibleColleges.push(collegeName);
        }
      } else {
        const index = this.formData.responsibleColleges.indexOf(collegeName);
        if (index > -1) {
          this.formData.responsibleColleges.splice(index, 1);
        }
      }
    },
    toggleTeacherCheckbox(teacherId) {
      // 兼容 Web 和微信小程序的点击事件
      const index = this.formData.responsibleTeachers.indexOf(teacherId);
      if (index > -1) {
        this.formData.responsibleTeachers.splice(index, 1);
      } else {
        this.formData.responsibleTeachers.push(teacherId);
      }
    },
    onResponsibleTeacherChange(teacherId, e) {
      // 兼容微信小程序和 Web 的事件处理
      let isChecked = false;
      if (e && e.detail) {
        // 微信小程序
        isChecked = e.detail.value && e.detail.value.length > 0;
      } else if (e && e.target) {
        // Web 端
        isChecked = e.target.checked;
      }
      
      if (isChecked) {
        if (!this.formData.responsibleTeachers.includes(teacherId)) {
          this.formData.responsibleTeachers.push(teacherId);
        }
      } else {
        const index = this.formData.responsibleTeachers.indexOf(teacherId);
        if (index > -1) {
          this.formData.responsibleTeachers.splice(index, 1);
        }
      }
    },
    saveUser() {
      if (!this.formData.username || !this.formData.name) {
        uni.showToast({
          title: '请填写完整信息',
          icon: 'none'
        });
        return;
      }
      
      if (!this.editingUser && !this.formData.password) {
        uni.showToast({
          title: '请设置密码',
          icon: 'none'
        });
        return;
      }

      // 如果是督导老师，验证负责范围
      if (this.formData.role === 'supervisor') {
        if (!this.formData.responsibleColleges || this.formData.responsibleColleges.length === 0) {
          uni.showToast({
            title: '请至少选择一个负责学院',
            icon: 'none'
          });
          return;
        }
        if (!this.formData.responsibleTeachers || this.formData.responsibleTeachers.length === 0) {
          uni.showToast({
            title: '请至少选择一个负责老师',
            icon: 'none'
          });
          return;
        }
      }

      // ========== 后端接入点：保存用户信息 ==========
      // TODO: 后期接入后端接口时，可在此处调用API保存用户信息
      // 示例：
      // const userData = {
      //   username: this.formData.username,
      //   name: this.formData.name,
      //   password: this.formData.password,
      //   role: this.formData.role,
      //   college: this.formData.college,
      //   responsibleColleges: this.formData.responsibleColleges,
      //   responsibleTeachers: this.formData.responsibleTeachers
      // };
      // if (this.editingUser) {
      //   // 编辑用户
      //   await uni.request({
      //     url: `/api/users/${this.editingUser.id}`,
      //     method: 'PUT',
      //     data: userData
      //   });
      // } else {
      //   // 添加用户
      //   await uni.request({
      //     url: '/api/users',
      //     method: 'POST',
      //     data: userData
      //   });
      // }
      // ============================================
      
      if (this.editingUser) {
        // 编辑用户
        const user = simpleStore.state.users.find(u => u.id === this.editingUser.id);
        if (user) {
          user.name = this.formData.name;
          if (this.formData.password) {
            user.password = this.formData.password;
          }
          user.role = this.formData.role;
          user.college = this.formData.college;
          // 如果是督导老师，更新负责范围
          if (this.formData.role === 'supervisor') {
            user.responsibleColleges = [...this.formData.responsibleColleges];
            user.responsibleTeachers = [...this.formData.responsibleTeachers];
          } else {
            // 如果不是督导老师，清除负责范围
            delete user.responsibleColleges;
            delete user.responsibleTeachers;
          }
        }
      } else {
        // 添加用户
        const newUser = {
          id: Date.now(),
          username: this.formData.username,
          password: this.formData.password,
          name: this.formData.name,
          role: this.formData.role,
          college: this.formData.college,
          courses: []
        };
        // 如果是督导老师，添加负责范围
        if (this.formData.role === 'supervisor') {
          newUser.responsibleColleges = [...this.formData.responsibleColleges];
          newUser.responsibleTeachers = [...this.formData.responsibleTeachers];
        }
        simpleStore.state.users.push(newUser);
      }
      
      simpleStore.saveAllToStorage();
      this.loadUsers();
      this.closeModal();
      uni.showToast({
        title: this.editingUser ? '更新成功' : '添加成功',
        icon: 'success'
      });
    },
    closeModal() {
      this.showAddModal = false;
      this.editingUser = null;
      this.formData = {
        username: '',
        name: '',
        password: '',
        role: 'teacher',
        college: '',
        responsibleColleges: [],
        responsibleTeachers: []
      };
      this.selectedRoleLabel = '教师';
      this.selectedCollegeName = '';
      this.teacherSearchKeyword = '';
      this.filterTeachers();
    },
    navigateBack() {
      uni.navigateBack();
    }
  }
};
</script>

<style scoped>
.page {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
}

.eyebrow {
  font-size: 14px;
  color: #4f46e5;
  display: block;
  margin-bottom: 4px;
}

.title {
  font-size: 24px;
  font-weight: bold;
  display: block;
  margin-bottom: 8px;
  color: #1f2933;
}

.desc {
  font-size: 14px;
  color: #666;
  display: block;
}

.add-btn {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 8px;
}

.badge {
  background-color: #e0e7ff;
  color: #4f46e5;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  border: none;
}

.panel {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.panel-title {
  margin-bottom: 16px;
}

.panel-title-text {
  font-size: 20px;
  font-weight: bold;
  display: block;
  margin-bottom: 4px;
  color: #1f2933;
}

.panel-desc {
  font-size: 14px;
  color: #666;
  display: block;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.filter-item {
  padding: 8px 12px;
  border: 1px solid #d7deea;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  color: #1f2933;
}

.table-container {
  margin-top: 16px;
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  overflow: hidden;
}

.table-header {
  display: flex;
  padding: 12px;
  background: #eef2ff;
  font-weight: bold;
}

.table-row {
  display: flex;
  padding: 12px;
  border-bottom: 1px solid #e4e9f1;
  align-items: center;
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  flex: 1;
  padding: 4px 8px;
  color: #1f2933;
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

.role-teacher {
  background: #dbeafe;
  color: #1e40af;
}

.role-admin {
  background: #fef3c7;
  color: #92400e;
}

.role-supervisor {
  background: #e0e7ff;
  color: #4f46e5;
}

.role-school-admin {
  background: #fee2e2;
  color: #991b1b;
}

.action-btn {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  border: none;
  margin-right: 4px;
}

.action-btn.edit {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.scope {
  background: #e0e7ff;
  color: #4f46e5;
}

.action-btn.reset {
  background: #fef3c7;
  color: #d97706;
}

.action-btn.delete {
  background: #fee2e2;
  color: #991b1b;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e4e9f1;
}

.modal-title {
  font-size: 20px;
  font-weight: bold;
  color: #1f2933;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  line-height: 30px;
}

.modal-body {
  padding: 20px;
}

.form-item {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 14px;
  color: #1f2933;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #d7deea;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.picker-view {
  padding: 12px;
  border: 1px solid #d7deea;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e4e9f1;
}

.btn-cancel {
  padding: 12px 24px;
  border-radius: 8px;
  border: 1px solid #d7deea;
  background: white;
  color: #1f2933;
  font-weight: 600;
}

.btn-save {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  background: #4f46e5;
  color: white;
  font-weight: 600;
}

.supervisor-scope {
  margin-top: 8px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #1f2933;
  padding: 4px 0;
  /* #ifdef H5 */
  cursor: pointer;
  /* #endif */
}

/* #ifdef H5 */
.checkbox-item:hover {
  background-color: #f0f0f0;
}
/* #endif */

.form-hint {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
  display: block;
}

.supervisor-teachers {
  margin-top: 8px;
}

.teacher-select-container {
  margin-top: 8px;
}

.teacher-filter {
  margin-bottom: 12px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d7deea;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.teacher-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 8px;
  background: #f8f9fa;
  margin-bottom: 8px;
}

.teacher-checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border-bottom: 1px solid #e4e9f1;
  /* #ifdef H5 */
  cursor: pointer;
  /* #endif */
}

/* #ifdef H5 */
.teacher-checkbox-item:hover {
  background-color: #f0f0f0;
}
/* #endif */

.teacher-checkbox-item:last-child {
  border-bottom: none;
}

.teacher-name {
  flex: 1;
  font-size: 14px;
  color: #1f2933;
  font-weight: 500;
}

.teacher-info {
  font-size: 12px;
  color: #666;
  margin-left: 8px;
}

.empty-teachers {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
}
</style>

