"""
【模块1】内容识别 (Content Identification)
功能：检测文本中是否包含预定义的敏感词和特定模式
"""
import re
from typing import Dict, List, Tuple
import json
from simhash import SimHash

class ContentIdentification:
    """内容识别模块"""
    
    def __init__(self, sensitive_keywords: List[str]):
        self.sensitive_keywords = sensitive_keywords
        
        # 敏感信息的正则模式
        self.patterns = {
            'id_number': r'\d{6}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
            'phone_number': r'1[3-9]\d{9}|0\d{2,3}-?\d{7,8}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'bank_card': r'\d{16,19}',
            'passport': r'[A-Z]{1,2}\d{6,9}',
        }
    
    def detect_keywords(self, content: str) -> Dict:
        """
        检测关键字
        返回检测到的关键字及其位置信息
        """
        results = {
            'detected_keywords': [],
            'keyword_count': 0,
            'risk_level': 'low'
        }
        
        content_lower = content.lower()
        
        for keyword in self.sensitive_keywords:
            # 不区分大小写的匹配
            pattern = re.compile(keyword, re.IGNORECASE)
            matches = pattern.finditer(content)
            
            for match in matches:
                results['detected_keywords'].append({
                    'keyword': keyword,
                    'position': match.start(),
                    'context': content[max(0, match.start()-20):min(len(content), match.end()+20)]
                })
                results['keyword_count'] += 1
        
        # 评估风险级别
        if results['keyword_count'] >= 5:
            results['risk_level'] = 'high'
        elif results['keyword_count'] >= 3:
            results['risk_level'] = 'medium'
        
        return results
    
    def detect_patterns(self, content: str) -> Dict:
        """
        检测特定模式
        如身份证号、电话号码、邮箱等
        """
        results = {
            'detected_patterns': {},
            'sensitive_entities': []
        }
        
        for pattern_name, pattern in self.patterns.items():
            regex = re.compile(pattern)
            matches = regex.finditer(content)
            
            entity_list = []
            for match in matches:
                # 数据脱敏：只显示部分
                value = match.group()
                masked_value = self._mask_sensitive_value(value, pattern_name)
                
                entity_list.append({
                    'original_length': len(value),
                    'masked_value': masked_value,
                    'position': match.start(),
                    'type': pattern_name
                })
            
            if entity_list:
                results['detected_patterns'][pattern_name] = len(entity_list)
                results['sensitive_entities'].extend(entity_list)
        
        return results
    
    def _mask_sensitive_value(self, value: str, pattern_type: str) -> str:
        """敏感信息脱敏"""
        length = len(value)
        
        if pattern_type == 'id_number':
            return value[:6] + '**'*(length//2-3) + value[-4:]
        elif pattern_type == 'phone_number':
            return value[:3] + '****' + value[-4:]
        elif pattern_type == 'email':
            parts = value.split('@')
            return parts[0][:2] + '***@' + parts[1]
        elif pattern_type == 'bank_card':
            return value[:4] + '*'*(length-8) + value[-4:]
        else:
            return '*' * length
    
    def calculate_simhash(self, content: str) -> str:
        """
        计算文件的SimHash指纹
        用于检测重复或相似文件
        """
        # 去除标点和空白
        clean_content = re.sub(r'[^\w\s]', '', content)
        simhash = SimHash(clean_content)
        return str(simhash.value)
    
    def identify_content(self, content: str) -> Dict:
        """
        综合内容识别
        返回完整的识别结果
        """
        keyword_results = self.detect_keywords(content)
        pattern_results = self.detect_patterns(content)
        simhash = self.calculate_simhash(content)
        
        has_sensitive_data = (
            len(keyword_results['detected_keywords']) > 0 or 
            len(pattern_results['sensitive_entities']) > 0
        )
        
        return {
            'has_sensitive_data': has_sensitive_data,
            'keywords': keyword_results,
            'patterns': pattern_results,
            'simhash': simhash,
            'overall_risk': keyword_results['risk_level']
        }
