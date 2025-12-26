<template>
  <view class="score-input">
    <view class="score-label">
      <text class="label-text">{{ label }}</text>
      <text class="score-value">{{ modelValue }}分</text>
    </view>
    <view class="score-controls">
      <view class="quick-buttons">
        <button
          v-for="quickValue in quickValues"
          :key="quickValue"
          type="button"
          class="quick-btn"
          :class="{ active: modelValue === quickValue }"
          :disabled="disabled"
          @click="updateValue(quickValue)"
        >
          {{ quickValue }}
        </button>
      </view>
      <view class="slider-container">
        <slider
          :min="min"
          :max="max"
          :step="step"
          :value="modelValue"
          :disabled="disabled"
          @change="onSliderChange"
          class="score-slider"
        />
        <view class="slider-labels">
          <text>{{ min }}</text>
          <text>{{ max }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  props: {
    label: {
      type: String,
      required: true
    },
    // 支持 v-model 双向绑定（Vue3 语法）
    modelValue: {
      type: Number,
      default: 0
    },
    disabled: {
      type: Boolean,
      default: false
    },
    min: {
      type: Number,
      default: 0
    },
    max: {
      type: Number,
      required: true
    },
    step: {
      type: Number,
      default: 0.5,
      validator: function(value) {
        return value > 0; // 确保步长为正数
      }
    }
  },
  computed: {
    quickValues() {
      const values = [];
      // 根据最大值动态调整快速选择按钮的步长
      const step = this.max <= 5 ? 1 : 2;
      // 生成快速选择值（确保包含最大值）
      for (let i = this.min; i <= this.max; i += step) {
        values.push(Number(i.toFixed(1))); // 处理浮点数精度问题
      }
      // 确保最大值被包含
      const lastValue = values[values.length - 1];
      if (lastValue !== this.max) {
        values.push(this.max);
      }
      return values;
    }
  },
  methods: {
    updateValue(value) {
      // 确保值在有效范围内
      if (value >= this.min && value <= this.max) {
        this.$emit('update:modelValue', value);
      }
    },
    onSliderChange(e) {
      // 处理滑块值变化，修复浮点数精度
      const value = Number(e.detail.value.toFixed(1));
      this.$emit('update:modelValue', value);
    }
  }
};
</script>

<style scoped>
.score-input {
  margin-bottom: 20px;
}

.score-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #2d3643;
}

.label-text {
  flex: 1;
  font-weight: 500;
  line-height: 1.5;
}

.score-value {
  font-weight: 600;
  color: #4f46e5;
  font-size: 16px;
  min-width: 50px;
  text-align: right;
}

.score-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-btn {
  flex: 1;
  min-width: 50px;
  padding: 8px 12px;
  border: 2px solid #e4e9f1;
  border-radius: 8px;
  background: #fff;
  color: #5d6673;
  font-weight: 600;
  font-size: 14px;
}

.quick-btn:hover {
  border-color: #4f46e5;
  color: #4f46e5;
  background: #eef2ff;
}

.quick-btn.active {
  background: #4f46e5;
  color: #fff;
  border-color: #4f46e5;
}

.quick-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.slider-container {
  position: relative;
}

.score-slider {
  width: 100%;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 12px;
  color: #1f2933;
}

/* 移动端优化 */
@media (max-width: 640px) {
  .score-label {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .score-value {
    text-align: left;
  }

  .quick-buttons {
    gap: 6px;
  }

  .quick-btn {
    min-width: 45px;
    padding: 10px 8px;
    font-size: 13px;
  }
}
</style>