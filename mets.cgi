#!/usr/bin/ruby -Ks
# -*- coding: utf-8 -*-

require("cgi")
require("csv")


#htmlからの入力
input = CGI.new
data = new Array
#運動METs表のCSV[[コード, METs, カテゴリ, 活動], ...]をコードをキーとして二次元ハッシュを作成
CSV.foreach("data.csv") do |row|
    data[row[0]] = {mets => row[1], category=> row[2], exercise => row[3]}
end

#入力された運動のMETs時の合計値
metsh_sum = 0
#処理中の項目番号
item_num = 1

#項目番号が存在する限りループ
while input.haskey?("excercize" + item_num)
    metsh_sum += data[input["exercize" + item_num]][mets] * input["time" + item_num].to_i / 60
    #処理中の項目番号に加算
    item_num += 1
end

print mets_sum