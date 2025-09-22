import asyncio
import json
import re
import logging
from collections import namedtuple
import httpx
import os
from . import search_model

# 定义敌人信息的命名元组
EnemyInfo = namedtuple('EnemyInfo', [
    'image_url', 'name', 'race', 'level', 'attack_type', 'damage_type',
    'motion', 'endure', 'attack', 'defence', 'move_speed', 'attack_speed',
    'resistance', 'enemy_res', 'enemy_damage_res', 'ability'])

# 定义关卡信息的命名元组
StageInfo = namedtuple('StageInfo', [
    'image_url', 'stage_name', 'wikitext'])  # 待完善

# 定义关卡下怪物信息的命名元组
StageEnemyInfo = namedtuple('StageEnemyInfo', [
    'image_url', 'stage_name', 'enemy_name', 'level_data'])  # 待完善

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定时刷新相关变量
enemy_data = {}
last_update_time = 0
UPDATE_INTERVAL = 300  # 5分钟更新一次

# 确保data目录存在
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
ENEMY_DATA_FILE = os.path.join(DATA_DIR, 'enemy_data.json')

# 创建data目录（如果不存在）
os.makedirs(DATA_DIR, exist_ok=True)

# 预编译正则表达式以提高性能
JSON_PATTERN = re.compile(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}')
STAGE_IMAGE_ID_PATTERN = re.compile(r"关卡id\s*=\s*([^|\n]+)")

