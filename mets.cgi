#!/usr/bin/ruby -Ks
# encoding: utf-8

require("cgi")
require("sqlite3")

#htmlからの入力
input = CGI.new
#データベースを参照
db = SQLite3::Database.new("mets.db")

#----------計算部分----------
#一日あたりの目標METs時
Target_metsh = 23.0 / 7
#入力された運動のMETs時の合計値
metsh_sum = 0.0
#処理中の項目番号
i = 1

#入力された各項目についてループ（項目番号が存在する限りループ）
while input.has_key?("exercise" + i.to_s)
    #ExerciseIDで検索した結果
    exercise = db.execute("select * from METs where ExerciseID == ?;", input["exercise" + i.to_s]).flatten!
    #合計METs時加算
    metsh_sum += exercise[1].to_f * input["time" + i.to_s].to_f / 60
    #処理中の項目番号に加算
    i += 1
end


#----------表示部分----------

print("Content-type: text/plain; charset=UTF-8\n\n")
p metsh_sum
p Target_metsh
