# import search_model
import ganyuan_info
import qita_info


print("欢迎使用干员信息查询系统")
print("-" * 30)
print(f"功能列表：\n0 获取干员信息(如：娜仁图亚)\n1 获取其他信息(待完善)(如：娜仁图亚的信物)")
print("-" * 30)

lei_xing = int(input("查找类型："))
if lei_xing == 0:
    ganyuan = input("请输入干员名称：")
    # ganyuan = "娜仁图亚"
    name, zhi_ye, fen_zhi, xing_ji = ganyuan_info.main(ganyuan)
    print(f"干员：{name}")
    print(f"职业：{zhi_ye}")
    print(f"分支：{fen_zhi}")
    print(f"星级：{xing_ji}")
else:
    qita = input("请输入名称：")
    # qita = "娜仁图亚的信物"
    qita_name, miao_shu, yong_tu, huode_fangshi, fen_lei = qita_info.main(qita)
    print(f"名称：{qita_name}")
    print(f"介绍：{miao_shu}")
    print(f"用途：{yong_tu}")
    print(f"获得方式：{huode_fangshi}")
    print(f"分类：{fen_lei}")
