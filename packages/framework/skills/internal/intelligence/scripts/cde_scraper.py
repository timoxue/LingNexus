"""
CDE（中国药品审评中心）爬虫

使用Playwright进行网页自动化，采集国内临床试验数据
增强反检测功能，模拟真实用户行为
"""

import random
import re
import time
from datetime import datetime
from typing import Dict, List, Optional


class CDEScraper:
    """CDE网站爬虫 - 增强反检测版本"""

    BASE_URL = "http://www.chinadrugtrials.org.cn"

    # 真实的浏览器User-Agent列表
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]

    # 真实的视口尺寸
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
    ]

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
        self.context = None

    def _random_delay(self, min_sec: float = 0.5, max_sec: float = 2.0):
        """随机延迟，模拟人类操作"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def _simulate_mouse_movement(self):
        """模拟真实的鼠标移动轨迹"""
        try:
            # 随机移动鼠标到几个位置
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                self.page.mouse.move(x, y)
                self._random_delay(0.1, 0.3)
        except Exception:
            pass

    def _simulate_scroll(self):
        """模拟页面滚动"""
        try:
            # 随机滚动几次
            for _ in range(random.randint(2, 4)):
                scroll_y = random.randint(100, 500)
                self.page.evaluate(f"window.scrollBy(0, {scroll_y})")
                self._random_delay(0.3, 0.8)
        except Exception:
            pass

    def start(self):
        """启动浏览器 - 增强反检测版本"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise ImportError(
                "请先安装 Playwright: pip install playwright && playwright install chromium"
            )

        # 直接启动（Python脚本通常没有asyncio loop问题）
        self.playwright = sync_playwright().start()

        # 随机选择User-Agent和视口
        user_agent = random.choice(self.USER_AGENTS)
        viewport = random.choice(self.VIEWPORTS)

        print(f"[CDE] 启动浏览器 (UA: Chrome, Viewport: {viewport['width']}x{viewport['height']})")

        # 启动浏览器时加入更多反检测选项
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",  # 关键：禁用自动化检测
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-site-isolation-trials",
                "--disable-features=BlockInsecurePrivateNetworkRequests",  # 允许私有网络请求
                "--window-size={},{}".format(viewport["width"], viewport["height"]),
            ],
            slow_mo=random.randint(50, 150),  # 随机化操作速度
        )

        # 创建context，设置更真实的浏览器属性
        self.context = self.browser.new_context(
            viewport=viewport,
            user_agent=user_agent,
            locale="zh-CN",
            timezone_id="Asia/Shanghai",
            permissions=["geolocation"],
            geolocation={"latitude": 39.9042, "longitude": 116.4074},  # 北京坐标
            color_scheme="light",
            device_scale_factor=1,
            # 添加真实的浏览器headers
            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0",
            },
        )

        # 创建页面
        self.page = self.context.new_page()

        # 注入JavaScript，隐藏webdriver特征
        self.page.add_init_script(
            """
            // 覆盖navigator.webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 覆盖chrome对象
            window.chrome = {
                runtime: {}
            };

            // 覆盖permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // 覆盖plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // 覆盖languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });
        """
        )

        print("[CDE] 浏览器已启动（反检测模式）")

    def stop(self):
        """停止浏览器"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if hasattr(self, "playwright") and self.playwright:
                self.playwright.stop()
            print("[CDE] 浏览器已关闭")
        except Exception as e:
            print(f"[CDE] 关闭浏览器时出错: {e}")

    def search_trials(
        self, keyword: str, max_results: int = 10, max_retries: int = 3
    ) -> List[Dict]:
        """
        搜索临床试验 - 增强反检测版本

        Args:
            keyword: 搜索关键词
            max_results: 最大结果数
            max_retries: 最大重试次数

        Returns:
            试验列表
        """
        if not self.page:
            self.start()

        for attempt in range(max_retries):
            try:
                print(f"[CDE] 正在搜索: {keyword} (尝试 {attempt + 1}/{max_retries})")

                # 模拟真实用户行为 - 先访问首页
                print("[CDE] 先访问首页建立会话...")
                self.page.goto(f"{self.BASE_URL}", timeout=30000, wait_until="domcontentloaded")
                self._random_delay(1.0, 2.0)

                # 模拟鼠标移动
                self._simulate_mouse_movement()

                # 滚动页面，模拟真实浏览
                self._simulate_scroll()

                # 访问搜索页面
                search_url = f"{self.BASE_URL}/clinicaltrials.searchlist.dhtml"
                print("[CDE] 访问搜索页面...")
                self.page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                print("[CDE] 已访问搜索页面")

                # 等待页面完全加载
                self._random_delay(2.0, 3.0)

                # 检查页面内容，确保不是空白页
                content = self.page.content()
                if len(content) < 1000:
                    print(f"[CDE] [WARNING] 页面内容异常（长度: {len(content)}），可能是被拦截")
                    if attempt < max_retries - 1:
                        print("[CDE] 等待后重试...")
                        self._random_delay(3.0, 5.0)
                        continue
                    else:
                        # 尝试截图保存
                        try:
                            screenshot_path = f"cde_error_attempt{attempt}.png"
                            self.page.screenshot(path=screenshot_path)
                            print(f"[CDE] 已保存错误截图: {screenshot_path}")
                        except Exception:
                            pass
                        return []

                print(f"[CDE] [OK] 页面内容正常 (长度: {len(content)} 字符)")

                # 尝试多种可能的选择器
                possible_selectors = [
                    'input[name="keyword"]',
                    'input[placeholder*="关键词"]',
                    'input[placeholder*="搜索"]',
                    'input[type="text"]',
                    "#keyword",
                    ".search-input",
                    "input.input-text",
                    ".form-input",
                ]

                input_found = False
                for selector in possible_selectors:
                    try:
                        input_box = self.page.query_selector(selector)
                        if input_box:
                            # 先点击输入框（模拟真实用户）
                            input_box.click()
                            self._random_delay(0.3, 0.6)

                            # 清空并输入关键词（逐字输入，更真实）
                            input_box.fill("")
                            self._random_delay(0.2, 0.4)

                            # 使用type而不是fill，模拟真实打字
                            for char in keyword:
                                self.page.keyboard.type(char)
                                self._random_delay(0.05, 0.15)

                            input_found = True
                            print(f"[CDE] [OK] 已输入关键词到: {selector}")
                            break
                    except Exception:
                        continue

                if not input_found:
                    print("[CDE] [WARNING] 未找到搜索输入框")
                    print("[CDE] 尝试输出页面结构用于调试...")

                    # 输出页面主要结构
                    try:
                        print(f"[CDE] 页面标题: {self.page.title()}")
                        inputs = self.page.query_selector_all("input")
                        print(f"[CDE] 找到 {len(inputs)} 个输入框")
                        buttons = self.page.query_selector_all("button")
                        print(f"[CDE] 找到 {len(buttons)} 个按钮")
                    except Exception:
                        pass

                    if attempt < max_retries - 1:
                        self._random_delay(2.0, 3.0)
                        continue
                    else:
                        return []

                # 再次延迟，模拟用户思考
                self._random_delay(0.5, 1.0)

                # 点击搜索按钮
                possible_button_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("搜索")',
                    'button:has-text("查询")',
                    'button:has-text("提交")',
                    ".search-button",
                    "#searchBtn",
                    ".btn-search",
                    'input[value="搜索"]',
                ]

                button_clicked = False
                for selector in possible_button_selectors:
                    try:
                        button = self.page.query_selector(selector)
                        if button:
                            # 滚动到按钮可见
                            button.scroll_into_view_if_needed()
                            self._random_delay(0.3, 0.6)

                            # 点击按钮
                            button.click()
                            button_clicked = True
                            print(f"[CDE] [OK] 已点击搜索按钮: {selector}")
                            break
                    except Exception:
                        continue

                if not button_clicked:
                    # 尝试按回车键
                    try:
                        self.page.keyboard.press("Enter")
                        button_clicked = True
                        print("[CDE] [OK] 已按回车键搜索")
                    except Exception:
                        pass

                # 等待结果加载（给足够时间）
                print("[CDE] 等待搜索结果加载...")
                self._random_delay(3.0, 5.0)

                # 等待网络空闲
                try:
                    self.page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    pass

                # 检查是否跳转或页面是否正常
                current_url = self.page.url
                print(f"[CDE] 当前URL: {current_url}")

                # 再次检查页面内容
                content = self.page.content()
                if len(content) < 1000:
                    print("[CDE] [WARNING] 搜索后页面内容异常")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return []

                # 解析结果页
                trials = self._parse_search_results(max_results)

                print(f"[CDE] [OK] 找到 {len(trials)} 条结果")

                return trials

            except Exception as e:
                print(f"[CDE] [ERROR] 搜索失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                import traceback

                traceback.print_exc()

                if attempt < max_retries - 1:
                    print("[CDE] 等待后重试...")
                    self._random_delay(3.0, 5.0)
                else:
                    return []

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
                "table tbody tr",  # 表格体（排除表头）
                ".trial-list .trial-item",
                ".result-list .result-item",
                "table tr:not(:has(th))",  # 表格行但排除表头
                '[class*="trial"]',
                '[class*="result"]',
            ]

            list_items = []
            for selector in possible_list_selectors:
                try:
                    items = self.page.query_selector_all(selector)
                    if items and len(items) > 0:
                        # 过滤掉表头行（包含th标签的行）
                        filtered_items = []
                        for item in items:
                            try:
                                th = item.query_selector("th")
                                if not th:  # 只保留不包含th的行
                                    filtered_items.append(item)
                            except Exception:
                                filtered_items.append(item)

                        if filtered_items:
                            list_items = filtered_items
                            print(f"[CDE] 找到结果列表: {selector} ({len(list_items)} 项)")
                            break
                except Exception:
                    continue

            # 如果还是没找到，尝试直接获取所有tr然后跳过前几个
            if not list_items:
                try:
                    all_rows = self.page.query_selector_all("table tr")
                    if len(all_rows) > 1:
                        # 跳过前1-2行（通常是表头）
                        list_items = all_rows[1:] if len(all_rows) > 1 else []
                        print(f"[CDE] 使用备用方法，找到 {len(list_items)} 行（跳过表头）")
                except Exception:
                    pass

            if not list_items:
                print("[CDE] [WARNING] 未找到结果列表，返回空结果")
                return []

            # 解析每一项
            for i, item in enumerate(list_items[:max_results]):
                try:
                    trial = self._parse_trial_item(item)
                    if trial and trial.get("title"):  # 确保有标题
                        trials.append(trial)
                except Exception as e:
                    print(f"[CDE] 解析第 {i + 1} 项失败: {e}")
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
            # 尝试提取表格单元格（td）
            tds = item.query_selector_all("td")

            trial = {
                "title": "",
                "company": "",
                "phase": "",
                "status": "",
                "indication": "",
                "registration_number": "",
                "source": "CDE",
                "url": self.page.url,
                "collected_at": datetime.now().isoformat(),
            }

            if tds and len(tds) >= 1:
                # CDE表格列结构（已验证）：
                # 列0: 序号
                # 列1: 注册号
                # 列2: 试验状态
                # 列3: 药品名称
                # 列4: 适应症
                # 列5: 相关通办项目

                for idx, td in enumerate(tds):
                    try:
                        cell_text = td.inner_text().strip()

                        if idx == 0:
                            # 序号，跳过
                            pass
                        elif idx == 1:
                            # 注册号
                            trial["registration_number"] = cell_text
                            trial["title"] = cell_text  # 用注册号作为标题
                        elif idx == 2:
                            # 试验状态
                            trial["status"] = cell_text
                        elif idx == 3:
                            # 药品名称（可作为公司或药品信息）
                            trial["company"] = cell_text  # 暂时存到company字段
                        elif idx == 4:
                            # 适应症
                            trial["indication"] = cell_text
                        elif idx == 5:
                            # 相关通办项目（可选）
                            pass

                    except Exception:
                        continue

                # 尝试从单元格中提取链接
                try:
                    link = item.query_selector("a")
                    if link:
                        href = link.get_attribute("href")
                        if href:
                            if href.startswith("http"):
                                trial["url"] = href
                            else:
                                trial["url"] = f"{self.BASE_URL}/{href.lstrip('/')}"

                        # 如果链接有文本，可能包含更多信息
                        link_text = link.inner_text().strip()
                        if link_text and link_text != trial["title"]:
                            # 如果链接文本与注册号不同，可能是更详细的信息
                            pass
                except Exception:
                    pass

            else:
                # 如果不是表格，使用通用解析
                text = item.inner_text()

                # 尝试查找标题
                title_selectors = [".title", ".trial-title", "h3", "h4", "a", '[class*="title"]']

                for selector in title_selectors:
                    try:
                        title_elem = item.query_selector(selector)
                        if title_elem:
                            trial["title"] = title_elem.inner_text().strip()
                            break
                    except Exception:
                        continue

                # 如果没找到特定的标题元素，使用整个项的文本
                if not trial["title"]:
                    trial["title"] = text.strip()[:100]  # 限制长度

                # 尝试从文本中提取信息
                # 例如：匹配 "III期"、"I期" 等关键词
                phase_patterns = [
                    r"(I{1,3}期|Phase\s+[I123])",
                    r"(一期|二期|三期|四期)",
                    r"([I]{1,3}\s*phase)",
                ]

                for pattern in phase_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        trial["phase"] = match.group(1)
                        break

                # 尝试匹配公司名（通常在"申请人"、"申办方"等字段）
                company_patterns = [
                    r"申办[方人]?[:：]\s*([^\s,，]+)",
                    r"申请人[:：]\s*([^\s,，]+)",
                    r"企业[:：]\s*([^\s,，]+)",
                    r"公司[:：]\s*([^\s,，]+)",
                ]

                for pattern in company_patterns:
                    match = re.search(pattern, text)
                    if match:
                        trial["company"] = match.group(1)
                        break

                # 尝试提取状态
                status_keywords = [
                    "进行中",
                    "已完成",
                    "招募中",
                    "已结束",
                    "已完成招募",
                    "recruiting",
                    "completed",
                    "active",
                ]
                for keyword in status_keywords:
                    if keyword in text:
                        trial["status"] = keyword
                        break

                # 尝试提取适应症
                indication_patterns = [r"适应症[:：]\s*([^\n]+)", r"用于治疗\s*([^\n,，]+)"]

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
            if trial_id.startswith("http"):
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
            except Exception:
                pass

            # 尝试提取详细信息
            # 这里需要根据实际页面结构调整选择器
            info_selectors = [
                ".detail-info",
                ".trial-detail",
                ".info-section",
                "table",
                ".content",
            ]

            for selector in info_selectors:
                try:
                    info_elem = self.page.query_selector(selector)
                    if info_elem:
                        detail["raw_detail"] = info_elem.inner_text()
                        break
                except Exception:
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

            for idx, keyword in enumerate(keywords):
                print(f"\n{'=' * 60}")
                print(f"[CDE] 搜索关键词 ({idx + 1}/{len(keywords)}): {keyword}")
                print(f"{'=' * 60}")

                trials = self.search_trials(keyword)

                results[keyword] = trials

                # 添加较长延迟，避免请求过快被识别
                if keyword != keywords[-1]:
                    delay = random.uniform(5.0, 10.0)
                    print(f"[CDE] 等待 {delay:.1f} 秒后继续...")
                    time.sleep(delay)

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
    import json

    # 方式1: 使用上下文管理器（推荐）
    # headless=False 可以看到浏览器操作，便于调试
    with CDEScraper(headless=False) as scraper:
        # 搜索关键词
        results = scraper.scrape(["司美格鲁肽"])

        # 输出结果
        for keyword, trials in results.items():
            print(f"\n{'=' * 80}")
            print(f"关键词: {keyword}")
            print(f"找到 {len(trials)} 条结果")
            print(f"{'=' * 80}")

            for i, trial in enumerate(trials, 1):
                print(f"\n【试验 {i}】")
                print(f"  注册号: {trial.get('registration_number', 'N/A')}")
                print(f"  状态: {trial.get('status', 'N/A')}")
                print(f"  药品: {trial.get('company', 'N/A')}")
                print(f"  适应症: {trial.get('indication', 'N/A')}")
                print(f"  来源: {trial.get('source', 'N/A')}")

            # 保存为JSON
            if trials:
                output_file = (
                    f"cde_trials_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(trials, f, ensure_ascii=False, indent=2)
                print(f"\n[OK] 结果已保存到: {output_file}")
