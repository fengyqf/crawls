# 词频统计器使用说明

## 运行环境： python 2.x版
如果没有安装，请从这里下载
https://www.python.org/downloads/
注意：请选择2.x版，*不要*使用3.x版；尽量使用64位版本。

强烈推荐使用64位版 (本脚本使用大量内存，可能超过4G，这是32位python所不能支持的)
windows下默认下载的安装包似乎是32位版，请注意手工选择
windows下推荐使用cygwin下的python，cygwin下有更多工具可用，python运行效率似乎更快一些


## windows下使用步骤
0. 将 run.py 放到一个空文件夹里，最好不要放在中文名的文件夹里；将rconfig.ini.sample复制一份，改名为 rconfig.ini (这是配置文件，可以处行编辑)
1. 将待统计词频的数据保存成纯文本格式(如txt, csv等)
2. 转化为utf-8编码(可使用notepad++, edit plus, ultra edit等工具另存为..., 编码选择utf-8)
3. 将utf-8编码的文件保存为 a.txt, 拷贝到run.py所在的文件夹里
4. 双击 run.py, 程序运行(可能花费较长时间，视a.txt文件大小及切词长度而定)
5. 等执行完毕后, 执行窗口将自动退出, 当前目录下会新出现新文件 output.txt, 即运行结果(tab键分隔的文件)
6. 可以通过“导入外部数据”功能将output.txt导入excel使用, 导入时注意编码为 65001/Unicode/UTF-8, 分隔符号为Tab键

## linux/maxosx下使用
将 run.py 放到一个空文件夹里；将rconfig.ini.sample复制一份，改名为 rconfig.ini
进入run.py所在目录python run.py
别的不需多说，很直接的


## 批量处理多个文件（逐个处理，非并行）
1. 将待处理的文件命名为 a_***.txt 的形式，放到run.py所在的文件夹里
2. 双击运行run.py


## 注意事项
1. 按上面步骤运行时，程序运行窗口中将显示的是乱码，这是windows默认ansi编码所致，这不影响运行结果。
2. 本程序运行通常要花费较长时间，示例：以10k的a.txt花费200秒（cygwin下执行效率有所提升，当前的run.py直接在windows下运行效率有明显提升，与cygwin下稍慢，但已没有成倍差距）
3. 如果运行run.py窗口立即消息，请先确认该目录下是否有 a.txt 文件，是否转换成utf-8编码
4. 如果有多个处理任务，推荐多任务同时执行。方法是将 run.py 分别复制到多个文件夹里，并分别准备a.txt文件，然后执行每个run.py
5. 每次执行，会将之前的 output.txt 文件（如果有）改名备份，因此不会丢失旧数结果数据。但还是建议每次处理将结果转移到其他文件夹
6. 如果待片文件较大，请考虑在cygwin下的python中运行，可能会有数倍的效率提升


## 高级使用说明
1. 本程序使用python标准库编写，不含非标准库，可以unix/linux/max osx/cygwin等环境下运行
2. 可以参考配置参数以实现个性化，具体参看后面一节“配置选项”
（注意，不要使用windows自带的记事本、word、写字板等工具编辑；推荐使用notepad++, edit plus, ultra edit等工具）
3. 测试发现本脚本在cygwin中运行速度比直接使用windows下双击快10倍以上，因此widnows下推荐使用cygwin环境


## 专题参考

### 将一系列文件快速改名成 a_***.txt的形式
在cygwin下操作，将所有文件（注意，文件名不能包含空格）放到一个空目录里，cygwin进入该目录，执行如下
for file in `ls`; do mv $file a_$file ;done

### 转换文件编码
windows下的txt文件通常是ansi编码，可以通过cygwin快速转编码
iconv -c -f gbk -t utf-8 your-file-name > your-file-utf8
一次转当前目录下的多个txt文件
for file in `ls -d *.txt`; do iconv -c -f gbk -t utf-8 $file > $file.utf8.txt; done


## 配置选项
配置文件是

注意，不要使用windows自带的记事本、word、写字板等工具编辑；推荐使用notepad++, edit plus, ultra edit等工具

word_width_min=2    // 切词时最短词长度
word_width_max=15   // 切词时最短词长度
output_words_min_count=3    // 输出结果时，输出最小词频次数；即只输出3次以上的词
debug=0             //输出调试信息，默认不输出，这样执行速度更快


//停止词，包含这些字符(串)的词将被忽略，而不做统计
stop_words=[',','，','。','．','、','"','“','”','：',' '
    ,'\n','\r','\t'
    ,'1','2','3','4','5','6','7','8','9','0'
    ,'１','２','３','４','５','６','７','８','９','０'
    ,'Ａ','Ｂ','Ｃ','Ｄ','Ｅ','Ｆ','Ｇ','Ｈ','Ｉ','Ｊ','Ｋ','Ｌ','Ｍ','Ｎ'
    ,'Ｏ','Ｐ','Ｑ','Ｒ','Ｓ','Ｔ','Ｕ','Ｖ','Ｗ','Ｘ','Ｙ','Ｚ'
    ,'ａ','ｂ','ｃ','ｄ','ｅ','ｆ','ｇ','ｈ','ｉ','ｊ','ｋ','ｌ','ｍ','ｎ'
    ,'ｏ','ｐ','ｑ','ｒ','ｓ','ｔ','ｕ','ｖ','ｗ','ｘ','ｙ','ｚ'
]

