import time, json, re, logging, httpx, os
from collections import namedtuple
from bs4 import BeautifulSoup
import search_model

# 定义敌人信息的命名元组
EnemyInfo = namedtuple('EnemyInfo', [
    'image_url', 'name', 'race', 'level', 'describe', 'attack_type', 'damage_type', 'motion', 'endure', 'attack',
    'defence', 'move_speed', 'attack_speed', 'resistance', 'enemy_damage_res', 'ability'])

# 定义关卡信息的命名元组
StageInfo = namedtuple('StageInfo', ['image_url', 'stage_name', 'wikitext'])  # 待完善

# 定义关卡下怪物信息的命名元组
StageEnemyInfo = namedtuple('StageEnemyInfo', [
    'image_url', 'enemy_name', 'enemy_number', 'status', 'level', 'endure', 'attack', 'defence', 'resistance',
    'attack_speed', 'weight', 'move_speed', 'attack_range'])

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定时刷新相关变量
enemy_data = []  # 只存储敌人名称列表
last_update_time = 0
UPDATE_INTERVAL = 300  # 5分钟更新一次

# 图片输出控制变量
stage_image = False
enemy_image = False

# 确保data目录存在
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
ENEMY_DATA_FILE = os.path.join(DATA_DIR, 'enemy_data.json')

# 创建data目录（如果不存在）
os.makedirs(DATA_DIR, exist_ok=True)

# 预编译正则表达式以提高性能
JSON_PATTERN = re.compile(r'\{[^{}]*(?:\{[^{}]*}[^{}]*)*}')
STAGE_IMAGE_ID_PATTERN = re.compile(r"关卡id\s*=\s*([^|\n]+)")
COMMON_PATTERN = re.compile(r"\{\{敌人信息/common2\s*\|(.*?)}}", re.DOTALL)
LEVEL_PATTERN = re.compile(r"\{\{敌人信息/levelcontent\s*\|(.*?index=0.*?)}}", re.DOTALL)

# 预编译敌人信息字段正则表达式
ENEMY_FIELDS_PATTERNS = {
    'name': re.compile(r"[|]名称\s*=\s*([^\n|}]+)"),
    'enemy_race': re.compile(r"[|]种类\s*=\s*([^\n|}]+)"),
    'level': re.compile(r"[|]地位级别\s*=\s*([^\n|}]+)"),
    'attack_type': re.compile(r"[|]攻击方式\s*=\s*([^\n|}]+)"),
    'damage_type': re.compile(r"[|]伤害类型\s*=\s*([^\n|}]+)"),
    'motion': re.compile(r"[|]行动方式\s*=\s*([^\n|}]+)"),
    'describe': re.compile(r"[|]描述\s*=\s*([^\n|}]+)"),
    'ability': re.compile(r"[|]能力\s*=\s*([^\n|}]+)"),
    'endure': re.compile(r"[|]最大生命值\s*=\s*([^\n|}]+)"),
    'attack': re.compile(r"[|]攻击力\s*=\s*([^\n|}]+)"),
    'defence': re.compile(r"[|]防御力\s*=\s*([^\n|}]+)"),
    'move_speed': re.compile(r"[|]移动速度\s*=\s*([^\n|}]+)"),
    'attack_speed': re.compile(r"[|]攻击速度\s*=\s*([^\n|}]+)"),
    'resistance': re.compile(r"[|]法术抗性\s*=\s*([^\n|}]+)")
}

# 预编译wikitext清理正则表达式
COLOR_PATTERN = re.compile(r'\{\{color\|#[0-9A-F]{6}\|(.*?)}}')
LINK_PATTERN_1 = re.compile(r'\[\[([^]|]+)\|([^]]+)]]')
LINK_PATTERN_2 = re.compile(r'\[\[([^]]+)]]')
BOLD_ITALIC_PATTERN = re.compile(r"''+(.*?)''+")


