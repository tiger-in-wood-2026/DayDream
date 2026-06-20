# DayDream

> 我的个人项目仓库 — 同步于本机 `C:\DayDream` 与 GitHub。

## 用途

这里存放我在本机的开发笔记、代码片段、实验性项目。  
GitHub 作为云端备份 + 跨设备访问 + 协作入口。

## 本机与远端同步约定

```powershell
# 首次配置（只需一次）
git config --global user.name  "tiger-in-wood-2026"
git config --global user.email "你的GitHub注册邮箱"

# 日常三板斧
cd C:\DayDream
git add .
git commit -m "描述这次改了什么"
git push                     # 本地 → GitHub
git pull                     # GitHub → 本地（别人改了或你在网页上改了之后）
```

## 目录约定（待定）

按需创建子目录，建议结构：

```
C:\DayDream\
├── README.md
├── .gitignore
├── notes\        # 学习笔记、随笔
├── snippets\     # 可复用代码片段
├── experiments\  # 一次性实验
└── projects\     # 正式项目
```

## 同步状态

- [x] 本地 git 仓库初始化
- [x] 远端 origin 配置
- [x] 首个 commit 待推送
