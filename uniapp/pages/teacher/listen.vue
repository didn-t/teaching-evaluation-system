<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">教师端</text>
        <text class="title">听课评价</text>
        <text class="desc">欢迎，{{ currentUser.name }}</text>
      </view>
      <view class="header-badges">
        <text class="badge">{{ currentUser.college }}</text>
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">听课记录</text>
        <text class="panel-desc">您参与的听课评价记录</text>
      </view>
      
      <view v-if="listenRecords.length === 0" class="empty">
        暂无听课记录
      </view>
      <view v-else class="list">
        <view v-for="record in listenRecords" :key="record.id" class="card">
          <view class="card-head">
            <view>
              <text class="name">{{ record.courseName }}</text>
              <text class="title">授课教师：{{ record.teacherName }}</text>
              <view class="meta">
                <text>评价时间：{{ formatDate(record.createdAt) }}</text>
              </view>
            </view>
            <view class="rating-info">
              <text class="rating-number">{{ record.totalScore }}</text>
              <text class="level-badge" :class="getLevelClass(record.level)">{{ record.level }}</text>
            </view>
          </view>
          <view class="score-details">
            <text class="score-item">教学态度：{{ record.scores.teachingAttitude }}分</text>
            <text class="score-item">教学内容：{{ record.scores.content }}分</text>
            <text class="score-item">教学方法：{{ record.scores.method }}分</text>
            <text class="score-item">教学效果：{{ record.scores.effect }}分</text>
          </view>
          <view v-if="record.suggestion || (record.suggestions && (record.suggestions.advantages || record.suggestions.problems || record.suggestions.improvements))" class="content">
            <text class="strong">文字评价建议：</text>
            <view v-if="record.suggestions && (record.suggestions.advantages || record.suggestions.problems || record.suggestions.improvements)" class="suggestions-detail">
              <view v-if="record.suggestions.advantages" class="suggestion-part">
                <text class="suggestion-part-label">优点：</text>
                <text class="suggestion-part-text">{{ record.suggestions.advantages }}</text>
              </view>
              <view v-if="record.suggestions.problems" class="suggestion-part">
                <text class="suggestion-part-label">问题：</text>
                <text class="suggestion-part-text">{{ record.suggestions.problems }}</text>
              </view>
              <view v-if="record.suggestions.improvements" class="suggestion-part">
                <text class="suggestion-part-label">改进方向：</text>
                <text class="suggestion-part-text">{{ record.suggestions.improvements }}</text>
              </view>
            </view>
            <view v-else-if="record.suggestion" class="suggestion-text">
              <text>{{ record.suggestion }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">填写听课评价</text>
      </view>
      
      <view class="form-actions">
        <button @click="startListenEvaluation" class="action-button primary">
          开始填写听课评价
        </button>
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
      listenRecords: []
    };
  },
  onLoad() {
    this.loadUserData();
    // 普通老师和督导老师都可以进行听课评价，无需权限检查
    this.loadListenRecords();
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadListenRecords() {
      try {
        // 获取当前用户作为听课者提交的听课记录
        const userId = this.currentUser.id || this.currentUser._id;
        this.listenRecords = simpleStore.state.listenRecords.filter(r => 
          r.listenerId == userId
        );
        // 按时间倒序排序
        this.listenRecords.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      } catch (error) {
        console.error('加载听课记录失败:', error);
        uni.showToast({
          title: '加载听课记录失败',
          icon: 'none'
        });
      }
    },
    getLevelClass(level) {
      const map = {
        '优秀': 'level-excellent',
        '良好': 'level-good',
        '一般': 'level-normal',
        '合格': 'level-pass',
        '不合格': 'level-fail'
      };
      return map[level] || '';
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString('zh-CN');
    },
    handleLogout() {
      simpleStore.logout();
      uni.redirectTo({
        url: '/pages/login/login'
      });
    },
    startListenEvaluation() {
      uni.navigateTo({
        url: '/pages/teacher/evaluate?type=listen'
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
  margin-right: 10px;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-title-text {
  font-size: 20px;
  font-weight: bold;
  display: block;
  color: #1f2933;
}

.panel-desc {
  font-size: 14px;
  color: #666;
  display: block;
}

.card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.card-head {
  display: flex;
  justify-content: space-between;
}

.name {
  font-size: 18px;
  font-weight: bold;
  display: block;
  margin-bottom: 4px;
}

.title {
  font-size: 14px;
  color: #666;
  display: block;
  margin-bottom: 8px;
}

.meta {
  display: flex;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

.dot {
  margin: 0 4px;
}

.rating-info {
  text-align: right;
}

.rating-number {
  font-size: 32px;
  font-weight: 700;
  color: #4f46e5;
  display: block;
  margin-bottom: 4px;
}

.level-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.score-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
  margin: 12px 0;
  padding: 12px;
  background: #eef2ff;
  border-radius: 8px;
}

.score-item {
  font-size: 14px;
  color: #5d6673;
  display: block;
}

.content {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.strong {
  font-weight: bold;
  margin-right: 8px;
}

.suggestions-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.suggestion-part {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #4f46e5;
}

.suggestion-part-label {
  font-weight: 600;
  color: #4f46e5;
  font-size: 14px;
  margin-bottom: 4px;
}

.suggestion-part-text {
  color: #333;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.suggestion-text {
  margin-top: 8px;
  color: #333;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.form-actions {
  display: flex;
  justify-content: center;
  margin: 20px 0;
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
}

.action-button.ghost {
  background: #fff;
  border: 1px solid #d7deea;
  color: #1f2933;
}
</style>