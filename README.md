# Python
### 一键移除有道云笔记广告
```console
.remove_youdaonote_ads.py
```
#


### OpenVPN全自动管理
```console
./openvpn_manager_class.py
```
自动创建或删除openvpn账户（生成随机密码并输出），生成或续期用户证书
#

### 多线程端口扫描（Linux上运行，必须安装nmap工具）
```console
./port_scan/port_scan_muti.py
```
读入log文件（log文件格式示例host_information.log，也可以是逗号隔开），输出一个json格式的端口扫描结果
#

### SVN按路径批量更新
```console
./svn_update/update_code.py
```
按研发给的svn路径，自动批量更新文件，示例路径如svn_path.log中所示
#

### SVN项目部署
```console
./svn_co.py
```
svn部署脚本，一键部署新的负载项目；如果有相同项目文件夹则告警；自动svn checkout代码，同时修改文件权限
#

### 百度云AI识别
```console
./picture_AI_for_Zabbix2.py
```
针对老版本zabbix2.4统计无法导出这种情况，利用了百度云AI图片识别，把zabbix里的数据识别出来
#

## demo代码
### 多线程示例代码
```console
./queue_study.py
```

### 去掉有道云笔记pc版广告
```console
自行修改path的值，运行即可
./remove_youdaonote_ads.py
```
