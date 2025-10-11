# 桌面灵宠 Desktop Pet Assistant

一款集互动娱乐与日程管理于一体的桌面宠物应用 🐱

**当前版本**：v0.4.0（智能成长版）🚀  
**更新日期**：2025-10-11  
**状态**：✅ 稳定可用 + AI智能加持

## ✨ 功能特性

### 核心功能
- 🎮 **可爱的桌面宠物** - 在桌面上自由活动的萌宠，支持**成长和进化** ✨新
- 🖱️ **丰富的互动** - 点击、拖拽、喂食、玩耍等多种互动方式
- 📝 **待办事项管理** - 完整的任务增删改查功能，支持标签分类
- ⏰ **智能提醒** - 宠物会在任务到期时提醒你，带有音效提示
- 🍅 **番茄钟系统** - 完整的番茄工作法，提升专注力 ✨新
- 🤖 **AI对话系统** - 与宠物智能对话，获得建议和陪伴 ✨新
- 📸 **图片识别** - 拖放图片自动生成待办任务 ✨创新
- 🏆 **成长系统** - 经验、等级、进化、成就、道具 ✨新
- 🐾 **多宠物** - 收集和管理多只宠物 ✨新
- 📊 **数据统计** - 查看任务完成情况和数据分析
- 🎨 **主题切换** - 支持浅色/暗色主题，保护眼睛

### v0.4.0 重大更新 🎉
- 🍅 **番茄钟完整版** - 计时器、桌面小组件、专注模式、统计报表
- 🐱 **宠物成长完整版** - 经验/等级/属性/进化系统，30+成就，14种道具
- 🤖 **AI对话API版** - OpenAI集成，3种性格，智能建议，对话记忆
- 🐾 **多宠物完整版** - 最多5只宠物，独立成长，宠物商店，积分系统
- 📸 **图片识别生成待办** - AI视觉识别，拖放即用，自动生成任务

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows 10/11 (目前主要支持Windows平台)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/desktop-pet.git
cd desktop-pet
```

2. **创建虚拟环境** (推荐)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行程序**
```bash
python main.py
```

## 📁 项目结构

```
desktop-pet/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖包
├── config.ini             # 配置文件
├── README.md              # 本文件
├── 开发需求文档.md         # 详细的需求文档
│
├── src/                   # 源代码
│   ├── __init__.py
│   ├── pet_window.py      # 宠物窗口
│   ├── todo_window.py     # 待办窗口
│   ├── settings_window.py # 设置窗口
│   ├── database.py        # 数据库操作
│   ├── reminder.py        # 提醒系统
│   └── utils.py           # 工具函数
│
├── assets/                # 资源文件
│   ├── images/            # 图片资源
│   ├── sounds/            # 音效文件
│   └── icons/             # 图标
│
└── tests/                 # 测试文件
```

## 🎯 使用说明

### 基础操作

- **拖动宠物**: 用鼠标左键拖动宠物到任意位置
- **互动**: 单击宠物触发互动动画
- **菜单**: 右键点击宠物打开功能菜单
- **隐藏/显示**: 使用系统托盘图标控制显示

### 待办事项

1. 右键点击宠物选择"待办事项"
2. 点击"添加任务"按钮创建新任务
3. 设置任务名称、截止时间和优先级
4. 宠物会在任务到期时提醒你

### 设置选项

- 更换宠物皮肤
- 调整动画和移动速度
- 设置提醒方式和音效
- 配置开机自启动

## 🛠️ 技术栈

- **GUI框架**: PyQt5
- **数据库**: SQLite3
- **语言**: Python 3.8+

## 📚 完整文档

**所有详细文档已整理到 `docs/` 目录** 📁

### 快速导航
- 💡 [START_HERE.md](START_HERE.md) - 3步快速开始
- 📌 [docs/需求实现文档.md](docs/需求实现文档.md) - **活文档**，所有实现细节
- 📖 [docs/使用指南_v0.2.md](docs/使用指南_v0.2.md) - v0.2.0 使用手册
- 📦 [docs/打包说明.md](docs/打包说明.md) - 打包发布指南
- 🎨 [docs/设计需求清单.md](docs/设计需求清单.md) - 设计规范
- 🔧 [docs/优化建议清单.md](docs/优化建议清单.md) - 44个优化点

**文档索引**：[docs/README.md](docs/README.md) - 文档中心，包含全部20个文档

---

## 📚 参考项目

本项目参考了以下优秀的开源项目：

- [DyberPet](https://github.com/ChaozhongLiu/DyberPet) - PySide6桌面宠物框架
- [Pet-GPT](https://github.com/Hanzoe/Pet-GPT) - 集成GPT的桌面宠物
- [Desktop-Pet](https://github.com/cgy2003/desktop-pet) - Python桌面宠物

## 📝 开发计划

- [x] 创建项目结构
- [x] 编写需求文档
- [ ] 实现基础窗口框架
- [ ] 添加宠物动画
- [ ] 开发待办功能
- [ ] 实现提醒系统
- [ ] 完善设置选项
- [ ] 测试和优化

详细的开发计划请查看 [开发需求文档.md](./开发需求文档.md)

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📧 联系方式

- 项目地址: [GitHub](https://github.com/yourusername/desktop-pet)
- 问题反馈: [Issues](https://github.com/yourusername/desktop-pet/issues)

## 🙏 致谢

感谢所有为桌面宠物开源项目做出贡献的开发者们！

---

⭐ 如果这个项目对你有帮助，欢迎给个 Star！

