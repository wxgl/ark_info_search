import asyncio
from 测试代码.ark_info_search import ganyuan, qita, gongzhao_model, stage_enemy, search_model


async def main():
    """
    程序的主异步函数
    """
    print("欢迎使用干员信息查询系统")
    print("-" * 30)
    print(f"功能列表：\n0 获取干员信息(如：娜仁图亚)\n1 获取其他信息(如：娜仁图亚的信物)\n2 公招查询"
          f"\n3 关卡及敌人查询")
    print("-" * 30)

    try:
        lei_xing = int(input("查找类型："))
        if lei_xing == 0:
            await ganyuan.main()
        elif lei_xing == 1:
            await qita.main()
        elif lei_xing == 2:
            await gongzhao_model.main()
        elif lei_xing == 3:
            await stage_enemy.main()
        else:
            print("输入的功能选项无效。")

    except ValueError:
        print("请输入有效数字作为查找类型。")
    finally:
        # 确保关闭HTTP客户端
        await search_model.close_http_client()


if __name__ == "__main__":
    # 使用 asyncio.run() 来运行主异步函数
    asyncio.run(main())
