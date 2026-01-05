"""
竞品情报监控系统使用示例

演示如何使用监控系统的各项功能
"""

from lingnexus.scheduler.monitoring import DailyMonitoringTask
from lingnexus.storage.raw import RawStorage
from lingnexus.storage.vector import VectorDB
from lingnexus.storage.structured import StructuredDB


def example_1_basic_monitoring():
    """示例1: 基础监控"""
    print("\n" + "="*60)
    print("示例1: 执行监控任务")
    print("="*60)

    # 创建监控任务
    task = DailyMonitoringTask()

    # 执行监控（所有项目）
    results = task.run()

    # 查看结果
    for project_name, project_results in results.items():
        if "error" in project_results:
            print(f"❌ {project_name}: {project_results['error']}")
        else:
            total = sum(len(r.get('items', [])) for r in project_results.values())
            print(f"✅ {project_name}: {total} 条数据")


def example_2_single_project():
    """示例2: 监控单个项目"""
    print("\n" + "="*60)
    print("示例2: 监控单个项目")
    print("="*60)

    task = DailyMonitoringTask()

    # 只监控司美格鲁肽
    results = task.run(project_names=["司美格鲁肽"])

    print(f"\n司美格鲁肽监控结果:")
    print(results)


def example_3_check_status():
    """示例3: 查看监控状态"""
    print("\n" + "="*60)
    print("示例3: 查看系统状态")
    print("="*60)

    task = DailyMonitoringTask()
    status = task.get_status()

    print(f"\n向量数据库文档数: {status['vector_db_count']}")
    print(f"监控项目数: {status['monitored_projects_count']}")
    print(f"项目列表: {', '.join(status['vector_projects'])}")


def example_4_save_raw_data():
    """示例4: 保存原始数据"""
    print("\n" + "="*60)
    print("示例4: 保存原始数据")
    print("="*60)

    storage = RawStorage()

    # 保存示例数据
    data_id = storage.save(
        source="CDE",
        data="<html><body><h1>试验标题</h1></body></html>",
        url="http://example.com/trial/1",
        project="测试项目",
        metadata={"test": True}
    )

    print(f"\n数据已保存，ID: {data_id}")

    # 加载数据
    loaded_data, loaded_meta = storage.load(data_id)
    print(f"加载的数据: {loaded_data[:50]}...")
    print(f"元数据: {loaded_meta}")


def example_5_vector_search():
    """示例5: 向量搜索"""
    print("\n" + "="*60)
    print("示例5: 向量数据库搜索")
    print("="*60)

    vectordb = VectorDB()

    # 添加测试数据
    test_data_id = "test_001"
    vectordb.add(
        data_id=test_data_id,
        text="司美格鲁肽III期临床试验，评估其在2型糖尿病患者中的疗效和安全性",
        metadata={
            "source": "CDE",
            "project": "司美格鲁肽",
            "collected_at": "2026-01-05T10:00:00"
        }
    )

    print(f"\n已添加测试数据")

    # 搜索
    results = vectordb.search(
        query="糖尿病临床试验",
        n_results=5
    )

    print(f"\n搜索结果:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['document']}")
        print(f"   相似度: {result.get('similarity', 'N/A')}")


def example_6_structured_query():
    """示例6: 结构化数据查询"""
    print("\n" + "="*60)
    print("示例6: 查询结构化数据")
    print("="*60)

    db = StructuredDB()

    # 添加项目
    project = db.add_project(
        name="司美格鲁肽",
        english_name="Semaglutide",
        category="糖尿病",
        type="GLP-1受体激动剂"
    )

    print(f"\n已添加项目: {project.name} (ID: {project.id})")

    # 获取所有项目
    all_projects = db.get_all_projects()
    print(f"\n所有项目:")
    for p in all_projects:
        print(f"  - {p['name']}: {p.get('english_name', 'N/A')}")


def example_7_list_raw_data():
    """示例7: 列出原始数据"""
    print("\n" + "="*60)
    print("示例7: 列出原始数据")
    print("="*60)

    storage = RawStorage()

    # 按项目列出
    project_data = storage.list_by_project("司美格鲁肽", limit=10)

    print(f"\n找到 {len(project_data)} 条数据:")
    for data in project_data:
        print(f"  - {data['data_id']}: {data['source']} @ {data['collected_at']}")


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("竞品情报监控系统使用示例")
    print("="*60)

    # 运行示例
    example_3_check_status()
    example_4_save_raw_data()
    example_5_vector_search()
    example_6_structured_query()

    print("\n" + "="*60)
    print("所有示例运行完成")
    print("="*60)


if __name__ == "__main__":
    main()
