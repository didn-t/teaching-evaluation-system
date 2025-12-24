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
      this.config.anonymousMode = e.target.value ? 'global' : 'optional';
      this.config.globalAnonymous = e.target.value;
    },
    toggleSelfListen(e) {
      this.config.allowSelfListen = e.target.value;
    },
    toggleAuditLog(e) {
      this.config.auditLog = e.target.value;
    },
    onSemesterChange(e) {
      this.currentSemester = e.target.value;
    },
    saveConfig() {
      // 这里应该调用API保存配置，目前仅做演示
      uni.showToast({
        title: '保存成功',
        icon: 'success'
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
</style>