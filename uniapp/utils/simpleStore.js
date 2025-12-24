// 初始化默认数据
const defaultUsers = [
  { id: 1, username: 'teacher1', password: '123456', name: '张老师', role: 'teacher', college: '信息工程学院', courses: ['Vue.js开发', '前端框架'] },
  { id: 2, username: 'teacher2', password: '123456', name: '李老师', role: 'teacher', college: '信息工程学院', courses: ['Java程序设计', '数据结构'] },
  { id: 3, username: 'college1', password: '123456', name: '王主任', role: 'college_admin', college: '信息工程学院' },
  { id: 4, username: 'school1', password: '123456', name: '系统管理员', role: 'school_admin', college: '' },
];

const defaultColleges = [
  { id: 1, name: '信息工程学院' },
  { id: 2, name: '数学学院' },
  { id: 3, name: '物理学院' },
];

const defaultCourses = [
  { id: 1, name: 'Vue.js开发', teacherId: 1, teacherName: '张老师', college: '信息工程学院', semester: '2025春' },
  { id: 2, name: 'Java程序设计', teacherId: 2, teacherName: '李老师', college: '信息工程学院', semester: '2025春' },
  { id: 3, name: '数据结构', teacherId: 2, teacherName: '李老师', college: '信息工程学院', semester: '2025春' },
];

// 示例评价数据
const defaultEvaluations = [
  {
    id: 1001,
    courseId: 1,
    courseName: 'Vue.js开发',
    teacherId: 1,
    teacherName: '张老师',
    evaluatorId: 101,
    evaluatorName: '学生A',
    evaluatorRole: 'student',
    anonymous: true,
    scores: {
      teachingAttitude: 18,
      content: 45,
      method: 13,
      effect: 14,
      detail: {
        teachingAttitude: { punctuality: 5, management: 5, appearance: 8 },
        content: { objectives: 9, familiarity: 9, innovation: 9, ideology: 9, practice: 9 },
        method: { materials: 5, interaction: 8 },
        effect: { atmosphere: 9, inspiration: 5 }
      }
    },
    totalScore: 90,
    level: '优秀',
    suggestion: '老师讲课非常清晰，案例丰富，能够很好地引导学生思考。建议可以增加一些实际项目练习。',
    createdAt: new Date('2025-03-15T10:30:00').toISOString()
  },
  {
    id: 1002,
    courseId: 1,
    courseName: 'Vue.js开发',
    teacherId: 1,
    teacherName: '张老师',
    evaluatorId: 102,
    evaluatorName: '学生B',
    evaluatorRole: 'student',
    anonymous: true,
    scores: {
      teachingAttitude: 19,
      content: 48,
      method: 14,
      effect: 15,
      detail: {
        teachingAttitude: { punctuality: 5, management: 5, appearance: 9 },
        content: { objectives: 10, familiarity: 10, innovation: 9, ideology: 9, practice: 10 },
        method: { materials: 5, interaction: 9 },
        effect: { atmosphere: 10, inspiration: 5 }
      }
    },
    totalScore: 96,
    level: '优秀',
    suggestion: '课程内容深入浅出，老师讲解生动有趣，课堂互动很好。希望可以多分享一些实战经验。',
    createdAt: new Date('2025-03-18T14:20:00').toISOString()
  },
  {
    id: 1003,
    courseId: 1,
    courseName: 'Vue.js开发',
    teacherId: 1,
    teacherName: '张老师',
    evaluatorId: 2,
    evaluatorName: '李老师',
    evaluatorRole: 'teacher',
    anonymous: false,
    scores: {
      teachingAttitude: 17,
      content: 42,
      method: 12,
      effect: 13,
      detail: {
        teachingAttitude: { punctuality: 5, management: 4, appearance: 8 },
        content: { objectives: 8, familiarity: 8, innovation: 8, ideology: 9, practice: 9 },
        method: { materials: 4, interaction: 8 },
        effect: { atmosphere: 8, inspiration: 5 }
      }
    },
    totalScore: 84,
    level: '良好',
    suggestion: '教学思路清晰，建议在课程思政融入方面可以更加自然一些。',
    createdAt: new Date('2025-03-20T09:15:00').toISOString()
  },
  {
    id: 1004,
    courseId: 2,
    courseName: 'Java程序设计',
    teacherId: 2,
    teacherName: '李老师',
    evaluatorId: 103,
    evaluatorName: '学生C',
    evaluatorRole: 'student',
    anonymous: true,
    scores: {
      teachingAttitude: 18,
      content: 46,
      method: 13,
      effect: 14,
      detail: {
        teachingAttitude: { punctuality: 5, management: 5, appearance: 8 },
        content: { objectives: 9, familiarity: 9, innovation: 9, ideology: 9, practice: 10 },
        method: { materials: 5, interaction: 8 },
        effect: { atmosphere: 9, inspiration: 5 }
      }
    },
    totalScore: 91,
    level: '优秀',
    suggestion: '老师对Java的理解很深入，讲解透彻。建议可以增加一些代码调试的演示。',
    createdAt: new Date('2025-03-16T11:00:00').toISOString()
  },
  {
    id: 1005,
    courseId: 2,
    courseName: 'Java程序设计',
    teacherId: 2,
    teacherName: '李老师',
    evaluatorId: 104,
    evaluatorName: '学生D',
    evaluatorRole: 'student',
    anonymous: true,
    scores: {
      teachingAttitude: 16,
      content: 40,
      method: 11,
      effect: 12,
      detail: {
        teachingAttitude: { punctuality: 4, management: 4, appearance: 8 },
        content: { objectives: 8, familiarity: 8, innovation: 8, ideology: 8, practice: 8 },
        method: { materials: 4, interaction: 7 },
        effect: { atmosphere: 7, inspiration: 5 }
      }
    },
    totalScore: 79,
    level: '一般',
    suggestion: '课程内容不错，但节奏稍快，希望可以放慢一些，让基础薄弱的同学也能跟上。',
    createdAt: new Date('2025-03-19T15:30:00').toISOString()
  },
  {
    id: 1006,
    courseId: 3,
    courseName: '数据结构',
    teacherId: 2,
    teacherName: '李老师',
    evaluatorId: 105,
    evaluatorName: '学生E',
    evaluatorRole: 'student',
    anonymous: true,
    scores: {
      teachingAttitude: 19,
      content: 47,
      method: 14,
      effect: 15,
      detail: {
        teachingAttitude: { punctuality: 5, management: 5, appearance: 9 },
        content: { objectives: 9, familiarity: 10, innovation: 9, ideology: 9, practice: 10 },
        method: { materials: 5, interaction: 9 },
        effect: { atmosphere: 10, inspiration: 5 }
      }
    },
    totalScore: 95,
    level: '优秀',
    suggestion: '数据结构讲解非常清晰，图示和动画演示帮助很大。建议可以增加一些算法优化的讲解。',
    createdAt: new Date('2025-03-17T13:45:00').toISOString()
  }
];

