<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学院管理员</text>
        <text class="title">用户管理</text>
        <text class="desc">维护本院用户账号基础信息</text>
      </view>
      <view class="header-badges">
        <button @click="showAddModal = true" class="add-btn">+ 添加用户</button>
        <button @click="navigateBack" class="badge">返回</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">本院用户列表</text>
        <text class="panel-desc">{{ currentUser.college }}的所有用户</text>
      </view>
      
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">用户名</view>
          <view class="table-cell">姓名</view>
          <view class="table-cell">角色</view>
          <view class="table-cell">操作</view>
        </view>
        <view v-for="user in collegeUsers" :key="user.id" class="table-row">
          <view class="table-cell">{{ user.username }}</view>
          <view class="table-cell">{{ user.name }}</view>
          <view class="table-cell">
            <text class="role-badge" :class="getRoleClass(user.role)">{{ getRoleLabel(user.role) }}</text>
          </view>
          <view class="table-cell">
            <button @click="editUser(user)" class="action-btn edit">编辑</button>
            <button @click="resetPassword(user)" class="action-btn reset">重置密码</button>
            <button @click="deleteUser(user)" class="action-btn delete">删除</button>
          </view>
        </view>
        <view v-if="collegeUsers.length === 0" class="empty">暂无用户</view>
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
      collegeUsers: [],
      showAddModal: false,
      editingUser: null,
      formData: {
        username: '',
        name: '',
        password: '',
        role: 'teacher'
      },
      roleOptions: [
        { label: '教师', value: 'teacher' },
        { label: '学院管理员', value: 'college_admin' },
        { label: '督导老师', value: 'supervisor' }
      ],
      selectedRoleLabel: '教师'
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadCollegeUsers();
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadCollegeUsers() {
      // 加载本学院的所有用户
      this.collegeUsers = simpleStore.state.users.filter(
        u => u.college === this.currentUser.college
      );
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
    editUser(user) {
      this.editingUser = user;
      this.formData = {
        username: user.username,
        name: user.name,
        password: '',
        role: user.role
      };
      this.selectedRoleLabel = this.getRoleLabel(user.role);
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
      if (user.role === 'college_admin' && user.id === this.currentUser.id) {
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
            const index = simpleStore.state.users.findIndex(u => u.id === user.id);
            if (index !== -1) {
              simpleStore.state.users.splice(index, 1);
              simpleStore.saveAllToStorage();
              this.loadCollegeUsers();
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
      const index = e.detail.value;
      this.formData.role = this.roleOptions[index].value;
      this.selectedRoleLabel = this.roleOptions[index].label;
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

      // ========== 后端接入点：保存用户信息 ==========
      // TODO: 后期接入后端接口时，可在此处调用API保存用户信息
      // 示例：
      // const userData = {
      //   username: this.formData.username,
      //   name: this.formData.name,
      //   password: this.formData.password,
      //   role: this.formData.role,
      //   college: this.currentUser.college
      // };
      // if (this.editingUser) {
      //   await uni.request({
      //     url: `/api/users/${this.editingUser.id}`,
      //     method: 'PUT',
      //     data: userData
      //   });
      // } else {
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
        }
      } else {
        // 添加用户
        const newUser = {
          id: Date.now(),
          username: this.formData.username,
          password: this.formData.password,
          name: this.formData.name,
          role: this.formData.role,
          college: this.currentUser.college,
          courses: []
        };
        simpleStore.state.users.push(newUser);
      }
      
      simpleStore.saveAllToStorage();
      this.loadCollegeUsers();
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
        role: 'teacher'
      };
      this.selectedRoleLabel = '教师';
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
</style>

