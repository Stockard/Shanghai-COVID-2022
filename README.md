# Shanghai-COVID-2022

Data Sharing Portal
清理完毕的数据在 data/use/里可以看到

最新的工作流见[Notion链接](https://stockard-halfway.notion.site/9aace6bd589c490f8015f98d87ea735f?v=7b2a1b31be1a469d9f373e1cb0e59f0d)

# 使用方法
需要的包：codecs, requests, newspaper(newspaper3k), retrying, pandas

- 申请高德key 写入 keys.py #
  keys.py 没有在目录里，主要是定义gaode_ak, 防止key暴露

MACOS
运行 ./run.sh
  会生成卫健委的文件，但中间有一步需要手动 - 根据显示的微信文章地址把文章数据贴在最新几天的文件里。 -> raw/data/address
再次运行 ./run.sh

其他系统
按 ./run.sh的说明依次运行即可

# Tableau Viz

[点击查看](https://public.tableau.com/app/profile/stockard.feng/viz/_16494860765160/1)

# 项目整体框架

项目的目的在于提高上海数据的可见性。
此外，上海疫情发展要看每个街道和小区层面的处理，下一步是街道和小区路网的可视化。**

三月初上海的精准防疫建立在应测尽测，阳性闭环管理基础上。
**三月初防疫中漏掉的地区可能是系统性的遗漏，并不完全代表精准防疫的失败。** 而且目前疫情的来源也多半是这些遗漏的地区。


# 工作进度

- 数据获取和预处理
    - [x]  数据主要来源于上海发布，每天11点发布两条信息，一条包含宏观信息，一条包含详细的地址信息
    - [x]  原始数据获取 - 已经转为自动
    - [x]  清理出地址信息 - 目前的脚本可以把地址清出来，仅供参考
    - [x]  预处理：把地址转成经纬度，整理宏观数据
        - [x]  经纬度：包括，地址，经纬度，街道，小区。处理异常值
        - [x]  宏观数据：需要处理区一级和市一级的数据
- 数据清洗
    - [ ]  街道级别合并，地址数，新增地址数，趋势
    - [ ]  地址级别合并，新增地址标记
- 数据呈现
    - [ ]  搭一个网站快速可视化
    - [ ]  研究街道数据可视化



# Github上的项目链接
[疫情发布会通知](https://github.com/liurenjie520/Shanghai_COVID-19_Push)
[生活必需品词库](https://github.com/xuanskyer/shanghai_covid_19_goods)
[疫情数据分析](https://github.com/kekincai/shanghai_covid19)
[疫情地址viz](https://github.com/Xenofex/covid-shanghai-viz)
[各类疫情记录](https://github.com/000fan000/covid19-shanghai2022)

#其他
[上海生活指南](https://www.wolai.com/6TLbKJYT1JTq3cFqXTWVXC)

仅为记录，以守为攻
