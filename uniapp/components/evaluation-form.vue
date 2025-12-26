<template>
  <view class="evaluation-form">
    <view class="form-section">
      <text class="section-title">教学态度（共20分）</text>
      <score-input
        :model-value="scores.teachingAttitude.punctuality"
        @update:model-value="val => scores.teachingAttitude.punctuality = val"
        label="按时上、下课，无迟到、拖堂等现象（5分）"
        :min="0"
        :max="5"
        :step="0.5"
        :disabled="isReadOnly"
      />
      <score-input
        :model-value="scores.teachingAttitude.management"
        @update:model-value="val => scores.teachingAttitude.management = val"
        label="严格课堂管理，检查学生出勤情况（5分）"
        :min="0"
        :max="5"
        :step="0.5"
      />
      <score-input
        :model-value="scores.teachingAttitude.appearance"
        @update:model-value="val => scores.teachingAttitude.appearance = val"
        label="仪态大方、精神饱满、富有感染力（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <view class="section-total">小计：{{ teachingAttitudeTotal.toFixed(1) }}分</view>
    </view>

    <view class="form-section">
      <text class="section-title">教学内容（共50分）</text>
      <score-input
        :model-value="scores.content.objectives"
        @update:model-value="val => scores.content.objectives = val"
        label="教学目标明确，符合教学大纲（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        :model-value="scores.content.familiarity"
        @update:model-value="val => scores.content.familiarity = val"
        label="熟悉教学内容、节奏流畅、重点难点突出（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        :model-value="scores.content.innovation"
        @update:model-value="val => scores.content.innovation = val"
        label="教学理念/设计/改革具有高阶性、创新性（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        :model-value="scores.content.ideology"
        @update:model-value="val => scores.content.ideology = val"
        label="课程思政融入明显（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        :model-value="scores.content.practice"
        @update:model-value="val => scores.content.practice = val"
        label="理论联系实际，注重能力素质培养（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <view class="section-total">小计：{{ contentTotal.toFixed(1) }}分</view>
    </view>

    <view class="form-section">
      <text class="section-title">教学方法与手段（共15分）</text>
      <score-input
        :model-value="scores.method.materials"
        @update:model-value="val => scores.method.materials = val"
        label="板书合理、课件规范（5分）"
        :min="0"
        :max="5"
        :step="0.5"
      />
      <score-input
        :model-value="scores.method.interaction"
        @update:model-value="val => scores.method.interaction = val"
        label="启发式、讨论式教学，注重互动（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <view class="section-total">小计：{{ methodTotal.toFixed(1) }}分</view>
    </view>

    <view class="form-section">
      <text class="section-title">教学效果（共15分）</text>
      <score-input
        :model-value="scores.effect.atmosphere"
        @update:model-value="val => scores.effect.atmosphere = val"
        label="课堂气氛活跃、听课率高（10分）"
        :min="0"
        :max="10"
        :step="0.5"
      />
      <score-input
        :model-value="scores.effect.inspiration"
        @update:model-value="val => scores.effect.inspiration = val"
        label="能启发学生创新、收获大（5分）"
        :min="0"
        :max="5"
        :step="0.5"
      />
      <view class="section-total">小计：{{ effectTotal.toFixed(1) }}分</view>
    </view>

    <view class="form-section summary">
      <view class="summary-header">
        <text class="section-title">总分及等级</text>
        <view v-if="submitStatus" class="submit-status" :class="submitStatus === 'during' ? 'status-during' : 'status-after'">
          <text class="status-icon">{{ submitStatus === 'during' ? '⏱️' : '✅' }}</text>
          <text class="status-text">{{ submitStatus === 'during' ? '课中' : '课后' }}</text>
        </view>
      </view>
      <view class="summary-info">
        <view class="total-score">总分：<text class="score-number">{{ totalScore.toFixed(1) }}</text>分</view>
        <view class="level">等级：<text :class="['level-text', levelClass]">{{ level }}</text></view>
      </view>
    </view>

    <view class="form-section">
      <text class="section-title">文字评价建议</text>
      <view class="suggestion-group">
        <view class="suggestion-item">
          <text class="suggestion-label">优点</text>
          <textarea 
            :value="suggestions.advantages" 
            @input="suggestions.advantages = $event.target.value" 
            placeholder="请填写教学优点，如：课程导入生动有趣、互动方式多样等..." 
            class="suggestion-textarea"
            :disabled="isReadOnly"
            maxlength="500"
          ></textarea>
          <text class="char-count">{{ suggestions.advantages.length }}/500</text>
        </view>
        <view class="suggestion-item">
          <text class="suggestion-label">问题</text>
          <textarea 
            :value="suggestions.problems" 
            @input="suggestions.problems = $event.target.value" 
            placeholder="请填写存在的问题，如：课程节奏过快、互动不足等..." 
            class="suggestion-textarea"
            :disabled="isReadOnly"
            maxlength="500"
          ></textarea>
          <text class="char-count">{{ suggestions.problems.length }}/500</text>
        </view>
        <view class="suggestion-item">
          <text class="suggestion-label">改进方向</text>
          <textarea 
            :value="suggestions.improvements" 
            @input="suggestions.improvements = $event.target.value" 
            placeholder="请填写改进方向和建议，如：建议增加实际案例、优化互动方式等..." 
            class="suggestion-textarea"
            :disabled="isReadOnly"
            maxlength="500"
          ></textarea>
          <text class="char-count">{{ suggestions.improvements.length }}/500</text>
        </view>
      </view>
    </view>

    <view v-if="showAnonymous" class="form-section">
      <view class="switch">
        <label class="switch-label">
          <switch 
            :checked="anonymous" 
            @change="anonymous = $event.detail.value" 
          />
          <text>匿名评价</text>
        </label>
      </view>
    </view>

    <view class="actions">
      <button v-if="!isReadOnly" @click="handleCancel" class="ghost">取消</button>
      <button v-if="!isReadOnly" @click="handleSubmit" class="primary" :disabled="!isValid">提交评价</button>
      <view v-if="isReadOnly" class="readonly-notice">
        <text class="notice-text">⚠️ 此评价已提交，不可修改</text>
      </view>
    </view>
  </view>
