<template>
  <view class="page">
    <view class="header">
      <view>
        <text class="eyebrow">学校管理员</text>
        <text class="title">评教通知管理</text>
        <text class="desc">发布或删除评教通知</text>
      </view>
      <view class="header-badges">
        <button @click="showAddModal = true" class="add-btn">+ 发布通知</button>
        <button @click="navigateBack" class="badge">返回</button>
      </view>
    </view>

    <view class="panel">
      <view class="panel-title">
        <text class="panel-title-text">通知列表</text>
        <text class="panel-desc">所有评教相关通知</text>
      </view>
      
      <view v-if="notices.length === 0" class="empty">暂无通知</view>
      <view v-else class="notice-list">
        <view v-for="notice in notices" :key="notice.id" class="notice-item">
          <view class="notice-header">
            <view>
              <text class="notice-title">{{ notice.title }}</text>
              <text class="notice-time">{{ formatDate(notice.createdAt) }}</text>
            </view>
            <view class="notice-actions">
              <button @click="editNotice(notice)" class="action-btn edit">编辑</button>
              <button @click="deleteNotice(notice)" class="action-btn delete">删除</button>
            </view>
          </view>
          <text class="notice-content">{{ notice.content }}</text>
          <view class="notice-footer">
            <text class="notice-sender">发布人：{{ notice.sender }}</text>
            <text class="notice-target">目标：{{ getTargetLabel(notice.targetCollege) }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 添加/编辑通知弹窗 -->
    <view v-if="showAddModal || editingNotice" class="modal-overlay" @click="closeModal">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <text class="modal-title">{{ editingNotice ? '编辑通知' : '发布通知' }}</text>
          <button @click="closeModal" class="close-btn">×</button>
        </view>
        <view class="modal-body">
          <view class="form-item">
            <text class="form-label">通知标题</text>
            <input class="form-input" v-model="formData.title" placeholder="请输入通知标题" />
          </view>
          <view class="form-item">
            <text class="form-label">通知内容</text>
            <textarea 
              class="form-textarea" 
              v-model="formData.content" 
              placeholder="请输入通知内容"
              maxlength="500"
            ></textarea>
            <text class="char-count">{{ formData.content.length }}/500</text>
          </view>
          <view class="form-item">
            <text class="form-label">发布范围</text>
            <picker mode="selector" :range="targetOptions" :range-key="'label'" @change="onTargetChange">
              <view class="picker-view">{{ selectedTargetLabel }}</view>
            </picker>
          </view>
        </view>
        <view class="modal-footer">
          <button @click="closeModal" class="btn-cancel">取消</button>
          <button @click="saveNotice" class="btn-save">保存</button>
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
      notices: [],
      showAddModal: false,
      editingNotice: null,
      formData: {
        title: '',
        content: '',
        targetCollege: 'all'
      },
      targetOptions: [
        { label: '全部学院', value: 'all' },
        { label: '信息工程学院', value: '信息工程学院' },
        { label: '数学学院', value: '数学学院' },
        { label: '物理学院', value: '物理学院' }
      ],
      selectedTargetLabel: '全部学院'
    };
  },
  onLoad() {
    this.loadUserData();
    this.loadNotices();
    this.updateTargetOptions();
  },
  methods: {
    loadUserData() {
      this.currentUser = simpleStore.state.currentUser || {};
    },
    loadNotices() {
      // 从本地存储加载所有通知
      this.notices = (simpleStore.state.notices || []).sort((a, b) => 
        new Date(b.createdAt) - new Date(a.createdAt)
      );
    },
    updateTargetOptions() {
      // 动态获取所有学院
      const colleges = simpleStore.getColleges();
      this.targetOptions = [
        { label: '全部学院', value: 'all' },
        ...colleges.map(c => ({ label: c.name, value: c.name }))
      ];
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleString('zh-CN');
    },
    getTargetLabel(targetCollege) {
      if (!targetCollege || targetCollege === 'all') return '全部学院';
      return targetCollege;
    },
    editNotice(notice) {
      this.editingNotice = notice;
      this.formData = {
        title: notice.title,
        content: notice.content,
        targetCollege: notice.targetCollege || 'all'
      };
      this.selectedTargetLabel = this.getTargetLabel(notice.targetCollege);
    },
    deleteNotice(notice) {
      uni.showModal({
        title: '确认删除',
        content: `确定要删除通知"${notice.title}"吗？`,
        success: (res) => {
          if (res.confirm) {
            const index = simpleStore.state.notices.findIndex(n => n.id === notice.id);
            if (index !== -1) {
              simpleStore.state.notices.splice(index, 1);
              simpleStore.saveAllToStorage();
              this.loadNotices();
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              });
            }
          }
        }
      });
    },
    onTargetChange(e) {
      const index = e.detail.value;
      this.formData.targetCollege = this.targetOptions[index].value;
      this.selectedTargetLabel = this.targetOptions[index].label;
    },
    saveNotice() {
      if (!this.formData.title || !this.formData.content) {
        uni.showToast({
          title: '请填写完整信息',
          icon: 'none'
        });
        return;
      }

      // ========== 后端接入点：保存通知 ==========
      // TODO: 后期接入后端接口时，可在此处调用API保存通知
      // 示例：
      // const noticeData = {
      //   title: this.formData.title,
      //   content: this.formData.content,
      //   targetCollege: this.formData.targetCollege
      // };
      // if (this.editingNotice) {
      //   // 编辑通知
      //   await uni.request({
      //     url: `/api/notices/${this.editingNotice.id}`,
      //     method: 'PUT',
      //     data: noticeData
      //   });
      // } else {
      //   // 发布新通知
      //   await uni.request({
      //     url: '/api/notices',
      //     method: 'POST',
      //     data: noticeData
      //   });
      // }
      // ============================================
      
      if (this.editingNotice) {
        // 编辑通知
        const notice = simpleStore.state.notices.find(n => n.id === this.editingNotice.id);
        if (notice) {
          notice.title = this.formData.title;
          notice.content = this.formData.content;
          notice.targetCollege = this.formData.targetCollege;
          notice.updatedAt = new Date().toISOString();
        }
      } else {
        // 发布新通知
        const newNotice = {
          id: Date.now(),
          title: this.formData.title,
          content: this.formData.content,
          sender: this.currentUser.name || '系统管理员',
          targetCollege: this.formData.targetCollege,
          createdAt: new Date().toISOString(),
          isRead: false
        };
        simpleStore.state.notices.push(newNotice);
      }
      
      simpleStore.saveAllToStorage();
      this.loadNotices();
      this.closeModal();
      uni.showToast({
        title: this.editingNotice ? '更新成功' : '发布成功',
        icon: 'success'
      });
    },
    closeModal() {
      this.showAddModal = false;
      this.editingNotice = null;
      this.formData = {
        title: '',
        content: '',
        targetCollege: 'all'
      };
      this.selectedTargetLabel = '全部学院';
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
  display: block;
  margin-bottom: 4px;
}

.notice-time {
  font-size: 12px;
  color: #666;
  display: block;
}

.notice-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  border: none;
}

.action-btn.edit {
  background: #dbeafe;
  color: #1e40af;
}

.action-btn.delete {
  background: #fee2e2;
  color: #991b1b;
}

.notice-content {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
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

.notice-target {
  font-size: 12px;
  color: #4f46e5;
  font-weight: 500;
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
  max-width: 600px;
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

.form-textarea {
  width: 100%;
  min-height: 120px;
  padding: 12px;
  border: 1px solid #d7deea;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  line-height: 1.6;
}

.char-count {
  font-size: 12px;
  color: #999;
  text-align: right;
  margin-top: 4px;
  display: block;
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

