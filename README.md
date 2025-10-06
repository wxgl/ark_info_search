# ark_info_search

本人为高中生，编写代码的时间并不多，一部分使用AI辅助完成。
个人获取明日方舟 PRTS WIKI 信息的尝试，使用原生的 Media API 调用，目的给astrbot添加明日方舟信息查询功能

## 功能简介

- 从明日方舟 PRTS Wiki 查询信息 ([PRTS WIKI][2])
- 使用原生的 Media API 进行调用 ([PRTS WIKI API页面][3])
- 目前支持图片链接获取：干员立绘，敌人图片，关卡地图

## 项目结构

| 文件／模块                  | 作用                         |
|------------------------|----------------------------|
| `search_model.py`      | 负责大部分信息获取，将请求发送到 Media API |
| `ganyuan.py`           | 干员信息查询模块（目前少量信息可查)         |
| `other_thing.py`       | 非干员的信息查询模块（待完善）            |
| `__main__.py`          | 主程序(使用的是相对导入)              |
| `gongzhao.py`          | 公招信息查询模块                   |
| `stage_enemy.py`       | 关卡怪物数值查询模块                 |
| `data/enemy_data.json` | 怪物存储                       |

## 依赖项

安装依赖：httpx、asyncio、beautifulsoup4

```bash
pip install -r requirements.txt
```

### 
 - [x] config设置（目前仅有图片输出控制）
 - [ ] 材料查询

## 贡献

欢迎贡献！ 若你想提交 bug 报告、功能建议或拉取请求，可以提交issue

[2]: https://prts.wiki/w/%E9%A6%96%E9%A1%B5 "PRTS WIKI 首页"

[3]: https://prts.wiki/api.php "PRTS WIKI API页面"