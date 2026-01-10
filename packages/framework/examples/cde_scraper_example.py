"""
CDE爬虫使用示例

演示如何使用CDE爬虫采集中国药物临床试验数据
"""

from skills.internal.intelligence.scripts.cde_scraper import CDEScraper


def main():
    """CDE爬虫使用示例"""
    print("=" * 80)
    print("CDE爬虫示例 - 采集司美格鲁肽临床试验数据")
    print("=" * 80)
    print("\n注意事项：")
    print("1. 必须使用 headless=False（显示浏览器窗口）")
    print("2. 不能使用 uv run（会创建asyncio loop冲突）")
    print("3. 直接使用 python 运行此脚本")
    print("\n" + "=" * 80 + "\n")

    # 使用爬虫
    with CDEScraper(headless=False) as scraper:
        # 搜索关键词
        keyword = "司美格鲁肽"
        print(f"正在搜索: {keyword}\n")

        trials = scraper.search_trials(keyword, max_results=10)

        # 输出结果
        print(f"\n找到 {len(trials)} 条记录:\n")

        for i, trial in enumerate(trials, 1):
            print(f"[{i}] {trial.get('registration_number', 'N/A')}")
            print(f"    状态: {trial.get('status', 'N/A')}")
            print(f"    药品: {trial.get('company', 'N/A')}")
            print(f"    适应症: {trial.get('indication', 'N/A')}")
            print()

        # 保存为JSON
        if trials:
            import json
            from datetime import datetime

            output_file = (
                f"data/cde_trials_{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            # 确保目录存在
            import os

            os.makedirs("data", exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(trials, f, ensure_ascii=False, indent=2)

            print(f"✓ 结果已保存到: {output_file}")

    print("\n" + "=" * 80)
    print("采集完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
