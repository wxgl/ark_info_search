import asyncio, yaml # , logging
import ganyuan, other_thing, gongzhao_model, stage_enemy, search_model

# 配置日志
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

def load_yaml_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    print("已加载配置文件")
    return config


async def main():
    """
    程序的主异步函数
    """
    # logger.info("程序启动") # 用于测试加载速度。使用asyncio更耗时
    config = load_yaml_config('config.yaml')
    print("PRTS信息查询系统")
    print("-" * 30)
    print(f"功能列表："
          f"\n1 获取干员信息(支持时装立绘查询)"
          f"\n   精确：娜仁图亚，模糊：娜仁(需连贯)"
          f"\n2 获取其他信息(如：娜仁图亚的信物)"
          f"\n3 公招查询"
          f"\n4 关卡及敌人查询"
          f"\n图片一般为6MB左右，下载可能有点慢")
    print("-" * 30)

    try:
        lei_xing = int(input("查找类型："))
        if lei_xing == 1:
            ganyuan1 = ganyuan.initialize_ganyuan(config)
            await ganyuan1.run()
        elif lei_xing == 2:
            other_thing1 = other_thing.initialize_other_thing(config)
            await other_thing1.run()
        elif lei_xing == 3:
            gongzhao_model1 = gongzhao_model.initialize_gongzhao_model(config)
            await gongzhao_model1.run()
        elif lei_xing == 4:
            stage_enemy1 = stage_enemy.initialize_stage_enemy(config)
            await stage_enemy1.run()
        else:
            print("输入的功能选项无效。")
    except ValueError:
        print("请输入有效数字作为查找类型。")
    finally:
        # 确保关闭HTTP客户端
        await search_model.search_model.close_http_client()


if __name__ == "__main__":
    # 使用 asyncio.run() 来运行主异步函数
    asyncio.run(main())