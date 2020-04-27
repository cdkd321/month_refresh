月月生鲜项目

## 2020-04-07

1. 实现了注册和登录功能
2. 实现session保存用户密码，和勾选记住账户功能
3. 实现celery异步任务发邮件功能

## 2020-04-17
1. 实现了全文检索的配置
2. 实现了goods_sku表的索引建立
3. jieba分词和中文分词分析器的修改

## 2020-04-25
1. 添加数据内容：[dailyfresh](dailyfresh.sql)
    * 使用mysql进入命令行，创建数据库month_refresh(是的，我改名字了 月月生鲜 logo还没换)
    * 执行 `source dailyfresh.sql ` 命令，会导入数据
2. 实现了购物车功能
3. 实现了下单功能

todo 
   * 支付宝支付流程
   * 部署流程
   

## 运行环境要求说明：
   * ubuntu 等类unix系统
   * python 3.4 
   * django 1.8+
   * nginx 1.8.1
   * redis 
   * mysql 6.3+
   * virtualenv 环境
   * alibaba fdfs
   
上述环境配置和安装文件，在黄老师的教程中都有，请注意。

## 附带给出我自己的 pip list：
celery                3.1.25    
certifi               2020.4.5.1
cffi                  1.14.0    
chardet               3.0.4     
cryptography          2.8       
Django                1.8.2     
django-haystack       2.8.1     
django-redis          3.8.2     
django-redis-sessions 0.5.6     
django-tinymce        2.6.0     
fdfs-client-py        1.2.6     
idna                  2.8       
itsdangerous          1.1.0     
jieba                 0.42.1    
kombu                 3.0.37    
mutagen               1.42.0    
mysql                 0.0.2     
mysqlclient           1.4.6     
Pillow                5.4.1     
pip                   19.1.1    
pycparser             2.20      
pycryptodomex         3.9.4     
PyMySQL               0.9.3     
pyOpenSSL             19.1.0    
python-alipay-sdk     2.0.1     
pytz                  2019.3    
redis                 2.10.6    
requests              2.21.0    
setuptools            43.0.0   
six                   1.14.0    
urllib3               1.24.3    
vine                  1.3.0     
wheel                 0.33.6    
Whoosh                2.7.4
   

 