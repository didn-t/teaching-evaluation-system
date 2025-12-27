<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">督导端</text>
        <text class="title">进行评教</text>
        <text class="desc">对负责范围内的课程进行教学质量评价</text>
      </view>
      <view class="header-badges">
        <button @click="navigateBack" class="badge">返回</button>
      </view>
    </view>

    <!-- 权限检查提示 -->
    <view v-if="!hasPermission" class="panel error-panel">
      <text class="error-text">⚠️ 只有督导老师才能进行评教操作</text>
    </view>

    <view v-else>
      <view class="panel">
        <view class="panel-title">
          <text class="panel-title-text">选择课程</text>
        </view>
        <view class="form-grid">
          <view class="field">
            <text class="label">选择课程</text>
            <picker mode="selector" :range="courseOptions" :range-key="'name'" @change="onCourseChange">
              <view class="picker-text">{{ selectedCourseName || '请选择课程' }}</view>
            </picker>
            <text class="help-text">仅显示您负责范围内的课程</text>
          </view>
          <view class="field">
            <text class="label">评价人角色</text>
            <picker mode="selector" :range="roleOptions" @change="onRoleChange">
              <view class="picker-text">{{ selectedRoleLabel }}</view>
            </picker>
            <text class="help-text">督导老师身份进行评价</text>
          </view>
          <view class="field">
            <text class="label">提交状态</text>
            <picker mode="selector" :range="statusOptions" :range-key="'label'" @change="onStatusChange">
              <view class="picker-text">{{ selectedStatusLabel }}</view>
            </picker>
            <text class="help-text">选择课中或课后提交</text>
          </view>
        </view>
      </view>

      <view v-if="selectedCourseId" class="panel">
        <evaluation-form 
          :show-anonymous="showAnonymous" 
          :submit-status="submitStatus"
          :is-read-only="false"
          @submit="handleSubmit" 
          @cancel="handleCancel" 
        />
      </view>
    </view>
  </view>
</template>

<script>
import EvaluationForm from '../../components/evaluation-form.vue';
import { simpleStore } from '../../utils/simpleStore';

