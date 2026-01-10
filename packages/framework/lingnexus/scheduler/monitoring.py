"""
每日监控任务

负责定时爬取数据、存储、检测变化和告警
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from lingnexus.storage.raw import RawStorage
from lingnexus.storage.structured import StructuredDB

# VectorDB是可选的
try:
    from lingnexus.storage.vector import VectorDB
    _vector_available = True
except ImportError:
    VectorDB = None
    _vector_available = False


class DailyMonitoringTask:
    """每日监控任务"""

    def __init__(self, config_path: str = None):
        """
        初始化监控任务

        Args:
            config_path: 配置文件路径
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "projects_monitoring.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()

        # 初始化存储
        self.raw_storage = RawStorage()
        self.structured_db = StructuredDB()

        # VectorDB是可选的
        if _vector_available and VectorDB:
            self.vector_db = VectorDB()
        else:
            self.vector_db = None
            print("[WARN] ChromaDB未安装，向量搜索功能将不可用")

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if not self.config_path.exists():
            print(f"Warning: Config file not found: {self.config_path}")
            return {"monitored_projects": []}

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def run(self, project_names: List[str] = None) -> Dict:
        """
        执行监控任务

        Args:
            project_names: 要监控的项目列表（None表示监控所有项目）

        Returns:
            监控结果字典
        """
        print(f"\n{'='*60}")
        print(f"开始执行监控任务: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        results = {}

        # 获取要监控的项目
        all_projects = self.config.get('monitored_projects', [])

        if project_names:
            # 过滤指定项目
            projects = [p for p in all_projects if p['name'] in project_names]
        else:
            projects = all_projects

        print(f"共监控 {len(projects)} 个项目\n")

        # 遍历每个项目
        for project in projects:
            project_name = project['name']
            print(f"\n{'─'*60}")
            print(f"项目: {project_name}")
            print(f"{'─'*60}")

            try:
                # 采集数据
                project_results = self._monitor_project(project)
                results[project_name] = project_results

                # 显示统计
                total_collected = sum(len(r.get('items', [])) for r in project_results.values())
                print(f"\n✅ {project_name}: 采集到 {total_collected} 条数据")

            except Exception as e:
                print(f"\n❌ {project_name}: 监控失败 - {e}")
                results[project_name] = {"error": str(e)}

        # 汇总
        print(f"\n{'='*60}")
        print(f"监控任务完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总计: {len(results)} 个项目")
        print(f"{'='*60}\n")

        return results

    def _monitor_project(self, project: Dict) -> Dict:
        """
        监控单个项目

        Args:
            project: 项目配置字典

        Returns:
            项目监控结果
        """
        results = {}

        # 获取数据源配置
        data_sources = project.get('data_sources', [])

        # 按优先级排序
        sorted_sources = sorted(data_sources, key=lambda x: x.get('priority', 999))

        for source_config in sorted_sources:
            source = source_config['source']
            print(f"\n  [{source}] 开始采集...")

            try:
                # 根据数据源调用相应的采集器
                if source == "CDE":
                    source_results = self._scrape_cde(project)
                elif source == "ClinicalTrials.gov":
                    source_results = self._scrape_clinical_trials_gov(project)
                elif source == "Insight":
                    source_results = self._scrape_insight(project)
                else:
                    source_results = {"items": [], "message": f"暂不支持 {source}"}

                results[source] = source_results

                # 显示结果
                items_count = len(source_results.get('items', []))
                print(f"  [{source}] ✅ 采集到 {items_count} 条数据")

            except Exception as e:
                print(f"  [{source}] ❌ 采集失败: {e}")
                results[source] = {"error": str(e)}

        return results

    def _scrape_cde(self, project: Dict) -> Dict:
        """
        爬取CDE数据

        Args:
            project: 项目配置

        Returns:
            采集结果
        """
        try:
            from skills.internal.intelligence.scripts.cde_scraper import CDEScraper
        except ImportError as e:
            return {
                "items": [],
                "message": f"CDE爬虫导入失败: {e}",
                "error": str(e)
            }

        keywords = project.get('keywords', [])
        if not keywords:
            return {
                "items": [],
                "message": "未配置关键词"
            }

        collected_trials = []

        try:
            # 使用上下文管理器
            # 注意：CDE爬虫必须使用 headless=False 才能绕过反爬虫检测
            with CDEScraper(headless=False) as scraper:
                for keyword in keywords[:3]:  # 限制最多3个关键词
                    print(f"\n  [CDE] 搜索关键词: {keyword}")
                    trials = scraper.search_trials(keyword, max_results=5)

                    for trial in trials:
                        # 添加项目名称
                        trial['project'] = project['name']
                        collected_trials.append(trial)

                    # 添加延迟
                    if keyword != keywords[-1]:
                        scraper.page.wait_for_timeout(2000)

            # 保存和索引数据
            for trial in collected_trials:
                # 字段映射：CDE 使用 registration_number，映射到 nct_id
                trial_data = trial.copy()
                if 'registration_number' in trial_data and 'nct_id' not in trial_data:
                    trial_data['nct_id'] = trial_data['registration_number']

                # 移除不需要保存到数据库的字段
                trial_data.pop('project', None)  # project 通过 project_id 关联
                trial_data.pop('registration_number', None)  # 已映射到 nct_id

                self._save_and_index(
                    source="CDE",
                    raw_data=trial.get('raw_detail', trial.get('title', '')),
                    url=trial.get('url', ''),
                    project=project,
                    extracted_data=trial_data
                )

            return {
                "items": collected_trials,
                "count": len(collected_trials),
                "message": f"成功采集 {len(collected_trials)} 条数据"
            }

        except Exception as e:
            import traceback
            print(f"\n  [CDE] ❌ 错误详情: {e}")
            print(f"  [CDE] 错误堆栈:\n{traceback.format_exc()}")
            return {
                "items": collected_trials,
                "count": len(collected_trials),
                "error": str(e),
                "message": f"采集出错: {e}"
            }

    def _scrape_clinical_trials_gov(self, project: Dict) -> Dict:
        """
        爬取ClinicalTrials.gov数据

        Args:
            project: 项目配置

        Returns:
            采集结果
        """
        try:
            from skills.internal.intelligence.scripts.clinical_trials_scraper import ClinicalTrialsGovScraper
        except ImportError as e:
            return {
                "items": [],
                "message": f"ClinicalTrials.gov爬虫导入失败: {e}",
                "error": str(e)
            }

        keywords = project.get('keywords', [])
        if not keywords:
            return {
                "items": [],
                "message": "未配置关键词"
            }

        collected_trials = []

        try:
            scraper = ClinicalTrialsGovScraper()

            # 使用英文名称或中文名称搜索
            search_keywords = []
            for kw in keywords[:3]:  # 限制最多3个关键词
                # 优先使用英文关键词
                if kw.isascii() and len(kw) > 2:
                    search_keywords.append(kw)

            # 如果没有英文关键词，使用中文
            if not search_keywords and keywords:
                search_keywords = keywords[:1]

            for keyword in search_keywords:
                print(f"\n  [ClinicalTrials.gov] 搜索关键词: {keyword}")
                trials = scraper.search_trials(keyword, max_results=5)

                for trial in trials:
                    # 添加项目名称
                    trial['project'] = project['name']
                    collected_trials.append(trial)

            # 保存和索引数据
            for trial in collected_trials:
                self._save_and_index(
                    source="ClinicalTrials.gov",
                    raw_data=trial.get('title', ''),
                    url=trial.get('url', ''),
                    project=project,
                    extracted_data=trial
                )

            return {
                "items": collected_trials,
                "count": len(collected_trials),
                "message": f"成功采集 {len(collected_trials)} 条数据"
            }

        except Exception as e:
            return {
                "items": collected_trials,
                "count": len(collected_trials),
                "error": str(e),
                "message": f"采集出错: {e}"
            }

    def _scrape_insight(self, project: Dict) -> Dict:
        """
        爬取Insight数据

        Args:
            project: 项目配置

        Returns:
            采集结果
        """
        # TODO: 实现Insight爬虫
        # 这里暂时返回模拟数据
        return {
            "items": [],
            "message": "Insight爬虫待实现"
        }

    def _save_and_index(self, source: str, raw_data: str, url: str,
                       project: Dict, extracted_data: Dict) -> str:
        """
        保存数据并建立索引

        Args:
            source: 数据源名称
            raw_data: 原始数据
            url: 数据URL
            project: 项目配置
            extracted_data: 提取的结构化数据

        Returns:
            data_id
        """
        project_name = project['name']

        # 清理数据：转换日期字符串为date对象
        cleaned_data = self._clean_dates(extracted_data)

        # 1. 保存原始数据
        data_id = self.raw_storage.save(
            source=source,
            data=raw_data,
            url=url,
            project=project_name
        )

        # 2. 添加到向量数据库（如果可用）
        if self.vector_db:
            text = self._extract_text_for_vector(cleaned_data)
            metadata = {
                "source": source,
                "project": project_name,
                "url": url,
                "collected_at": datetime.now().isoformat(),
                "extracted_data": cleaned_data
            }
            try:
                self.vector_db.add(data_id=data_id, text=text, metadata=metadata)
            except Exception as e:
                print(f"[WARN] 保存到向量数据库失败: {e}")
        else:
            print("[INFO] 跳过向量数据库保存（未安装ChromaDB）")

        # 3. 保存到结构化数据库
        if source in ["CDE", "ClinicalTrials.gov"]:
            # 临床试验数据
            self.structured_db.save_trial(
                raw_data_id=data_id,
                extracted_data=cleaned_data,
                project_name=project_name
            )
        elif source == "Insight":
            # 申报进度数据
            self.structured_db.save_application(
                raw_data_id=data_id,
                extracted_data=cleaned_data,
                project_name=project_name
            )

        return data_id

    def _clean_dates(self, data: Dict) -> Dict:
        """
        清理日期字段，将字符串转换为date对象

        Args:
            data: 原始数据字典

        Returns:
            清理后的数据字典
        """
        from datetime import datetime

        date_fields = ['start_date', 'completion_date', 'primary_completion_date',
                      'submission_date', 'approval_date']

        cleaned = data.copy()

        for field in date_fields:
            if field in cleaned and cleaned[field]:
                date_str = cleaned[field]

                # 如果是字符串，尝试转换为date对象
                if isinstance(date_str, str):
                    try:
                        # 尝试多种日期格式
                        for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                            try:
                                if fmt == '%Y':
                                    cleaned[field] = datetime.strptime(date_str, fmt).date()
                                    break
                                else:
                                    cleaned[field] = datetime.strptime(date_str, fmt).date()
                                    break
                            except ValueError:
                                continue
                        else:
                            # 如果所有格式都失败，删除该字段
                            del cleaned[field]
                    except:
                        del cleaned[field]

        return cleaned

    def _extract_text_for_vector(self, extracted_data: Dict) -> str:
        """
        从提取的数据中生成用于向量化的文本

        Args:
            extracted_data: 提取的数据字典

        Returns:
            文本字符串
        """
        parts = []

        if extracted_data.get('title'):
            parts.append(extracted_data['title'])

        if extracted_data.get('nct_id'):
            parts.append(f"NCT ID: {extracted_data['nct_id']}")

        if extracted_data.get('company'):
            parts.append(f"公司: {extracted_data['company']}")

        if extracted_data.get('status'):
            parts.append(f"状态: {extracted_data['status']}")

        if extracted_data.get('phase'):
            parts.append(f"阶段: {extracted_data['phase']}")

        if extracted_data.get('indication'):
            parts.append(f"适应症: {extracted_data['indication']}")

        return "\n".join(parts)

    def get_status(self) -> Dict:
        """
        获取监控状态

        Returns:
            状态信息字典
        """
        # 统计结构化数据库
        all_projects = self.structured_db.get_all_projects()

        status = {
            "structured_projects": all_projects,
            "config_file": str(self.config_path),
            "monitored_projects_count": len(self.config.get('monitored_projects', [])),
            "vector_db_available": self.vector_db is not None
        }

        # 统计向量数据库（如果可用）
        if self.vector_db:
            try:
                status["vector_db_count"] = self.vector_db.count()
                status["vector_projects"] = self.vector_db.get_all_projects()
            except Exception as e:
                status["vector_db_error"] = str(e)
        else:
            status["vector_db_count"] = 0
            status["vector_projects"] = []

        return status
