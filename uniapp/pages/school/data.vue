<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学校管理员</text>
        <text class="title">数据管理</text>
        <text class="desc">欢迎，{{ currentUser.name }}</text>
      </view>
      <view class="header-badges">
        <button @click="handleLogout" class="logout-btn">退出登录</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">学院列表</text>
      </view>
      
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">学院名称</view>
        </view>
        <view v-for="college in colleges" :key="college.id" class="table-row">
          <view class="table-cell">{{ college.name }}</view>
        </view>
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
        <view v-for="teacher in allTeachers" :key="teacher.id" class="table-row">
          <view class="table-cell">{{ teacher.name }}</view>
          <view class="table-cell">{{ teacher.college }}</view>
          <view class="table-cell">{{ teacher.courses ? teacher.courses.join(', ') : '无' }}</view>
        </view>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">课程列表</text>
      </view>
      
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">课程名称</view>
          <view class="table-cell">任课教师</view>
          <view class="table-cell">所属学院</view>
        </view>
        <view v-for="course in allCourses" :key="course.id" class="table-row">
          <view class="table-cell">{{ course.name }}</view>
          <view class="table-cell">{{ course.teacherName }}</view>
          <view class="table-cell">{{ course.college }}</view>
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
      colleges: [],
      allTeachers: [],
      allCourses: []
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
      this.colleges = simpleStore.getColleges();
      this.allTeachers = simpleStore.getUsers().filter(u => u.role === 'teacher');
      this.allCourses = simpleStore.getCourses();
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
</style>