export default {
  components: {
    EvaluationForm
  },
  data() {
    return {
      currentUser: {},
      hasPermission: false,
      selectedCourseId: '',
      selectedCourseName: '',
      selectedCourse: null,
      evaluatorRole: 'supervisor', // 督导老师默认角色
      selectedRoleLabel: '👨‍🏫 督导老师',
      courseOptions: [],
      roleOptions: [
        { label: '👨‍🏫 督导老师', value: 'supervisor' }
      ],
      submitStatus: 'after', // 提交状态：'during' 课中, 'after' 课后
      statusOptions: [
        { label: '⏱️ 课中', value: 'during' },
        { label: '✅ 课后', value: 'after' }
      ],
      selectedStatusLabel: '✅ 课后'
    };
  },
  computed: {
    showAnonymous() {
      // 根据学校管理员配置显示匿名选项
      // 如果配置为全局匿名，则不显示选项（强制匿名）
      // 如果配置为可选匿名，则显示选项（用户自主选择）
      const config = simpleStore.getConfig();
      if (config.anonymousMode === 'global' && config.globalAnonymous) {
        // 全局匿名模式，不显示选项，但需要设置为匿名
        return false; // 不显示开关，但会在提交时设置为匿名
      }
      // 可选匿名模式，显示选项
      return true;
    },
    defaultAnonymous() {
      // 根据配置返回默认匿名状态
      const config = simpleStore.getConfig();
      return config.anonymousMode === 'global' && config.globalAnonymous;
    }
  },
  onLoad(options) {
    // 检查权限
    this.checkPermission();
    
    // 统一评教逻辑，不再区分普通评教和听课评教
    
    // 如果从课表页面跳转，直接设置课程信息
    if (options && options.courseId) {
      this.selectedCourseId = options.courseId;
      this.selectedCourseName = decodeURIComponent(options.courseName || '');
      // 预填充课程信息
      this.selectedCourse = {
        id: options.courseId,
        name: decodeURIComponent(options.courseName || ''),
        teacherId: options.teacherId,
        teacherName: decodeURIComponent(options.teacherName || '')
      };
    }
    
    this.loadCourses();
    
    // 更新标题
    this.$scope && this.$scope.$page && (this.$scope.$page.navigationBarTitleText = '督导端-进行评教');
  },
  methods: {
    checkPermission() {
      // 从本地存储检查权限，不进行服务器连接检测
      // TODO: 后期接入后端接口时，可在此处调用API检查权限
      // 示例：
      // try {
      //   const response = await uni.request({ 
      //     url: `/api/permissions/can-evaluate?userId=${this.currentUser.id}`,
      //     timeout: 10000
      //   });
      //   this.hasPermission = response.data.hasPermission;
      // } catch (error) {
      //   console.error('检查权限失败:', error);
      //   // 失败时使用本地数据作为降级方案
      //   this.hasPermission = simpleStore.canEvaluate(this.currentUser.id || this.currentUser._id);
      // }
      
      const currentUser = simpleStore.state.currentUser || {};
      this.currentUser = currentUser;
      this.hasPermission = simpleStore.canEvaluate(currentUser.id || currentUser._id);
      
      if (!this.hasPermission) {
        uni.showToast({
          title: '您没有评教权限',
          icon: 'none',
          duration: 2000
        });
      }
    },
    loadCourses() {
      // 从本地存储加载课程列表，不进行服务器连接检测
      // TODO: 后期接入后端接口时，可在此处调用API获取课程列表
      // 示例：
      // try {
      //   const userId = this.currentUser.id || this.currentUser._id;
      //   const response = await uni.request({ 
      //     url: `/api/supervisor/courses?supervisorId=${userId}`,
      //     timeout: 10000
      //   });
      //   const courses = response.data;
      //   this.courseOptions = courses.map(course => ({
      //     ...course,
      //     name: `${course.name} - ${course.teacherName} (${course.semester})`
      //   }));
      // } catch (error) {
      //   console.error('加载课程失败:', error);
      //   // 失败时使用本地数据作为降级方案
      //   const courses = simpleStore.getSupervisorCourses(userId);
      //   this.courseOptions = courses.map(course => ({
      //     ...course,
      //     name: `${course.name} - ${course.teacherName} (${course.semester})`
      //   }));
      // }
      
      try {
        const userId = this.currentUser.id || this.currentUser._id;
        
        // 使用本地存储数据，不进行网络请求
        const courses = simpleStore.getSupervisorCourses(userId);
        
        this.courseOptions = courses.map(course => ({
          ...course,
          name: `${course.name} - ${course.teacherName} (${course.semester})`
        }));
        
        // 如果已预选课程，更新选中状态
        if (this.selectedCourseId && this.selectedCourse) {
          const found = this.courseOptions.find(c => (c.id || c._id) == this.selectedCourseId);
          if (found) {
            this.selectedCourse = found;
            this.selectedCourseName = found.name;
          }
        }
      } catch (error) {
        console.error('加载课程失败:', error);
        // 静默处理错误
      }
    },
    onCourseChange(e) {
      const selectedIndex = e.detail.value;
      const selectedCourse = this.courseOptions[selectedIndex];
      this.selectedCourseId = selectedCourse.id || selectedCourse._id;
      this.selectedCourseName = selectedCourse.name;
      this.selectedCourse = selectedCourse;
    },
    onRoleChange(e) {
      const selectedIndex = e.detail.value;
      this.evaluatorRole = this.roleOptions[selectedIndex].value;
      this.selectedRoleLabel = this.roleOptions[selectedIndex].label;
    },
    onStatusChange(e) {
      const selectedIndex = e.detail.value;
      this.submitStatus = this.statusOptions[selectedIndex].value;
      this.selectedStatusLabel = this.statusOptions[selectedIndex].label;
    },
    handleSubmit(evaluationData) {
      if (!this.selectedCourseId || !this.selectedCourse) {
        uni.showToast({
          title: '请选择课程',
          icon: 'none'
        });
        return;
      }

      const currentUser = simpleStore.state.currentUser || {};
      
      // 获取课程所属学院信息，确保记录自动留存到各学院每位教师
      const course = simpleStore.state.courses.find(c => 
        (c.id || c._id) == (this.selectedCourse.id || this.selectedCourse._id)
      );
      const college = course ? course.college : (currentUser.college || '');
      
      const evaluation = {
        courseId: this.selectedCourse.id || this.selectedCourse._id,
        courseName: this.selectedCourse.name,
        teacherId: this.selectedCourse.teacherId || this.selectedCourse.teacherId,
        teacherName: this.selectedCourse.teacherName,
        college: college, // 保存学院信息，确保记录自动留存到各学院
        evaluatorId: currentUser.id || currentUser._id,
        evaluatorName: currentUser.name || '督导老师',
        evaluatorRole: this.evaluatorRole,
        anonymous: this.defaultAnonymous || evaluationData.anonymous, // 根据配置设置匿名状态
        scores: evaluationData.scores,
        suggestions: evaluationData.suggestions || {}, // 保存详细的文字建议（优点、问题、改进方向）
        totalScore: evaluationData.totalScore,
        level: evaluationData.level,
        suggestion: evaluationData.suggestion, // 保留合并后的建议文本（兼容旧格式）
        submitStatus: this.submitStatus, // 保存提交状态（听课中/课后）
        createdAt: new Date().toISOString(),
        id: Date.now() // 简单生成唯一ID
      };

      try {
        // ========== 后端接入点：提交评教数据 ==========
        // TODO: 后期接入后端接口时，可在此处调用API提交评教数据
        // 示例：
        // const response = await uni.request({
        //   url: '/api/evaluations/submit',
        //   method: 'POST',
        //   data: evaluation,
        //   header: {
        //     'Authorization': 'Bearer ' + token
        //   }
        // });
        // ============================================
        
        // 统一评教逻辑：所有评教都保存到evaluations中，不再区分普通评教和听课评教
        // 添加评价者信息（如果还没有）
        if (!evaluation.evaluatorId) {
          evaluation.evaluatorId = currentUser.id || currentUser._id;
          evaluation.evaluatorName = currentUser.name || '督导老师';
        }
        
        const evaluations = simpleStore.state.evaluations || [];
        evaluations.push(evaluation);
        simpleStore.state.evaluations = evaluations;
        
        // 自动保存记录到各学院每位教师（记录已包含学院和教师信息）
        simpleStore.saveAllToStorage();

        uni.showToast({
          title: '评价提交成功！记录已自动保存',
          icon: 'success',
          duration: 2000
        });

        setTimeout(() => {
          uni.navigateBack();
        }, 2000);
      } catch (error) {
        console.error('评价提交失败:', error);
        uni.showToast({
          title: '评价提交失败',
          icon: 'none'
        });
      }
    },
    handleCancel() {
      uni.navigateBack();
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

.error-panel {
  background: #fee;
  border: 1px solid #fed7d7;
}

.error-text {
  color: #e53e3e;
  font-size: 14px;
  display: block;
  text-align: center;
}

.panel-title {
  margin-bottom: 16px;
}

.panel-title-text {
  font-size: 20px;
  font-weight: bold;
  display: block;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.label {
  font-weight: 500;
  font-size: 14px;
  color: #333;
}

.picker-text {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 12px;
  font-size: 14px;
  background: white;
}

.help-text {
  margin: 4px 0 0;
  font-size: 12px;
  color: #666;
}
</style>

