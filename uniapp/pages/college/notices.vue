<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学院管理员</text>
        <text class="title">评教通知</text>
        <text class="desc">查看学校下发的评教通知</text>
      </view>
      <view class="header-badges">
        <button @click="navigateBack" class="badge">返回</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">通知列表</text>
        <text class="panel-desc">学校下发的评教相关通知</text>
      </view>
      
      <view v-if="notices.length === 0" class="empty">暂无通知</view>
      <view v-else class="notice-list">
        <view v-for="notice in notices" :key="notice.id" class="notice-item" @click="viewNotice(notice)">
          <view class="notice-header">
            <text class="notice-title">{{ notice.title }}</text>
            <text class="notice-time">{{ formatDate(notice.createdAt) }}</text>
          </view>
          <text class="notice-content">{{ notice.content }}</text>
          <view class="notice-footer">
            <text class="notice-sender">发布人：{{ notice.sender }}</text>
            <text v-if="notice.isRead" class="read-badge">已读</text>
            <text v-else class="unread-badge">未读</text>
          </view>
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
      notices: []
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadNotices();
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadNotices() {
      // 从本地存储加载通知（实际应该从后端获取）
      // 这里使用模拟数据
      const allNotices = simpleStore.state.notices || [];
      // 筛选本学院相关的通知
      this.notices = allNotices.filter(n => 
        !n.targetCollege || n.targetCollege === this.currentUser.college || n.targetCollege === 'all'
      ).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleString('zh-CN');
    },
    viewNotice(notice) {
      // 标记为已读
      if (!notice.isRead) {
        notice.isRead = true;
        simpleStore.saveAllToStorage();
      }
      
      uni.showModal({
        title: notice.title,
        content: notice.content + '\n\n发布时间：' + this.formatDate(notice.createdAt) + '\n发布人：' + notice.sender,
        showCancel: false,
        confirmText: '知道了'
      });
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

.notice-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.notice-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e9f1;
  /* #ifdef H5 */
  cursor: pointer;
  /* #endif */
}

.notice-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.notice-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2933;
  flex: 1;
}

.notice-time {
  font-size: 12px;
  color: #666;
  margin-left: 12px;
}

.notice-content {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notice-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e4e9f1;
}

.notice-sender {
  font-size: 12px;
  color: #999;
}

.read-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #d1fae5;
  color: #059669;
}

.unread-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #fee2e2;
  color: #dc2626;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}
</style>