// 示例听课记录
const defaultListenRecords = [
  {
    id: 2001,
    courseId: 1,
    courseName: 'Vue.js开发',
    teacherId: 1,
    teacherName: '张老师',
    listenerId: 2,
    listenerName: '李老师',
    scores: {
      teachingAttitude: 18,
      content: 44,
      method: 13,
      effect: 14,
      detail: {
        teachingAttitude: { punctuality: 5, management: 5, appearance: 8 },
        content: { objectives: 9, familiarity: 9, innovation: 9, ideology: 8, practice: 9 },
        method: { materials: 5, interaction: 8 },
        effect: { atmosphere: 9, inspiration: 5 }
      }
    },
    totalScore: 89,
    level: '良好',
    suggestion: '教学思路清晰，课堂组织有序。建议在互动环节可以更加活跃一些。',
    createdAt: new Date('2025-03-14T10:00:00').toISOString()
  },
  {
    id: 2002,
    courseId: 2,
    courseName: 'Java程序设计',
    teacherId: 2,
    teacherName: '李老师',
    listenerId: 1,
    listenerName: '张老师',
    scores: {
      teachingAttitude: 17,
      content: 43,
      method: 12,
      effect: 13,
      detail: {
        teachingAttitude: { punctuality: 5, management: 4, appearance: 8 },
        content: { objectives: 8, familiarity: 9, innovation: 8, ideology: 9, practice: 9 },
        method: { materials: 4, interaction: 8 },
        effect: { atmosphere: 8, inspiration: 5 }
      }
    },
    totalScore: 85,
    level: '良好',
    suggestion: '课程内容充实，讲解详细。建议可以增加一些实际案例的分析。',
    createdAt: new Date('2025-03-15T14:00:00').toISOString()
  }
];

