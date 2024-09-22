### 使用方法

- 把脚本放在需要备份的文件夹的根目录下

- 建立文件索引&分卷

  ```shell
  python backup_manager.py list --group-size 23
  ```

- 查看分卷信息

  ```shell
  python backup_manager.py view
  ```

  ```shell
  Group 1: 15570 files, Total size: 23.00 GB
  Group 2: 4275 files, Total size: 22.83 GB
  Group 3: 7517 files, Total size: 23.00 GB
  Group 4: 8891 files, Total size: 23.00 GB
  Group 5: 4384 files, Total size: 22.61 GB
  Group 6: 122 files, Total size: 22.99 GB
  Group 7: 446 files, Total size: 22.98 GB
  Group 8: 356 files, Total size: 22.99 GB
  Group 9: 247 files, Total size: 22.32 GB
  Group 10: 86 files, Total size: 22.91 GB
  Group 11: 5700 files, Total size: 11.30 GB
  ```

- 设置备份组名称

  ```shell
  python backup_manager.py name "backup_name"
  ```

- 生成备份分卷，以**硬链接**的形式输出

  ```shell
  python backup_manager.py copy <group id>
  ```

### 说明

- 文件分卷索引和备份名称存放在./.file_info文件夹中
- 生成的备份分卷位于./.backup_files文件夹中