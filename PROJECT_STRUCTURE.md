"""
校园信息泄露保护(DLP)系统 - 项目结构说明文档

项目整体架构：
================================================================================

campus-dlp-system/
│
├── requirements.txt                 # 项目依赖包列表
├── config.py                        # 系统配置文件
├── app.py                           # Flask应用主入口
│
├── modules/                         # 核心功能模块目录
│   ├── __init__.py
│   ├── content_identifier.py       # 步骤1: 内容识别模块
│   ├── intelligent_classifier.py   # 步骤2: 智能分类与发现
│   ├── channel_control.py          # 步骤3: 通道管控模块
│   ├── behavior_audit.py           # 步骤4: 行为审计模块
│   ├── static_protection.py        # 步骤5: 静态保护模块
│   ├── file_handler.py             # 文件处理模块
│   └── utils.py                    # 工具函数
│
├── models/                         # 数据库模型目录
│   ├── __init__.py
│   ├── user.py                     # 用户模型
│   ├── file.py                     # 文件模型
│   ├── audit_log.py                # 审计日志模型
│   └── scan_result.py              # 扫描结果模型
│
├── routes/                         # 路由处理目录
│   ├── __init__.py
│   ├── auth.py                     # 认证相关路由
│   ├── upload.py                   # 文件上传路由
│   ├── scan.py                     # 文件扫描路由
│   ├── dashboard.py                # 仪表板路由
│   └── admin.py                    # 管理员路由
│
├── templates/                      # HTML模板目录
│   ├── base.html
│   ├── login.html
│   ├── upload.html
│   ├── dashboard.html
│   ├── scan_result.html
│   └── admin.html
│
├── static/                         # 静态文件目录
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── uploads/                        # 用户上传文件目录
│
├── logs/                           # 日志文件目录
│   ├── dlp_system.log
│   └── dlp_audit.log
│
├── tests/                          # 测试文件目录
│   ├── __init__.py
│   ├── test_content_identifier.py
│   ├── test_classifier.py
│   └── test_protection.py
│
└── run.py                          # 项目运行入口


================================================================================
详细文件说明：
================================================================================

1. 根目录文件
───────────────────────────────────────────────────────────────────────────────

📄 requirements.txt
位置: 项目根目录
用途: 声明所有Python依赖包
内容: Flask、SQLAlchemy、easyocr、cryptography等所有库的版本号
运行: pip install -r requirements.txt

📄 config.py
位置: 项目根目录
用途: 全局配置文件，包含所有系统配置参数
内容:
  - 数据库连接字符串
  - Flask配置(SECRET_KEY, SESSION配置)
  - 文件上传限制
  - 敏感词库配置
  - OCR、加密参数配置
使用: from config import config

📄 app.py
位置: 项目根目录
用途: Flask应用初始化和配置
内容:
  - 创建Flask应用实例
  - 初始化数据库(SQLAlchemy)
  - 注册蓝图(路由)
  - 配置错误处理器
  - 配置日志系统

📄 run.py
位置: 项目根目录
用途: 项目启动入口
内容:
  from app import create_app
  if __name__ == '__main__':
      app = create_app()
      app.run(debug=True, host='0.0.0.0', port=5000)
运行: python run.py


================================================================================
2. modules/ 核心模块 (实现5个DLP功能模块)
───────────────────────────────────────────────────────────────────────────────

📄 modules/content_identifier.py
🎯 作用: 步骤1 - 内容识别模块
功能:
  ✓ 1.1 关键字检测 - keyword_detection()
      检测文本中是否包含敏感关键词(学号、身份证号等)
  ✓ 1.2 文档内容检查 - document_content_check()
      对上传的文档进行内容提取和敏感信息检查
  ✓ 1.3 文档指纹 - file_fingerprint()
      使用SimHash生成文件指纹，用于后续重复检测

代码示例:
    from modules.content_identifier import ContentIdentifier
    
    identifier = ContentIdentifier(sensitive_keywords=['学号', '身份证'])
    results = identifier.keyword_detection(text)  # 检测敏感词
    check = identifier.document_content_check(text)  # 检查文档
    fingerprint = identifier.file_fingerprint(text)  # 生成指纹


📄 modules/intelligent_classifier.py
🎯 作用: 步骤2 - 智能分类与发现模块
功能:
  ✓ 2.1 光学字符识别(OCR) - ocr_recognition()
      从图片、PDF、扫描件中提取文本(支持中英文)
  ✓ 2.2 命名实体识别(NER) - named_entity_recognition()
      识别人名、组织、地点、日期等敏感实体
  ✓ 实体分类 - entity_classification()
      综合分类和敏感性评估

使用工具:
  - easyocr: 光学字符识别
  - regex: 命名实体识别规则匹配

代码示例:
    from modules.intelligent_classifier import IntelligentClassifier
    
    classifier = IntelligentClassifier()
    ocr_result = classifier.ocr_recognition('image.png')  # OCR识别
    ner_result = classifier.named_entity_recognition(text)  # NER识别


📄 modules/channel_control.py
🎯 作用: 步骤3 - 通道管控模块(访问控制)
功能:
  ✓ 3.1 访问控制制 - 基于角色的权限限制
      定义admin/manager/user/guest等角色
      每个角色对应不同的权限

权限系统:
  - admin: 完全访问权限
  - manager: 管理权限(无删除权限)
  - user: 基础权限(只能上传自己的文件)
  - guest: 最小权限(只读)

装饰器:
  @require_login          # 要求登录
  @require_role('admin')  # 要求特定角色
  @require_permission('manage_users')  # 要求特定权限

代码示例:
    from modules.channel_control import ChannelControl
    
    channel = ChannelControl()
    
    @channel.require_permission('view_all_files')
    def view_all_files():
        return "显示所有文件"


📄 modules/behavior_audit.py
🎯 作用: 步骤4 - 行为审计模块
功能:
  ✓ 4.1 关键操作日志记录 - log_sensitive_operation()
      记录所有敏感操作:
      - 用户登录/登出
      - 访问敏感文件
      - 下载数据
      - 修改权限
      - 删除文件
  ✓ 4.2 日志查询与审计 - get_audit_logs() / search_logs()
      提供管理员查询日志功能
      生成审计报告(用户活动、文件访问、安全事件)

日志格式: JSON格式，包含时间戳、用户ID、操作类型、IP等

代码示例:
    from modules.behavior_audit import BehaviorAudit
    
    audit = BehaviorAudit()
    audit.log_sensitive_operation(
        user_id='user123',
        operation_type='access',
        resource='file.pdf'
    )
    logs = audit.get_audit_logs({'user_id': 'user123'})


📄 modules/static_protection.py
🎯 作用: 步骤5 - 静态保护模块(加密和脱敏)
功能:
  ✓ 5.1 敏感数据加密存储 - encrypt_sensitive_data()
      对API密钥、数据库密码等进行加密
      使用Fernet (AES-128加密)
  ✓ 5.2 用户密码加盐哈希 - hash_password()
      使用bcrypt进行密码哈希
      不可逆加密
  ✓ 5.3 数据脱敏/假数据 - mask_data() / generate_fake_data()
      对敏感字段进行部分遮蔽:
      - 学号: 202301***456
      - 身份证: 110101********1234
      - 手机: 138***1234
      - 邮箱: us***@gmail.com

代码示例:
    from modules.static_protection import StaticProtection
    
    protection = StaticProtection('master_password')
    
    # 加密
    encrypted = protection.encrypt_sensitive_data('api_key')
    
    # 密码哈希
    hashed_pwd = protection.hash_password('password123')
    
    # 数据脱敏
    masked = protection.mask_data('13800138000', 'phone')


📄 modules/file_handler.py (待创建)
🎯 作用: 文件处理模块
功能:
  - 处理文件上传(限制大小、扩展名)
  - 提取文件内容(PDF、DOCX、TXT)
  - 管理文件存储
  - 文件删除和清理


📄 modules/utils.py (待创建)
🎯 作用: 工具函数模块
功能:
  - 时间格式化
  - 字符串处理
  - 文件路径处理
  - 通用验证函数


================================================================================
3. models/ 数据库模型
───────────────────────────────────────────────────────────────────────────────

📄 models/user.py
用途: 用户数据模型
字段: id, username, email, password_hash, role, created_at

📄 models/file.py
用途: 上传文件数据模型
字段: id, filename, file_path, user_id, upload_time, risk_level

📄 models/audit_log.py
用途: 审计日志数据模型
字段: id, user_id, operation_type, resource, timestamp

📄 models/scan_result.py
用途: 扫描结果数据模型
字段: id, file_id, sensitive_found, pii_count, risk_level


================================================================================
4. routes/ 路由处理(Web页面和API)
───────────────────────────────────────────────────────────────────────────────

📄 routes/auth.py
路由:
  POST /login         - 用户登录
  POST /logout        - 用户登出
  POST /register      - 用户注册

📄 routes/upload.py
路由:
  POST /upload        - 上传文件
  GET /uploads        - 查看已上传文件列表

📄 routes/scan.py
路由:
  POST /scan          - 扫描文件(调用内容识别模块)
  GET /scan-result/:id - 查看扫描结果

📄 routes/dashboard.py
路由:
  GET /dashboard      - 显示仪表板
  GET /statistics     - 获取统计数据

📄 routes/admin.py
路由:
  GET /admin/users    - 用户管理
  GET /admin/logs     - 审计日志查询
  GET /admin/reports  - 生成报告


================================================================================
5. templates/ 前端HTML模板
───────────────────────────────────────────────────────────────────────────────

📄 templates/login.html
页面: 用户登录页面

📄 templates/upload.html
页面: 文件上传页面

📄 templates/scan_result.html
页面: 扫描结果显示页面

📄 templates/dashboard.html
页面: 用户仪表板

📄 templates/admin.html
页面: 管理员控制面板


================================================================================
6. static/ 静态资源
───────────────────────────────────────────────────────────────────────────────

📄 static/css/style.css
样式表

📄 static/js/script.js
前端JavaScript脚本


================================================================================
代码执行流程示例：
================================================================================

用户上传文件流程:
1. 用户访问 /upload 页面 (routes/upload.py)
2. 用户选择文件并提交
3. Flask处理POST请求 (routes/upload.py)
4. 文件保存到 uploads/ 目录 (modules/file_handler.py)
5. 调用内容识别模块扫描 (modules/content_identifier.py)
   - 检测敏感关键词
   - 生成文件指纹
6. 调用智能分类模块 (modules/intelligent_classifier.py)
   - 如果是图片，进行OCR识别
   - 进行NER命名实体识别
7. 记录审计日志 (modules/behavior_audit.py)
8. 如果发现敏感信息，进行脱敏处理 (modules/static_protection.py)
9. 保存扫描结果到数据库 (models/scan_result.py)
10. 返回扫描结果页面 (templates/scan_result.html)


================================================================================
"""