// 从uni.setStorage获取数据或使用默认数据
const getStoredData = (key, defaultValue) => {
  try {
    const stored = uni.getStorageSync(key);
    return stored ? JSON.parse(stored) : defaultValue;
  } catch (e) {
    return defaultValue;
  }
};

// 保存数据到uni.setStorage
const saveToStorage = (key, data) => {
  try {
    uni.setStorageSync(key, JSON.stringify(data));
  } catch (e) {
    console.error('保存数据到storage失败:', e);
  }
};

// 初始化状态
const initState = () => {
  return {
    users: getStoredData('users', defaultUsers),
    colleges: getStoredData('colleges', defaultColleges),
    courses: getStoredData('courses', defaultCourses),
    evaluations: getStoredData('evaluations', defaultEvaluations),
    listenRecords: getStoredData('listenRecords', defaultListenRecords),
    config: getStoredData('config', {
      anonymousMode: 'global',
      globalAnonymous: true,
      allowSelfListen: true,
      auditLog: true
    }),
    currentUser: getStoredData('currentUser', null),
  };
};

// 简化版store
export const simpleStore = {
  state: initState(),
  
  // 保存所有数据到storage
  saveAllToStorage() {
    saveToStorage('users', this.state.users);
    saveToStorage('colleges', this.state.colleges);
    saveToStorage('courses', this.state.courses);
    saveToStorage('evaluations', this.state.evaluations);
    saveToStorage('listenRecords', this.state.listenRecords);
    saveToStorage('config', this.state.config);
    saveToStorage('currentUser', this.state.currentUser);
  },
  
  // 用户登录
  login(username, password) {
    const user = this.state.users.find(u => u.username === username && u.password === password);
    if (user) {
      // 清理密码信息
      const userWithoutPassword = { ...user };
      delete userWithoutPassword.password;
      
      this.state.currentUser = userWithoutPassword;
      saveToStorage('currentUser', userWithoutPassword);
      // 注意：微信小程序不支持btoa，所以这里我们简单保存用户信息
      saveToStorage('token', JSON.stringify({ userId: user.id, exp: Date.now() + 3600000 }));
      return true;
    }
    return false;
  },
  
  // 用户退出
  logout() {
    this.state.currentUser = null;
    uni.removeStorageSync('currentUser');
    uni.removeStorageSync('token');
    return true;
  },
  
  // 获取教师评价
  getTeacherEvaluations(teacherId) {
    return this.state.evaluations.filter(e => e.teacherId == teacherId);
  },
  
  // 获取学院评价
  getCollegeEvaluations(collegeName) {
    return this.state.evaluations.filter(e => {
      const course = this.state.courses.find(c => c.id == e.courseId);
      return course && course.college === collegeName;
    });
  },
  
  // 获取所有评价
  getAllEvaluations() {
    return [...this.state.evaluations];
  },
  
  // 获取教师听课记录
  getTeacherListenRecords(teacherId) {
    return this.state.listenRecords.filter(r => r.teacherId == teacherId);
  },
  
  // 获取学院听课记录
  getCollegeListenRecords(collegeName) {
    return this.state.listenRecords.filter(r => {
      const course = this.state.courses.find(c => c.id == r.courseId);
      return course && course.college === collegeName;
    });
  },
  
  // 获取学院用户
  getCollegeUsers(collegeName) {
    return this.state.users.filter(u => u.college === collegeName);
  },
  
  // 获取学院课程
  getCollegeCourses(collegeName) {
    return this.state.courses.filter(c => c.college === collegeName);
  },
  
  // 获取所有课程
  getCourses() {
    return [...this.state.courses];
  },
  
  // 获取所有学院
  getColleges() {
    return [...this.state.colleges];
  },
  
  // 获取所有用户
  getUsers() {
    return [...this.state.users];
  },
  
  // 获取配置
  getConfig() {
    return { ...this.state.config };
  }
};