"""
监控相关的CLI命令

包含：monitor、status、db、search、report等命令
"""

import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from lingnexus.scheduler.monitoring import DailyMonitoringTask

# VectorDB是可选的
try:
    from lingnexus.storage.vector import VectorDB
except ImportError:
    VectorDB = None

from lingnexus.storage.structured import StructuredDB


def cmd_monitor(args):
    """执行监控任务"""
    task = DailyMonitoringTask()

    if args.project:
        # 监控指定项目
        results = task.run(project_names=[args.project])
    else:
        # 监控所有项目
        results = task.run()

    # 显示结果摘要
    print("\n" + "="*60)
    print("监控结果摘要")
    print("="*60)

    for project_name, project_results in results.items():
        if "error" in project_results:
            print(f"\n❌ {project_name}: {project_results['error']}")
        else:
            total = sum(len(r.get('items', [])) for r in project_results.values())
            print(f"\n✅ {project_name}: {total} 条数据")


def cmd_status(args):
    """查看监控状态"""
    task = DailyMonitoringTask()
    status = task.get_status()

    print("\n" + "="*60)
    print("监控状态")
    print("="*60)

    print(f"\n向量数据库:")
    print(f"  - 总文档数: {status['vector_db_count']}")
    print(f"  - 项目数: {len(status['vector_projects'])}")
    if status['vector_projects']:
        print(f"  - 项目列表: {', '.join(status['vector_projects'])}")

    print(f"\n结构化数据库:")
    print(f"  - 项目数: {len(status['structured_projects'])}")
    for proj in status['structured_projects']:
        print(f"    - {proj['name']} ({proj.get('english_name', 'N/A')})")

    print(f"\n配置:")
    print(f"  - 配置文件: {status['config_file']}")
    print(f"  - 监控项目数: {status['monitored_projects_count']}")


def cmd_search(args):
    """搜索向量数据库"""
    if VectorDB is None:
        print("\n错误: ChromaDB未安装，向量搜索功能不可用")
        print("提示: 可以使用 'db' 命令查看结构化数据库")
        return

    vectordb = VectorDB()

    print(f"\n搜索: {args.query}")
    print("="*60)

    results = vectordb.search(
        query=args.query,
        n_results=args.n,
        filter={"project": args.project} if args.project else None
    )

    print(f"\n找到 {len(results)} 条结果:\n")

    for i, result in enumerate(results, 1):
        metadata = result['metadata']
        print(f"{i}. [{metadata['source']}] {metadata.get('collected_at', 'N/A')}")
        print(f"   项目: {metadata.get('project', 'N/A')}")
        print(f"   内容: {result['document'][:100]}...")
        if 'similarity' in result:
            print(f"   相似度: {result['similarity']:.2f}")
        print()


def cmd_report(args):
    """生成报告（占位）"""
    print(f"\n生成报告功能待实现")
    print(f"项目: {args.project}")
    print(f"类型: {args.type}")


def view_database(project_name: Optional[str] = None, nct_id: Optional[str] = None):
    """查看数据库"""
    from tabulate import tabulate
    from lingnexus.storage.structured import ClinicalTrial

    db = StructuredDB()

    print("\n" + "="*80)
    print("竞品情报数据库")
    print("="*80)

    if nct_id:
        # 查看特定试验详情
        print(f"\n试验详情: {nct_id}")
        print("-"*80)

        trial = db.session.query(ClinicalTrial).filter_by(nct_id=nct_id).first()

        if trial:
            print(f"\n基本信息:")
            print(f"  NCT ID: {trial.nct_id}")
            print(f"  标题: {trial.title}")
            print(f"  公司: {trial.company or 'N/A'}")
            print(f"  阶段: {trial.phase or 'N/A'}")
            print(f"  状态: {trial.status or 'N/A'}")
            print(f"  适应症: {trial.indication or 'N/A'}")
            print(f"  入组人数: {trial.enrollment or 'N/A'}")

            print(f"\n时间信息:")
            print(f"  开始日期: {trial.start_date or 'N/A'}")
            print(f"  完成日期: {trial.completion_date or 'N/A'}")

            print(f"\n采集信息:")
            print(f"  来源: {trial.source or 'N/A'}")
            print(f"  URL: {trial.url or 'N/A'}")
            print(f"  采集时间: {trial.collected_at.strftime('%Y-%m-%d %H:%M:%S') if trial.collected_at else 'N/A'}")
            print(f"  项目: {trial.project.name if trial.project else 'N/A'}")

        else:
            print(f"未找到试验 {nct_id}")

    elif project_name:
        # 查看特定项目
        print(f"\n项目: {project_name}")
        print("-"*80)

        trials = db.get_project_trials(project_name, limit=50)

        if trials:
            trial_data = []
            for t in trials:
                trial_data.append([
                    t['nct_id'],
                    t['title'][:60] + '...' if len(t['title']) > 60 else t['title'],
                    t['company'] or 'N/A',
                    t['phase'] or 'N/A',
                    t['status'] or 'N/A',
                    t.get('start_date') or 'N/A',
                    t.get('completion_date') or 'N/A',
                ])

            print(tabulate(
                trial_data,
                headers=['NCT ID', '标题', '公司', '阶段', '状态', '开始日期', '完成日期'],
                tablefmt='grid'
            ))
            print(f"\n总计: {len(trials)} 条试验")
        else:
            print(f"未找到项目 '{project_name}' 的数据")

    else:
        # 查看所有数据
        # 1. 显示所有项目
        print("\n【监控项目】")
        print("-"*80)

        projects = db.get_all_projects()

        if projects:
            project_data = []
            for p in projects:
                project_data.append([
                    p['id'],
                    p['name'],
                    p.get('english_name', 'N/A'),
                    p.get('category', 'N/A'),
                ])

            print(tabulate(
                project_data,
                headers=['ID', '名称', '英文名', '分类'],
                tablefmt='grid'
            ))
        else:
            print("暂无项目")

        # 2. 显示临床试验统计
        print("\n【临床试验统计】")
        print("-"*80)

        stats = []
        for p in projects:
            trials = db.get_project_trials(p['name'], limit=1000)
            stats.append([
                p['name'],
                len(trials),
                f"{sum(1 for t in trials if t['status'] == 'RECRUITING')} 条招募中",
                f"{sum(1 for t in trials if t['status'] == 'COMPLETED')} 条已完成",
            ])

        if stats:
            print(tabulate(
                stats,
                headers=['项目', '总试验数', '招募中', '已完成'],
                tablefmt='grid'
            ))

        # 3. 显示最新采集的数据
        print("\n【最新采集（前5条）】")
        print("-"*80)

        latest_trials = db.session.query(ClinicalTrial).order_by(
            ClinicalTrial.collected_at.desc()
        ).limit(5).all()

        if latest_trials:
            for i, t in enumerate(latest_trials, 1):
                print(f"\n{i}. {t.nct_id}")
                print(f"   标题: {t.title[:70]}...")
                print(f"   状态: {t.status or 'N/A'}")
                print(f"   项目: {t.project.name if t.project else 'N/A'}")
                print(f"   采集时间: {t.collected_at.strftime('%Y-%m-%d %H:%M') if t.collected_at else 'N/A'}")

    db.close()

    print("\n" + "="*80)


def cmd_db(args):
    """数据库查看命令"""
    view_database(project_name=args.project, nct_id=args.nct)
