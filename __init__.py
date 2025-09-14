import asyncio
import ganyuan_info
import qita_info
import gongzhao_model


async def main():
    """
    程序的主异步函数
    """
    print("欢迎使用干员信息查询系统")
    print("-" * 30)
    print(f"功能列表：\n0 获取干员信息(如：娜仁图亚)\n1 获取其他信息(如：娜仁图亚的信物)\n2 公招查询")
    print("-" * 30)

    try:
        lei_xing = int(input("查找类型："))
        if lei_xing == 0:
            await ganyuan_info.main()
        elif lei_xing == 1:
            await qita_info.main()
            print("未找到该物品的信息。")
        elif lei_xing == 2:
            await gongzhao_model.main()
        else:
            print("输入的功能选项无效。")

    except ValueError:
        print("请输入有效数字作为查找类型。")
    except Exception as e:
        print(f"发生了一个错误: {e}")


if __name__ == "__main__":
    # 使用 asyncio.run() 来运行主异步函数
    asyncio.run(main())
