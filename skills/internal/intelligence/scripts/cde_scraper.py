"""
CDE（中国药品审评中心）爬虫

使用Playwright进行网页自动化，采集国内临床试验数据
"""

from typing import List, Dict, Optional
from datetime import datetime
import re


class CDEScraper:
    """CDE网站爬虫"""

    BASE_URL = "http://www.chinadrugtrials.org.cn"

    def __init__(self, headless: bool = True):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式（不显示浏览器）
        """
        self.headless = headless
        self.browser = None
        self.page = None
        self.playwright = None

    def start(self):
        """启动浏览器"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "请先安装 Playwright: "
                "pip install playwright && playwright install chromium"
            )

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=100  # 减慢操作速度，模拟人类行为
        )
        self.page = self.browser.new_page()

        print(f"[CDE] 浏览器已启动")

    def stop(self):
        """停止浏览器"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            self.playwright.stop()
        print(f"[CDE] 浏览器已关闭")

    def search_trials(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        搜索临床试验

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数

        Returns:
            试验列表
        """
        if not self.page:
            self.start()

        try:
            print(f"[CDE] 正在搜索: {keyword}")

            # 访问搜索页面
            search_url = f"{self.BASE_URL}/clinicaltrials.searchlist.dhtml"
            self.page.goto(search_url, timeout=30000, wait_until="networkidle")
            print(f"[CDE] 已访问搜索页面")

            # 等待页面加载
            self.page.wait_for_timeout(2000)

            # 尝试多种可能的选择器
            possible_selectors = [
                'input[name="keyword"]',
                'input[placeholder*="关键词"]',
                'input[type="text"]',
                '#keyword',
                '.search-input'
            ]

            input_found = False
            for selector in possible_selectors:
                try:
                    input_box = self.page.query_selector(selector)
                    if input_box:
                        input_box.fill(keyword)
                        input_found = True
                        print(f"[CDE] 已输入关键词到: {selector}")
                        break
                except:
                    continue

            if not input_found:
                print(f"[CDE] ⚠️ 未找到搜索输入框，可能需要手动分析页面结构")
                return []

            # 点击搜索按钮
            possible_button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("搜索")',
                'button:has-text("查询")',
                '.search-button',
                '#searchBtn'
            ]

            button_clicked = False
            for selector in possible_button_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button:
                        button.click()
                        button_clicked = True
                        print(f"[CDE] 已点击搜索按钮")
                        break
                except:
                    continue

            if not button_clicked:
                # 尝试按回车键
                try:
                    self.page.keyboard.press('Enter')
                    button_clicked = True
                    print(f"[CDE] 已按回车键搜索")
                except:
                    pass

            # 等待结果加载
            self.page.wait_for_timeout(3000)

            # 解析结果页
            trials = self._parse_search_results(max_results)

            print(f"[CDE] 找到 {len(trials)} 条结果")

            return trials

        except Exception as e:
            print(f"[CDE] ❌ 搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _parse_search_results(self, max_results: int) -> List[Dict]:
        """
        解析搜索结果页

        Args:
            max_results: 最大结果数

        Returns:
            试验列表
        """
        trials = []

        try:
            # 尝试多种可能的列表容器选择器
            possible_list_selectors = [
                '.trial-list',
                '.result-list',
                'table tr',
                '.search-result-item',
                '[class*="trial"]',
                '[class*="result"]'
            ]

            list_items = []
            for selector in possible_list_selectors:
                try:
                    items = self.page.query_selector_all(selector)
                    if items and len(items) > 1:
                        list_items = items
                        print(f"[CDE] 找到结果列表: {selector} ({len(items)} 项)")
                        break
                except:
                    continue

            if not list_items:
                print(f"[CDE] ⚠️ 未找到结果列表，返回空结果")
                return []

            # 解析每一项
            for i, item in enumerate(list_items[:max_results]):
                try:
                    trial = self._parse_trial_item(item)
                    if trial:
                        trials.append(trial)
                except Exception as e:
                    print(f"[CDE] 解析第 {i+1} 项失败: {e}")
                    continue

        except Exception as e:
            print(f"[CDE] 解析结果页失败: {e}")

        return trials

    def _parse_trial_item(self, item) -> Optional[Dict]:
        """
        解析单个试验列表项

        Args:
            item: Playwright元素对象

        Returns:
            试验字典
        """
        try:
            # 获取文本内容
            text = item.inner_text()

            # 尝试提取常见字段
            trial = {
                "title": "",
                "company": "",
                "phase": "",
                "status": "",
                "indication": "",
                "source": "CDE",
                "url": self.page.url,
                "collected_at": datetime.now().isoformat()
            }

            # 尝试查找标题
            title_selectors = [
                '.title',
                '.trial-title',
                'h3',
                'h4',
                'a',
                '[class*="title"]'
            ]

            for selector in title_selectors:
                try:
                    title_elem = item.query_selector(selector)
                    if title_elem:
                        trial["title"] = title_elem.inner_text().strip()
                        break
                except:
                    continue

            # 如果没找到特定的标题元素，使用整个项的文本
            if not trial["title"]:
                trial["title"] = text.strip()[:100]  # 限制长度

            # 尝试从文本中提取信息
            # 例如：匹配 "III期"、"I期" 等关键词
            phase_patterns = [
                r'(I{1,3}期|Phase\s+[I123])',
                r'(一期|二期|三期|四期)',
                r'([I]{1,3}\s*phase)'
            ]

            for pattern in phase_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    trial["phase"] = match.group(1)
                    break

            # 尝试匹配公司名（通常在"申请人"、"申办方"等字段）
            company_patterns = [
                r'申办[方人]?[:：]\s*([^\s,，]+)',
                r'申请人[:：]\s*([^\s,，]+)',
                r'企业[:：]\s*([^\s,，]+)',
                r'公司[:：]\s*([^\s,，]+)'
            ]

            for pattern in company_patterns:
                match = re.search(pattern, text)
                if match:
                    trial["company"] = match.group(1)
                    break

            # 尝试提取状态
            status_keywords = ['进行中', '已完成', '招募中', '已结束', '已完成招募', 'recruiting', 'completed', 'active']
            for keyword in status_keywords:
                if keyword in text:
                    trial["status"] = keyword
                    break

            # 尝试提取适应症
            indication_patterns = [
                r'适应症[:：]\s*([^\n]+)',
                r'用于治疗\s*([^\n,，]+)'
            ]

            for pattern in indication_patterns:
                match = re.search(pattern, text)
                if match:
                    trial["indication"] = match.group(1).strip()
                    break

            return trial

        except Exception as e:
            print(f"[CDE] 解析试验项失败: {e}")
            return None

    def get_trial_detail(self, trial_id: str) -> Optional[Dict]:
        """
        获取试验详情

        Args:
            trial_id: 试验ID或URL

        Returns:
            试验详情字典
        """
        if not self.page:
            self.start()

        try:
            print(f"[CDE] 获取详情: {trial_id}")

            # 如果是完整URL，直接访问
            if trial_id.startswith('http'):
                detail_url = trial_id
            else:
                # 否则构建URL
                detail_url = f"{self.BASE_URL}/clinicaltrials.detail.dhtml?id={trial_id}"

            self.page.goto(detail_url, timeout=30000, wait_until="networkidle")

            # 等待页面加载
            self.page.wait_for_timeout(2000)

            # 解析详情页
            detail = {}

            # 获取页面标题
            try:
                title = self.page.title()
                detail["title"] = title
            except:
                pass

            # 尝试提取详细信息
            # 这里需要根据实际页面结构调整选择器
            info_selectors = [
                '.detail-info',
                '.trial-detail',
                '.info-section',
                'table',
                '.content'
            ]

            for selector in info_selectors:
                try:
                    info_elem = self.page.query_selector(selector)
                    if info_elem:
                        detail["raw_detail"] = info_elem.inner_text()
                        break
                except:
                    continue

            # 添加元数据
            detail["source"] = "CDE"
            detail["url"] = detail_url
            detail["collected_at"] = datetime.now().isoformat()

            return detail

        except Exception as e:
            print(f"[CDE] 获取详情失败: {e}")
            return None

    def scrape(self, keywords: List[str]) -> Dict[str, List[Dict]]:
        """
        爬取多个关键词的试验数据

        Args:
            keywords: 关键词列表

        Returns:
            {keyword: [trials]}
        """
        results = {}

        try:
            self.start()

            for keyword in keywords:
                print(f"\n{'='*60}")
                print(f"[CDE] 搜索关键词: {keyword}")
                print(f"{'='*60}")

                trials = self.search_trials(keyword)

                results[keyword] = trials

                # 添加延迟，避免请求过快
                if keyword != keywords[-1]:
                    self.page.wait_for_timeout(2000)

            return results

        finally:
            self.stop()

    def __enter__(self):
        """上下文管理器入口"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.stop()


# 使用示例
if __name__ == "__main__":
    # 方式1: 使用上下文管理器（推荐）
    with CDEScraper(headless=False) as scraper:
        results = scraper.scrape(["曲普瑞林"])

        for keyword, trials in results.items():
            print(f"\n关键词: {keyword}")
            print(f"找到 {len(trials)} 条结果")

            for i, trial in enumerate(trials, 1):
                print(f"\n{i}. {trial.get('title', 'N/A')}")
                print(f"   公司: {trial.get('company', 'N/A')}")
                print(f"   阶段: {trial.get('phase', 'N/A')}")
                print(f"   状态: {trial.get('status', 'N/A')}")