def clean_wikitext(text):
    """清理wikitext中的标记，提取纯文本内容（同步版本）"""
    if not text:
        return ""  # 返回空字符串而不是None

    # 移除颜色标记
    text = COLOR_PATTERN.sub(r'\1', text)

    # 移除其他常见的wikitext标记
    text = LINK_PATTERN_1.sub(r'\2', text)  # [[链接|显示文字]] -> 显示文字
    text = LINK_PATTERN_2.sub(r'\1', text)  # [[链接]] -> 链接
    text = BOLD_ITALIC_PATTERN.sub(r'\1', text)  # 移除粗体和斜体标记
    text = text.replace('*', '')
    return text.strip()


async def update_enemy_data(force_update=False):
    """定时更新敌人名称数据"""
    global enemy_data, last_update_time
    current_time = time.time()
    # 如果不是强制更新，检查是否需要更新数据
    if not force_update and current_time - last_update_time <= UPDATE_INTERVAL:
        return False  # 返回False表示未执行更新
    try:
        name_out, wikitext = await search_model.get_wikitext("敌人一览/数据")
        if wikitext:
            # 解析wikitext，只提取敌人名称
            enemy_names = []
            json_matches = JSON_PATTERN.findall(wikitext)
            for json_str in json_matches:
                try:
                    enemy = json.loads(json_str)
                    # 提取敌人名称
                    if 'name' in enemy:
                        enemy_names.append(enemy['name'])
                except json.JSONDecodeError:
                    logger.error(f"JSON解析错误: {json_str}")
            enemy_data = enemy_names
            last_update_time = current_time
            # 将数据写入data文件夹下的enemy_data.json文件
            with open(ENEMY_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'enemy_data': enemy_data,
                    'last_update_time': last_update_time
                }, f, ensure_ascii=False, indent=2)
            logger.info(f"已更新敌人数据，共获取到 {len(enemy_data)} 个敌人")
            return True  # 返回True表示成功执行更新
        return False  # 返回False表示未成功执行更新
    except Exception as e:
        logger.error(f"更新敌人数据失败: {e}")
        return False  # 返回False表示更新失败


