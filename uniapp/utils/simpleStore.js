// 初始化默认数据
const defaultUsers = [
  { id: 1, username: 'teacher1', password: '123456', name: '张老师', role: 'teacher', college: '信息工程学院', courses: ['Vue.js开发', '前端框架'] },
  { id: 2, username: 'teacher2', password: '123456', name: '李老师', role: 'teacher', college: '信息工程学院', courses: ['Java程序设计', '数据结构'] },
  { id: 3, username: 'college1', password: '123456', name: '王主任', role: 'college_admin', college: '信息工程学院' },
  { id: 4, username: 'school1', password: '123456', name: '系统管理员', role: 'school_admin', college: '' },
  // 督导老师：负责学院/教研组的教学质量督导
  { id: 5, username: 'supervisor1', password: '123456', name: '赵督导', role: 'supervisor', college: '信息工程学院', responsibleColleges: ['信息工程学院'], responsibleTeachers: [1, 2] },
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

// 示例评价数据（只保留督导老师和教师评教记录，移除学生评教记录）
// 注意：只有督导老师才能进行评教，学生不能评教
const defaultEvaluations = [
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
  // 督导老师评教记录示例
  {
    id: 1007,
    courseId: 1,
    courseName: 'Vue.js开发',
    teacherId: 1,
    teacherName: '张老师',
    evaluatorId: 5,
    evaluatorName: '赵督导',
    evaluatorRole: 'supervisor',
    anonymous: false,
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
    suggestion: '教学效果良好，课堂组织有序，建议可以增加一些互动环节。',
    createdAt: new Date('2025-03-21T10:00:00').toISOString()
  },
  {
    id: 1008,
    courseId: 2,
    courseName: 'Java程序设计',
    teacherId: 2,
    teacherName: '李老师',
    evaluatorId: 5,
    evaluatorName: '赵督导',
    evaluatorRole: 'supervisor',
    anonymous: false,
    scores: {
      teachingAttitude: 19,
      content: 46,
      method: 14,
      effect: 15,
      detail: {
        teachingAttitude: { punctuality: 5, management: 5, appearance: 9 },
        content: { objectives: 9, familiarity: 10, innovation: 9, ideology: 9, practice: 9 },
        method: { materials: 5, interaction: 9 },
        effect: { atmosphere: 10, inspiration: 5 }
      }
    },
    totalScore: 94,
    level: '优秀',
    suggestion: '课程内容充实，讲解详细，建议可以增加一些实际案例的分析。',
    createdAt: new Date('2025-03-22T14:00:00').toISOString()
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
  // 获取存储的评价数据，并过滤掉学生评教记录（只保留督导老师和教师评教记录）
  const storedEvaluations = getStoredData('evaluations', defaultEvaluations);
  const filteredEvaluations = storedEvaluations.filter(e => e.evaluatorRole !== 'student');
  
  // 如果过滤后的数据与原始数据不同，说明有学生评教记录，需要更新存储
  if (filteredEvaluations.length !== storedEvaluations.length) {
    saveToStorage('evaluations', filteredEvaluations);
  }
  
  return {
    users: getStoredData('users', defaultUsers),
    colleges: getStoredData('colleges', defaultColleges),
    courses: getStoredData('courses', defaultCourses),
    evaluations: filteredEvaluations, // 使用过滤后的评价数据
    listenRecords: getStoredData('listenRecords', defaultListenRecords),
    config: getStoredData('config', {
      anonymousMode: 'global',
      globalAnonymous: true,
      allowSelfListen: true,
      auditLog: true
    }),
    currentUser: getStoredData('currentUser', null),
    notices: getStoredData('notices', [
      {
        id: 1,
        title: '关于开展2025年春季学期评教工作的通知',
        content: '各学院、各位老师：根据学校教学工作安排，现启动2025年春季学期评教工作。请各学院认真组织，确保评教工作顺利进行。',
        sender: '教务处',
        targetCollege: 'all',
        createdAt: new Date('2025-03-01').toISOString(),
        isRead: false
      }
    ]),
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
    saveToStorage('notices', this.state.notices);
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
  
  // 获取教师评价（过滤掉学生评教记录，只保留督导老师和教师评教记录）
  getTeacherEvaluations(teacherId) {
    if (!teacherId) return [];
    if (!this.state.evaluations || !Array.isArray(this.state.evaluations)) return [];
    return this.state.evaluations.filter(e => 
      e && (e.teacherId == teacherId || e._teacherId == teacherId) && e.evaluatorRole !== 'student'
    );
  },
  
  // 获取学院评价（过滤掉学生评教记录）
  getCollegeEvaluations(collegeName) {
    if (!collegeName) return [];
    if (!this.state.evaluations || !Array.isArray(this.state.evaluations)) return [];
    if (!this.state.courses || !Array.isArray(this.state.courses)) return [];
    
    return this.state.evaluations.filter(e => {
      if (!e) return false;
      // 过滤掉学生评教记录
      if (e.evaluatorRole === 'student') return false;
      const course = this.state.courses.find(c => c && (c.id == e.courseId || c._id == e.courseId));
      return course && course.college === collegeName;
    });
  },
  
  // 获取所有评价（过滤掉学生评教记录）
  getAllEvaluations() {
    // 只返回督导老师和教师的评教记录，不包含学生评教记录
    if (!this.state.evaluations || !Array.isArray(this.state.evaluations)) return [];
    return this.state.evaluations.filter(e => e && e.evaluatorRole !== 'student');
  },
  
  // 获取教师听课记录
  getTeacherListenRecords(teacherId) {
    if (!teacherId) return [];
    if (!this.state.listenRecords || !Array.isArray(this.state.listenRecords)) return [];
    return this.state.listenRecords.filter(r => r && (r.teacherId == teacherId || r._teacherId == teacherId));
  },
  
  // 获取学院听课记录
  getCollegeListenRecords(collegeName) {
    if (!collegeName) return [];
    if (!this.state.listenRecords || !Array.isArray(this.state.listenRecords)) return [];
    if (!this.state.courses || !Array.isArray(this.state.courses)) return [];
    
    return this.state.listenRecords.filter(r => {
      if (!r) return false;
      const course = this.state.courses.find(c => c && (c.id == r.courseId || c._id == r.courseId));
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
  },

  // ========== 督导老师相关方法 ==========
  // 获取督导老师负责范围内的教师列表
  // TODO: 后端接口 - GET /api/supervisor/teachers?supervisorId={id}
  getSupervisorTeachers(supervisorId) {
    const supervisor = this.state.users.find(u => (u.id || u._id) == supervisorId && u.role === 'supervisor');
    if (!supervisor) return [];
    
    const responsibleTeachers = supervisor.responsibleTeachers || [];
    const responsibleColleges = supervisor.responsibleColleges || [];
    
    // 优先使用指定的负责老师列表
    if (responsibleTeachers && responsibleTeachers.length > 0) {
      return this.state.users.filter(u => {
        if (u.role !== 'teacher') return false;
        return responsibleTeachers.includes(u.id || u._id);
      });
    }
    
    // 如果没有指定负责老师，则根据负责的学院筛选教师（向后兼容）
    if (responsibleColleges && responsibleColleges.length > 0) {
      return this.state.users.filter(u => {
        if (u.role !== 'teacher') return false;
        return responsibleColleges.includes(u.college);
      });
    }
    
    return [];
  },

  // 获取督导老师负责范围内的课程列表
  // TODO: 后端接口 - GET /api/supervisor/courses?supervisorId={id}
  getSupervisorCourses(supervisorId) {
    const supervisor = this.state.users.find(u => (u.id || u._id) == supervisorId && u.role === 'supervisor');
    if (!supervisor) return [];
    
    const responsibleColleges = supervisor.responsibleColleges || [];
    const teachers = this.getSupervisorTeachers(supervisorId);
    const teacherIds = teachers.map(t => t.id || t._id);
    
    return this.state.courses.filter(c => {
      if (responsibleColleges.length > 0 && !responsibleColleges.includes(c.college)) return false;
      if (teacherIds.length > 0 && !teacherIds.includes(c.teacherId)) return false;
      return true;
    });
  },

  // 获取督导老师负责范围内教师的评教汇总数据
  // TODO: 后端接口 - GET /api/supervisor/evaluations/summary?supervisorId={id}
  getSupervisorEvaluationsSummary(supervisorId) {
    const teachers = this.getSupervisorTeachers(supervisorId);
    const teacherIds = teachers.map(t => t.id || t._id).filter(id => id);
    
    if (teacherIds.length === 0) {
      return [];
    }
    
    // 统一获取所有评教记录（evaluations和listenRecords合并处理）
    const evaluations = this.state.evaluations.filter(e => 
      e && teacherIds.includes(e.teacherId) && e.evaluatorRole !== 'student'
    );
    
    // 也包含listenRecords中的评教记录（统一处理）
    const listenRecords = (this.state.listenRecords || []).filter(e => 
      e && teacherIds.includes(e.teacherId) && e.evaluatorRole !== 'student'
    );
    
    // 合并所有评教记录
    const allEvaluations = [...evaluations, ...listenRecords];
    
    // 按教师汇总
    const summary = {};
    teacherIds.forEach(teacherId => {
      const teacher = teachers.find(t => (t.id || t._id) == teacherId);
      const teacherEvals = allEvaluations.filter(e => e && e.teacherId == teacherId);
      
      if (teacherEvals.length > 0) {
        const validScores = teacherEvals.filter(e => e.totalScore && typeof e.totalScore === 'number');
        if (validScores.length > 0) {
          const totalScore = validScores.reduce((sum, e) => sum + e.totalScore, 0);
          const avgScore = totalScore / validScores.length;
          
          summary[teacherId] = {
            teacherId: teacherId,
            teacherName: teacher ? teacher.name : '未知',
            totalEvaluations: validScores.length,
            totalScore: totalScore,
            averageScore: avgScore,
            evaluations: teacherEvals
          };
        }
      }
    });
    
    // 计算排名
    const sorted = Object.values(summary)
      .filter(item => item && typeof item.averageScore === 'number')
      .sort((a, b) => b.averageScore - a.averageScore);
    sorted.forEach((item, index) => {
      item.rank = index + 1;
    });
    
    return sorted;
  },

  // 获取督导老师负责范围内的听课记录
  // TODO: 后端接口 - GET /api/supervisor/listen-records?supervisorId={id}
  getSupervisorListenRecords(supervisorId) {
    const courses = this.getSupervisorCourses(supervisorId);
    const courseIds = courses.map(c => c.id || c._id);
    
    return this.state.listenRecords.filter(r => 
      courseIds.includes(r.courseId)
    );
  },

  // 检查用户是否有评教权限（普通老师和督导老师都可以评教）
  // TODO: 后端接口 - GET /api/permissions/can-evaluate?userId={id}
  canEvaluate(userId) {
    const user = this.state.users.find(u => (u.id || u._id) == userId);
    if (!user) return false;
    // 普通老师和督导老师都可以进行评教和听课评价
    return user.role === 'teacher' || user.role === 'supervisor';
  }
};