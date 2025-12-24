<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学院管理员</text>
        <text class="title">数据管理</text>
        <text class="desc">欢迎，{{ currentUser.name }} - {{ currentUser.college }}</text>
      </view>
      <view class="header-badges">
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">教师列表</text>
      </view>
      
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">姓名</view>
          <view class="table-cell">所属学院</view>
          <view class="table-cell">任教课程</view>
        </view>
        <view v-for="teacher in collegeTeachers" :key="teacher.id" class="table-row">
          <view class="table-cell">{{ teacher.name }}</view>
          <view class="table-cell">{{ teacher.college }}</view>
          <view class="table-cell">{{ teacher.courses ? teacher.courses.join(', ') : '无' }}</view>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">评价记录</text>
      </view>
      
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">课程</view>
          <view class="table-cell">任课教师</view>
          <view class="table-cell">评价人</view>
          <view class="table-cell">总分</view>
          <view class="table-cell">等级</view>
        </view>
        <view v-for="evaluation in evaluations" :key="evaluation.id" class="table-row">
          <view class="table-cell">{{ evaluation.courseName }}</view>
          <view class="table-cell">{{ evaluation.teacherName }}</view>
          <view class="table-cell">{{ evaluation.evaluatorName }}</view>
          <view class="table-cell">{{ evaluation.totalScore }}</view>
          <view class="table-cell">
            <text class="level-badge" :class="getLevelClass(evaluation.level)">{{ evaluation.level }}</text>
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
      evaluations: [],
      collegeTeachers: []
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadData();
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadData() {
      this.evaluations = simpleStore.getCollegeEvaluations(this.currentUser.college);
      this.collegeTeachers = simpleStore.state.users.filter(
        u => u.college === this.currentUser.college && u.role === 'teacher'
      );
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
}

.table-row:last-child {
  border-bottom: none;
}

.table-cell {
  flex: 1;
  padding: 4px 8px;
  color: #1f2933; /* 添加字体颜色 */
}

.level-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.level-excellent {
  background: #d1fae5;
  color: #059669;
}

.level-good {
  background: #cffafe;
  color: #0891b2;
}

.level-normal {
  background: #fef3c7;
  color: #d97706;
}

.level-pass {
  background: #fee2e2;
  color: #dc2626;
}

.level-fail {
  background: #fee2e2;
  color: #991b1b;
}
</style>