(若没有安装pyecharts，anaconda prompt下执行： pip install pyecharts
若安装失败，可以查看这篇博文：https://blog.csdn.net/f823154/article/details/80671072)
1、执行 models.py 文件，在 teacher 库中生成 nlp_analysis 表 （环境若配置正确，执行 run.py 文件会自动在对应库下生成表）

2、入口程序 run.py

3、执行 run.py ，做如下三件事：
（1）根据提示输入对应关键词即可（源码见 server文件夹下 get_input_info.py）。比如首先会提示  请输入关键词（比如python）：
（2）从网站取得数据并存储到数据库，爬取到的结果信息保存在teacher库的nlp_analysis表中（源码见 server文件夹下 info_search.py）
（3）从nlp_analysis表中取得数据，通过jieba分词并做词频统计，最后生成对应图的html文件，存放于static文件夹下（源码见 server文件夹下 word_count.py）

4、rule文件夹中的 key_words.py 中可以添加不需要过滤的词组。

5、执行完成后，会自动在static下生成或覆盖bar_horizontal.html、pie.html、word_cloud.html 这三个html文件，
static 文件夹下的 bar_horizontal.html、pie.html、word_cloud.html 对应三种不同类型的图表，在浏览器中打开即可查看对应效果。
