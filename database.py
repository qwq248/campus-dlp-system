"""
数据库模型 - 校园DLP系统数据存储
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    department = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    upload_files = db.relationship('UploadedFile', backref='uploader', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """检查是否是管理员"""
        return self.role == 'admin'

class UploadedFile(db.Model):
    """上传文件模型"""
    __tablename__ = 'uploaded_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # DLP信息
    sensitivity_level = db.Column(db.String(20), default='public')
    contains_sensitive_data = db.Column(db.Boolean, default=False)
    detected_sensitive_info = db.Column(db.Text)  # JSON格式的检测结果
    simhash_value = db.Column(db.String(100))  # SimHash指纹
    
    # 文件识别结果
    identified_keywords = db.Column(db.Text)  # JSON格式
    ocr_text = db.Column(db.Text)  # OCR提取的文本
    
    # 访问控制
    access_level = db.Column(db.String(20), default='private')  # private, department, public
    allowed_users = db.Column(db.Text)  # JSON格式的允许用户列表
    
    # 元数据
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)
    download_count = db.Column(db.Integer, default=0)
    
    # 关系
    detection_results = db.relationship('SensitiveDataDetection', backref='file', lazy='dynamic', cascade='all, delete-orphan')
    access_logs = db.relationship('FileAccessLog', backref='file', lazy='dynamic', cascade='all, delete-orphan')

class SensitiveDataDetection(db.Model):
    """敏感数据检测结果"""
    __tablename__ = 'sensitive_data_detection'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id'), nullable=False)
    
    # 检测信息
    detection_type = db.Column(db.String(50))  # keyword, ocr, pattern
    detected_value = db.Column(db.Text)
    detection_confidence = db.Column(db.Float, default=1.0)
    location = db.Column(db.String(200))  # 检测位置
    
    # 分类信息
    classified_entity = db.Column(db.String(100))  # 实体类型: person_name, id_number, phone等
    classification_confidence = db.Column(db.Float, default=1.0)
    
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

class FileAccessLog(db.Model):
    """文件访问日志"""
    __tablename__ = 'file_access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_files.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 访问信息
    access_time = db.Column(db.DateTime, default=datetime.utcnow)
    access_type = db.Column(db.String(20))  # view, download, share
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(200))
    
    # 操作结果
    access_granted = db.Column(db.Boolean, default=True)
    denial_reason = db.Column(db.String(200))

class AuditLog(db.Model):
    """审计日志"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 操作信息
    operation_type = db.Column(db.String(50), nullable=False)  # upload, download, delete, modify, login
    operation_target = db.Column(db.String(255))  # 操作目标
    operation_details = db.Column(db.Text)  # 操作详情(JSON)
    
    # 日志信息
    operation_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20))  # success, failed
    
    # 风险评估
    risk_level = db.Column(db.String(20), default='low')  # low, medium, high, critical

class DataClassification(db.Model):
    """数据分类标签"""
    __tablename__ = 'data_classifications'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    sensitivity_level = db.Column(db.Integer, default=1)  # 1-4
    color_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SecurityPolicy(db.Model):
    """安全策略"""
    __tablename__ = 'security_policies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    policy_type = db.Column(db.String(50))  # access_control, encryption, watermark
    policy_content = db.Column(db.Text)  # 策略内容(JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