</template>

<script>
import ScoreInput from './score-input.vue';

export default {
  components: {
    ScoreInput
  },
  props: {
    showAnonymous: {
      type: Boolean,
      default: true
    },
    initialData: {
      type: Object,
      default: null
    },
    isReadOnly: {
      type: Boolean,
      default: false
    },
    submitStatus: {
      type: String,
      default: 'after' // 'during' 课中, 'after' 课后
    }
  },
  data() {
    return {
      scores: {
        teachingAttitude: {
          punctuality: 0,
          management: 0,
          appearance: 0
        },
        content: {
          objectives: 0,
          familiarity: 0,
          innovation: 0,
          ideology: 0,
          practice: 0
        },
        method: {
          materials: 0,
          interaction: 0
        },
        effect: {
          atmosphere: 0,
          inspiration: 0
        }
      },
      suggestions: {
        advantages: '', // 优点
        problems: '', // 问题
        improvements: '' // 改进方向
      },
      suggestion: '', // 保留旧字段以兼容
      anonymous: false
    };
  },
  computed: {
    teachingAttitudeTotal() {
      return Number((
        (this.scores.teachingAttitude.punctuality || 0) +
        (this.scores.teachingAttitude.management || 0) +
        (this.scores.teachingAttitude.appearance || 0)
      ).toFixed(1));
    },
    contentTotal() {
      return Number((
        (this.scores.content.objectives || 0) +
        (this.scores.content.familiarity || 0) +
        (this.scores.content.innovation || 0) +
        (this.scores.content.ideology || 0) +
        (this.scores.content.practice || 0)
      ).toFixed(1));
    },
    methodTotal() {
      return Number((
        (this.scores.method.materials || 0) +
        (this.scores.method.interaction || 0)
      ).toFixed(1));
    },
    effectTotal() {
      return Number((
        (this.scores.effect.atmosphere || 0) +
        (this.scores.effect.inspiration || 0)
      ).toFixed(1));
    },
    totalScore() {
      return Number((
        this.teachingAttitudeTotal + 
        this.contentTotal + 
        this.methodTotal + 
        this.effectTotal
      ).toFixed(1));
    },
    level() {
      const score = this.totalScore;
      if (score >= 90) return '优秀';
      if (score >= 80) return '良好';
      if (score >= 70) return '一般';
      if (score >= 60) return '合格';
      return '不合格';
    },
    levelClass() {
      const score = this.totalScore;
      if (score >= 90) return 'level-excellent';
      if (score >= 80) return 'level-good';
      if (score >= 70) return 'level-normal';
      if (score >= 60) return 'level-pass';
      return 'level-fail';
    },
    isValid() {
      const isAllFilled = Object.values(this.scores).every(section => 
        Object.values(section).every(score => score !== null && score !== undefined && !isNaN(score))
      );
      return isAllFilled && this.totalScore > 0 && this.totalScore <= 100;
    }
  },
  methods: {
    handleSubmit() {
      // 合并文字建议（兼容旧格式）
      const combinedSuggestion = [
        this.suggestions.advantages ? `优点：${this.suggestions.advantages}` : '',
        this.suggestions.problems ? `问题：${this.suggestions.problems}` : '',
        this.suggestions.improvements ? `改进方向：${this.suggestions.improvements}` : ''
      ].filter(s => s).join('\n\n') || this.suggestion;
      
      const evaluationData = {
        scores: {
          teachingAttitude: this.teachingAttitudeTotal,
          content: this.contentTotal,
          method: this.methodTotal,
          effect: this.effectTotal,
          detail: this.scores
        },
        totalScore: this.totalScore,
        level: this.level,
        suggestion: combinedSuggestion, // 合并后的建议
        suggestions: {
          advantages: this.suggestions.advantages,
          problems: this.suggestions.problems,
          improvements: this.suggestions.improvements
        },
        anonymous: this.anonymous
      };
      this.$emit('submit', evaluationData);
    },
    handleCancel() {
      this.$emit('cancel');
    }
  },
  created() {
    if (this.initialData) {
      this.scores = this.initialData.scores?.detail || this.scores;
      this.suggestion = this.initialData.suggestion || '';
      // 如果已有新的建议格式，使用新格式；否则尝试从旧格式解析
      if (this.initialData.suggestions) {
        this.suggestions = {
          advantages: this.initialData.suggestions.advantages || '',
          problems: this.initialData.suggestions.problems || '',
          improvements: this.initialData.suggestions.improvements || ''
        };
      } else if (this.initialData.suggestion) {
        // 尝试从旧格式解析（如果包含"优点："、"问题："、"改进方向："等关键词）
        const suggestion = this.initialData.suggestion;
        const advantagesMatch = suggestion.match(/优点[：:]\s*(.+?)(?=\n\n|问题|改进方向|$)/s);
        const problemsMatch = suggestion.match(/问题[：:]\s*(.+?)(?=\n\n|改进方向|$)/s);
        const improvementsMatch = suggestion.match(/改进方向[：:]\s*(.+?)$/s);
        this.suggestions = {
          advantages: advantagesMatch ? advantagesMatch[1].trim() : '',
          problems: problemsMatch ? problemsMatch[1].trim() : '',
          improvements: improvementsMatch ? improvementsMatch[1].trim() : ''
        };
      }
      this.anonymous = this.initialData.anonymous || false;
    }
  }
};
</script>