async def load_enemy_data():
    """从data文件夹下的enemy_data.json文件加载敌人数据"""
    global enemy_data, last_update_time
    try:
        # 先尝试从文件加载数据
        with open(ENEMY_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            enemy_data = data.get('enemy_data', [])  # 只加载敌人名称列表
            last_update_time = data.get('last_update_time', 0)
        # 检查数据是否需要更新
        await update_enemy_data()  # 尝试更新，但不会每次都强制更新
        logger.info(f"已加载敌人数据，共 {len(enemy_data)} 个敌人")
    except FileNotFoundError:
        logger.info("未找到敌人数据文件，将创建新文件")
        # 如果文件不存在，强制更新数据
        updated = await update_enemy_data(force_update=True)
        if updated:
            logger.info("已创建并初始化敌人数据文件")
    except Exception as e:
        logger.error(f"加载敌人数据失败: {e}")
    return enemy_data


async def find_exact_enemy_name(input_name):
    """在本地敌人数据中查找完全匹配的敌人名称"""
    global enemy_data
    if not enemy_data:
        await load_enemy_data()
    # 首先尝试精确匹配
    if input_name in enemy_data:
        return input_name
    # 如果没有精确匹配，尝试清理输入名称后匹配
    cleaned_input = re.sub(r'[^\u4e00-\u9fff\w]', '', input_name)
    cleaned_enemy = [re.sub(r'[^\u4e00-\u9fff\w]', '', enemy_name) for enemy_name in enemy_data]
    # 使用enumerate避免重复查找索引
    for i, r in enumerate(cleaned_enemy):
        if r == cleaned_input:
            return enemy_data[i]
    # 若未找到精确匹配，则选取包含该字段的最短项
    matching_items = []
    for i, r in enumerate(cleaned_enemy):
        if cleaned_input in r:
            matching_items.append((len(r), enemy_data[i]))
    # 如果有包含该字段的项，返回其中最短的
    if matching_items:
        matching_items.sort(key=lambda x: x[0])  # 按长度排序
        shortest_item = matching_items[0][1]
        print(f"未找到精确匹配项，使用包含该字段的最短项: {shortest_item}")
        return shortest_item
    return input_name


async def get_enemy_image(name: str):
    """异步获取敌人的image"""
    name = f"文件:头像 敌人 {name}.png"
    return await search_model.get_images_url([name])


async def get_enemy_info(enemy_name: str):
    """获取敌人信息和图片"""
    try:
        # 在本地查找精确匹配的敌人名称
        exact_enemy_name = await find_exact_enemy_name(enemy_name)
        if not exact_enemy_name:
            return print(f"未找到敌人: {enemy_name}")
        # 通过get_wikitext获取敌人详细信息
        name_out, wikitext = await search_model.get_wikitext(exact_enemy_name)
        if not wikitext:
            return None
        # 使用正则表达式从wikitext中提取敌人信息
        # 提取基础信息 (common2模板)
        common_match = COMMON_PATTERN.search(wikitext)
        # 提取等级信息 (levelcontent模板)
        level_match = LEVEL_PATTERN.search(wikitext)
        # 初始化字段
        name = exact_enemy_name
        enemy_race = ""
        level = ""
        describe = ""
        attack_type = ""
        damage_type = ""
        motion = ""
        ability = ""
        endure = ""
        attack = ""
        defence = ""
        move_speed = ""
        attack_speed = ""
        resistance = ""
        enemy_damage_res = ""

        # 解析common2模板中的信息
        if common_match:
            common_content = common_match.group(1)
            # 提取各种字段
            fields_map = {
                'name': 'name',
                'enemy_race': 'enemy_race',
                'level': 'level',
                'attack_type': 'attack_type',
                'damage_type': 'damage_type',
                'motion': 'motion',
                'describe': 'describe'
            }
            for field_key, var_name in fields_map.items():
                pattern = ENEMY_FIELDS_PATTERNS[field_key]
                match = pattern.search(common_content)
                if match:
                    value = clean_wikitext(match.group(1).strip())
                    if var_name == 'name':
                        name = value
                    elif var_name == 'enemy_race':
                        if value == '':
                            enemy_race = '无'
                        else:
                            enemy_race = value
                    elif var_name == 'level':
                        level = value
                    elif var_name == 'attack_type':
                        attack_type = value
                    elif var_name == 'damage_type':
                        damage_type = value
                    elif var_name == 'motion':
                        motion = value
                    elif var_name == 'describe':
                        describe = value

        # 解析levelcontent模板中的信息
        if level_match:
            level_content = level_match.group(1)
            # 提取数值字段
            fields_map = {
                'endure': 'endure',
                'attack': 'attack',
                'defence': 'defence',
                'move_speed': 'move_speed',
                'attack_speed': 'attack_speed',
                'resistance': 'resistance'
            }
            for field_key, var_name in fields_map.items():
                pattern = ENEMY_FIELDS_PATTERNS[field_key]
                match = pattern.search(level_content)
                if match:
                    value = match.group(1).strip()
                    if var_name == 'endure':
                        endure = value
                    elif var_name == 'attack':
                        attack = value
                    elif var_name == 'defence':
                        defence = value
                    elif var_name == 'move_speed':
                        move_speed = value
                    elif var_name == 'attack_speed':
                        attack_speed = value
                    elif var_name == 'resistance':
                        resistance = value

        image_url = await get_enemy_image(exact_enemy_name)
        return EnemyInfo(
            image_url=image_url,
            name=name,
            race=enemy_race,
            level=level,
            describe=describe,
            attack_type=attack_type,
            damage_type=damage_type,
            motion=motion,
            endure=endure,
            attack=attack,
            defence=defence,
            move_speed=move_speed,
            attack_speed=attack_speed,
            resistance=resistance,
            enemy_damage_res=enemy_damage_res,
            ability=ability
        )
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error(f"获取敌人信息失败: {e}")
        return None
    except Exception as e:
        logger.error(f"解析敌人信息失败: {e}")
        return None


async def enemy_info_out(enemy_info):
    """输出敌人信息"""
    if enemy_info and isinstance(enemy_info, EnemyInfo):
        # 显示敌人信息
        print(f"图片链接: {enemy_info.image_url}")
        print(f"敌人名称: {enemy_info.name}")
        print(f"种族: {enemy_info.race}")
        print(f"地位级别: {enemy_info.level}")
        print(f"描述: {enemy_info.describe}")
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
        name_out, wikitext = await search_model.get_wikitext(stage_name)
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


async def get_enemy_in_stage(stage_name: str):
    """获取关卡下敌人的信息，不使用get_enemy_info，单开一个"""
    try:
        stage_name = ''.join(char.upper() if char.isalpha() and ord(char) < 128 else char for char in stage_name)
        # 获取页面html
        url = "https://prts.wiki/api.php"
        params = {
            "action": "parse",
            "page": stage_name,
            "format": "json",
            "prop": "text",
            "redirects": 1
        }
        resp = await search_model.http_client.get(url, params=params)
        resp.raise_for_status()
        html_data = resp.json()["parse"]["text"]["*"]
        # 解析页面html
        soup = BeautifulSoup(html_data, "html.parser")
        enemies = []
        enemy_names = []  # 收集所有敌人名称
        enemy_data_list = []  # 临时存储敌人数据

        # PRTS敌人信息基本都在<tr>里
        for tr in soup.find_all("tr"):
            # 查找敌人图标
            icon_div = tr.find("div", class_="enemyicon") # 仅做判断是否为敌人行
            if not icon_div:
                continue  # 跳过非敌人行
            # 敌人名称（在a标签title里）
            name_a = tr.find("a", title=True)
            enemy_name = name_a["title"] if name_a else None
            if enemy_name:
                enemy_names.append(enemy_name)
                # 剩下的td为属性值
                tds = tr.find_all("td")
                # 第一个td是名字旁边的div，跳过
                stats = [td.get_text(strip=True) for td in tds[2:]]  # 从第3个td开始才是数值
                # 临时存储敌人数据
                enemy_data_list.append({
                    "name": enemy_name,
                    "stats": stats
                })
        enemy_images = {}
        if enemy_image:
        # 并发获取所有敌人头像URL
            if enemy_names:
                image_names = [f"文件:头像 敌人 {name}.png" for name in enemy_names]
                image_urls = await search_model.get_images_url(image_names)
                for i, name in enumerate(enemy_names):
                    if i < len(image_urls):
                        enemy_images[name] = image_urls[i]
        # 组合敌人信息，有头像
            for enemy_data in enemy_data_list:
                enemy_name = enemy_data["name"]
                enemies.append({
                    "name": enemy_name,
                    "icon_url": enemy_images.get(enemy_name, None),
                    "stats": enemy_data["stats"]
                })
        else:
        # 组合敌人信息，无头像
            for enemy_data in enemy_data_list:
                enemy_name = enemy_data["name"]
                enemies.append({
                    "name": enemy_name,
                    "stats": enemy_data["stats"]
                })
        return enemies
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error(f"获取关卡 {stage_name} 信息失败: {e}")
        return []
    except KeyError as e:
        logger.error(f"解析关卡 {stage_name} 数据时出错，缺少键值: {e}")
        return []
    except Exception as e:
        logger.error(f"获取关卡 {stage_name} 信息时发生未知错误: {e}")
        return []


async def all_enemy_and_stage_info_out(enemies, stageinfo):
    """输出关卡下所有敌人的信息"""
    stats_labels = ["数量", "地位", "等级", "生命值", "攻击力", "防御力", "法术抗性", "攻击间隔", "重量", "移动速度",
                    "攻击范围", "目标价值"]
    if stageinfo and isinstance(stageinfo, StageInfo):
        print(f"关卡: {stageinfo.stage_name}")
        if stage_image:
            print(f"地图: {stageinfo.image_url}")
        else:
            print(f"是否输出地图：{stage_image}")
        print(f"关卡描述: {stageinfo.wikitext}")
        if enemy_image:
            for e in enemies:
                print("敌人：", e["name"])
                print("头像：", e["icon_url"])
                for i, stat in enumerate(e["stats"]):
                    if i < len(stats_labels):
                        print(f"  {stats_labels[i]}: {stat}")
                    else:
                        print(f"未知属性{i}: {stat}")
                print("-" * 30)
        else:
            for e in enemies:
                print("敌人：", e["name"])
                for i, stat in enumerate(e["stats"]):
                    if i < len(stats_labels):
                        print(f"  {stats_labels[i]}: {stat}")
                    else:
                        print(f"未知属性{i}: {stat}")
                print("-" * 30)


async def once_enemy_and_stage_info_out(enemies, enemy_name, stageinfo):
    """输出关卡下单个敌人的信息"""
    stats_labels = ["数量", "地位", "等级", "生命值", "攻击力", "防御力", "法术抗性", "攻击间隔", "重量", "移动速度",
                    "攻击范围", "目标价值"]
    if stageinfo and isinstance(stageinfo, StageInfo):
        print(f"关卡: {stageinfo.stage_name}")
        if enemy_image:
            for e in enemies:
                print("敌人：", e["name"])
                print("头像：", e["icon_url"])
                for i, stat in enumerate(e["stats"]):
                    if i < len(stats_labels):
                        print(f"  {stats_labels[i]}: {stat}")
                    else:
                        print(f"未知属性{i}: {stat}")
                print("-" * 30)
        elif not enemy_image:
            for e in enemies:
                print("敌人：", e["name"])
                for i, stat in enumerate(e["stats"]):
                    if i < len(stats_labels):
                        print(f"  {stats_labels[i]}: {stat}")
                    else:
                        print(f"未知属性{i}: {stat}")
                print("-" * 30)
        else:
            print(f"该关卡未找到{enemy_name}敌人信息")


async def main(config, text1=None, text2=None):
    """主函数，负责用户交互和数据处理"""
    print("-" * 30)
    print("敌人名称（如: 源石虫）或关卡名称（如: SS-8，3-3）")
    print("或均输入，查询关卡下改名敌人数值（空格，中英文逗号分隔）")
    print("-" * 30)
    query_text = input("请输入要查询的敌人或关卡名称: ").strip()
    # 只在需要时加载敌人数据
    if not enemy_data:
        await load_enemy_data()
    enemy_name_data = enemy_data
    global stage_image, enemy_image  # 声明图片设置为全局变量
    stage_image = config["image"]["stage_image_output"]
    enemy_image = config["image"]["enemy_image_output"]
    # 根据输入的空格或中英文逗号切分并赋值
    if query_text:
        # 使用正则表达式按空格或中英文逗号分割输入
        parts = re.split(r'[\s,，]+', query_text)
        if len(parts) >= 1:
            text1 = parts[0]
        if len(parts) >= 2:
            text2 = parts[1]
    if text1 and not text2:
        # 单个参数查询
        text1 = await find_exact_enemy_name(text1)
        if text1 in enemy_name_data:
            enemy_info = await get_enemy_info(text1)
            if enemy_info:
                await enemy_info_out(enemy_info)
            else:
                print(f"未找到敌人: {text1}")
        else:
            stage_info = await get_stage_info(text1)
            if stage_info:
                # 获取关卡中的敌人信息
                enemies = await get_enemy_in_stage(text1)
                await all_enemy_and_stage_info_out(enemies, stage_info)
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
        stageinfo = await get_stage_info(stage_name)
        if stageinfo:
            enemies = await get_enemy_in_stage(enemy_name)
            await once_enemy_and_stage_info_out(enemies, enemy_name, stageinfo)
        else:
            print(f"未找到关卡 {stage_name} 的信息")
    else:
        print("请输入有效的查询参数")
    return None
