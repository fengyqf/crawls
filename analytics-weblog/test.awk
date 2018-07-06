#!/bin/awk -f

# 按指定格式将日期字符串转换为unix timestamp
#   为了避免在32位机器(?)上mktime()函数溢出问题(?)，故对不处理[1970-2038]之间年份，直接返回 0
#   使用时，可以依照情况注释掉该行


#运行前
BEGIN {

}

#运行中
{

    #s=sprintf("%s %s",$1,$2)
    #print s,"       ",fs_str2time(s,3,+8)

    #ext=sub(/\.[^\/]+(\/|$)/,$6,x)
    #print ext,x,$6

    #pos=match($3,/\.[a-zA-Z0-9]*(\/|$|\?)/)
    #print pos,$3



}


#运行后
END {


}