async def update_enemy_data():
    """定时更新敌人名称数据"""
    global enemy_data, last_update_time
    current_time = asyncio.get_event_loop().time()
    await load_enemy_data()

    # 检查是否需要更新数据
    if current_time - last_update_time > UPDATE_INTERVAL:
        try:
            name_out, wikitext = await search_model.get_wikitext("敌人一览/数据")
            if wikitext:
                # 解析wikitext
                enemy_data = wikitext
                last_update_time = current_time
                # 将数据写入data文件夹下的enemy_data.json文件
                with open(ENEMY_DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump({
                        'enemy_data.json': enemy_data,
                        'last_update_time': last_update_time
                    }, f, ensure_ascii=False, indent=2)
                logger.info(f"已更新敌人数据")
        except Exception as e:
            logger.error(f"更新敌人数据失败: {e}")


async def load_enemy_data():
    """从data文件夹下的enemy_data.json文件加载敌人数据"""
    global enemy_data, last_update_time
    try:
        with open(ENEMY_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            enemy_data = data.get('enemy_data.json', '')  # 修复键名错误
            last_update_time = data.get('last_update_time', 0)
        logger.info(f"已从文件加载敌人数据，共 {len(enemy_data)} 个敌人")
    except FileNotFoundError:
        logger.info("未找到敌人数据文件，将创建新文件")
    except Exception as e:
        logger.error(f"加载敌人数据失败: {e}")
    return enemy_data


async def get_enemy_image(name: str):
    """异步获取敌人的image"""
    name = f"文件:头像 敌人 {name}.png"
    return await search_model.get_images_url([name])


async def get_enemy_info(enemy_name: str):
    """获取敌人信息和图片"""
    await update_enemy_data()
    try:
        image_url = await get_enemy_image(enemy_name)
        # 查找匹配的敌人
        # 从enemy_data中查找符合enemy_name的数据
        if enemy_data:
            # 使用正则表达式提取所有JSON对象
            json_matches = JSON_PATTERN.findall(enemy_data)
            for json_str in json_matches:
                try:
                    enemy = json.loads(json_str)
                    # 检查是否包含name字段且与enemy_name匹配
                    if enemy.get('name') == enemy_name:
                        return EnemyInfo(
                            image_url=image_url,
                            name=enemy.get('name', ''),
                            race=enemy.get('enemyRace', ''),
                            level=enemy.get('enemyLevel', ''),
                            attack_type=enemy.get('attackType', ''),
                            damage_type=enemy.get('damageType', ''),
                            motion=enemy.get('motion', ''),
                            endure=enemy.get('endure', ''),
                            attack=enemy.get('attack', ''),
                            defence=enemy.get('defence', ''),
                            move_speed=enemy.get('moveSpeed', ''),
                            attack_speed=enemy.get('attackSpeed', ''),
                            resistance=enemy.get('resistance', ''),
                            enemy_res=enemy.get('enemyRes', ''),
                            enemy_damage_res=enemy.get('enemyDamageRes', ''),
                            ability=enemy.get('ability', '')
                        )
                except json.JSONDecodeError:
                    logger.error(f"JSON解析错误: {json_str}")
        return None
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error(f"获取敌人信息失败: {e}")
        return None


async def enemy_info_out(enemy_info):
    """输出敌人信息"""
    if enemy_info and isinstance(enemy_info, EnemyInfo):
        # 显示敌人信息
        print(f"图片链接: {enemy_info.image_url}")
        print(f"敌人名称: {enemy_info.name}")
        print(f"种族: {enemy_info.race}")
        print(f"等级: {enemy_info.level}")
        print(f"攻击方式: {enemy_info.attack_type}")
        print(f"伤害类型: {enemy_info.damage_type}")
        print(f"移动方式: {enemy_info.motion}")
        print(f"生命值: {enemy_info.endure}")
        print(f"攻击力: {enemy_info.attack}")
        print(f"防御力: {enemy_info.defence}")
        print(f"移动速度: {enemy_info.move_speed}")
        print(f"攻击速度: {enemy_info.attack_speed}")
        print(f"法术抗性: {enemy_info.resistance}")
        if enemy_info.ability:
            print(f"能力: {enemy_info.ability}")


async def get_stage_image(wikitext: str):
    """获取关卡地图缩略图"""
    match = STAGE_IMAGE_ID_PATTERN.search(wikitext)
    if match:
        stage_image_id = match.group(1)
        return f"https://torappu.prts.wiki/assets/map_preview/{stage_image_id}.png"
    return ""


async def get_stage_info(stage_name: str):
    """获取关卡信息和图片"""
    try:
        stage_name = ''.join(char.upper() if char.isalpha() and ord(char) < 128 else char for char in stage_name)
        url = "https://prts.wiki/api.php"
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": stage_name,
            "rvprop": "content",
            "format": "json",
            "redirects": ""
        }
        response = await search_model.http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        pages = data["query"]["pages"]
        # 获取第一个页面的信息，因为API返回的page id是动态的
        page_id = next(iter(pages))
        page_data = pages[page_id]

        name_out = page_data["title"]
        # 检查页面是否存在或是否包含修订版本
        if "revisions" not in page_data or not page_data["revisions"]:
            # 页面不存在或没有修订版本，返回None
            wikitext = None
        else:
            wikitext = page_data["revisions"][0]["*"]
        
        if wikitext:
            image_url = await get_stage_image(wikitext)
            return StageInfo(
                image_url=image_url,
                stage_name=name_out,
                wikitext=wikitext
            )
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error(f"获取关卡信息失败: {e}")
        return None


async def stage_info_out(stage_info):
    """输出关卡信息"""
    if stage_info and isinstance(stage_info, StageInfo):
        # 显示关卡信息
        print(f"图片链接: {stage_info.image_url}")
        print(f"关卡名称: {stage_info.stage_name}")


async def get_enemy_and_stage(enemy_name: str, stage_name: str):
    """获取关卡下敌人的信息"""
    stage_info = await get_stage_info(stage_name)
    if stage_info:
        # 这里可以进一步解析关卡中的敌人配置信息
        return StageEnemyInfo(
            image_url=stage_info.image_url,
            stage_name=stage_info.stage_name,
            enemy_name=enemy_name,
            level_data=""  # 待实现详细数据提取
        )
    return None


async def enemy_and_stage_info_out(result):
    """输出关卡下敌人的信息"""
    if result and isinstance(result, StageEnemyInfo):
        print(f"关卡: {result.stage_name}")
        print(f"敌人: {result.enemy_name}")
        print(f"等级数据: {result.level_data if result.level_data else '暂无详细数据'}")


async def main(text1 = None, text2 = None):
    """主函数，负责用户交互和数据处理"""
    print("PRTS敌人和关卡信息查询系统")
    print("-" * 30)
    print("输入敌人名称（如: 源石虫）查询敌人信息")
    print("输入关卡名称（如: 1-7）查询关卡敌人配置")
    print("-" * 30)
    await update_enemy_data()
    # 正确解析enemy_data中的敌人名称
    enemy_name_data = []
    if enemy_data:
        # 使用正则表达式提取所有JSON对象
        json_matches = JSON_PATTERN.findall(enemy_data)
        
        for json_str in json_matches:
            try:
                enemy = json.loads(json_str)
                # 提取敌人名称
                if 'name' in enemy:
                    enemy_name_data.append(enemy['name'])
            except json.JSONDecodeError:
                logger.error(f"JSON解析错误: {json_str}")
    # 根据输入的空格或中英文逗号切分并赋值
    query_text = input("请输入要查询的敌人或关卡名称: ").strip()
    if query_text:
        # 使用正则表达式按空格或中英文逗号分割输入
        parts = re.split(r'[\s,，]+', query_text)
        if len(parts) >= 1:
            text1 = parts[0]
        if len(parts) >= 2:
            text2 = parts[1]
    
    if text1 and not text2:
        # 单个参数查询
        if text1 in enemy_name_data:
            enemy_info = await get_enemy_info(text1)
            if enemy_info:
                await enemy_info_out(enemy_info)
            else:
                print(f"未找到敌人: {text1}")
        else:
            stage_info = await get_stage_info(text1)
            if stage_info:
                await stage_info_out(stage_info)
            else:
                print(f"未找到关卡: {text1}")
    elif text1 and text2:
        # 两个参数查询
        if text2 in enemy_name_data:
            enemy_name = text2
            stage_name = text1
        else:
            enemy_name = text1
            stage_name = text2
            
        result = await get_enemy_and_stage(enemy_name, stage_name)
        if result:
            await enemy_and_stage_info_out(result)
        else:
            print(f"未找到关卡 {stage_name} 或敌人 {enemy_name} 的信息")
    else:
        print("请输入有效的查询参数")
    return None
