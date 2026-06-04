"""
【模块3】访问控制 (Access Control)
功能：实现基于角色的访问控制(RBAC)，管理用户权限
"""
from typing import Dict, List, Tuple
from datetime import datetime
import json

class AccessControl:
    """访问控制模块"""
    
    def __init__(self):
        # 角色权限映射
        self.role_permissions = {
            'admin': ['view', 'download', 'upload', 'delete', 'share', 'manage_users', 'view_audit'],
            'manager': ['view', 'download', 'upload', 'share', 'view_audit'],
            'user': ['view', 'download', 'upload', 'share']
        }
        
        # 敏感等级与访问权限的映射
        self.sensitivity_access_level = {
            'public': ['admin', 'manager', 'user'],
            'internal': ['admin', 'manager'],
            'confidential': ['admin'],
            'restricted': ['admin']
        }
    
    def check_access_permission(self, user_role: str, file_sensitivity: str, 
                               access_type: str) -> Tuple[bool, str]:
        """
        检查用户是否有权访问文件
        返回：(是否允许, 拒绝原因)
        """
        # 检查用户角色是否有该访问类型的权限
        if access_type not in self.role_permissions.get(user_role, []):
            return False, f'用户角色 {user_role} 没有 {access_type} 权限'
        
        # 检查敏感等级限制
        if user_role not in self.sensitivity_access_level.get(file_sensitivity, []):
            return False, f'用户角色 {user_role} 无法访问敏感等级为 {file_sensitivity} 的文件'
        
        return True, ''
    
    def check_fine_grained_access(self, user_id: int, file_id: int, 
                                 allowed_users: List[int]) -> Tuple[bool, str]:
        """
        细粒度访问控制：检查用户是否在允许列表中
        """
        if allowed_users and user_id not in allowed_users:
            return False, '用户不在文件的访问白名单中'
        
        return True, ''
    
    def check_time_based_access(self, current_time: datetime, 
                               access_start: datetime, access_end: datetime) -> Tuple[bool, str]:
        """
        基于时间的访问控制：检查当前时间是否在允许范围内
        """
        if current_time < access_start or current_time > access_end:
            return False, f'访问时间限制: {access_start} 至 {access_end}'
        
        return True, ''
    
    def enforce_access_control(self, user_info: Dict, file_info: Dict) -> Dict:
        """
        综合访问控制检查
        返回访问决策和原因
        """
        results = {
            'access_granted': False,
            'access_reasons': [],
            'denial_reasons': [],
            'access_type': file_info.get('access_level', 'private')
        }
        
        # 检查1：角色权限
        can_access, reason = self.check_access_permission(
            user_info['role'], 
            file_info['sensitivity_level'],
            'download'
        )
        
        if not can_access:
            results['denial_reasons'].append(reason)
        else:
            results['access_reasons'].append('角色权限检查通过')
        
        # 检查2：细粒度访问控制
        if file_info.get('access_level') == 'private':
            allowed_users = file_info.get('allowed_users', [])
            if isinstance(allowed_users, str):
                try:
                    allowed_users = json.loads(allowed_users)
                except:
                    allowed_users = []
            
            can_access, reason = self.check_fine_grained_access(
                user_info['id'],
                file_info['id'],
                allowed_users
            )
            
            if not can_access:
                results['denial_reasons'].append(reason)
            else:
                results['access_reasons'].append('细粒度访问检查通过')
        
        # 最终决策
        results['access_granted'] = len(results['denial_reasons']) == 0
        
        return results
    
    def get_user_permissions(self, user_role: str) -> List[str]:
        """获取用户的所有权限"""
        return self.role_permissions.get(user_role, [])
    
    def grant_temporary_access(self, user_id: int, file_id: int, 
                              duration_hours: int) -> Dict:
        """
        授予临时访问权限
        """
        return {
            'user_id': user_id,
            'file_id': file_id,
            'grant_time': datetime.utcnow().isoformat(),
            'expiry_time': (datetime.utcnow().timestamp() + duration_hours * 3600),
            'status': 'active'
        }
