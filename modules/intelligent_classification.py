"""
【模块2】智能分类与发现 (Intelligent Classification & Discovery)
功能：使用OCR和NLP进行智能分析，识别实体信息
"""
import easyocr
import json
import re
from typing import Dict, List
from datetime import datetime

class IntelligentClassification:
    """智能分类模块"""
    
    def __init__(self):
        try:
            # 初始化OCR识别器（支持中文）
            self.ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
        except:
            self.ocr_reader = None
            print("警告：OCR初始化失败，某些功能不可用")
        
        # 实体分类规则
        self.entity_classifiers = {
            'person_name': self._classify_person_name,
            'organization': self._classify_organization,
            'location': self._classify_location,
            'date': self._classify_date,
            'contact': self._classify_contact
        }
    
    def ocr_recognition(self, image_path: str) -> Dict:
        """
        OCR识别：从图片、PDF等文件中提取文本
        应用场景：处理扫描文档、PDF文件
        """
        results = {
            'extracted_text': '',
            'confidence_scores': [],
            'detected_text_regions': [],
            'contains_sensitive': False
        }
        
        if not self.ocr_reader:
            results['error'] = 'OCR引擎未初始化'
            return results
        
        try:
            # 进行OCR识别
            ocr_results = self.ocr_reader.readtext(image_path)
            
            extracted_texts = []
            for (bbox, text, confidence) in ocr_results:
                extracted_texts.append(text)
                results['confidence_scores'].append({
                    'text': text,
                    'confidence': float(confidence),
                    'bbox': str(bbox)
                })
            
            results['extracted_text'] = ''.join(extracted_texts)
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def entity_recognition(self, text: str) -> Dict:
        """
        实体识别：识别文本中的人名、组织、地点等
        应用场景：自动识别并分类提取的文本中的重要信息
        """
        results = {
            'identified_entities': [],
            'entity_types': {},
            'classification_confidence': {}
        }
        
        # 识别人名
        person_names = self._classify_person_name(text)
        if person_names:
            results['identified_entities'].extend(person_names)
            results['entity_types']['person_name'] = len(person_names)
            results['classification_confidence']['person_name'] = 0.85
        
        # 识别组织机构
        organizations = self._classify_organization(text)
        if organizations:
            results['identified_entities'].extend(organizations)
            results['entity_types']['organization'] = len(organizations)
            results['classification_confidence']['organization'] = 0.78
        
        # 识别地点
        locations = self._classify_location(text)
        if locations:
            results['identified_entities'].extend(locations)
            results['entity_types']['location'] = len(locations)
            results['classification_confidence']['location'] = 0.80
        
        # 识别日期
        dates = self._classify_date(text)
        if dates:
            results['identified_entities'].extend(dates)
            results['entity_types']['date'] = len(dates)
            results['classification_confidence']['date'] = 0.92
        
        # 识别联系方式
        contacts = self._classify_contact(text)
        if contacts:
            results['identified_entities'].extend(contacts)
            results['entity_types']['contact'] = len(contacts)
            results['classification_confidence']['contact'] = 0.88
        
        return results
    
    def _classify_person_name(self, text: str) -> List[Dict]:
        """分类：人名识别"""
        # 常见中文姓氏
        surnames = ['王', '李', '张', '刘', '陈', '杨', '黄', '赵', '周', '徐', 
                   '孙', '马', '朱', '林', '郭', '何', '高', '罗', '郑', '谢']
        
        names = []
        for surname in surnames:
            # 姓+名(1-3字)
            pattern = f'{surname}[\\u4e00-\\u9fff]{{1,3}}'
            matches = re.finditer(pattern, text)
            for match in matches:
                names.append({
                    'entity_type': 'person_name',
                    'value': match.group(),
                    'position': match.start(),
                    'confidence': 0.85
                })
        
        return names
    
    def _classify_organization(self, text: str) -> List[Dict]:
        """分类：组织机构识别"""
        orgs = []
        keywords = ['大学', '公司', '部门', '学院', '中心', '研究院', '集团', '协会', '学校']
        
        for keyword in keywords:
            pattern = f'[\\u4e00-\\u9fff]*{keyword}'
            matches = re.finditer(pattern, text)
            for match in matches:
                orgs.append({
                    'entity_type': 'organization',
                    'value': match.group(),
                    'position': match.start(),
                    'confidence': 0.78
                })
        
        return orgs
    
    def _classify_location(self, text: str) -> List[Dict]:
        """分类：地点识别"""
        locations = []
        provinces = ['北京', '上海', '广东', '浙江', '江苏', '四川', '山东', 
                    '湖北', '湖南', '福建', '安徽', '江西', '河南', '河北',
                    '宿舍', '教室', '实验室']
        
        for province in provinces:
            pattern = f'{province}[\\u4e00-\\u9fff]*'
            matches = re.finditer(pattern, text)
            for match in matches:
                locations.append({
                    'entity_type': 'location',
                    'value': match.group(),
                    'position': match.start(),
                    'confidence': 0.80
                })
        
        return locations
    
    def _classify_date(self, text: str) -> List[Dict]:
        """分类：日期识别"""
        dates = []
        
        # 匹配日期格式: 2024年1月1日、2024-01-01等
        date_patterns = [
            r'\d{4}年\d{1,2}月\d{1,2}日',
            r'\d{4}-\d{1,2}-\d{1,2}',
            r'\d{1,2}/\d{1,2}/\d{4}'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                dates.append({
                    'entity_type': 'date',
                    'value': match.group(),
                    'position': match.start(),
                    'confidence': 0.92
                })
        
        return dates
    
    def _classify_contact(self, text: str) -> List[Dict]:
        """分类：联系方式识别"""
        contacts = []
        
        # 电话号码
        phone_pattern = r'1[3-9]\d{9}|0\d{2,3}-?\d{7,8}'
        phone_matches = re.finditer(phone_pattern, text)
        for match in phone_matches:
            contacts.append({
                'entity_type': 'phone',
                'value': match.group(),
                'position': match.start(),
                'confidence': 0.88
            })
        
        # 邮箱
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_matches = re.finditer(email_pattern, text)
        for match in email_matches:
            contacts.append({
                'entity_type': 'email',
                'value': match.group(),
                'position': match.start(),
                'confidence': 0.90
            })
        
        return contacts
    
    def classify_sensitivity_level(self, content: str, detected_entities: Dict) -> str:
        """
        根据检测到的敏感信息，自动分类文件的敏感等级
        """
        entity_count = len(detected_entities.get('identified_entities', []))
        
        if entity_count >= 10:
            return 'restricted'
        elif entity_count >= 5:
            return 'confidential'
        elif entity_count >= 2:
            return 'internal'
        else:
            return 'public'
