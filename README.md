# 搜狗 scel 字典爬虫

## scrapy

进入 `sogou` 目录

运行 `scrapy crawl subtitle`

## scel 转成文本文件

scel 是 sogou 使用的 unicode 编码文件

开头 12 个字节是文件标识符 `\x40\x15\x00\x00\x44\x43\x53\x01\x01\x00\x00\x00` 如果前 12 字节不等于这个字符串，就不是 scel 文件

然后四段偏移位置是文件描述：

	data[0x130:0x338] 词库名
	data[0x338:0x540] 词库类型
	data[0x540:0xd40] 描述信息
	data[0xd40:0x1540] 词库示例
	
从 0x1540 开始到最后是字典内容  
字典分为两个部分：`全局拼音表` 和 `汉语词组表`

### 1.全局拼音表，貌似是所有的拼音组合，字典序
	格式为(index,len,pinyin)的列表
	index: 两个字节的整数 代表这个拼音的索引
	len: 两个字节的整数 拼音的字节长度
	pinyin: 当前的拼音，每个字符两个字节，总长len
	
### 2.汉语词组表
	格式为(same,py_table_len,py_table,{word_len,word,ext_len,ext})的一个列表
	same: 两个字节 整数 同音词数量
	py_table_len:  两个字节 整数
	py_table: 整数列表，每个整数两个字节,每个整数代表一个拼音的索引
	
	word_len:两个字节 整数 代表中文词组字节数长度
	word: 中文词组,每个中文汉字两个字节，总长度word_len
	ext_len: 两个字节 整数 代表扩展信息的长度，好像都是10
	ext: 扩展信息 前两个字节是一个整数(不知道是不是词频) 后八个字节全是0
	
	{word_len,word,ext_len,ext} 一共重复same次 同音词 相同拼音表