<style scoped>
.evaluation-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-section {
  background: #eef2ff;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e4e9f1;
}

.section-title {
  display: block;
  margin: 0 0 16px;
  font-size: 18px;
  color: #2d3643;
  font-weight: bold;
}

.section-total {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e9f1;
  text-align: right;
  font-weight: 600;
  color: #4f46e5;
}

.summary {
  background: linear-gradient(135deg, #dbeafe, #eef2ff);
  border-color: #c7d2fe;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.submit-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-during {
  background: #fef3c7;
  color: #d97706;
}

.status-after {
  background: #d1fae5;
  color: #059669;
}

.status-icon {
  font-size: 14px;
}

.status-text {
  font-size: 12px;
}

.summary-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.total-score {
  font-size: 18px;
}

.score-number {
  font-size: 24px;
  color: #4f46e5;
  font-weight: bold;
}

.level {
  font-size: 18px;
}

.level-text {
  font-size: 20px;
  padding: 4px 12px;
  border-radius: 8px;
  font-weight: bold;
}

.level-excellent {
  color: #059669;
  background: #d1fae5;
}

.level-good {
  color: #0891b2;
  background: #cffafe;
}

.level-normal {
  color: #d97706;
  background: #fef3c7;
}

.level-pass {
  color: #dc2626;
  background: #fee2e2;
}

.level-fail {
  color: #991b1b;
  background: #fee2e2;
}

.suggestion-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.suggestion-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-label {
  font-size: 16px;
  font-weight: 600;
  color: #2d3643;
  display: block;
}

.suggestion-textarea {
  width: 100%;
  min-height: 100px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
  line-height: 1.6;
}

.suggestion-textarea:disabled {
  background-color: #f5f5f5;
  color: #666;
  cursor: not-allowed;
}

.char-count {
  font-size: 12px;
  color: #999;
  text-align: right;
  margin-top: -4px;
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

.primary {
  background: #4f46e5;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: bold;
}

.ghost {
  background: #fff;
  border: 1px solid #d7deea;
  color: #1f2933;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: bold;
}

.primary:disabled {
  opacity: 0.5;
}

.readonly-notice {
  padding: 12px;
  background: #fef3c7;
  border-radius: 8px;
  border-left: 4px solid #f59e0b;
  text-align: center;
}

.notice-text {
  color: #92400e;
  font-size: 14px;
  font-weight: 500;
}

@media (max-width: 640px) {
  .form-section {
    padding: 16px;
  }
  
  .section-title {
    font-size: 16px;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .actions button {
    width: 100%;
  }
  
  .summary-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>