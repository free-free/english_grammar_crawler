### english_grammar_crawler
英语语法网(http://www.yingyuyufa.com/)爬虫

###一、功能描述

使用scrapy爬虫框架对[英语语法网](http://www.yingyuyufa.com/)的所有语法页面进行爬取，通过xpath解析出相关数据，
储存到bomb后端平台，并通过小程序将所有页面呈现出来。


###二、爬取策略

在仔细观察了[英语语法网](http://www.yingyuyufa.com/)的链接结构之后，发现它的链接是以语法名称来进行组织的树型结构
，即树的根节点链接是`http://www.yingyuyufa.com`，下一层节点链接是`http://www.yingyuyufa.com/cixing`,`http://www.yingyuyufa.com/jufa`
以此类推，直到到达以`.html`结尾的叶子节点，叶子节点才是真正语法页面。除叶子节点外，其他的节点都是列表页面，只表达语法之间的从属关系，
并没有真正的语法内容。为此有两种爬取策略。

#### **1. 深度优先爬取**
即先从根节点链接爬取，从根节点的页面中解析出下一层节点的链接，再任意选取一个节点继续进行爬取，不断递归下去，直到到达叶子节点。大体步骤如下：

　1. 爬取根节点，从根节点页面解析出下一层节点的链接；

　2. 随机选取未爬取的节点爬取，再从页面中解析出下一层节点链接；
　
　3. 判断当前要爬取的叶子链接是否以`.html`结尾，如果是，则说明已经爬取到叶子节点，则将页面内容保存下来，然后退回上一层，并选取一个节点进行爬取；如果否，则跳转到步骤2。不断的递归上述过程，直到爬取完所有页面。
　　
