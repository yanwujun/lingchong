# OpenAI API 配置指南

## 📖 简介

桌面灵宠 v0.4.0 集成了OpenAI的AI功能，包括：
- 💬 **AI对话** - 与宠物智能对话
- 📸 **图片识别** - 识别图片生成待办任务

这些功能需要OpenAI API Key才能使用。本指南将帮助您完成配置。

---

## 🔑 获取API Key

### 步骤1：注册OpenAI账号
1. 访问 https://platform.openai.com/signup
2. 使用邮箱注册账号
3. 验证邮箱

### 步骤2：创建API Key
1. 登录后访问 https://platform.openai.com/api-keys
2. 点击 "Create new secret key"
3. 输入密钥名称（如：Desktop Pet）
4. 点击创建
5. **⚠️ 重要**: 立即复制并保存API Key，页面关闭后无法再次查看

### 步骤3：充值（新用户有免费额度）
1. 访问 https://platform.openai.com/account/billing
2. 新用户通常有$5免费额度
3. 如需更多，可添加信用卡充值

---

## ⚙️ 在应用中配置API Key

### 方法一：通过应用界面（推荐）

1. **启动应用**
   ```bash
   python main.py
   ```

2. **打开AI对话窗口**
   - 右键点击桌面宠物
   - 选择 "💬 AI对话"

3. **打开设置**
   - 点击窗口右上角的 ⚙️ 按钮

4. **输入API Key**
   - 在"API Key"输入框中粘贴您的密钥
   - 选择模型（推荐 gpt-3.5-turbo）
   - 选择宠物性格
   - 点击"保存"

### 方法二：通过配置文件

1. **创建配置文件**
   ```bash
   mkdir config
   ```

2. **编辑配置文件**
   创建 `config/api_keys.json`:
   ```json
   {
     "openai_api_key": "sk-proj-your-api-key-here"
   }
   ```

3. **保存并重启应用**

### 方法三：使用环境变量

**Windows**:
```powershell
# 临时设置（当前会话）
$env:OPENAI_API_KEY="sk-proj-your-api-key-here"
python main.py

# 永久设置
setx OPENAI_API_KEY "sk-proj-your-api-key-here"
```

**Linux/Mac**:
```bash
# 临时设置
export OPENAI_API_KEY="sk-proj-your-api-key-here"
python main.py

# 永久设置（添加到 ~/.bashrc）
echo 'export OPENAI_API_KEY="sk-proj-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## 💰 费用说明

### AI对话
- **GPT-3.5-turbo**: 约 $0.002/对话
- **GPT-4**: 约 $0.03/对话
- **GPT-4-turbo**: 约 $0.01/对话

**建议**: 日常使用GPT-3.5-turbo性价比最高

### 图片识别
- **GPT-4-vision-preview**: 约 $0.01-0.03/图片

**预估月费用**（中度使用）：
- AI对话（每天10次）: $0.60/月
- 图片识别（每天2次）: $0.60/月
- **总计**: 约 $1.2/月

---

## 🧪 测试API Key

### 在应用中测试

1. **测试AI对话**:
   - 打开"💬 AI对话"窗口
   - 输入简单消息："你好"
   - 如果收到回复，说明配置成功！

2. **测试图片识别**:
   - 准备一张包含文字的图片
   - 拖动到桌面宠物上
   - 等待3-5秒
   - 查看识别结果

### 命令行测试

```python
# test_api.py
import openai

openai.api_key = "your-api-key-here"

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("✅ API Key有效！")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"❌ API Key无效或网络错误: {e}")
```

---

## 🔒 安全建议

### API Key安全
1. **不要分享** - 永远不要将API Key分享给他人
2. **不要提交到Git** - `config/api_keys.json`已在.gitignore中
3. **定期更换** - 建议每3个月更换一次
4. **限制权限** - 在OpenAI后台设置使用限额

### 使用限额设置
1. 访问 https://platform.openai.com/account/limits
2. 设置每月使用上限（如$5）
3. 避免意外高额费用

---

## ❓ 常见问题

### Q1: API Key在哪里保存？
**A**: 保存在 `config/api_keys.json` 文件中，本地存储，安全可靠。

### Q2: 可以免费使用吗？
**A**: 新用户有$5免费额度，足够试用。后续需要充值。

### Q3: 不配置API Key可以使用应用吗？
**A**: 可以！只是AI对话和图片识别功能无法使用。其他功能（任务管理、番茄钟、成长系统等）完全正常。

### Q4: API调用失败怎么办？
**A**: 
- 检查网络连接
- 确认API Key正确
- 查看OpenAI账户余额
- 查看错误提示信息

### Q5: 对话很慢怎么办？
**A**:
- 网络问题：检查网络速度
- 模型选择：GPT-3.5比GPT-4快得多
- 高峰时段：避开使用高峰期

### Q6: 识别结果不准确？
**A**:
- 图片质量：使用清晰的图片
- 光线良好：避免模糊、反光
- 文字清晰：手写字迹尽量工整
- 适当裁剪：只保留任务相关内容

---

## 🔧 高级配置

### 自定义模型
编辑 `config/api_keys.json`:
```json
{
  "openai_api_key": "sk-proj-xxx",
  "model": "gpt-4-turbo",
  "max_tokens": 500,
  "temperature": 0.9
}
```

### 使用代理
```python
# 在 src/ai_chat.py 中添加
openai.proxy = "http://your-proxy:port"
```

### 本地模型（进阶）
如不想使用API，可以考虑本地模型：
- Ollama + llama2
- GPT4All
- 需要额外配置，不在本指南范围

---

## 📞 获取帮助

- **OpenAI文档**: https://platform.openai.com/docs
- **API参考**: https://platform.openai.com/docs/api-reference
- **定价页面**: https://openai.com/pricing
- **状态页面**: https://status.openai.com/

---

## ✅ 配置完成检查清单

- [ ] 已注册OpenAI账号
- [ ] 已创建API Key
- [ ] 已在应用中配置API Key
- [ ] 已测试AI对话功能
- [ ] 已测试图片识别功能
- [ ] 已设置使用限额（可选）
- [ ] 已了解费用情况

---

**祝您使用愉快！** 🎉

如有问题，请查看日志文件或联系技术支持。

---

*最后更新: 2025-10-11*  
*版本: v1.0*  
*适用于: 桌面灵宠 v0.4.0+*

