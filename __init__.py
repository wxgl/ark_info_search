import asyncio
import ganyuan_info
import qita_info

async def main():
    """
    程序的主异步函数
    """
    print("欢迎使用干员信息查询系统")
    print("-" * 30)
    print(f"功能列表：\n0 获取干员信息(如：娜仁图亚)\n1 获取其他信息(如：娜仁图亚的信物)")
    print("-" * 30)

    try:
        lei_xing = int(input("查找类型："))
        if lei_xing == 0:
            ganyuan = input("请输入干员名称：")
            # 使用 await 等待异步函数的结果
            result = await ganyuan_info.main(ganyuan)
            if result:
                name, zhi_ye, fen_zhi, xing_ji, te_xing, te_xing_b = result
                print(f"干员：{name}")
                print(f"职业：{zhi_ye}")
                print(f"分支：{fen_zhi}")
                print(f"星级：{xing_ji}")
                print(f"特性：{te_xing}")
                print(f"特性备注：{te_xing_b}")
            else:
                print("未找到该干员的信息。")

        elif lei_xing == 1:
            qita = input("请输入名称：")
            # 使用 await 等待异步函数的结果
            result = await qita_info.main(qita)
            if result:
                qita_name, miao_shu, yong_tu, huode_fangshi, fen_lei = result
                print(f"名称：{qita_name}")
                print(f"介绍：{miao_shu}")
                print(f"用途：{yong_tu}")
                print(f"获得方式：{huode_fangshi}")
                print(f"分类：{fen_lei}")
            else:
                print("未找到该物品的信息。")
        else:
            print("输入的功能选项无效。")

    except ValueError:
        print("请输入有效数字作为查找类型。")
    except Exception as e:
        print(f"发生了一个错误: {e}")

if __name__ == "__main__":
    # 使用 asyncio.run() 来运行主异步函数
    asyncio.run(main())