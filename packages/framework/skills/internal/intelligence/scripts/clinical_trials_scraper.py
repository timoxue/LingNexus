"""
ClinicalTrials.gov 爬虫

使用公开API采集国际临床试验数据
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime


class ClinicalTrialsGovScraper:
    """ClinicalTrials.gov API爬虫"""

    # 使用API v2
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def __init__(self, timeout: int = 30):
        """
        初始化爬虫

        Args:
            timeout: 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        # 设置User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_trials(
        self,
        keyword: str,
        max_results: int = 10,
        expression: Optional[str] = None
    ) -> List[Dict]:
        """
        搜索临床试验

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数
            expression: 高级搜索表达式（可选）

        Returns:
            试验列表
        """
        print(f"[ClinicalTrials.gov] 正在搜索: {keyword}")

        try:
            # 构建查询参数 (API v2格式)
            if expression:
                query_term = expression
            else:
                query_term = keyword

            params = {
                'query.term': query_term,
                'pageSize': max_results
            }

            # 发送请求
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()

            # 解析JSON
            data = response.json()

            # 提取试验数据
            trials = self._parse_response_v2(data)

            print(f"[ClinicalTrials.gov] 找到 {len(trials)} 条结果")

            return trials

        except requests.exceptions.RequestException as e:
            print(f"[ClinicalTrials.gov] 请求失败: {e}")
            return []
        except Exception as e:
            print(f"[ClinicalTrials.gov] 解析失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_response_v2(self, data: Dict) -> List[Dict]:
        """
        解析API v2响应

        Args:
            data: API返回的JSON数据

        Returns:
            试验列表
        """
        trials = []

        try:
            # API v2 格式: { "studies": [ ... ] }
            studies = data.get('studies', [])

            for study in studies:
                try:
                    trial = self._parse_study_v2(study)
                    if trial:
                        trials.append(trial)
                except Exception as e:
                    print(f"[ClinicalTrials.gov] 解析单条研究失败: {e}")
                    continue

        except Exception as e:
            print(f"[ClinicalTrials.gov] 解析响应失败: {e}")

        return trials

    def _parse_response(self, data: Dict) -> List[Dict]:
        """
        解析API响应（旧版本，保留兼容）
        """
        return self._parse_response_v2(data)

    def _parse_study_v2(self, study: Dict) -> Optional[Dict]:
        """
        解析单个研究 (API v2格式)

        Args:
            study: 研究数据字典

        Returns:
            试验字典
        """
        try:
            # API v2 格式
            protocol = study.get('protocolSection', {})

            # 基本信息
            identification = protocol.get('identificationModule', {})
            nct_id = identification.get('nctId', '')
            title = identification.get('briefTitle', '')

            # 状态信息
            status = protocol.get('statusModule', {})
            overall_status = status.get('overallStatus', '')

            # 日期
            start_date_struct = status.get('startDateStruct', {})
            completion_date_struct = status.get('primaryCompletionDateStruct', {})

            # 设计信息
            design = protocol.get('designModule', {})
            phases = design.get('phases', [])

            if isinstance(phases, list):
                phase = ', '.join(phases)
            else:
                phase = phases

            # 人员和机构
            sponsors = protocol.get('sponsorsCollaboratorsModule', {})
            lead_sponsor = sponsors.get('leadSponsor', {}).get('name', '')
            collaborators = sponsors.get('collaborators', [])

            if isinstance(collaborators, list):
                collab_names = [c.get('name', '') for c in collaborators]
                collaborators_str = ', '.join(collab_names)
            else:
                collaborators_str = collaborators

            # 适应症
            conditions = protocol.get('conditionsModule', {}).get('conditions', [])

            if isinstance(conditions, list):
                conditions_list = conditions
                indication = ', '.join(conditions_list)
            else:
                indication = conditions

            # 简化的干预信息
            arms_interventions = protocol.get('armsInterventionsModule', {})
            interventions_list = arms_interventions.get('interventions', [])

            if isinstance(interventions_list, list):
                interventions_str = ', '.join([
                    i.get('name', '') if isinstance(i, dict) else str(i)
                    for i in interventions_list[:5]  # 只取前5个
                ])
            else:
                interventions_str = ''

            # 构建试验对象
            trial = {
                'nct_id': nct_id,
                'title': title,
                'company': lead_sponsor or '',
                'phase': phase,
                'status': overall_status,
                'indication': indication,
                'interventions': interventions_str,
                'collaborators': collaborators_str,

                # 日期
                'start_date': self._parse_date_v2(start_date_struct),
                'completion_date': self._parse_date_v2(completion_date_struct),

                # 元数据
                'source': 'ClinicalTrials.gov',
                'url': f"https://clinicaltrials.gov/ct2/show/{nct_id}",
                'collected_at': datetime.now().isoformat()
            }

            return trial

        except Exception as e:
            print(f"[ClinicalTrials.gov] 解析研究失败: {e}")
            return None

    def _parse_study(self, study: Dict) -> Optional[Dict]:
        """
        解析单个研究

        Args:
            study: 研究数据字典

        Returns:
            试验字典
        """
        try:
            # 获取协议部分
            protocol = study.get('Study', {}).get('ProtocolSection', {})

            # 基本信息
            identification = protocol.get('IdentificationModule', {})
            nct_id = identification.get('NCTId', '')
            title = identification.get('BriefTitle', '')

            # 状态信息
            status = protocol.get('StatusModule', {})
            overall_status = status.get('OverallStatus', '')
            start_date = status.get('StartDateStruct', {})
            completion_date = status.get('PrimaryCompletionDateStruct', {})

            # 设计信息
            design = protocol.get('DesignModule', {})
            phases = design.get('PhaseList', {}).get('Phase', [])

            if isinstance(phases, list):
                phase = ', '.join(phases)
            else:
                phase = phases

            # 人员和机构
            sponsors = protocol.get('SponsorsCollaboratorsModule', {})
            lead_sponsor = sponsors.get('LeadSponsor', {}).get('Organization', '')
            collaborators = sponsors.get('CollaboratorList', {}).get('Collaborator', [])

            if isinstance(collaborators, list):
                collab_names = [c.get('Organization', '') for c in collaborators]
                collaborators_str = ', '.join(collab_names)
            else:
                collaborators_str = collaborators

            # 适应症
            conditions = protocol.get('ConditionsModule', {}).get('ConditionList', {}).get('Condition', [])

            if isinstance(conditions, list):
                conditions_list = [c if isinstance(c, str) else c.get('ConditionOrDisease', '')
                                 for c in conditions]
                indication = ', '.join(conditions_list)
            else:
                indication = conditions

            # 简化的干预信息
            interventions = protocol.get('ArmsInterventionsModule', {})
            intervention_list = interventions.get('InterventionList', {}).get('Intervention', [])

            if isinstance(intervention_list, list):
                interventions_str = ', '.join([
                    i.get('InterventionName', '') if isinstance(i, dict) else str(i)
                    for i in intervention_list[:5]  # 只取前5个
                ])
            else:
                interventions_str = ''

            # 构建试验对象
            trial = {
                'nct_id': nct_id,
                'title': title,
                'company': lead_sponsor or '',
                'phase': phase,
                'status': overall_status,
                'indication': indication,
                'interventions': interventions_str,
                'collaborators': collaborators_str,

                # 日期
                'start_date': self._parse_date(start_date),
                'completion_date': self._parse_date(completion_date),

                # 元数据
                'source': 'ClinicalTrials.gov',
                'url': f"https://clinicaltrials.gov/ct2/show/{nct_id}",
                'collected_at': datetime.now().isoformat()
            }

            return trial

        except Exception as e:
            print(f"[ClinicalTrials.gov] 解析研究失败: {e}")
            return None

    def _parse_date(self, date_struct: Dict) -> Optional[str]:
        """
        解析日期结构

        Args:
            date_struct: 日期字典

        Returns:
            日期字符串 (YYYY-MM-DD) 或 None
        """
        if not date_struct:
            return None

        try:
            year = date_struct.get('Year')
            month = date_struct.get('Month')
            day = date_struct.get('Day')

            if year:
                if month:
                    if day:
                        return f"{year}-{month:02d}-{day:02d}"
                    else:
                        return f"{year}-{month:02d}"
                else:
                    return str(year)

            return None

        except Exception:
            return None

    def _parse_date_v2(self, date_struct: Dict) -> Optional[str]:
        """
        解析日期结构 (API v2格式)

        Args:
            date_struct: 日期字典

        Returns:
            日期字符串 (YYYY-MM-DD) 或 None
        """
        if not date_struct:
            return None

        try:
            date_str = date_struct.get('date')
            if date_str:
                return date_str

            # 如果没有date字段，尝试从其他字段构建
            year = date_struct.get('Year')
            month = date_struct.get('Month')
            day = date_struct.get('Day')

            if year:
                if month:
                    if day:
                        return f"{year}-{month:02d}-{day:02d}"
                    else:
                        return f"{year}-{month:02d}"
                else:
                    return str(year)

            return None

        except Exception:
            return None

    def _parse_date(self, date_struct: Dict) -> Optional[str]:
        """兼容旧版本"""
        return self._parse_date_v2(date_struct)

    def get_study_details(self, nct_id: str) -> Optional[Dict]:
        """
        获取研究详情

        Args:
            nct_id: NCT编号（如 NCT05823451）

        Returns:
            详细信息字典
        """
        print(f"[ClinicalTrials.gov] 获取详情: {nct_id}")

        try:
            # 使用NCT ID直接查询
            params = {
                'query.term': nct_id,
                'pageSize': 1
            }

            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            # 提取研究
            studies = data.get('studies', [])

            if studies:
                return self._parse_study_v2(studies[0])

            return None

        except Exception as e:
            print(f"[ClinicalTrials.gov] 获取详情失败: {e}")
            return None

    def scrape(self, keywords: List[str], max_results: int = 10) -> Dict[str, List[Dict]]:
        """
        爬取多个关键词的试验数据

        Args:
            keywords: 关键词列表
            max_results: 每个关键词的最大结果数

        Returns:
            {keyword: [trials]}
        """
        results = {}

        for keyword in keywords:
            print(f"\n{'='*60}")
            print(f"[ClinicalTrials.gov] 搜索关键词: {keyword}")
            print(f"{'='*60}")

            trials = self.search_trials(keyword, max_results)
            results[keyword] = trials

        return results


# 使用示例
if __name__ == "__main__":
    scraper = ClinicalTrialsGovScraper()

    # 搜索司美格鲁肽相关试验
    results = scraper.scrape(["semaglutide", "Ozempic"], max_results=5)

    for keyword, trials in results.items():
        print(f"\n{'='*60}")
        print(f"关键词: {keyword}")
        print(f"{'='*60}")
        print(f"找到 {len(trials)} 条结果\n")

        for i, trial in enumerate(trials, 1):
            print(f"{i}. {trial.get('nct_id', 'N/A')}")
            print(f"   标题: {trial.get('title', 'N/A')}")
            print(f"   公司: {trial.get('company', 'N/A')}")
            print(f"   阶段: {trial.get('phase', 'N/A')}")
            print(f"   状态: {trial.get('status', 'N/A')}")
            print(f"   适应症: {trial.get('indication', 'N/A')}")
            print(f"   开始日期: {trial.get('start_date', 'N/A')}")
            print(f"   完成日期: {trial.get('completion_date', 'N/A')}")
            print(f"   URL: {trial.get('url', 'N/A')}")
            print()
