<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学校管理员</text>
        <text class="title">系统配置</text>
        <text class="desc">欢迎，{{ currentUser.name }}</text>
      </view>
      <view class="header-badges">
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">系统参数设置</text>
      </view>
      
      <view class="form-group">
        <view class="form-item">
          <text class="label">匿名评价模式</text>
          <view class="switch-container">
            <switch :checked="config.anonymousMode === 'global'" @change="toggleAnonymousMode" />
            <text class="switch-label">{{ config.anonymousMode === 'global' ? '全局匿名' : '可选匿名' }}</text>
          </view>
        </view>
        
        <view class="form-item">
          <text class="label">允许自我听课</text>
          <view class="switch-container">
            <switch :checked="config.allowSelfListen" @change="toggleSelfListen" />
            <text class="switch-label">{{ config.allowSelfListen ? '开启' : '关闭' }}</text>
          </view>
        </view>
        
        <view class="form-item">
          <text class="label">操作日志记录</text>
          <view class="switch-container">
            <switch :checked="config.auditLog" @change="toggleAuditLog" />
            <text class="switch-label">{{ config.auditLog ? '开启' : '关闭' }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">学期设置</text>
      </view>
      
      <view class="form-group">
        <view class="form-item">
          <text class="label">当前学期</text>
          <input class="input" type="text" :value="currentSemester" @input="onSemesterChange" placeholder="例如: 2025春季" />
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">数据备份与维护</text>
      </view>
      
      <view class="form-group">
        <view class="form-item">
          <text class="label">数据备份</text>
          <button @click="handleBackup" class="action-btn backup">备份数据</button>
        </view>
        <view class="form-item">
          <text class="label">数据恢复</text>
          <button @click="handleRestore" class="action-btn restore">恢复数据</button>
        </view>
        <view class="form-item">
          <text class="label">数据清理</text>
          <button @click="handleCleanup" class="action-btn cleanup">清理过期数据</button>
        </view>
        <view class="form-item">
          <text class="label">系统维护</text>
          <button @click="handleMaintenance" class="action-btn maintenance">执行维护</button>
        </view>
      </view>
    </view>

    <view class="actions">
      <button @click="saveConfig" class="action-button primary">保存设置</button>
    </view>
  </view>
</template>

<script>
import { simpleStore } from '../../utils/simpleStore';

export default {
  data() {
    return {
      currentUser: {},
      config: {
        anonymousMode: 'global',
        globalAnonymous: true,
        allowSelfListen: true,
        auditLog: true
      },
      currentSemester: '2025春季'
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadConfig();
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadConfig() {
      this.config = simpleStore.getConfig();
    },
    toggleAnonymousMode(e) {
      // 切换匿名模式：全局匿名（统一匿名）或可选匿名（用户自主选择）
      // 兼容 Web 和微信小程序
      const value = e.detail ? e.detail.value : (e.target ? e.target.checked : false);
      this.config.anonymousMode = value ? 'global' : 'optional';
      this.config.globalAnonymous = value;
    },
    toggleSelfListen(e) {
      // 兼容 Web 和微信小程序
      const value = e.detail ? e.detail.value : (e.target ? e.target.checked : false);
      this.config.allowSelfListen = value;
    },
    toggleAuditLog(e) {
      // 兼容 Web 和微信小程序
      const value = e.detail ? e.detail.value : (e.target ? e.target.checked : false);
      this.config.auditLog = value;
    },
    onSemesterChange(e) {
      // 兼容 Web 和微信小程序
      const value = e.detail ? e.detail.value : (e.target ? e.target.value : '');
      this.currentSemester = value;
    },
    saveConfig() {
      // TODO: 后期接入后端接口时，可在此处保存配置
      // 示例：
      // try {
      //   await uni.request({
      //     url: '/api/admin/config',
      //     method: 'POST',
      //     data: this.config,
      //     timeout: 10000
      //   });
      //   uni.showToast({
      //     title: '保存成功',
      //     icon: 'success'
      //   });
      // } catch (error) {
      //   console.error('保存配置失败:', error);
      //   uni.showToast({
      //     title: '保存失败，请稍后重试',
      //     icon: 'none'
      //   });
      // }
      
      // 当前使用本地存储保存配置
      simpleStore.state.config = { ...this.config };
      simpleStore.saveAllToStorage();
      
      uni.showToast({
        title: '保存成功',
        icon: 'success'
      });
    },
    handleBackup() {
      uni.showModal({
        title: '数据备份',
        content: '确定要备份所有数据吗？',
        success: (res) => {
          if (res.confirm) {
            try {
              // 备份所有数据到本地存储
              const backupData = {
                users: simpleStore.state.users,
                colleges: simpleStore.state.colleges,
                courses: simpleStore.state.courses,
                evaluations: simpleStore.state.evaluations,
                listenRecords: simpleStore.state.listenRecords,
                config: simpleStore.state.config,
                backupTime: new Date().toISOString()
              };
              uni.setStorageSync('data_backup', backupData);
              uni.showToast({
                title: '备份成功',
                icon: 'success'
              });
            } catch (error) {
              console.error('备份失败:', error);
              uni.showToast({
                title: '备份失败',
                icon: 'none'
              });
            }
          }
        }
      });
    },
    handleRestore() {
      uni.showModal({
        title: '数据恢复',
        content: '确定要恢复备份数据吗？此操作将覆盖当前所有数据！',
        success: (res) => {
          if (res.confirm) {
            try {
              const backupData = uni.getStorageSync('data_backup');
              if (!backupData) {
                uni.showToast({
                  title: '没有找到备份数据',
                  icon: 'none'
                });
                return;
              }
              // 恢复数据
              simpleStore.state.users = backupData.users || simpleStore.state.users;
              simpleStore.state.colleges = backupData.colleges || simpleStore.state.colleges;
              simpleStore.state.courses = backupData.courses || simpleStore.state.courses;
              simpleStore.state.evaluations = backupData.evaluations || simpleStore.state.evaluations;
              simpleStore.state.listenRecords = backupData.listenRecords || simpleStore.state.listenRecords;
              simpleStore.state.config = backupData.config || simpleStore.state.config;
              simpleStore.saveAllToStorage();
              uni.showToast({
                title: '恢复成功',
                icon: 'success'
              });
            } catch (error) {
              console.error('恢复失败:', error);
              uni.showToast({
                title: '恢复失败',
                icon: 'none'
              });
            }
          }
        }
      });
    },
    handleCleanup() {
      uni.showModal({
        title: '数据清理',
        content: '确定要清理过期数据吗？此操作不可恢复！',
        success: (res) => {
          if (res.confirm) {
            try {
              // 清理一年前的评价数据
              const oneYearAgo = new Date();
              oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);
              
              simpleStore.state.evaluations = simpleStore.state.evaluations.filter(e => {
                if (!e.createdAt) return true;
                return new Date(e.createdAt) > oneYearAgo;
              });
              
              simpleStore.state.listenRecords = simpleStore.state.listenRecords.filter(r => {
                if (!r.createdAt) return true;
                return new Date(r.createdAt) > oneYearAgo;
              });
              
              simpleStore.saveAllToStorage();
              uni.showToast({
                title: '清理完成',
                icon: 'success'
              });
            } catch (error) {
              console.error('清理失败:', error);
              uni.showToast({
                title: '清理失败',
                icon: 'none'
              });
            }
          }
        }
      });
    },
    handleMaintenance() {
      uni.showModal({
        title: '系统维护',
        content: '确定要执行系统维护吗？',
        success: (res) => {
          if (res.confirm) {
            try {
              // 执行维护操作：清理无效数据、优化存储等
              // 清理无效的评价记录
              simpleStore.state.evaluations = simpleStore.state.evaluations.filter(e => 
                e && e.teacherId && e.totalScore !== undefined
              );
              
              // 清理无效的听课记录
              simpleStore.state.listenRecords = simpleStore.state.listenRecords.filter(r => 
                r && r.teacherId && r.totalScore !== undefined
              );
              
              simpleStore.saveAllToStorage();
              uni.showToast({
                title: '维护完成',
                icon: 'success'
              });
            } catch (error) {
              console.error('维护失败:', error);
              uni.showToast({
                title: '维护失败',
                icon: 'none'
              });
            }
          }
        }
      });
    },
    handleLogout() {
      simpleStore.logout();
      uni.redirectTo({
        url: '/pages/login/login'
      });
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
  color: #1f2933; /* 添加字体颜色 */
}

.desc {
  font-size: 14px;
  color: #666;
  display: block;
}

.logout-btn {
  background-color: #ef4444;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
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
  color: #1f2933; /* 添加字体颜色 */
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e4e9f1;
}

.form-item:last-child {
  border-bottom: none;
}

.label {
  font-size: 16px;
  color: #1f2933; /* 添加字体颜色 */
}

.switch-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.switch-label {
  font-size: 14px;
  color: #666;
}

.input {
  padding: 8px 12px;
  border: 1px solid #d7deea;
  border-radius: 4px;
  font-size: 14px;
  color: #1f2933; /* 添加字体颜色 */
}

.actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.action-button {
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  border: none;
}

.action-button.primary {
  background: #4f46e5;
  color: #fff;
  min-width: 120px;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  /* #ifdef H5 */
  cursor: pointer;
  /* #endif */
}

.action-btn.backup {
  background: #10b981;
  color: white;
}

.action-btn.restore {
  background: #3b82f6;
  color: white;
}

.action-btn.cleanup {
  background: #f59e0b;
  color: white;
}

.action-btn.maintenance {
  background: #8b5cf6;
  color: white;
}
</style>