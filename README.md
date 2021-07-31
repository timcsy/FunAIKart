# GameAIKartDraft

在 Kart 根目錄新增一個 .gitignore 檔案
```
**/*
!.gitignore
!Assets
Assets/**/*
!Assets/Karting
Assets/Karting/**/*
!Assets/Karting/Scripts
!Assets/Karting/Scripts/**/*
!README.md
.DS_Store
```

開始一個 Git
```
git init
```

變更 git branch 的名字變成 main（原本是 master 的話）
```
可以用 VS Code 操作
```

```
git remote add github https://github.com/timcsy/GameAIKartDraft.git
```

第一次 pull 才要
```
git pull github main --allow-unrelated-histories
```

