# ark\_info\_search

个人获取明日方舟 PRTS WIKI 信息的尝试，使用原生的 Media API 调用，目的给astrbot添加明日方舟信息查询功能

## 功能简介
从明日方舟 PRTS Wiki 查询信息 ([PRTS WIKI][2])
使用原生的 Media API 进行调用 ([PRTS WIKI API页面][3])

## 项目结构

| 文件／模块             | 作用                      |
| ----------------- |-------------------------|
| `search_model.py` | 负责核心信息获取，将请求发送到 Media API |
| `ganyuan_info.py` | 干员信息查询模块                |
| `qita_info.py`    | 非干员的信息查询模块（待完善）         |
| `__init__.py`     | 主程序                     |

## 依赖项
安装依赖：目前仅requests模块需导入
```bash
pip install -r requirements.txt
```

## 贡献

欢迎贡献！ 若你想提交 bug 报告、功能建议或拉取请求，请说明。

[1]: https://github.com/wxgl/ark_info_search "GitHub - wxgl/ark_info_search: 个人获取明日方舟PRTS WIKI信息的尝试，使用原生的Media API调用"
[2]: https://prts.wiki/w/%E9%A6%96%E9%A1%B5 "PRTS WIKI 首页"
[3]: https://prts.wiki/api.php "PRTS WIKI API页面"